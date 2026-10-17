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

import bpy
import ifcopenshell.api.material
import ifcopenshell.api.root
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def add_beam(name, profile, location):
    ifc_file = tool.Ifc.get()
    element_type = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcBeamType", name=name)
    material = ifcopenshell.api.material.add_material(ifc_file, name=name)
    profile_set = ifcopenshell.api.material.add_material_set(ifc_file, name=name, set_type="IfcMaterialProfileSet")
    ifcopenshell.api.material.add_profile(ifc_file, profile_set=profile_set, material=material, profile=profile)
    ifcopenshell.api.material.assign_material(ifc_file, products=[element_type], material=profile_set)
    props = bpy.context.scene.BIMModelProperties
    props.ifc_class = "IfcBeamType"
    props.relating_type_id = str(element_type.id())
    bpy.context.scene.cursor.location = location
    bpy.ops.bim.add_occurrence()
    return bpy.context.active_object


def joined_end_x(obj, z):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return min((p.x for p in points if abs(p.z - z) < 1e-4), key=lambda x: abs(x - 1))


class TestExtendProfileToSlopedFace(NewFile):
    @pytest.mark.parametrize("start_x, bottom_x, top_x", [(3.0, 1.2, 1.4), (-5.0, 0.8, 0.6)])
    def test_extended_profile_meets_the_sloped_face(self, start_x, bottom_x, top_x):
        bpy.ops.bim.create_project()
        ifc_file = tool.Ifc.get()
        points = [(-0.2, -0.2), (0.2, -0.2), (0.4, 0.2), (-0.4, 0.2), (-0.2, -0.2)]
        sloped = ifc_file.createIfcArbitraryClosedProfileDef(
            "AREA", None, ifc_file.createIfcPolyline([ifc_file.createIfcCartesianPoint(p) for p in points])
        )
        target = add_beam("Sloped", sloped, (1, -2, 0))
        bpy.ops.bim.hotkey(hotkey="S_R")
        beam = add_beam(
            "Rectangle", ifc_file.createIfcRectangleProfileDef("AREA", None, None, 0.2, 0.4), (start_x, 0, 0)
        )
        bpy.ops.object.select_all(action="DESELECT")
        beam.select_set(True)
        target.select_set(True)
        bpy.context.view_layer.objects.active = target
        bpy.ops.bim.hotkey(hotkey="S_E")
        assert joined_end_x(beam, -0.2) == pytest.approx(bottom_x, abs=1e-4)
        assert joined_end_x(beam, 0.2) == pytest.approx(top_x, abs=1e-4)
