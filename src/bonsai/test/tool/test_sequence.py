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


import json
from datetime import datetime
from types import SimpleNamespace

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.sequence
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


class TestGetAnimationProductFrames(NewFile):
    def test_carrying_the_object_type_of_the_task(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc)
        task = ifcopenshell.api.sequence.add_task(ifc, work_schedule=schedule)
        task.PredefinedType = "USERDEFINED"
        task.ObjectType = "COLORRED"
        task_time = ifcopenshell.api.sequence.add_task_time(ifc, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            ifc, task_time=task_time, attributes={"ScheduleStart": "2026-01-01", "ScheduleFinish": "2026-01-10"}
        )
        wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
        ifcopenshell.api.sequence.assign_product(ifc, relating_product=wall, related_object=task)
        settings = {
            "start": datetime(2026, 1, 1),
            "duration": datetime(2026, 1, 10) - datetime(2026, 1, 1),
            "start_frame": 1,
            "total_frames": 100,
        }
        frames = subject.get_animation_product_frames(schedule, settings)
        assert [(f["type"], f["object_type"]) for f in frames[wall.id()]] == [("USERDEFINED", "COLORRED")]


class TestGetAnimationProductFramesAggregation(NewFile):
    def _setup(self, should_aggregate: bool):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(ifc, name="Schedule")
        parent = ifcopenshell.api.sequence.add_task(ifc, work_schedule=work_schedule, name="Parent")
        walls = []
        dates = ((datetime(2026, 1, 1), datetime(2026, 1, 3)), (datetime(2026, 1, 8), datetime(2026, 1, 10)))
        for i, (start, finish) in enumerate(dates):
            child = ifcopenshell.api.sequence.add_task(ifc, parent_task=parent, name=f"Child {i}")
            task_time = ifcopenshell.api.sequence.add_task_time(ifc, task=child)
            ifcopenshell.api.sequence.edit_task_time(
                ifc, task_time=task_time, attributes={"ScheduleStart": start, "ScheduleFinish": finish}
            )
            wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
            ifcopenshell.api.sequence.assign_product(ifc, relating_product=wall, related_object=child)
            walls.append(wall)
        props = tool.Sequence.get_work_schedule_props()
        props.should_aggregate_contracted_tasks = should_aggregate
        props.contracted_tasks = json.dumps([parent.id()])
        settings = {
            "start": datetime(2026, 1, 1),
            "finish": datetime(2026, 1, 10),
            "duration": datetime(2026, 1, 10) - datetime(2026, 1, 1),
            "start_frame": 1,
            "total_frames": 100,
        }
        return subject.get_animation_product_frames(work_schedule, settings), walls

    def test_contracted_task_animates_all_products_over_its_derived_range(self):
        frames, walls = self._setup(should_aggregate=True)
        assert frames[walls[0].id()] == frames[walls[1].id()]
        assert frames[walls[0].id()][0]["COMPLETED"] - frames[walls[0].id()][0]["STARTED"] > 100

    def test_products_keep_their_own_task_range_when_not_aggregating(self):
        frames, walls = self._setup(should_aggregate=False)
        assert frames[walls[0].id()][0]["COMPLETED"] < frames[walls[1].id()][0]["STARTED"]


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

    def test_using_the_color_of_the_object_type_for_a_userdefined_type(self):
        colors = {
            "USERDEFINED": SimpleNamespace(color=Color((0.5, 0.5, 0.5))),
            "COLORRED": SimpleNamespace(color=Color((1.0, 0.0, 0.0))),
        }
        assert subject.get_animation_color(colors, "USERDEFINED", "COLORRED")[:] == (1.0, 0.0, 0.0)

    def test_falling_back_to_the_userdefined_color_for_an_unknown_object_type(self):
        colors = {"USERDEFINED": SimpleNamespace(color=Color((0.5, 0.5, 0.5)))}
        assert subject.get_animation_color(colors, "USERDEFINED", "COLORRED")[:] == (0.5, 0.5, 0.5)
        assert subject.get_animation_color(colors, "USERDEFINED", "")[:] == (0.5, 0.5, 0.5)

    def test_ignoring_the_object_type_for_a_regular_predefined_type(self):
        colors = {
            "CONSTRUCTION": SimpleNamespace(color=Color((0.0, 1.0, 0.0))),
            "COLORRED": SimpleNamespace(color=Color((1.0, 0.0, 0.0))),
        }
        assert subject.get_animation_color(colors, "CONSTRUCTION", "COLORRED")[:] == (0.0, 1.0, 0.0)

    def test_falling_back_to_grey_without_any_matching_color(self):
        assert subject.get_animation_color({}, "USERDEFINED")[:] == pytest.approx((0.2, 0.2, 0.2))


class TestAddAnimationTaskTypeColor(NewFile):
    def test_adding_a_color_keyed_by_object_type(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        assert "COLORRED" in props.task_input_colors
        assert "COLORRED" not in props.task_output_colors

    def test_not_adding_a_blank_object_type(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("output", "  ")
        assert len(props.task_output_colors) == 0

    def test_not_duplicating_an_existing_entry(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        subject.add_animation_task_type_color("input", "COLORRED")
        assert len(props.task_input_colors) == 1


class TestRemoveAnimationTaskTypeColor(NewFile):
    def test_removing_the_active_color(self):
        bpy.ops.bim.create_project()
        props = tool.Sequence.get_animation_props()
        subject.add_animation_task_type_color("input", "COLORRED")
        props.active_color_component_inputs_index = 0
        subject.remove_animation_task_type_color("input")
        assert "COLORRED" not in props.task_input_colors
