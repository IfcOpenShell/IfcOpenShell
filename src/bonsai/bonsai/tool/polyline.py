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

import bpy
import bmesh
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.module.drawing.helper import format_distance
from dataclasses import dataclass
from lark import Lark, Transformer
from math import degrees, radians, sin, cos, tan
from mathutils import Vector, Matrix
from typing import Optional


class Polyline(bonsai.core.tool.Polyline):

    @dataclass
    class PolylineUI:
        _D: str = ""
        _A: str = ""
        _X: str = ""
        _Y: str = ""
        _Z: Optional[str] = None
        _AREA: Optional[str] = None
        init_z: bool = False
        init_area: bool = False

        def __post_init__(self):
            if self.init_z:
                self._Z = ""
            if self.init_area:
                self._AREA = ""

        def set_value(self, attribute_name, value):
            value = str(value)
            setattr(self, f"_{attribute_name}", value)

        def get_text_value(self, attribute_name):
            value = getattr(self, f"_{attribute_name}")
            return value

        def get_number_value(self, attribute_name):
            value = getattr(self, f"_{attribute_name}")
            if value:
                return float(value)
            else:
                return value

        def get_formatted_value(self, attribute_name):
            value = self.get_number_value(attribute_name)
            context = bpy.context
            if value is None:
                return None
            if attribute_name == "A":
                value = float(self.get_text_value(attribute_name))
                return f"{value:.2f}"
            else:
                return self.format_input_ui_units(context, value)

        def format_input_ui_units(cls, context, value):
            unit_system = tool.Drawing.get_unit_system()
            if unit_system == "IMPERIAL":
                precision = context.scene.DocProperties.imperial_precision
                factor = 3.28084
            else:
                precision = None
                factor = 1
                if context.scene.unit_settings.length_unit == "MILLIMETERS":
                    factor = 1000

            return format_distance(value * factor, precision=precision, suppress_zero_inches=True, in_unit_length=True)

    @dataclass
    class ToolState:
        use_default_container: bool = None
        snap_angle: float = None
        is_input_on: bool = None
        # angle_axis_start: Vector
        # angle_axis_end: Vector
        axis_method: str = None
        plane_method: str = None
        instructions: str = """TAB: Cycle Input
        M: Modify Snap Point
        C: Close
        Backspace: Remove
        X Y: Axis
        Shift: Lock axis
    """
        snap_info: str = None
        mode: str = None
        input_type: str = None

    @classmethod
    def create_input_ui(cls, init_z=False, init_area=False):
        return cls.PolylineUI(init_z=init_z, init_area=init_area)

    @classmethod
    def create_tool_state(cls):
        return cls.ToolState()

    @classmethod
    def calculate_distance_and_angle(cls, context, input_ui, tool_state):

        try:
            polyline_data = context.scene.BIMPolylineProperties.polyline_point
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_data[len(polyline_data) - 1]
        except:
            default_container_elevation = 0
            last_point_data = None

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]

        if last_point_data:
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        else:
            last_point = Vector((0, 0, 0))

        if tool_state.is_input_on:
            if tool_state.use_default_container:
                snap_vector = Vector(
                    (input_ui.get_number_value("X"), input_ui.get_number_value("Y"), default_container_elevation)
                )
            else:
                snap_vector = Vector(
                    (input_ui.get_number_value("X"), input_ui.get_number_value("Y"), input_ui.get_number_value("Z"))
                )
        else:
            if tool_state.use_default_container:
                snap_vector = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
            else:
                snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        second_to_last_point = None
        if len(polyline_data) > 1:
            second_to_last_point_data = polyline_data[len(polyline_data) - 2]
            second_to_last_point = Vector(
                (second_to_last_point_data.x, second_to_last_point_data.y, second_to_last_point_data.z)
            )
        else:
            # Creates a fake "second to last" point away from the first point but in the same x axis
            # this allows to calculate the angle relative to x axis when there is only one point
            second_to_last_point = Vector((last_point.x + 1000, last_point.y, last_point.z))

        distance = (snap_vector - last_point).length
        if distance < 0:
            return
        if distance > 0:
            angle = tool.Cad.angle_3_vectors(
                second_to_last_point, last_point, snap_vector, new_angle=None, degrees=True
            )

            # Round angle to the nearest 0.05
            angle = round(angle / 0.05) * 0.05

        if distance == 0:
            angle = 0
        if input_ui:
            input_ui.set_value("X", snap_vector.x)
            input_ui.set_value("Y", snap_vector.y)
            if input_ui.get_number_value("Z") is not None:
                input_ui.set_value("Z", snap_vector.z)

            input_ui.set_value("D", distance)
            input_ui.set_value("A", angle)
            return

        return

    @classmethod
    def calculate_area(cls, context, input_ui):
        try:
            polyline_data = context.scene.BIMPolylineProperties.polyline_point
        except:
            return input_ui

        if len(polyline_data) < 3:
            return input_ui

        points = []
        for data in polyline_data:
            points.append(Vector((data.x, data.y, data.z)))

        if points[0] == points[-1]:
            points = points[1:]

        # TODO move this to CAD
        # Calculate the normal vector of the plane formed by the first three vertices
        v1, v2, v3 = points[:3]
        normal = (v2 - v1).cross(v3 - v1).normalized()

        # Check if all points are coplanar
        is_coplanar = True
        tolerance = 1e-6  # Adjust this value as needed
        for v in points:
            if abs((v - v1).dot(normal)) > tolerance:
                is_coplanar = False

        if is_coplanar:
            area = 0
            for i in range(len(points)):
                j = (i + 1) % len(points)
                area += points[i].cross(points[j]).dot(normal)

            area = abs(area) / 2
        else:
            area = 0

        if input_ui.get_text_value("A") is not None:
            input_ui.set_value("A", area)
        return

    @classmethod
    def calculate_x_y_and_z(cls, context, input_ui, tool_state):
        try:
            polyline_data = context.scene.BIMPolylineProperties.polyline_point
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_data[len(polyline_data) - 1]
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        except:
            default_container_elevation = 0
            last_point = Vector((0, 0, 0))

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        if tool_state.use_default_container:
            snap_vector = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
        else:
            snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        if len(polyline_data) > 1:
            second_to_last_point_data = polyline_data[len(polyline_data) - 2]
            second_to_last_point = Vector(
                (second_to_last_point_data.x, second_to_last_point_data.y, second_to_last_point_data.z)
            )
        else:
            # Creates a fake "second to last" point away from the first point but in the same x axis
            # this allows to calculate the angle relative to x axis when there is only one point
            second_to_last_point = Vector((last_point.x + 1000, last_point.y, last_point.z))

        distance = input_ui.get_number_value("D")

        if distance < 0 or distance > 0:
            angle = radians(input_ui.get_number_value("A"))

            rot_vector = tool.Cad.angle_3_vectors(second_to_last_point, last_point, snap_vector, angle, degrees=True)

            coords = rot_vector * distance + last_point

            x = coords[0]
            y = coords[1]
            z = coords[2]
            if input_ui:
                input_ui.set_value("X", x)
                input_ui.set_value("Y", y)
                if input_ui.get_number_value("Z") is not None:
                    input_ui.set_value("Z", z)

                return

        input_ui.set_value("X", last_point.x)
        input_ui.set_value("Y", last_point.y)
        if input_ui.get_number_value("Z") is not None:
            input_ui.set_value("Z", last_point.z)

        return

    @classmethod
    def create_wall_preview_vertices(cls, context, relating_type):
        def create_bmesh_from_vertices(vertices):
            bm = bmesh.new()

            new_verts = [bm.verts.new(v) for v in base_vertices]
            if is_closed:
                new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
                new_edges.append(
                    bm.edges.new((new_verts[-1], new_verts[0]))
                )  # Add an edge between the last an first point to make it closed.
            else:
                new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]

            bm.verts.index_update()
            bm.edges.index_update()
            return bm

        # Get properties from object type
        layers = tool.Model.get_material_layer_parameters(relating_type)
        if not layers["thickness"]:
            return
        thickness = layers["thickness"]

        height = float(context.scene.BIMModelProperties.extrusion_depth)
        rl = float(context.scene.BIMModelProperties.rl1)
        x_angle = float(context.scene.BIMModelProperties.x_angle)
        angle_distortion = height * tan(x_angle)

        base_vertices = []
        top_vertices = []
        polyline_data = context.scene.BIMPolylineProperties.polyline_point
        if len(polyline_data) < 2:
            context.scene.BIMPolylineProperties.product_preview.clear()
            return
        for point in polyline_data:
            base_vertices.append(Vector((point.x, point.y, point.z)))

        is_closed = False
        if (
            base_vertices[0].x == base_vertices[-1].x
            and base_vertices[0].y == base_vertices[-1].y
            and base_vertices[0].z == base_vertices[-1].z
        ):
            is_closed = True
            base_vertices.pop(-1)  # Remove the last point. The edges are going to inform that the shape is closed.

        bm_base = create_bmesh_from_vertices(base_vertices)
        bm_top = create_bmesh_from_vertices(base_vertices)

        offset_base_verts = tool.Cad.offset_edges(bm_base, thickness)
        top_vertices = tool.Cad.offset_edges(bm_top, angle_distortion)
        offset_top_verts = tool.Cad.offset_edges(bm_top, angle_distortion + thickness)

        if is_closed:
            base_vertices.append(base_vertices[0])
            offset_base_verts.append(offset_base_verts[0])
            top_vertices.append(top_vertices[0])
            offset_top_verts.append(offset_top_verts[0])

        if offset_base_verts is not None:
            context.scene.BIMPolylineProperties.product_preview.clear()
            for v in base_vertices:
                prop = context.scene.BIMPolylineProperties.product_preview.add()
                prop.x = v.x
                prop.y = v.y
                prop.z = v.z + rl

            for v in offset_base_verts[::-1]:
                new_v = Vector((v.co.x, v.co.y, v.co.z))
                prop = context.scene.BIMPolylineProperties.product_preview.add()
                prop.x = new_v.x
                prop.y = new_v.y
                prop.z = new_v.z + rl

            for v in top_vertices:
                # new_v = v #+ scaled_direction
                new_v = Vector((v.co.x, v.co.y, v.co.z))
                prop = context.scene.BIMPolylineProperties.product_preview.add()
                prop.x = new_v.x
                prop.y = new_v.y
                prop.z = new_v.z + rl + height

            for v in offset_top_verts[::-1]:
                new_v = Vector((v.co.x, v.co.y, v.co.z))  # + scaled_direction
                prop = context.scene.BIMPolylineProperties.product_preview.add()
                prop.x = new_v.x
                prop.y = new_v.y
                prop.z = new_v.z + rl + height

        bm_base.free()
        bm_top.free()

    @classmethod
    def validate_input(cls, input_number, input_type):

        grammar_imperial = """
        start: (FORMULA dim expr) | dim
        dim: imperial

        FORMULA: "="

        imperial: feet? "-"? inches?
        feet: NUMBER? "-"? fraction? "'"
        inches: NUMBER? "-"? fraction? "\\""
        fraction: NUMBER "/" NUMBER

        expr: (ADD | SUB) dim | (MUL | DIV) NUMBER

        NUMBER: /-?\\d+(?:\\.\\d+)?/
        ADD: "+"
        SUB: "-"
        MUL: "*"
        DIV: "/"

        %ignore " "
        """

        grammar_metric = """
        start: FORMULA? dim expr?
        dim: metric

        FORMULA: "="

        metric: NUMBER

        expr: (ADD | SUB | MUL | DIV) dim

        NUMBER: /-?\\d+(?:\\.\\d+)?/
        ADD: "+"
        SUB: "-"
        MUL: "*"
        DIV: "/"

        %ignore " "
        """

        class InputTransform(Transformer):
            def NUMBER(self, n):
                return float(n)

            def fraction(self, numbers):
                return numbers[0] / numbers[1]

            def inches(self, args):
                if len(args) > 1:
                    result = args[0] + args[1]
                else:
                    result = args[0]
                return result / 12

            def feet(self, args):
                return args[0]

            def imperial(self, args):
                if len(args) > 1:
                    if args[0] <= 0:
                        result = args[0] - args[1]
                    else:
                        result = args[0] + args[1]
                else:
                    result = args[0]
                return result

            def metric(self, args):
                return args[0]

            def dim(self, args):
                return args[0]

            def expr(self, args):
                op = args[0]
                value = float(args[1])
                if op == "+":
                    return lambda x: x + value
                elif op == "-":
                    return lambda x: x - value
                elif op == "*":
                    return lambda x: x * value
                elif op == "/":
                    return lambda x: x / value

            def FORMULA(cls, args):
                return args[0]

            def start(self, args):
                i = 0
                if args[0] == "=":
                    i += 1
                else:
                    if len(args) > 1:
                        raise ValueError("Invalid input.")
                dimension = args[i]
                if len(args) > i + 1:
                    expression = args[i + 1]
                    return expression(dimension) * factor
                else:
                    return dimension * factor

        try:
            if bpy.context.scene.unit_settings.system == "IMPERIAL":
                parser = Lark(grammar_imperial)
                factor = 0.3048
            else:
                parser = Lark(grammar_metric)
                factor = 1
                if bpy.context.scene.unit_settings.length_unit == "MILLIMETERS":
                    factor = 0.001

            if input_type == "A":
                parser = Lark(grammar_metric)
                factor = 1

            parse_tree = parser.parse(input_number)

            transformer = InputTransform()
            result = transformer.transform(parse_tree)
            return True, str(result)
        except:
            return False, "0"
