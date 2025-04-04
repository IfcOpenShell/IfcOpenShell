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

import bmesh
import bpy
import copy
from bpy_extras import view3d_utils
import bonsai.core.tool
import bonsai.tool as tool
import mathutils
from mathutils import Vector
from typing import Union


class Raycast(bonsai.core.tool.Raycast):
    offset = 10
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

    @classmethod
    def get_visible_objects(cls, context: bpy.types.Context):
        depsgraph = context.evaluated_depsgraph_get()
        all_objs = []
        for dup in depsgraph.object_instances:
            if dup.is_instance:  # Real dupli instance
                obj = dup.instance_object
                all_objs.append(obj)
            else:  # Usual object
                obj = dup.object
                all_objs.append(obj)

        visible_objs = []
        for obj in all_objs:
            if obj.type in {"MESH", "EMPTY", "CURVE"} and (
                obj.visible_in_viewport_get(bpy.context.space_data) or obj.library
            ):  # Check for local view and local collections for this viewport and object
                visible_objs.append(obj)
        return visible_objs

    @classmethod
    def get_on_screen_2d_bounding_boxes(cls, context: bpy.types.Context, obj: bpy.types.Object):
        obj_matrix = obj.matrix_world.copy()
        bbox = [obj_matrix @ Vector(v) for v in obj.bound_box]

        transposed_bbox = []
        bbox_2d = []

        for v in bbox:
            coord_2d = view3d_utils.location_3d_to_region_2d(context.region, context.space_data.region_3d, v)
            if coord_2d is not None:
                transposed_bbox.append(coord_2d)

        region = context.region
        borders = (0, region.width, 0, region.height)
        for i, axis in enumerate(zip(*transposed_bbox)):
            min_point = min(axis)
            max_point = max(axis)
            bbox_2d.extend([min_point, max_point])

        if len(bbox_2d) == 0:
            return None
        # AABB
        if (
            bbox_2d[0] <= borders[1]
            and bbox_2d[1] >= borders[0]
            and bbox_2d[2] <= borders[3]
            and bbox_2d[3] >= borders[2]
        ):
            return (obj, bbox_2d)
        return None


    @classmethod
    def intersect_mouse_2d_bounding_box(cls, mouse_pos: tuple[int, int], bbox: list[float, float, float, float]):
        x, y = mouse_pos
        xmin, xmax, ymin, ymax = bbox

        # extends bbox boundaries to improve snap
        if cls.offset:
            xmin -= cls.offset
            xmax += cls.offset
            ymin -= cls.offset
            ymax += cls.offset

        if xmin < x < xmax and ymin < y < ymax:
            return True
        else:
            return False

    @classmethod
    def get_viewport_ray_data(
        cls, context: bpy.types.Context, event: bpy.types.Event, mouse_pos: tuple[int, int] = None
    ):
        region = context.region
        rv3d = context.region_data
        original_perspective = rv3d.view_perspective

        # TODO The raycast was working for orthographic view, but not when you are inside a camera view. This solution feels hacky,
        # but it temporarily switches the perspective_matrix from camera to the perspective_matrix from ortho view.
        if original_perspective == "CAMERA":
            rv3d.view_perspective = "ORTHO"
        if not mouse_pos:
            mouse_pos = event.mouse_region_x, event.mouse_region_y

        view_vector = view3d_utils.region_2d_to_vector_3d(region, rv3d, mouse_pos)
        ray_origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, mouse_pos)
        ray_target = ray_origin + view_vector
        ray_direction = ray_target - ray_origin

        if original_perspective == "CAMERA":
            rv3d.view_perspective = "CAMERA"

        return ray_origin, ray_target, ray_direction

    @classmethod
    def get_object_ray_data(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        obj_matrix: mathutils.Matrix,
        mouse_pos: tuple[int, int] = None,
    ):
        if mouse_pos:
            ray_origin, ray_target, _ = cls.get_viewport_ray_data(context, event, mouse_pos)
        else:
            ray_origin, ray_target, _ = cls.get_viewport_ray_data(context, event)
        matrix_inv = obj_matrix.inverted()
        ray_origin_obj = matrix_inv @ ray_origin
        ray_target_obj = matrix_inv @ ray_target
        ray_direction_obj = ray_target_obj - ray_origin_obj

        return ray_origin_obj, ray_target_obj, ray_direction_obj

    @classmethod
    def obj_ray_cast(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        obj: bpy.types.Object,
        mouse_pos: tuple[int, int] = None,
    ):
        if mouse_pos:
            ray_origin_obj, _, ray_direction_obj = cls.get_object_ray_data(
                context, event, obj.matrix_world.copy(), mouse_pos
            )
        else:
            ray_origin_obj, _, ray_direction_obj = cls.get_object_ray_data(context, event, obj.matrix_world.copy())
        success, location, normal, face_index = obj.ray_cast(ray_origin_obj, ray_direction_obj)
        if success:
            return location, normal, face_index
        else:
            return None, None, None

    @classmethod
    def ray_cast_by_proximity(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        obj: bpy.types.Object,
        face: bpy.types.MeshPolygon = None,
        custom_bmesh: bmesh.types.BMesh = None,
    ):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)
        points = []

        # Makes the snapping point more or less sticky than others
        # It changes the distance and affects how the snapping point are sorted
        # We multiply by the increment snap which is based on the viewport zoom
        snap_threshold = 10 * tool.Snap.get_increment_snap_value(bpy.context)
        if face:
            snap_threshold = tool.Snap.get_increment_snap_value(bpy.context)

        try:
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_direction)
        except:
            loc = Vector((0, 0, 0))

        # For empty object we just get the object location and return

        if obj and obj.type == "EMPTY":
            v = obj.location
            intersection = tool.Cad.point_on_edge(v, (ray_target, loc))
            distance = (v - intersection).length
            if distance < snap_threshold:
                snap_point = {
                    "object": obj,
                    "type": "Vertex",
                    "point": v.copy(),
                    "distance": distance,
                }
                points.append(snap_point)
            return points
        if obj and obj.type == "CURVE":
            obj = bpy.data.objects.new("new_object", obj.to_mesh().copy())

        if not custom_bmesh:
            bm = bmesh.new()
            if face is None:  # Object without faces
                bm.from_mesh(obj.data)
            else:  # Object with faces
                verts = [bm.verts.new(obj.data.vertices[i].co) for i in face.vertices]
                bm.faces.new(verts)
        else:
            # Measure polylines
            bm = custom_bmesh

        for vertex in bm.verts:
            v = vertex.co
            if obj:
                v = obj.matrix_world.copy() @ v
            intersection = tool.Cad.point_on_edge(v, (ray_target, loc))
            distance = (v - intersection).length
            if distance < snap_threshold:
                snap_point = {
                    "object": obj,
                    "type": "Vertex",
                    "point": v.copy(),
                    "distance": distance,
                }
                points.append(snap_point)

        for edge in bm.edges:
            v1 = edge.verts[0].co
            v2 = edge.verts[1].co
            if obj:
                v1 = obj.matrix_world.copy() @ v1
                v2 = obj.matrix_world.copy() @ v2
            division_point = (v1 + v2) / 2  # TODO Make it work for different divisions

            intersection = tool.Cad.point_on_edge(division_point, (ray_target, loc))
            distance = (division_point - intersection).length
            if distance < snap_threshold:
                snap_point = {
                    "object": obj,
                    "type": "Edge Center",
                    "point": division_point.copy(),
                    "distance": distance,
                }
                points.append(snap_point)

            intersection = tool.Cad.intersect_edges_v2((ray_target, loc), (v1, v2))
            if intersection[0]:
                if tool.Cad.is_point_on_edge(intersection[1], (v1, v2)):
                    distance = (intersection[1] - intersection[0]).length
                    if distance < snap_threshold:
                        snap_point = {
                            "object": obj,
                            "type": "Edge",
                            "point": intersection[1].copy(),
                            "edge_verts": (v1, v2),
                            "distance": distance,
                        }
                        points.append(snap_point)
        bm.free()

        return points

    @classmethod
    def ray_cast_to_polyline(cls, context: bpy.types.Context, event: bpy.types.Event):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)
        snap_threshold = tool.Snap.get_increment_snap_value(bpy.context)

        try:
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_direction)
        except:
            loc = Vector((0, 0, 0))

        polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline[0]
        polyline_points = polyline_data.polyline_points
        polyline_points = polyline_points[
            : len(polyline_points) - 1
        ]  # It doesn't make sense to snap to the last point created
        polyline_verts = []
        for point_data in polyline_points:
            vertex = Vector((point_data.x, point_data.y, point_data.z))

            intersection, _ = mathutils.geometry.intersect_point_line(vertex, ray_target, loc)
            distance = (vertex - intersection).length
            if distance < snap_threshold:
                snap_point = {
                    "type": "Vertex",
                    "point": vertex,
                    "distance": distance,
                    "object": None,
                }
                polyline_verts.append(snap_point)

        return polyline_verts

    @classmethod
    def ray_cast_to_measure(cls, context: bpy.types.Context, event: bpy.types.Event, points: bpy.types.Collection):
        bm = bmesh.new()
        bm.verts.index_update()
        bm.edges.index_update()

        indices = list(range(len(points) - 1))
        edges = [(i, i + 1) for i in range(len(points) - 1)]
        new_verts = [bm.verts.new(Vector((point.x, point.y, point.z))) for point in points]
        new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in edges]
        bm.verts.index_update()
        bm.edges.index_update()

        snapping_points = cls.ray_cast_by_proximity(context, event, None, custom_bmesh=bm)
        bm.free()
        return snapping_points

    @classmethod
    def ray_cast_to_plane(
        cls, context: bpy.types.Context, event: bpy.types.Event, plane_origin: Vector, plane_normal: Vector
    ):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)

        if tool.Ifc.get():
            default_container_elevation = tool.Root.get_default_container_elevation()
        else:
            default_container_elevation = 0.0
        intersection = Vector((0, 0, default_container_elevation))
        try:
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_direction)
            intersection = mathutils.geometry.intersect_line_plane(ray_target, loc, plane_origin, plane_normal)
        except:
            intersection = Vector((0, 0, default_container_elevation))

        if intersection == None:
            intersection = Vector((0, 0, default_container_elevation))

        return intersection

    @classmethod
    def ray_cast_to_edge_intersection(cls, context: bpy.types.Context, event: bpy.types.Event, edges: list[dict]):
        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)
        snap_threshold = tool.Snap.get_increment_snap_value(bpy.context)

        try:
            loc = view3d_utils.region_2d_to_location_3d(region, rv3d, mouse_pos, ray_direction)
        except:
            loc = Vector((0, 0, 0))

        for e1, e2 in zip(edges, edges[1:] + [edges[0]]):
            if tool.Cad.are_vectors_equal(e1["point"], e2["point"], tolerance=0.1):
                edge_intersection = tool.Cad.intersect_edges_v2(e1["edge_verts"], e2["edge_verts"])
                if edge_intersection[1]:
                    mouse_intersection, _ = mathutils.geometry.intersect_point_line(
                        edge_intersection[1], ray_target, loc
                    )
                    distance = (edge_intersection[1] - mouse_intersection).length
                    if distance < snap_threshold:
                        snap_point = {
                            "object": None,
                            "type": "Edge Intersection",
                            "point": edge_intersection[1],
                            "distance": distance,
                        }
                        return snap_point

    @classmethod
    def filter_objects_to_raycast(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        objs_2d_bbox: Union[tuple[bpy.types.Object, list[float]]],
    ) -> list[bpy.types.Object]:
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        objs_to_raycast = []
        for obj, bbox_2d in objs_2d_bbox:
            if bbox_2d:
                if tool.Raycast.intersect_mouse_2d_bounding_box(mouse_pos, bbox_2d):
                    objs_to_raycast.append(obj)
        return objs_to_raycast

    @classmethod
    def cast_rays_to_single_object(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        obj: bpy.types.Object,
    ) -> Union[tuple[bpy.types.Object, Vector, int], tuple[None, None, None]]:

        mouse_pos = event.mouse_region_x, event.mouse_region_y
        hit = None
        face_index = None
        # Wireframes
        if obj.type in {"EMPTY", "CURVE"} or (hasattr(obj.data, "polygons") and len(obj.data.polygons) == 0):
            snap_points = tool.Raycast.ray_cast_by_proximity(context, event, obj)
            if snap_points:
                hit = sorted(snap_points, key=lambda x: x["distance"])[0]["point"]
                if hit:
                    hit_world = obj.original.matrix_world @ hit
                    return obj, hit_world, face_index
            return None, None, None
        # Meshes
        else:
            hit, normal, face_index = tool.Raycast.obj_ray_cast(context, event, obj)
            if hit is None:
                # Tried original mouse position. Now it will try the offsets.
                original_mouse_pos = mouse_pos
                for value in cls.mouse_offset:
                    mouse_pos = tuple(x + y for x, y in zip(original_mouse_pos, value))
                    hit, normal, face_index = tool.Raycast.obj_ray_cast(context, event, obj, mouse_pos)
                    if hit:
                        break
                mouse_pos = original_mouse_pos
            if hit:
                hit_world = obj.original.matrix_world @ hit
                return obj, hit_world, face_index
            else:
                return None, None, None

    @classmethod
    def cast_rays_and_get_best_object(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        objs_to_raycast: list[bpy.types.Object],
        include_wireframes: bool = True,
    ) -> Union[tuple[bpy.types.Object, Vector, int], tuple[None, None, None]]:
        best_length_squared = 1.0
        best_obj = None
        best_hit = None
        best_face_index = None

        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)

        for obj in objs_to_raycast:
            if not include_wireframes and (
                obj.type in {"EMPTY", "CURVE"} or (hasattr(obj.data, "polygons") and len(obj.data.polygons) == 0)
            ):
                continue

            snap_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, obj)

            if hit is not None:
                length_squared = (hit - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = snap_obj
                    best_hit = hit
                    best_face_index = face_index

        if best_obj is not None:
            return best_obj, best_hit, best_face_index

        else:
            return None, None, None
