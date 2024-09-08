# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Cyril Waechter <cyril@biminsight.ch>
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
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.module.drawing.helper import format_distance
from dataclasses import dataclass, field
from lark import Lark, Transformer
from math import sin, cos, radians, degrees, atan2, acos
from mathutils import Vector, Matrix
from typing import Optional


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
        try:
            value = f"{float(value):.3g}"
        except:
            pass
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
        if attribute_name == 'A':
            return self.get_text_value(attribute_name)
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


class Polyline(bonsai.core.tool.Polyline):

    @classmethod
    def create_input_ui(cls, init_z=False, init_area=False):
        return PolylineUI(init_z=init_z, init_area=init_area)

    @classmethod
    def set_mouse_position(cls, event):
        cls.mouse_pos = event.mouse_region_x, event.mouse_region_y

    @classmethod
    def set_angle_axis_line(cls, start, end):
        cls.axis_start = start
        cls.axis_end = end

    @classmethod
    def set_axis_rectangle(cls, corners):
        cls.axis_rectangle = [*corners]

    @classmethod
    def set_use_default_container(cls, value=False):
        cls.use_default_container = value

    @classmethod
    def set_plane(cls, plane_origin, plane_normal):
        cls.plane_origin = plane_origin
        cls.plane_normal = plane_normal

    @classmethod
    def set_instructions(cls, instructions):
        cls.instructions = instructions

    @classmethod
    def set_snap_info(cls, snap_info):
        cls.snap_info = snap_info

    @classmethod
    def calculate_distance_and_angle(cls, context, is_input_on, input_ui):

        try:
            polyline_data = context.scene.BIMModelProperties.polyline_point
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_data[len(polyline_data) - 1]
        except:
            default_container_elevation = 0
            last_point_data = None

        snap_prop = context.scene.BIMModelProperties.snap_mouse_point[0]

        if last_point_data:
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        else:
            last_point = Vector((0, 0, 0))

        if is_input_on:
            if cls.use_default_container:
                snap_vector = Vector(
                    (input_ui.get_number_value("X"), input_ui.get_number_value("Y"), default_container_elevation)
                )
            else:
                snap_vector = Vector(
                    (input_ui.get_number_value("X"), input_ui.get_number_value("Y"), input_ui.get_number_value("Z"))
                )
        else:
            if cls.use_default_container:
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
        if distance > 0:
            angle = tool.Cad.angle_3_vectors(
                second_to_last_point, last_point, snap_vector, new_angle=None, degrees=True
            )

            # Round angle to the nearest 0.05
            angle = round(angle / 0.05) * 0.05

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
            polyline_data = context.scene.BIMModelProperties.polyline_point
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
    def calculate_x_y_and_z(cls, context, input_ui):
        try:
            polyline_data = context.scene.BIMModelProperties.polyline_point
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_data[len(polyline_data) - 1]
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        except:
            default_container_elevation = 0
            last_point = Vector((0, 0, 0))

        snap_prop = context.scene.BIMModelProperties.snap_mouse_point[0]
        snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        if cls.use_default_container:
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
