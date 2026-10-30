# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Regression test for https://github.com/IfcOpenShell/IfcOpenShell/issues/5374

``bim.add_default_type`` gives duct and pipe segment types a sensible default
profile (rectangular / circular) when created without a preloaded type.
Cable carrier and cable segment types had no matching branch in
``AddDefaultType._execute`` (bonsai/bim/module/model/product.py), so they fell
through with a stale or empty ``representation_template`` and ended up with
no distinguishing default profile.

This pins that all four "Segment" tool defaults get their own predefined
type and profile shape, and that the fix does not disturb the pre-existing
duct/pipe defaults."""

import bpy
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.model


class TestAddDefaultTypeFlowSegments(NewIfc):
    @pytest.mark.parametrize(
        "ifc_class,expected_predefined_type,expected_profile_class",
        [
            ("IfcDuctSegmentType", "RIGIDSEGMENT", "IfcRectangleProfileDef"),
            ("IfcPipeSegmentType", "RIGIDSEGMENT", "IfcCircleProfileDef"),
            ("IfcCableCarrierSegmentType", "CABLETRAYSEGMENT", "IfcUShapeProfileDef"),
            ("IfcCableSegmentType", "CABLESEGMENT", "IfcCircleProfileDef"),
        ],
    )
    def test_default_type_gets_a_shaped_profile(self, ifc_class, expected_predefined_type, expected_profile_class):
        bpy.ops.bim.add_default_type(ifc_element_type=ifc_class)
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)

        assert element.is_a(ifc_class)
        assert element.PredefinedType == expected_predefined_type

        profile_set = ifcopenshell.util.element.get_material(element)
        assert profile_set is not None and profile_set.is_a("IfcMaterialProfileSet")
        profile = profile_set.MaterialProfiles[0].Profile
        assert profile.is_a(expected_profile_class)

    def test_cable_carrier_and_cable_do_not_reuse_a_cube_or_stale_profile(self):
        """Before the fix, creating a duct/pipe type first would leave
        ``representation_template`` set to a duct/pipe value, so a
        subsequently-created cable carrier or cable type silently inherited
        the wrong (or no) profile shape instead of its own default."""
        bpy.ops.bim.add_default_type(ifc_element_type="IfcDuctSegmentType")
        bpy.ops.bim.add_default_type(ifc_element_type="IfcPipeSegmentType")

        bpy.ops.bim.add_default_type(ifc_element_type="IfcCableCarrierSegmentType")
        carrier = tool.Ifc.get_entity(bpy.context.active_object)
        carrier_profile = ifcopenshell.util.element.get_material(carrier).MaterialProfiles[0].Profile
        assert carrier_profile.is_a("IfcUShapeProfileDef")

        bpy.ops.bim.add_default_type(ifc_element_type="IfcCableSegmentType")
        cable = tool.Ifc.get_entity(bpy.context.active_object)
        cable_profile = ifcopenshell.util.element.get_material(cable).MaterialProfiles[0].Profile
        assert cable_profile.is_a("IfcCircleProfileDef")
