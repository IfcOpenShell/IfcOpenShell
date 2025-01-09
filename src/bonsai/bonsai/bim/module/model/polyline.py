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
import bpy
import copy
import math
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.type
import mathutils.geometry
import bonsai.core.type
import bonsai.core.root
import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from math import pi, sin, cos, degrees
from mathutils import Vector, Matrix
from bonsai.bim.module.model.opening import FilledOpeningGenerator
from bonsai.bim.module.model.decorator import PolylineDecorator
from typing import Optional, Union, Literal
from lark import Lark, Transformer


def get_profile_preview_data(context, relating_type):
    material = ifcopenshell.util.element.get_material(relating_type)
    try:
        profile_curve = material.MaterialProfiles[0].Profile
    except:
        return {}

    model_props = context.scene.BIMModelProperties
    cardinal_point = model_props.cardinal_point

    polyline_verts = []
    polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
    polyline_points = polyline_data[0].polyline_points if polyline_data else []
    if len(polyline_points) < 2:
        return
    for point in polyline_points:
        polyline_verts.append(Vector((point.x, point.y, point.z)))
    polyline_edges = [(i, i+1) for i in range(len(polyline_verts)-1)]

    # Get profile shape
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
    shape = ifcopenshell.geom.create_shape(settings, profile_curve)

    verts = shape.verts
    if not verts:
        raise RuntimeError("Profile shape has no vertices, it probably is invalid.")

    edges = shape.edges

    grouped_verts = [[verts[i], verts[i + 1], 0] for i in range(0, len(verts), 3)]
    grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

    # Create offsets based on cardinal point
    min_x = min(v[0] for v in grouped_verts)
    max_x = max(v[0] for v in grouped_verts)
    min_y = min(v[1] for v in grouped_verts)
    max_y = max(v[1] for v in grouped_verts)

    x_offset = (max_x - min_x) / 2
    y_offset = (max_y - min_y) / 2

    match cardinal_point:
        case "1":
            grouped_verts = [(v[0] - x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "2":
            grouped_verts = [(v[0], v[1] + y_offset, v[2]) for v in grouped_verts]
        case "3":
            grouped_verts = [(v[0] + x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "4":
            grouped_verts = [(v[0] - x_offset, v[1], v[2]) for v in grouped_verts]
        case "5":
            grouped_verts = [(v[0], v[1], v[2]) for v in grouped_verts]
        case "6":
            grouped_verts = [(v[0] + x_offset, v[1], v[2]) for v in grouped_verts]
        case "7":
            grouped_verts = [(v[0] - x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]
        case "8":
            grouped_verts = [(v[0], v[1] - y_offset, v[2]) for v in grouped_verts]
        case "9":
            grouped_verts = [(v[0] + x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]


    # Create profile curve
    scale_mat = Matrix.Scale(-1, 4, (1.0, 0.0, 0.0))
    grouped_verts = [scale_mat @ Vector(v) for v in grouped_verts]
    profile_curve = bpy.data.curves.new("Profile", type='CURVE')
    profile_curve.dimensions = "2D"
    profile_curve.splines.new('POLY')
    profile_curve.splines[0].points.add(len(grouped_verts))

    for i, point in enumerate(profile_curve.splines[0].points):
        if i == len(grouped_verts): # Close curve
            point.co = Vector((*grouped_verts[0], 0))
            continue
        point.co = Vector((*grouped_verts[i], 0))
    profile_obj = bpy.data.objects.new("Profile", profile_curve)

    # Create path curve with profile object as bevel
    path_curve = bpy.data.curves.new("Polyline", type='CURVE')
    path_curve.dimensions = "2D"
    path_curve.splines.new('POLY')
    path_curve.splines[0].points.add(len(polyline_verts) - 1)
    for i, point in enumerate(path_curve.splines[0].points):
        point.co = Vector((*polyline_verts[i], 0))
    path_curve.splines[0].use_smooth = False
    path_curve.bevel_mode = "OBJECT"
    path_curve.bevel_object = profile_obj

    # Convert path curve to mesh
    # This operation throws a warning when done during gpu drawing, so it was removed from the decorator file to be handled here 
    path_obj = bpy.data.objects.new("Preview", path_curve)
    context.scene.collection.objects.link(path_obj)
    bpy.context.view_layer.objects.active = path_obj
    dg = context.evaluated_depsgraph_get()
    path_obj = path_obj.evaluated_get(dg) 
    me = path_obj.to_mesh()

    # Create bmesh from path mesh
    bm = bmesh.new()
    new_verts = [bm.verts.new(v.co) for v in me.vertices]
    index = [[v for v in edge.vertices] for edge in me.edges]
    new_edges = [bm.edges.new((new_verts[i[0]], new_verts[i[1]])) for i in index]
    for face in me.polygons:
        verts = [new_verts[i] for i in face.vertices]
        bm.faces.new(verts)
    bm.verts.index_update()
    bm.edges.index_update()
    tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

    bpy.data.objects.remove(bpy.data.objects[path_obj.name], do_unlink=True)
    bpy.data.objects.remove(bpy.data.objects[profile_obj.name], do_unlink=True)
    try:
        bpy.data.curves.remove(profile_obj.data, do_unlink=True)
    except:
        pass
    try:
        bpy.data.curves.remove(path_obj.data, do_unlink=True)
    except:
        pass

    data = {}
    data["verts"] = [tuple(v.co) for v in bm.verts]
    data["edges"] = [(edge.verts[0].index, edge.verts[1].index) for edge in bm.edges]
    data["tris"] = tris

    # Update properties so it can be used by the decorator
    props = context.scene.BIMProductPreviewProperties
    props.verts.clear()
    props.edges.clear()
    props.tris.clear()
        
    for vert in data["verts"]:
        v = props.verts.add()
        v.value = vert
    for edge in data["edges"]:
        e = props.edges.add()
        e.tvalue = edge
    for tri in data["tris"]:
        t = props.tris.add()
        t.value = tri

    bm.free()

class PolylineOperator:
    # TODO Fill doc strings
    """ """

    number_input: list[str]
    input_type: tool.Polyline.InputType

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
        self.input_ui = tool.Polyline.create_input_ui()
        self.is_typing = False
        self.snap_angle = None
        self.snapping_points = []
        self.instructions = """TAB: Cycle Input
        D: Distance Input
        A: Angle Lock
        M: Modify Snap Point
        C: Close Polyline
        BACKSPACE: Remove Point
        X, Y: Choose Axis
        """
        self.snap_info = """
        Snap: 
        Axis:
        Plane: 
        """

        self.tool_state = tool.Polyline.create_tool_state()

    def recalculate_inputs(self, context: bpy.types.Context) -> Union[bool, None]:
        if self.number_input:
            is_valid, self.number_output = tool.Polyline.validate_input(self.number_output, self.input_type)
            self.input_ui.set_value(self.input_type, self.number_output)
            if not is_valid:
                self.report({"WARNING"}, "The number typed is not valid.")
                return is_valid
            else:
                if self.input_type in {"X", "Y"}:
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                elif self.input_type in {"D", "A"}:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                else:
                    self.input_ui.set_value(self.input_type, self.number_output)
            tool.Blender.update_viewport()
            return is_valid

    def choose_axis(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = False) -> None:
        if x:
            if not event.shift and event.value == "PRESS" and event.type == "X":
                self.tool_state.axis_method = "X" if self.tool_state.axis_method != event.type else None
                self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()

        if y:
            if not event.shift and event.value == "PRESS" and event.type == "Y":
                self.tool_state.axis_method = "Y" if self.tool_state.axis_method != event.type else None
                self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()
        if z:
            if not event.shift and event.value == "PRESS" and event.type == "Z":
                self.tool_state.axis_method = "Z" if self.tool_state.axis_method != event.type else None
                self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()

    def choose_plane(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = True) -> None:
        if x:
            if event.shift and event.value == "PRESS" and event.type == "X":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "YZ"
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

        if y:
            if event.shift and event.value == "PRESS" and event.type == "Y":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XZ"
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

        if z:
            if event.shift and event.value == "PRESS" and event.type == "Z":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XY"
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

    def handle_instructions(self, context: bpy.types.Context, custom_instructions: str = "") -> None:
        self.snap_info = f"""|
        Axis: {self.tool_state.axis_method}
        Plane: {self.tool_state.plane_method}
        Snap: {self.snapping_points[0][1]}
        """
        instructions = self.instructions + custom_instructions + self.snap_info

        def draw_instructions(self: bpy.types.Header, context: bpy.types.Context) -> None:
            for line in instructions.splitlines():
                line = line.strip()
                split = line.split(":", 1)
                if (key := split[0]) not in ("TAB", "D", "A", "M", "C", "E", "BACKSPACE"):
                    self.layout.label(text=line)
                    continue

                self.layout.label(text=split[1], icon=f"EVENT_{key}")

        context.workspace.status_text_set(draw_instructions)

    def handle_lock_axis(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if event.value == "PRESS" and event.type == "A":
            self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
            self.tool_state.snap_angle = self.input_ui.get_number_value("WORLD_ANGLE")
            # Round to the closest 5
            self.tool_state.snap_angle = round(self.tool_state.snap_angle / 5) * 5

        if self.tool_state.lock_axis and event.shift and event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            if event.type in {"WHEELUPMOUSE"}:
                self.tool_state.snap_angle += 5
            else:
                self.tool_state.snap_angle -= 5
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
            tool.Polyline.close_polyline()
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
                    self.objs_2d_bbox.append(tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj))

            if self.mousemove_count > 3:
                detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
                self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)

                if self.snapping_points[0][1] not in {"Plane", "Axis"}:
                    should_round = False

                tool.Polyline.calculate_distance_and_angle(
                    context, self.input_ui, self.tool_state, should_round=should_round
                )
                if should_round:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)

                tool.Blender.update_viewport()
                return {"RUNNING_MODAL"}

            if event.value == "RELEASE" and event.type == "BACK_SPACE":
                tool.Polyline.remove_last_polyline_point()
                tool.Blender.update_viewport()

    def get_product_preview_data(self, context: bpy.types.Context, relating_type: ifcopenshell.entity_isntance):
         if relating_type.is_a() in ["IfcBeamType", "IfcCoveringType", "IfcMemberType"]:
             return get_profile_preview_data(context, relating_type)

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
        self.visible_objs = tool.Raycast.get_visible_objects(context)
        for obj in self.visible_objs:
            self.objs_2d_bbox.append(tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj))
        detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
        self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
        tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)

        tool.Blender.update_viewport()
        context.window_manager.modal_handler_add(self)
