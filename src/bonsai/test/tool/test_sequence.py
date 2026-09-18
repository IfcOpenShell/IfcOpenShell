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

import os

import bpy
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.pset
import ifcopenshell.api.root

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


class TestGetTaskTypeColor(NewFile):
    """A task's PredefinedType USERDEFINED collapses every custom task into a single
    grey colour. These tests cover ObjectType being consulted as a finer colour key
    in that case, per https://github.com/IfcOpenShell/IfcOpenShell/issues/2748."""

    def test_uses_the_object_type_colour_when_predefined_type_is_userdefined_and_it_exists(self):
        from unittest.mock import Mock

        colors = {"USERDEFINED": Mock(color="grey"), "COLORRED": Mock(color="red")}
        product_frame = {"type": "USERDEFINED", "object_type": "COLORRED"}
        assert subject.get_task_type_color(colors, product_frame) == "red"

    def test_falls_back_to_the_userdefined_colour_when_no_object_type_colour_exists(self):
        from unittest.mock import Mock

        colors = {"USERDEFINED": Mock(color="grey")}
        product_frame = {"type": "USERDEFINED", "object_type": "COLORRED"}
        assert subject.get_task_type_color(colors, product_frame) == "grey"

    def test_falls_back_to_the_userdefined_colour_when_object_type_is_empty(self):
        from unittest.mock import Mock

        colors = {"USERDEFINED": Mock(color="grey")}
        product_frame = {"type": "USERDEFINED", "object_type": ""}
        assert subject.get_task_type_color(colors, product_frame) == "grey"

    def test_ignores_object_type_for_a_regular_predefined_type(self):
        from unittest.mock import Mock

        colors = {"CONSTRUCTION": Mock(color="green"), "COLORRED": Mock(color="red")}
        product_frame = {"type": "CONSTRUCTION", "object_type": "COLORRED"}
        assert subject.get_task_type_color(colors, product_frame) == "green"


class TestAddAnimationTaskTypeColor(NewFile):
    def test_adds_a_new_colour_keyed_by_object_type(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        assert "COLORRED" in props.task_input_colors
        assert "COLORRED" not in props.task_output_colors

    def test_does_not_add_a_blank_object_type(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("output", "  ")
        assert len(props.task_output_colors) == 0

    def test_does_not_duplicate_an_existing_entry(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        subject.add_animation_task_type_color("input", "COLORRED")
        assert len(props.task_input_colors) == 1


class TestRemoveAnimationTaskTypeColor(NewFile):
    def test_removes_the_active_colour(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        props.active_color_component_inputs_index = 0
        subject.remove_animation_task_type_color("input")
        assert "COLORRED" not in props.task_input_colors
