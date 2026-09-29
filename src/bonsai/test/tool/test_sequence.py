# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


from types import SimpleNamespace

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import pytest
from mathutils import Color

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.sequence import Sequence as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Sequence)


class TestGetElementStatus(NewFile):
    def test_common_pset(self):
        ifc = ifcopenshell.file()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "Pset_WallCommon")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}

    def test_epset(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        pset = ifcopenshell.api.pset.add_pset(ifc, element, "EPset_Status")
        ifcopenshell.api.pset.edit_pset(ifc, pset, properties={"Status": ["EXISTING", "TEMPORARY"]})
        assert subject.get_element_status(element) == {"EXISTING", "TEMPORARY"}


class TestAssignStatus(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=10, location=(0, 0, 4))
        obj = bpy.data.objects["Cube"]
        bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
        element = tool.Ifc.get_entity(obj)
        assert element

        bpy.ops.bim.assign_status(status="NEW")
        assert subject.get_element_status(element) == {"NEW"}

        bpy.ops.bim.assign_status(status="EXISTING")
        assert subject.get_element_status(element) == {"EXISTING"}

        bpy.ops.bim.assign_status(status="EXISTING", should_unassign_status=True)
        assert subject.get_element_status(element) == set()


class TestAnimateInputOutput(NewFile):
    def add_object(self):
        obj = bpy.data.objects.new("Object", None)
        bpy.context.scene.collection.objects.link(obj)
        subject.earliest_frame = None
        return obj

    def test_input_of_a_type_without_a_configured_color(self):
        obj = self.add_object()
        subject.animate_input(obj, 0, {"type": "USERDEFINED", "STARTED": 1, "COMPLETED": 10}, "snapshot")
        assert obj.animation_data.action

    def test_output_of_a_type_without_a_configured_color(self):
        obj = self.add_object()
        subject.animate_output(obj, 0, {"type": "USERDEFINED", "STARTED": 1, "COMPLETED": 10}, "snapshot")
        assert obj.animation_data.action


class TestGetAnimationColor(NewFile):
    def test_using_the_color_of_the_predefined_type(self):
        colors = {
            "CONSTRUCTION": SimpleNamespace(color=Color((1.0, 0.0, 0.0))),
            "NOTDEFINED": SimpleNamespace(color=Color((0.0, 1.0, 0.0))),
        }
        assert subject.get_animation_color(colors, "CONSTRUCTION")[:] == (1.0, 0.0, 0.0)

    def test_falling_back_to_the_notdefined_color_for_a_missing_predefined_type(self):
        colors = {"NOTDEFINED": SimpleNamespace(color=Color((0.0, 1.0, 0.0)))}
        assert subject.get_animation_color(colors, "USERDEFINED")[:] == (0.0, 1.0, 0.0)
        assert subject.get_animation_color(colors, None)[:] == (0.0, 1.0, 0.0)

    def test_falling_back_to_grey_without_any_matching_color(self):
        assert subject.get_animation_color({}, "USERDEFINED")[:] == pytest.approx((0.2, 0.2, 0.2))
