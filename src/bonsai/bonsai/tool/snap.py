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
from bonsai.bim.module.model.decorator import PolylineDecorator
import math
import mathutils
from mathutils import Matrix, Vector
from lark import Lark, Transformer


class Snap(bonsai.core.tool.Snap):
    mouse_pos = None
    snap_angle = None
    use_default_container = False
    snap_plane_method = None
    snap_axis_method = None

    @classmethod
    def set_use_default_container(cls, value=True):
        cls.use_default_container = value

    @classmethod
    def set_snap_plane_method(cls, value=True):
        if cls.snap_plane_method == value:
            cls.snap_plane_method = None
            return
        cls.snap_plane_method = value

    @classmethod
    def set_snap_axis_method(cls, value=True):
        if cls.snap_axis_method == value:
            cls.snap_axis_method = None
            return
        cls.snap_axis_method = value

    @classmethod
    def get_snap_points_on_raycasted_face(cls, context, event, obj, face_index):
        matrix = obj.matrix_world.copy()
        face = obj.data.polygons[face_index]
        verts = []
        for i in face.vertices:
            verts.append(matrix @ obj.data.vertices[i].co)

        hit, hit_type = tool.Raycast.ray_cast_by_proximity(context, event, obj, face)
        snap_point = (hit, hit_type)
        if hit is None:
            return (None, None)

        return snap_point

    @classmethod
    def get_snap_points_on_polyline(cls):
        snap_points = {}
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        polyline_points = []
        for point_data in polyline_data:
            point = Vector((point_data.x, point_data.y, point_data.z))
            polyline_points.append(point)
        snap_points.update({tuple(point): "Polyline Point" for point in polyline_points})

        return snap_points

    @classmethod
    def select_snap_point(cls, snap_points, hit, threshold):
        shortest_distance = None
        snap_point = None
        for point, snap_type in snap_points.items():
            point = Vector(point)
            distance = (point - hit).length
            if distance > threshold:
                continue
            if shortest_distance and distance < shortest_distance:
                shortest_distance = distance
                snap_point = (point, snap_type)

            elif not shortest_distance:
                shortest_distance = distance
                snap_point = (point, snap_type)
            else:
                pass

        return snap_point

    @classmethod
    def update_snapping_point(cls, snap_point, snap_type):
        try:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        except:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point.add()

        info = f"""Snap: {snap_type}
    Axis:{cls.snap_axis_method}
    Plane:{cls.snap_plane_method}
"""
        PolylineDecorator.set_snap_info(info)
        snap_vertex.x = snap_point[0]
        snap_vertex.y = snap_point[1]
        snap_vertex.z = snap_point[2]
        snap_vertex.snap_type = snap_type

    @classmethod
    def update_snapping_ref(cls, snap_point, snap_type):
        try:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_ref[0]
        except:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_ref.add()

        snap_vertex.x = snap_point[0]
        snap_vertex.y = snap_point[1]
        snap_vertex.z = snap_point[2]
        snap_vertex.snap_type = snap_type

    @classmethod
    def clear_snapping_ref(cls):
        bpy.context.scene.BIMModelProperties.snap_mouse_ref.clear()

    @classmethod
    def insert_polyline_point(cls, input_panel):
        x = float(input_panel["X"])
        y = float(input_panel["Y"])
        try:
            z = float(input_panel["Z"])
        except:
            z = Vector((0, 0, 0))
        d = input_panel["D"]
        a = input_panel["A"]

        snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        if cls.use_default_container:
            z = tool.Ifc.get_object(tool.Root.get_default_container()).location.z

        if x is None and y is None:
            x = snap_vertex.x
            y = snap_vertex.y
            z = snap_vertex.z

        # Avoids creating two points at the same location
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        if polyline_data:
            last_point = polyline_data[len(polyline_data) - 1]
            if (x, y, z) == (round(last_point.x, 4), round(last_point.y, 4), round(last_point.z, 4)):
                return

        polyline_point = bpy.context.scene.BIMModelProperties.polyline_point.add()
        polyline_point.x = x
        polyline_point.y = y
        polyline_point.z = z

        polyline_measurement = bpy.context.scene.BIMModelProperties.polyline_measurement.add()
        polyline_measurement.dim = d
        polyline_measurement.angle = a
        polyline_measurement.position = Vector((x, y, z))

    @classmethod
    def close_polyline(cls):
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        if len(polyline_data) > 2:
            first_point = polyline_data[0]
            polyline_point = bpy.context.scene.BIMModelProperties.polyline_point.add()
            polyline_point.x = first_point.x
            polyline_point.y = first_point.y
            polyline_point.z = first_point.z

    @classmethod
    def clear_polyline(cls):
        bpy.context.scene.BIMModelProperties.polyline_point.clear()
        bpy.context.scene.BIMModelProperties.polyline_measurement.clear()

    @classmethod
    def remove_last_polyline_point(cls):
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        polyline_data.remove(len(polyline_data) - 1)
        polyline_measurement = bpy.context.scene.BIMModelProperties.polyline_measurement
        polyline_measurement.remove(len(polyline_measurement) - 1)

    @classmethod
    def snap_on_axis(cls, intersection, lock_axis=None):

        def create_axis_line_data(rot_mat, origin):
            length = 1000
            direction = Vector((1, 0, 0))
            if cls.snap_plane_method == "YZ" or (not cls.snap_plane_method and cls.snap_axis_method == "Z"):
                direction = Vector((0, 0, 1))
            rot_dir = rot_mat.inverted() @ direction
            start = origin + rot_dir * length
            end = origin - rot_dir * length

            return start, end

        def create_axis_rectangle_data(origin):
            size = 0.5
            direction = Vector((1, 0, 0))
            if cls.snap_plane_method == "YZ":
                direction = Vector((0, 0, 1))
            rot_mat = Matrix.Rotation(math.radians(360), 3, pivot_axis)
            rot_dir = rot_mat.inverted() @ direction
            v1 = origin + rot_dir * 0
            v2 = origin + rot_dir * size
            if cls.snap_plane_method == "XY":
                angle = 270
            else:
                angle = 90
            rot_mat = Matrix.Rotation(math.radians(angle), 3, pivot_axis)
            rot_dir = rot_mat.inverted() @ direction
            v3 = origin + rot_dir * size
            v4 = v2 + rot_dir * size

            return (v1, v2, v3, v4)

        default_container_elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        if polyline_data:
            last_point_data = polyline_data[-1]
            last_point = Vector((last_point_data.x, last_point_data.y, last_point_data.z))
        else:
            last_point = Vector((0, 0, default_container_elevation))

        # Translates intersection point based on last_point
        translated_intersection = intersection - last_point
        snap_axis = []
        if not lock_axis:
            for i in range(1, 13):
                angle = 30 * i
                snap_axis.append(angle)
        else:
            snap_axis = [lock_axis]

        pivot_axis = "Z"
        if cls.snap_plane_method == "XZ":
            pivot_axis = "Y"
        if cls.snap_plane_method == "YZ":
            pivot_axis = "X"

        for axis in snap_axis:
            rot_mat = Matrix.Rotation(math.radians(360 - axis), 3, pivot_axis)
            start, end = create_axis_line_data(rot_mat, last_point)
            rot_intersection = rot_mat @ translated_intersection
            proximity = rot_intersection.y
            if cls.snap_plane_method == "XZ":
                proximity = rot_intersection.z
            PolylineDecorator.set_angle_axis_line(start, end)
            if lock_axis:
                is_on_rot_axis = True
            else:
                is_on_rot_axis = abs(proximity) <= 0.15

            if is_on_rot_axis:
                # Snap to axis
                rot_intersection = Vector((rot_intersection.x, 0, rot_intersection.z))
                if cls.snap_plane_method == "XZ":
                    rot_intersection = Vector((rot_intersection.x, rot_intersection.y, 0))
                # Convert it back
                snap_intersection = rot_mat.inverted() @ rot_intersection + last_point
                return snap_intersection, axis, start, end

        return None, None, None, None

    @classmethod
    def mix_snap_and_axis(cls, snap_point, axis_start, axis_end, elevation):
        # Creates a mixed snap point between the locked axis and
        # the object snap
        # TODO Use ALT key to give the user the option to choose between the two results.
        # TODO Create decorator for this
        snap_point_vector = Vector((snap_point[0].x, snap_point[0].y, snap_point[0].z))
        snap_point_axis_1 = (
            Vector((snap_point[0].x + 1000, snap_point[0].y, elevation)),
            Vector((snap_point[0].x - 1000, snap_point[0].y, elevation)),
        )
        snap_point_axis_2 = (
            Vector((snap_point[0].x, snap_point[0].y + 1000, elevation)),
            Vector((snap_point[0].x, snap_point[0].y - 1000, elevation)),
        )
        snap_angle_axis = (axis_start, axis_end)
        result_1 = tool.Cad.intersect_edges(snap_angle_axis, snap_point_axis_1)
        result_1 = Vector((result_1[0].x, result_1[0].y, elevation))
        distance_1 = (result_1 - snap_point_vector).length

        result_2 = tool.Cad.intersect_edges(snap_angle_axis, snap_point_axis_2)
        result_2 = Vector((result_2[0].x, result_2[0].y, elevation))
        distance_2 = (result_2 - snap_point_vector).length

        if distance_1 < distance_2:
            best_result = result_1
        else:
            best_result = result_2

        return best_result, "Mix"

    @classmethod
    def detect_snapping_points(cls, context, event, objs_2d_bbox):
        region = context.region
        rv3d = context.region_data
        cls.mouse_pos = event.mouse_region_x, event.mouse_region_y
        detected_snaps = []

        offset = 15
        snap_threshold = 0.3
        mouse_offset = (
            (-offset, offset),
            (0, offset),
            (offset, offset),
            (-offset, 0),
            (0, 0),
            (offset, 0),
            (-offset, -offset),
            (0, -offset),
            (offset, -offset),
        )

        def select_plane_method():
            if not last_polyline_point:
                plane_origin = Vector((0, 0, 0))
                plane_normal = Vector((0, 0, 1))

            if not cls.snap_plane_method:
                camera_rotation = rv3d.view_rotation
                plane_origin = Vector((0, 0, 0))
                view_direction = Vector((0, 0, -1)) @ camera_rotation.to_matrix().transposed()
                plane_normal = view_direction.normalized()

            if cls.snap_plane_method == "XY" or (not cls.snap_plane_method and cls.snap_axis_method in {"X", "Y"}):
                if cls.use_default_container:
                    plane_origin = Vector((0, 0, elevation))
                elif not last_polyline_point:
                    plane_origin = Vector((0, 0, 0))
                else:
                    plane_origin = Vector((last_polyline_point.x, last_polyline_point.y, last_polyline_point.z))
                plane_normal = Vector((0, 0, 1))

            elif cls.snap_plane_method == "XZ" or (not cls.snap_plane_method and cls.snap_axis_method == "Z"):
                if last_polyline_point:
                    plane_origin = Vector((last_polyline_point.x, last_polyline_point.y, last_polyline_point.z))
                plane_normal = Vector((0, 1, 0))

            elif cls.snap_plane_method == "YZ":
                if last_polyline_point:
                    plane_origin = Vector((last_polyline_point.x, last_polyline_point.y, last_polyline_point.z))
                plane_normal = Vector((1, 0, 0))

            return plane_origin, plane_normal

        def cast_rays_and_get_best_object(objs_to_raycast):
            best_length_squared = 1.0
            best_obj = None
            best_hit = None
            best_face_index = None

            for obj in objs_to_raycast:
                hit, normal, face_index = tool.Raycast.obj_ray_cast(context, event, obj)
                if hit is None:
                    # Tried original mouse position. Now it will try the offsets.
                    original_mouse_pos = cls.mouse_pos
                    for value in mouse_offset:
                        cls.mouse_pos = tuple(x + y for x, y in zip(original_mouse_pos, value))
                        hit, normal, face_index = tool.Raycast.obj_ray_cast(context, event, obj)
                        if hit:
                            break
                    cls.mouse_pos = original_mouse_pos

                if hit is not None:
                    hit_world = obj.original.matrix_world @ hit
                    length_squared = (hit_world - ray_origin).length_squared
                    if best_obj is None or length_squared < best_length_squared:
                        best_length_squared = length_squared
                        best_obj = obj
                        best_hit = hit_world
                        best_face_index = face_index

            if best_obj is not None:
                return best_obj, best_hit, best_face_index

            else:
                return None, None, None

        ray_origin, ray_target, ray_direction = tool.Raycast.get_viewport_ray_data(context, event)

        objs_to_raycast = []
        for obj, bbox_2d in objs_2d_bbox:
            if obj.type == "MESH" and bbox_2d:
                if tool.Raycast.in_view_2d_bounding_box(cls.mouse_pos, bbox_2d):
                    objs_to_raycast.append(obj)
        # Obj
        snap_obj, hit, face_index = cast_rays_and_get_best_object(objs_to_raycast)
        if hit is not None:
            detected_snaps.append({"Object": (snap_obj, hit, face_index)})

        # Edge-Vertex
        for obj in objs_to_raycast:
            options = tool.Raycast.ray_cast_by_proximity(context, event, obj)
            snap_obj = obj
            if options:
                detected_snaps.append({"Edge-Vertex": (snap_obj, options)})
                break
        # Polyline
        try:
            polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
            last_polyline_point = polyline_data[len(polyline_data) - 1]
        except:
            last_polyline_point = None
        snap_points = tool.Raycast.ray_cast_to_polyline(context, event)
        # snap_point = cls.select_snap_point(snap_points, intersection, snap_threshold)
        if snap_points:
            detected_snaps.append({"Polyline": snap_points})

        # Axis and Plane
        elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z

        plane_origin, plane_normal = select_plane_method()
        PolylineDecorator.set_plane(plane_origin, plane_normal)
        intersection = tool.Raycast.ray_cast_to_plane(context, event, plane_origin, plane_normal)

        axis_start = None
        axis_end = None

        # TODO It only work for XY plane. Make it work also for None plane_method
        rot_intersection = None
        if not cls.snap_plane_method:
            if cls.snap_axis_method == "X":
                cls.snap_angle = 180
            if cls.snap_axis_method == "Y":
                cls.snap_angle = 90
            if cls.snap_axis_method == "Z":
                cls.snap_angle = 90
            if cls.snap_axis_method:
                rot_intersection, _, axis_start, axis_end = cls.snap_on_axis(intersection, cls.snap_angle)

        if cls.snap_plane_method:
            if cls.snap_plane_method in {"XY", "XZ"} and cls.snap_axis_method == "X":
                cls.snap_angle = 180
            if cls.snap_plane_method in {"XY", "YZ"} and cls.snap_axis_method == "Y":
                cls.snap_angle = 90
            if cls.snap_plane_method in {"YZ"} and cls.snap_axis_method == "Z":
                cls.snap_angle = 180
            if cls.snap_plane_method in {"XZ"} and cls.snap_axis_method == "Z":
                cls.snap_angle = 90
            if event.shift or cls.snap_axis_method:
                # Doesn't update snap_angle so that it keeps in the same axis
                rot_intersection, _, axis_start, axis_end = cls.snap_on_axis(intersection, cls.snap_angle)
            else:
                rot_intersection, cls.snap_angle, axis_start, axis_end = cls.snap_on_axis(intersection, None)
        if rot_intersection:
            detected_snaps.append({"Axis": (rot_intersection, axis_start, axis_end)})

        detected_snaps.append({"Plane": intersection})


        return detected_snaps

    @classmethod
    def select_snapping_points(cls, context, event, detected_snaps):
        snapping_points = []
        for origin in detected_snaps:

            if "Object" in list(origin.keys()):
                snap_obj, hit, face_index = origin["Object"]

                matrix = snap_obj.matrix_world.copy()
                face = snap_obj.data.polygons[face_index]
                verts = []
                for i in face.vertices:
                    verts.append(matrix @ snap_obj.data.vertices[i].co)

                options = tool.Raycast.ray_cast_by_proximity(context, event, snap_obj, face)
                if not options:
                    snapping_points.append((hit, "Face"))
                else:
                    for op in options:
                        snapping_points.append(op)

            if "Edge-Vertex" in list(origin.keys()):
                snap_obj, options = origin["Edge-Vertex"]
                for op in options:
                    snapping_points.append(op)

            if "Polyline" in list(origin.keys()):
                options = origin["Polyline"]
                for op in options:
                    snapping_points.append(op)

            if "Axis" in list(origin.keys()):
                intersection = origin["Axis"]
                axis_start = intersection[1]
                axis_end = intersection[2]
                snapping_points.append((intersection[0], "Axis"))

            if "Plane" in list(origin.keys()):
                intersection = origin["Plane"]
                snapping_points.append((intersection, "Plane"))


        # Make Axis first priority
        if event.shift or cls.snap_axis_method in {"X", "Y", "Z"}:
            cls.update_snapping_ref(snapping_points[0][0], snapping_points[0][1])
            for point in snapping_points:
                if point[1] == "Axis":
                    if snapping_points[0][1] not in {"Axis", "Plane"}:
                        mixed_snap =  cls.mix_snap_and_axis(snapping_points[0], axis_start, axis_end, 0)
                        cls.update_snapping_point(mixed_snap[0], mixed_snap[1])
                        return snapping_points
                    cls.update_snapping_point(point[0], point[1])
                    return snapping_points

        cls.update_snapping_point(snapping_points[0][0], snapping_points[0][1])
        return snapping_points

    @classmethod
    def modify_snapping_point_selection(cls, snapping_points):
        shifted_list = snapping_points[1:] + snapping_points[:1]
        cls.update_snapping_point(shifted_list[0][0], shifted_list[0][1])
        return shifted_list

    @classmethod
    def validate_input(cls, input_number, input_type):

        grammar_imperial = """
        start: FORMULA? dim expr?
        dim: imperial

        FORMULA: "="

        imperial: feet? "-"? inches?
        feet: NUMBER? " "? fraction? "'"
        inches: NUMBER? " "? fraction? "\\""
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
