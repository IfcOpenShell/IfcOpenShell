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

import bpy
import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit

from mathutils import Vector

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.tool.polyline import Polyline as subject
from test.bim.bootstrap import NewFile


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Polyline)


class TestValidateInput(NewFile):
    def test_simple_units(self):
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(ifc, [unit])
        unit_settings = bpy.context.scene.unit_settings
        unit_settings.system = "METRIC"
        assert subject.validate_input("25", "D") == (True, "25.0")
        unit.Prefix = "MILLI"
        unit_settings.length_unit = "MILLIMETERS"
        assert subject.validate_input("25", "D") == (True, "0.025")

        unit_settings.system = "IMPERIAL"
        unit = ifcopenshell.api.unit.add_conversion_based_unit(ifc, name="foot")
        ifcopenshell.api.unit.assign_unit(ifc, [unit])
        assert subject.validate_input("25", "D") == (True, "7.62")
        assert subject.validate_input("25'", "D") == (True, "7.62")
        assert subject.validate_input('25"', "D") == (True, "0.635")

        # Angle.
        assert subject.validate_input("25", "A") == (True, "25.0")


class TestCalculateDistanceAndAngle(NewFile):
    def test_it_does_not_crash_when_distance_is_zero_and_should_round(self, monkeypatch):
        # Regression test for #8597: right after placing the first polyline
        # point, the initial mouse sample can equal the last placed point
        # (distance == 0), e.g. entering the viewport on a YZ plane wall.
        # angle_round_threshold used to only be assigned in the
        # `distance > 0` branch, crashing when should_round reads it here.
        # get_increment_snap_value requires a real 3D viewport rv3d, which
        # is unrelated to this bug, so it's stubbed out for a headless run.
        monkeypatch.setattr(tool.Snap, "get_increment_snap_value", classmethod(lambda cls, context: 1.0))

        polyline_props = tool.Model.get_polyline_props()
        mouse_point = polyline_props.snap_mouse_point.add()
        mouse_point.x, mouse_point.y, mouse_point.z = 0, 0, 0

        tool_state = subject.create_tool_state()
        tool_state.is_input_on = False
        tool_state.use_default_container = False
        tool_state.plane_method = "YZ"

        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y", "Z"])

        subject.calculate_distance_and_angle(bpy.context, input_ui, tool_state, should_round=True)

        assert input_ui.get_number_value("D") == 0
        assert input_ui.get_number_value("A") == 0


class TestGetRectangleCorners(NewFile):
    def test_it_returns_the_corners_of_the_rectangle(self):
        corners = subject.get_rectangle_corners(Vector((1, 2, 3)), Vector((4, 6, 3)))
        assert [tuple(c) for c in corners] == [(1, 2, 3), (4, 2, 3), (4, 6, 3), (1, 6, 3)]

    def test_it_works_in_any_direction(self):
        corners = subject.get_rectangle_corners(Vector((0, 0, 0)), Vector((-2, -5, 0)))
        assert [tuple(c) for c in corners] == [(0, 0, 0), (-2, 0, 0), (-2, -5, 0), (0, -5, 0)]

    def test_it_rounds_the_sides_and_not_the_diagonal(self):
        corners = subject.get_rectangle_corners(Vector((0, 0, 0)), Vector((3.13, 4.79, 0)), round_factor=0.25)
        assert [tuple(c) for c in corners] == [(0, 0, 0), (3.25, 0, 0), (3.25, 4.75, 0), (0, 4.75, 0)]


class TestUpdateRectanglePolyline(NewFile):
    def create_polyline(self, first_corner, opposite_corner):
        polyline_props = tool.Model.get_polyline_props()
        mouse_point = polyline_props.snap_mouse_point.add()
        mouse_point.x, mouse_point.y, mouse_point.z = opposite_corner
        polyline_data = polyline_props.insertion_polyline.add()
        point = polyline_data.polyline_points.add()
        point.x, point.y, point.z = first_corner
        point.dim = "0"

        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y"])
        input_ui.set_value("X", opposite_corner[0])
        input_ui.set_value("Y", opposite_corner[1])
        input_ui.set_value("D", (Vector(opposite_corner) - Vector(first_corner)).length)
        input_ui.set_value("A", 0)

        tool_state = subject.create_tool_state()
        tool_state.is_input_on = False
        tool_state.use_default_container = False
        tool_state.plane_method = "XY"
        tool_state.plane_origin = Vector((0, 0, 0))
        tool_state.rectangle_mode = True
        return polyline_data, input_ui, tool_state

    def test_it_replaces_the_polyline_with_the_rectangle_corners(self):
        polyline_data, input_ui, tool_state = self.create_polyline((0, 0, 0), (5, 3, 0))

        subject.update_rectangle_polyline(input_ui, tool_state)

        # The first corner is repeated at the end so that the shape is closed.
        assert [(p.x, p.y, p.z) for p in polyline_data.polyline_points] == [
            (0, 0, 0),
            (5, 0, 0),
            (5, 3, 0),
            (0, 3, 0),
            (0, 0, 0),
        ]

    def test_it_rebuilds_the_rectangle_instead_of_growing_the_polyline(self):
        polyline_data, input_ui, tool_state = self.create_polyline((0, 0, 0), (5, 3, 0))

        subject.update_rectangle_polyline(input_ui, tool_state)
        input_ui.set_value("X", -2)
        input_ui.set_value("Y", 4)
        subject.update_rectangle_polyline(input_ui, tool_state)

        assert [(p.x, p.y, p.z) for p in polyline_data.polyline_points] == [
            (0, 0, 0),
            (-2, 0, 0),
            (-2, 4, 0),
            (0, 4, 0),
            (0, 0, 0),
        ]

    def test_it_keeps_the_side_dimensions_up_to_date(self):
        ifc = ifcopenshell.api.project.create_file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        unit = ifcopenshell.api.unit.add_si_unit(ifc, unit_type="LENGTHUNIT", prefix=None)
        ifcopenshell.api.unit.assign_unit(ifc, [unit])
        bpy.context.scene.unit_settings.system = "METRIC"
        polyline_data, input_ui, tool_state = self.create_polyline((0, 0, 0), (5, 3, 0))

        subject.update_rectangle_polyline(input_ui, tool_state)

        assert [p.dim for p in polyline_data.polyline_points][1:] == ["5.000 m", "3.000 m", "5.000 m", "3.000 m"]
        assert polyline_data.total_length == "16.000 m"

    def test_it_detects_a_rectangle_with_a_zero_length_side(self):
        polyline_data, input_ui, tool_state = self.create_polyline((0, 0, 0), (5, 3, 0))

        subject.update_rectangle_polyline(input_ui, tool_state)
        assert subject.is_rectangle_valid() is True

        input_ui.set_value("X", 0)
        subject.update_rectangle_polyline(input_ui, tool_state)
        assert subject.is_rectangle_valid() is False
