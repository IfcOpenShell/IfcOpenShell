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
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit

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


class TestPolylineUIUnsetField(NewFile):
    def test_get_number_value_returns_none_for_an_unset_field(self):
        # Regression test: pressing "D" clears `_D` to "" to accept fresh
        # typing (bim/module/model/polyline.py). If the user tabs away before
        # typing a digit, `_D` stays "" rather than becoming a real number.
        # get_number_value() used to return that raw "" instead of None,
        # which crashed downstream code that only guards against None
        # (format_input_ui_units's `value / unit_scale`, and
        # calculate_x_y_and_z's `distance < 0 or distance > 0`).
        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y"])
        assert input_ui.get_number_value("D") is None
        assert input_ui.get_formatted_value("D") is None

    def test_it_does_not_crash_when_distance_has_not_been_typed_yet(self, monkeypatch):
        monkeypatch.setattr(tool.Snap, "get_increment_snap_value", classmethod(lambda cls, context: 1.0))

        polyline_props = tool.Model.get_polyline_props()
        mouse_point = polyline_props.snap_mouse_point.add()
        mouse_point.x, mouse_point.y, mouse_point.z = 1, 2, 0

        tool_state = subject.create_tool_state()
        tool_state.is_input_on = True
        tool_state.use_default_container = True

        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y"])
        input_ui.set_value("X", 1)
        input_ui.set_value("Y", 2)
        input_ui.set_value("A", 0)
        # "D" left unset, as if "D" was pressed but nothing typed before Tab.

        subject.calculate_x_y_and_z(bpy.context, input_ui, tool_state)

    def test_it_does_not_crash_for_a_2d_only_tool_with_no_z_input(self, monkeypatch):
        # Regression test: the alignment horizontal-draw tool (a plan/XY-only
        # workflow) sets use_default_container=False but, unlike
        # DrawPolylineProfile, never adds "Z" to input_options — so `_Z` is
        # never given a value. calculate_distance_and_angle/calculate_x_y_and_z
        # used to build `Vector((x, y, input_ui.get_number_value("Z")))`
        # unconditionally in the `is_input_on and not use_default_container`
        # branch, crashing with a None/str third component as soon as the
        # user tabbed into "D" or "A" (bim/module/alignment/operator.py's
        # ALIGN_OT_draw_horizontal_alignment).
        monkeypatch.setattr(tool.Snap, "get_increment_snap_value", classmethod(lambda cls, context: 1.0))

        polyline_props = tool.Model.get_polyline_props()
        mouse_point = polyline_props.snap_mouse_point.add()
        mouse_point.x, mouse_point.y, mouse_point.z = 1, 2, 0

        tool_state = subject.create_tool_state()
        tool_state.is_input_on = True
        tool_state.use_default_container = False
        tool_state.plane_method = "XY"

        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y"])
        input_ui.set_value("X", 1)
        input_ui.set_value("Y", 2)
        input_ui.set_value("A", 0)
        input_ui.set_value("D", 5)

        subject.calculate_x_y_and_z(bpy.context, input_ui, tool_state)
        subject.calculate_distance_and_angle(bpy.context, input_ui, tool_state)


class TestCalculateXYAndZStraightOn(NewFile):
    def _setup(self, points, mouse):
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline.add()
        for x, y in points:
            point = polyline_data.polyline_points.add()
            point.x, point.y, point.z = x, y, 0
        mouse_point = polyline_props.snap_mouse_point.add()
        mouse_point.x, mouse_point.y, mouse_point.z = mouse[0], mouse[1], 0
        tool_state = subject.create_tool_state()
        tool_state.is_input_on = True
        tool_state.use_default_container = False
        tool_state.plane_method = "XY"
        input_ui = subject.create_input_ui(input_options=["D", "A", "X", "Y", "Z"])
        input_ui.set_value("X", mouse[0])
        input_ui.set_value("Y", mouse[1])
        input_ui.set_value("Z", 0)
        return tool_state, input_ui

    def test_180_degrees_continues_a_diagonal_leg_straight_on(self):
        # Regression test: a typed angle of exactly 180 used to force the direction's x to -1,
        # which is only right for a leg along +X -- a 45 degree leg sent the point the wrong way.
        tool_state, input_ui = self._setup([(0, 0), (10, 10)], mouse=(30, 0))
        for angle in (180, -180):
            input_ui.set_value("D", 5)
            input_ui.set_value("A", angle)
            subject.calculate_x_y_and_z(bpy.context, input_ui, tool_state)
            assert round(input_ui.get_number_value("X"), 6) == round(10 + 5 / 2**0.5, 6)
            assert round(input_ui.get_number_value("Y"), 6) == round(10 + 5 / 2**0.5, 6)

    def test_180_degrees_from_a_single_point_still_goes_along_negative_x(self):
        # The old special case's intended behaviour: with one point, angles are measured from +X.
        tool_state, input_ui = self._setup([(1, 2)], mouse=(1, 2))
        input_ui.set_value("D", 3)
        input_ui.set_value("A", 180)
        subject.calculate_x_y_and_z(bpy.context, input_ui, tool_state)
        assert round(input_ui.get_number_value("X"), 6) == -2
        assert round(input_ui.get_number_value("Y"), 6) == 2
