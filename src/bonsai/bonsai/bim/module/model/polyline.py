# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bruno Perdigão <contact@brunopo.com>
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

from __future__ import annotations

from typing import Literal, Union

import bpy
import ifcopenshell
import ifcopenshell.util.unit
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.model.decorator import PolylineDecorator


class PolylineOperator:
    # TODO Fill doc strings
    """ """

    objs_2d_bbox: list[tuple[bpy.types.Object, list[float]]]

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.space_data.type == "VIEW_3D"

    def __init__(self):
        self.mousemove_count = 0
        self.action_count = 0
        self.visible_objs = []
        self.objs_2d_bbox = []
        self.number_options = {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            " ",
            ".",
            "+",
            "-",
            "*",
            "/",
            "'",
            '"',
            "=",
        }
        self.number_input = []
        self.number_output = ""
        self.number_is_negative = False
        self.input_options = ["D", "A", "X", "Y"]
        self.input_type = None
        self.input_value_xy = [None, None]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)
        self.is_typing = False
        self.snap_angle = None
        self.snapping_points = []
        self.unit_scale = 1.0
        self.instructions = {
            "Cycle Input": {"icons": True, "keys": ["EVENT_TAB"]},
            "Distance Input": {"icons": True, "keys": ["EVENT_D"]},
            "Angle Lock": {"icons": True, "keys": ["EVENT_A"]},
            "Increment Angle": {"icons": True, "keys": ["EVENT_SHIFT", "MOUSE_MMB_SCROLL"]},
            "Modify Snap Point": {"icons": True, "keys": ["EVENT_M"]},
            "Close Polyline": {"icons": True, "keys": ["EVENT_C"]},
            "Offset": {"icons": True, "keys": ["EVENT_O"]},
            "Remove Point": {"icons": True, "keys": ["EVENT_BACKSPACE"]},
        }

        self.info = [
            "Axis: ",
            "Plane: ",
            "Snap: ",
        ]

        self.tool_state = tool.Polyline.create_tool_state()

    def recalculate_inputs(self, context: bpy.types.Context) -> Union[bool, None]:
        if self.number_input:
            is_valid, self.number_output = tool.Polyline.validate_input(self.number_output, self.input_type)
            self.input_ui.set_value(self.input_type, self.number_output)
            if not is_valid:
                self.report({"WARNING"}, "The number typed is not valid.")
                return is_valid
            else:
                if self.input_type in {"X", "Y", "Z"}:
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                elif self.input_type in {"D", "A"}:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                else:
                    self.input_ui.set_value(self.input_type, self.number_output)
            tool.Blender.update_viewport()
            return is_valid

    def choose_axis(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = False) -> None:
        options = {"X", "Y"}
        if z:
            options = {"X", "Y", "Z"}
        if not event.shift and event.value == "PRESS" and event.type in options:
            self.tool_state.axis_method = event.type if self.tool_state.axis_method != event.type else None
            if self.tool_state.axis_method is not None:
                self.tool_state.lock_axis = True
            else:
                self.tool_state.lock_axis = False
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def choose_plane(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = True) -> None:
        def get_plane_origin():
            polyline_props = tool.Model.get_polyline_props()
            polyline_data = polyline_props.insertion_polyline
            polyline_points = polyline_data[0].polyline_points if polyline_data else []
            if len(polyline_points) > 0:
                reference_point = polyline_points[-1]
            else:
                reference_point = Vector((0.0, 0.0, 0.0))
            self.tool_state.plane_origin = Vector((reference_point.x, reference_point.y, reference_point.z))

        if x:
            if event.shift and event.value == "PRESS" and event.type == "X":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "YZ" if self.tool_state.plane_method != "YZ" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()
                get_plane_origin()

        if y:
            if event.shift and event.value == "PRESS" and event.type == "Y":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XZ" if self.tool_state.plane_method != "XZ" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()
                get_plane_origin()

        if z:
            if event.shift and event.value == "PRESS" and event.type == "Z":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XY" if self.tool_state.plane_method != "XY" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()
                get_plane_origin()

    def handle_instructions(
        self, context: bpy.types.Context, custom_instructions: dict = {}, custom_info: str = "", overwrite: bool = False
    ) -> None:
        self.info = [
            f"Axis: {self.tool_state.axis_method}",
            f"Plane: {self.tool_state.plane_method}",
            f"Snap: {self.snapping_points[0]['type']}",
        ]
        instructions = self.instructions | custom_instructions if custom_instructions else self.instructions
        infos = self.info + custom_info if custom_info else self.info

        if overwrite:
            instructions = custom_instructions
            infos = custom_info

        def draw_instructions(self: bpy.types.Header, context: bpy.types.Context) -> None:
            for action, settings in instructions.items():
                if settings["icons"]:
                    for key in settings["keys"]:
                        if bpy.app.version < (4, 3, 0) and key == "MOUSE_MMB_SCROLL":
                            self.layout.label(text="MMB")
                        else:
                            self.layout.label(text="", icon=key)
                    self.layout.label(text=action)
                else:
                    key = settings["keys"][0]
                    self.layout.label(text=key + action)

            if infos:
                self.layout.label(text="|")
                for info in infos:
                    self.layout.label(text=info)

        context.workspace.status_text_set(draw_instructions)

    def handle_lock_axis(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        angle_snap = tool.Snap.get_angle_snap_value(context)
        if event.value == "PRESS" and event.type == "A":
            self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
            if self.tool_state.lock_axis:
                self.tool_state.snap_angle = self.input_ui.get_number_value("WORLD_ANGLE")
                self.tool_state.snap_angle = round(self.tool_state.snap_angle / angle_snap) * angle_snap

        if event.shift and event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.tool_state.lock_axis = True
            self.tool_state.snap_angle = self.input_ui.get_number_value("WORLD_ANGLE")
            self.tool_state.snap_angle = round(self.tool_state.snap_angle / angle_snap) * angle_snap
            if event.type in {"WHEELUPMOUSE"}:
                self.tool_state.snap_angle += angle_snap
            else:
                self.tool_state.snap_angle -= angle_snap
            self.handle_mouse_move(context, event)
            detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
            self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
            tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def handle_keyboard_input(self, context: bpy.types.Context, event: bpy.types.Event) -> None:

        if self.tool_state.is_input_on and event.value == "PRESS" and event.type == "TAB":
            self.recalculate_inputs(context)
            index = self.input_options.index(self.input_type)
            size = len(self.input_options)
            self.input_type = self.input_options[((index + 1) % size)]
            self.tool_state.input_type = self.input_options[((index + 1) % size)]
            self.tool_state.mode = "Select"
            self.is_typing = False
            self.number_input = self.input_ui.get_formatted_value(self.input_type)
            self.number_input = list(self.number_input)
            self.number_output = "".join(self.number_input)
            self.input_ui.set_value(self.input_type, self.number_output)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type == "TAB":
            self.recalculate_inputs(context)
            self.tool_state.mode = "Select"
            self.tool_state.is_input_on = True
            self.input_type = "D"
            self.tool_state.input_type = "D"
            self.is_typing = False
            self.number_input = self.input_ui.get_formatted_value(self.input_type)
            self.number_input = list(self.number_input)
            self.number_output = "".join(self.number_input)
            self.input_ui.set_value(self.input_type, self.number_output)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on and event.ascii in self.number_options:
            self.recalculate_inputs(context)
            self.tool_state.mode = "Edit"
            self.tool_state.is_input_on = True
            self.input_type = "D"
            self.tool_state.input_type = "D"
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if event.value == "RELEASE" and event.type == "D":
            self.recalculate_inputs(context)
            self.tool_state.mode = "Edit"
            self.tool_state.is_input_on = True
            self.input_type = event.type
            self.tool_state.input_type = event.type
            self.input_ui.set_value(self.input_type, "")
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if self.input_type in self.input_options:
            if (event.ascii in self.number_options) or (event.value == "RELEASE" and event.type == "BACK_SPACE"):
                if not self.tool_state.mode == "Edit" and not (event.ascii == "=" or event.type == "BACK_SPACE"):
                    self.number_input = []

                if event.type == "BACK_SPACE":
                    if len(self.number_input) <= 1:
                        self.number_input = []
                    else:
                        self.number_input.pop(-1)
                elif event.ascii == "=":
                    if self.number_input and self.number_input[0] == "=":
                        self.number_input.pop(0)
                    else:
                        self.number_input.insert(0, "=")
                else:
                    self.number_input.append(event.ascii)

                if not self.number_input:
                    self.number_output = "0"

                self.tool_state.mode = "Edit"
                self.is_typing = True
                self.number_output = "".join(self.number_input)
                self.input_ui.set_value(self.input_type, self.number_output)
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()

    def handle_inserting_polyline(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type == "LEFTMOUSE":
            result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
            if result:
                self.report({"WARNING"}, result)
            tool.Blender.update_viewport()

        if event.value == "PRESS" and event.type == "C":
            # Get the first point coordinates to close the polyline
            polyline_props = tool.Model.get_polyline_props()
            polyline_data = polyline_props.insertion_polyline
            polyline_points = polyline_data[0].polyline_points if polyline_data else []
            if len(polyline_points) > 2:
                first_point = polyline_points[0]
                last_point = polyline_points[-1]
                if not (
                    first_point.x == last_point.x and first_point.y == last_point.y and first_point.z == last_point.z
                ):
                    mouse_point = polyline_props.snap_mouse_point[0]
                    mouse_point.x = first_point.x
                    mouse_point.y = first_point.y
                    if self.input_ui.get_number_value("Z") is not None:
                        mouse_point.z = first_point.z
                    else:
                        mouse_point.z = 0
                tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
            result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
            if result:
                self.report({"WARNING"}, result)

            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if (
            self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            is_valid = self.recalculate_inputs(context)
            if is_valid:
                result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                if result:
                    self.report({"WARNING"}, result)

            self.tool_state.mode = "Mouse"
            self.tool_state.is_input_on = False
            self.input_type = None
            self.tool_state.input_type = None
            self.number_input = []
            self.number_output = ""
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on:
            if event.value == "RELEASE" and event.type == "BACK_SPACE":
                tool.Polyline.remove_last_polyline_point()
                tool.Blender.update_viewport()

    def handle_snap_selection(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if not self.tool_state.is_input_on and event.value == "PRESS" and event.type == "M":
            self.snapping_points = tool.Snap.modify_snapping_point_selection(
                self.snapping_points, lock_axis=self.tool_state.lock_axis
            )
            tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def handle_cancelation(
        self, context: bpy.types.Context, event: bpy.types.Event
    ) -> Union[None, set[Literal["CANCELLED"]]]:
        if self.tool_state.is_input_on:
            if event.value == "RELEASE" and event.type in {"ESC", "LEFTMOUSE"}:
                self.recalculate_inputs(context)
                self.tool_state.mode = "Mouse"
                self.tool_state.is_input_on = False
                self.input_type = None
                self.tool_state.input_type = None
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()
        else:
            if event.value == "RELEASE" and event.type in {"ESC"}:
                self.tool_state.axis_method = None
                self.tool_state.plane_method = None
                context.workspace.status_text_set(text=None)
                PolylineDecorator.uninstall()
                tool.Polyline.clear_polyline()
                tool.Blender.update_viewport()
                return {"CANCELLED"}

    def handle_mouse_move(
        self, context: bpy.types.Context, event: bpy.types.Event, should_round: bool = False
    ) -> Union[None, set[Literal["RUNNING_MODAL"]]]:
        if not self.tool_state.is_input_on:
            if event.type == "MOUSEMOVE" or event.type == "INBETWEEN_MOUSEMOVE":
                self.mousemove_count += 1
                self.tool_state.mode = "Mouse"
                self.tool_state.is_input_on = False
                self.input_type = None
                self.tool_state.input_type = None
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Snap.clear_snapping_ref()
                tool.Blender.update_viewport()
            else:
                self.mousemove_count = 0

            if self.mousemove_count == 2:
                self.objs_2d_bbox = []
                for obj in self.visible_objs:
                    if bbox_2d := tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj):
                        self.objs_2d_bbox.append(bbox_2d)

            if self.mousemove_count > 3:
                detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
                self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)

                if self.snapping_points[0]["type"] not in {"Plane", "Axis"}:
                    should_round = False

                tool.Polyline.calculate_distance_and_angle(
                    context, self.input_ui, self.tool_state, should_round=should_round
                )
                if should_round:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)

                tool.Blender.update_viewport()
            return {"RUNNING_MODAL"}

    def set_offset(self, context: bpy.types.Context, relating_type: ifcopenshell.entity_instance) -> None:
        props = tool.Model.get_model_props()
        direction_sense = props.direction_sense
        if tool.Model.get_usage_type(relating_type) == "LAYER2":
            offset_type = "offset_type_vertical"
            direction = 1 if direction_sense == "POSITIVE" else -1
        elif tool.Model.get_usage_type(relating_type) == "LAYER3":
            offset_type = "offset_type_horizontal"
            direction = 1
        else:
            return

        layers = tool.Model.get_material_layer_parameters(relating_type)
        thickness = layers["thickness"]
        self.offset = 0
        if getattr(props, offset_type) == "CENTER":
            self.offset = (-thickness / 2) * direction
        elif getattr(props, offset_type) in {"INTERIOR", "TOP"}:
            self.offset = -thickness * direction

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.offset = self.offset / self.unit_scale
        tool.Blender.update_viewport()

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> Union[set[str], None]:
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            return {"PASS_THROUGH"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        PolylineDecorator.install(context)
        tool.Snap.clear_snapping_point()

        self.tool_state.use_default_container = False
        self.tool_state.axis_method = None
        self.tool_state.plane_method = None
        self.tool_state.mode = "Mouse"
        tool.Raycast.clear_snap_objs()
        self.visible_objs = tool.Raycast.get_visible_objects(context)
        for obj in self.visible_objs:
            if bbox_2d := tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj):
                self.objs_2d_bbox.append(bbox_2d)
        detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
        self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
        tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)

        tool.Blender.update_viewport()
        context.window_manager.modal_handler_add(self)
