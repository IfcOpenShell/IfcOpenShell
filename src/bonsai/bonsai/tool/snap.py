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
from bonsai.bim.module.model.decorator import WallPolylineDecorator
import math
import mathutils
from mathutils import Matrix, Vector


class Snap(bonsai.core.tool.Snap):
    mouse_pos = None
    snap_angle = None
    use_default_container = False
    snap_plane_method = "No Plane"

    @classmethod
    def set_use_default_container(cls, value=True):
        cls.use_default_container = value

    @classmethod
    def set_snap_plane_method(cls, value=True):
        cls.snap_plane_method = value

    @classmethod
    def get_snap_points_on_raycasted_obj(cls, obj, face_index):
        snap_points = {}
        matrix = obj.matrix_world.copy()
        face = obj.data.polygons[face_index]
        vertices = []
        for i in face.vertices:
            vertices.append(matrix @ obj.data.vertices[i].co)

        edges_center = []
        for v1, v2 in zip(vertices, vertices[1:] + [vertices[0]]):
            middle_dist = (v2 - v1) / 2
            edges_center.append(v1 + middle_dist)

        snap_points.update({tuple(vertex): "Vertices" for vertex in vertices})
        snap_points.update({tuple(edge_center): "Edge Center" for edge_center in edges_center})

        return snap_points

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
    def update_snaping_point(cls, snap_point, snap_type):
        try:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        except:
            snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point.add()

        snap_vertex.x = snap_point[0]
        snap_vertex.y = snap_point[1]
        snap_vertex.z = snap_point[2]
        snap_vertex.snap_type = snap_type

    @classmethod
    def insert_polyline_point(cls, x=None, y=None, z=None):
        snap_vertex = bpy.context.scene.BIMModelProperties.snap_mouse_point[0]
        polyline_point = bpy.context.scene.BIMModelProperties.polyline_point.add()
        if cls.use_default_container:
            elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
        else:
            elevation = snap_vertex.z
        if x is not None and y is not None:
            polyline_point.x = x
            polyline_point.y = y
            polyline_point.z = elevation
        else:
            polyline_point.x = snap_vertex.x
            polyline_point.y = snap_vertex.y
            polyline_point.z = elevation

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

    @classmethod
    def remove_last_polyline_point(cls):
        polyline_data = bpy.context.scene.BIMModelProperties.polyline_point
        polyline_data.remove(len(polyline_data) - 1)

    @classmethod
    def snap_on_axis(cls, intersection, lock_axis=None):

        def create_axis_line(rot_mat, origin):
            length = 1000
            direction = Vector((1, 0, 0))
            rot_dir = rot_mat.inverted() @ direction
            start = origin + rot_dir * length
            end = origin - rot_dir * length
            return start, end

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

        for axis in snap_axis:
            rot_mat = Matrix.Rotation(math.radians(360 - axis), 3, "Z")
            start, end = create_axis_line(rot_mat, last_point)
            rot_intersection = rot_mat @ translated_intersection
            WallPolylineDecorator.set_angle_axis_line(start, end)
            if lock_axis:
                is_on_rot_axis = True
            else:
                is_on_rot_axis = abs(rot_intersection.y) <= 0.15

            if is_on_rot_axis:
                # Snap to axis
                rot_intersection = Vector((rot_intersection.x, 0, rot_intersection.z))
                # Convert it back
                snap_intersection = rot_mat.inverted() @ rot_intersection + last_point
                return snap_intersection, axis, start, end

        return None, None, None, None

    @classmethod
    def snaping_movement(cls, context, event, objs_2d_bbox):
        region = context.region
        rv3d = context.region_data
        cls.mouse_pos = event.mouse_region_x, event.mouse_region_y

        offset = 5
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

        # TODO Create option for different planes. RANDOM, XY, YZ, XZ. This should change the code in the bottom
        if cls.snap_plane_method == "No Plane":
            camera_rotation = rv3d.view_rotation
            plane_origin = Vector((0, 0, 0))
            plane_normal = Vector((0, 1, 1, 1)) * Vector((camera_rotation))

        elif cls.snap_plane_method == "XY":
            if cls.use_default_container:
                elevation = tool.Ifc.get_object(tool.Root.get_default_container()).location.z
            else:
                elevation = 0
            plane_origin = Vector((0, 0, elevation))
            plane_normal = Vector((0, 0, 1))

        def cast_rays_and_get_best_object():
            best_length_squared = 1.0
            best_obj = None
            best_hit = None
            best_face_index = None

            objs_to_raycast = []

            for obj, bbox_2d in objs_2d_bbox:
                if obj.type == "MESH" and bbox_2d:
                    if tool.Raycast.in_view_2d_bounding_box(cls.mouse_pos, bbox_2d):
                        objs_to_raycast.append(obj)

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

        snap_threshold = 0.3
        ray_origin, ray_target, ray_direction = tool.Raycast.get_viewport_ray_data(context, event)
        obj, hit, face_index = cast_rays_and_get_best_object()
        intersection = tool.Raycast.ray_cast_to_plane(context, event, plane_origin, plane_normal)

        if cls.use_default_container:
            # Locks snap into an angle axis
            if event.shift:
                rot_intersection, _, axis_start, axis_end = cls.snap_on_axis(intersection, cls.snap_angle)
            else:
                cls.snap_angle = None
                rot_intersection, cls.snap_angle, _, _ = cls.snap_on_axis(intersection)
        else:
            rot_intersection = None

        if obj is not None:

            snap_points = cls.get_snap_points_on_raycasted_obj(obj, face_index)
            snap_point = cls.select_snap_point(snap_points, hit, snap_threshold)

            if snap_point:
                # Creates a mixed snap point between the locked axis and
                # the object snap
                # TODO Use ALT key to give the user the option to choose between the two results.
                # TODO Create decorator for this
                # try:
                #     snap_point_vector = Vector((snap_point[0].x, snap_point[0].y, snap_point[0].z))
                #     snap_point_axis_1 = (
                #         Vector((snap_point[0].x + 1000, snap_point[0].y, default_container_elevation)),
                #         Vector((snap_point[0].x - 1000, snap_point[0].y, default_container_elevation)),
                #     )
                #     snap_point_axis_2 = (
                #         Vector((snap_point[0].x, snap_point[0].y + 1000, default_container_elevation)),
                #         Vector((snap_point[0].x, snap_point[0].y - 1000, default_container_elevation)),
                #     )
                #     snap_angle_axis = (axis_start, axis_end)
                #     result_1 = tool.Cad.intersect_edges(snap_angle_axis, snap_point_axis_1)
                #     result_1 = Vector((result_1[0].x, result_1[0].y, default_container_elevation))
                #     distance_1 = (result_1 - snap_point_vector).length

                #     result_2 = tool.Cad.intersect_edges(snap_angle_axis, snap_point_axis_2)
                #     result_2 = Vector((result_2[0].x, result_2[0].y, default_container_elevation))
                #     distance_2 = (result_2 - snap_point_vector).length

                #     if distance_1 < distance_2:
                #         best_result = result_1
                #     else:
                #         best_result = result_2

                #     cls.update_snaping_point(best_result, "Axis")

                # except Exception as e:
                # cls.update_snaping_point(snap_point[0], snap_point[1])
                cls.update_snaping_point(snap_point[0], snap_point[1])

            else:
                cls.update_snaping_point(hit, "Face")

        else:
            snap_points = cls.get_snap_points_on_polyline()
            snap_point = cls.select_snap_point(snap_points, intersection, snap_threshold)

            if snap_point:
                cls.update_snaping_point(snap_point[0], snap_point[1])
            elif rot_intersection:
                cls.update_snaping_point(rot_intersection, "Axis")
            else:
                cls.update_snaping_point(intersection, "Plane")
