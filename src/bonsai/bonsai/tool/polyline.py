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
import math
import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.module.drawing.helper import format_distance
from dataclasses import dataclass
from lark import Lark, Transformer
from math import degrees, radians, sin, cos, tan
from mathutils import Vector, Matrix
from typing import Optional, Union


class Polyline(bonsai.core.tool.Polyline):

    @dataclass
    class PolylineUI:
        _D: str = ""
        _A: str = ""  # Relative to previous polyline points
        _WORLD_ANGLE: str = ""  # Relative to World Origin. Only used for specific operation. Not used on the UI.
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
                self._AREA = "0"

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
                return f"{value:.2f}°"
            else:
                return Polyline.format_input_ui_units(value)

    @dataclass
    class ToolState:
        use_default_container: bool = None
        snap_angle: float = None
        is_input_on: bool = None
        lock_axis: bool = False
        # angle_axis_start: Vector
        # angle_axis_end: Vector
        axis_method: str = None
        plane_method: str = None
        plane_origin: Vector = Vector((0.0, 0.0, 0.0))
        instructions: str = """TAB: Cycle Input
        M: Modify Snap Point
        C: Close
        Backspace: Remove
        X Y: Axis
        L: Lock axis
    """
        snap_info: str = None
        mode: str = None
        input_type: str = None

    @classmethod
    def create_input_ui(cls, init_z: bool = False, init_area: bool = False) -> PolylineUI:
        return cls.PolylineUI(init_z=init_z, init_area=init_area)

    @classmethod
    def create_tool_state(cls) -> ToolState:
        return cls.ToolState()

    @classmethod
    def calculate_distance_and_angle(
        cls, context: bpy.types.Context, input_ui: PolylineUI, tool_state: ToolState, should_round: bool = False
    ) -> None:

        try:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
            polyline_points = polyline_data.polyline_points
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_points[len(polyline_points) - 1]
        except:
            polyline_points = []
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
        if len(polyline_points) > 1:
            second_to_last_point_data = polyline_points[len(polyline_points) - 2]
            second_to_last_point = Vector(
                (second_to_last_point_data.x, second_to_last_point_data.y, second_to_last_point_data.z)
            )
        else:
            # Creates a fake "second to last" point away from the first point but in the same x axis
            # this allows to calculate the angle relative to x axis when there is only one point
            second_to_last_point = Vector((last_point.x + 1000, last_point.y, last_point.z))

        world_second_to_last_point = Vector((last_point.x + 1000, last_point.y, last_point.z))

        distance = (snap_vector - last_point).length
        if distance < 0:
            return
        if distance > 0:
            angle = tool.Cad.angle_3_vectors(
                second_to_last_point, last_point, snap_vector, new_angle=None, degrees=True
            )

            # Round angle to the nearest 0.05
            angle = round(angle / 0.05) * 0.05

            orientation_angle = tool.Cad.angle_3_vectors(
                world_second_to_last_point, last_point, snap_vector, new_angle=None, degrees=True
            )

            # Round angle to the nearest 0.05
            orientation_angle = round(orientation_angle / 0.05) * 0.05

        if distance == 0:
            angle = 0
            orientation_angle = 0
        if input_ui:
            if should_round:
                angle = 5 * round(angle / 5)
                factor = tool.Snap.get_increment_snap_value(context)
                distance = factor * round(distance / factor)
            input_ui.set_value("X", snap_vector.x)
            input_ui.set_value("Y", snap_vector.y)
            if input_ui.get_number_value("Z") is not None:
                input_ui.set_value("Z", snap_vector.z)

            input_ui.set_value("D", distance)
            input_ui.set_value("A", angle)
            input_ui.set_value("WORLD_ANGLE", orientation_angle)
            return

        return

    @classmethod
    def calculate_area(cls, context: bpy.types.Context, input_ui: PolylineUI) -> Union[PolylineUI, None]:
        try:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
            polyline_points = polyline_data.polyline_points
        except:
            return input_ui

        if len(polyline_points) < 3:
            return input_ui

        points = []
        for data in polyline_points:
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

        if input_ui.get_text_value("AREA") is not None:
            input_ui.set_value("AREA", area)

        area = input_ui.get_number_value("AREA")
        if area:
            area = tool.Polyline.format_input_ui_units(area, is_area=True)
            polyline_data.area = area
        return

    @classmethod
    def calculate_x_y_and_z(cls, context: bpy.types.Context, input_ui: PolylineUI, tool_state: ToolState) -> None:
        try:
            polyline_data = context.scene.BIMPolylineProperties.insertion_polyline[0]
            polyline_points = polyline_data.polyline_points
            default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            last_point_data = polyline_points[len(polyline_points) - 1]
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        except:
            polyline_points = []
            default_container_elevation = 0
            last_point = Vector((0, 0, 0))

        snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
        snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        if tool_state.use_default_container:
            snap_vector = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
        else:
            snap_vector = Vector((snap_prop.x, snap_prop.y, snap_prop.z))

        if len(polyline_points) > 1:
            second_to_last_point_data = polyline_points[len(polyline_points) - 2]
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

            # When the angle in 180 degrees it might create a rotation vector that is equal to
            # when the angle is 0 degress, leading the insertion point to the opposite direction
            # This prevents the issue by ensuring the the negative x direction
            if round(angle, 4) == round(math.pi, 4):
                rot_vector.x = -1.0

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
    def validate_input(cls, input_number, input_type) -> tuple[bool, str]:

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

        metric: NUMBER "mm"? "m"? "°"?

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

    @classmethod
    def format_input_ui_units(cls, value: float, is_area: bool = False) -> str:
        unit_system = tool.Drawing.get_unit_system()
        if unit_system == "IMPERIAL":
            precision = bpy.context.scene.DocProperties.imperial_precision
            factor = 3.28084
        else:
            precision = None
            factor = 1
            if bpy.context.scene.unit_settings.length_unit == "MILLIMETERS":
                factor = 1000

        return format_distance(
            value * factor,
            precision=precision,
            hide_units=False,
            isArea=is_area,
            suppress_zero_inches=True,
            in_unit_length=True,
        )

    @classmethod
    def insert_polyline_point(cls, input_ui: PolylineUI, tool_state: Optional[ToolState] = None) -> Union[str, None]:
        x = input_ui.get_number_value("X")
        y = input_ui.get_number_value("Y")
        if input_ui.get_number_value("Z") is not None:
            z = input_ui.get_number_value("Z")
        else:
            z = 0
        d = input_ui.get_formatted_value("D")
        a = input_ui.get_formatted_value("A")

        snap_vertex = bpy.context.scene.BIMPolylineProperties.snap_mouse_point[0]
        if tool_state and tool_state.use_default_container:
            z = tool.Ifc.get_object(tool.Root.get_default_container()).location.z

        # Lock one dimension when in plane method
        if tool_state.plane_origin:
            if tool_state.plane_method == "XY":
                z = tool_state.plane_origin.z
            elif tool_state.plane_method == "XZ":
                y = tool_state.plane_origin.y
            elif tool_state.plane_method == "YZ":
                x = tool_state.plane_origin.x

        if x is None and y is None:
            x = snap_vertex.x
            y = snap_vertex.y
            z = snap_vertex.z

        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
        if not polyline_data:
            polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline.add()
        else:
            polyline_data = polyline_data[0]
        polyline_points = polyline_data.polyline_points
        if polyline_points:
            # Avoids creating two points at the same location
            for point in polyline_points[1:]:  # The first can be repeated to form a wall loop
                if (x, y, z) == (point.x, point.y, point.z):
                    return "Cannot create two points at the same location"
            # TODO move this limitation to be Wall tool specific. Right now it also affects Measure tool
            # Avoids creating segments smaller then 0.1. This is a limitation from create_wall_from_2_points
            length = (
                Vector((x, y, z)) - Vector((polyline_points[-1].x, polyline_points[-1].y, polyline_points[-1].z))
            ).length
            if round(length, 4) < 0.1:
                return "Cannot create a segment smaller then 10cm"

        polyline_point = polyline_points.add()
        polyline_point.x = x
        polyline_point.y = y
        polyline_point.z = z

        polyline_point.dim = d
        polyline_point.angle = a
        polyline_point.position = Vector((x, y, z))

        # Add total length
        total_length = 0
        for i, point in enumerate(polyline_points):
            if i == 0:
                continue
            dim = float(tool.Polyline.validate_input(point.dim, "D")[1])
            total_length += dim
        total_length = tool.Polyline.format_input_ui_units(total_length)
        polyline_data.total_length = total_length

    @classmethod
    def close_polyline(cls) -> None:
        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        if len(polyline_points) > 2:
            first_point = polyline_points[0]
            last_point = polyline_points[-1]
            if not (first_point.x == last_point.x and first_point.y == last_point.y and first_point.z == last_point.z):
                polyline_point = polyline_points.add()
                polyline_point.x = first_point.x
                polyline_point.y = first_point.y
                polyline_point.z = first_point.z
                polyline_point.dim = first_point.dim
                polyline_point.angle = first_point.angle
                polyline_point.position = first_point.position

    @classmethod
    def clear_polyline(cls) -> None:
        bpy.context.scene.BIMPolylineProperties.insertion_polyline.clear()

    @classmethod
    def remove_last_polyline_point(cls) -> None:
        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        polyline_points.remove(len(polyline_points) - 1)

    @classmethod
    def move_polyline_to_measure(cls, context: bpy.types.Context, input_ui: PolylineUI) -> None:
        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
        polyline_points = polyline_data[0].polyline_points if polyline_data else []
        measurement_data = bpy.context.scene.BIMPolylineProperties.measurement_polyline.add()
        measurement_type = bpy.context.scene.MeasureToolSettings.measurement_type
        measurement_data.measurement_type = measurement_type
        for point in polyline_points:
            measurement_point = measurement_data.polyline_points.add()
            measurement_point.x = point.x
            measurement_point.y = point.y
            measurement_point.z = point.z
            measurement_point.dim = point.dim
            measurement_point.angle = point.angle
            measurement_point.position = point.position

        measurement_data.total_length = polyline_data[0].total_length
        measurement_data.area = polyline_data[0].area
