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

from __future__ import annotations

import math
from typing import Union

import bmesh
import bpy
import mathutils
import numpy as np
from bpy_extras import view3d_utils
from mathutils import Vector

import bonsai.core.tool
import bonsai.tool as tool


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
    snap_objs = []

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
    def get_on_screen_2d_bounding_boxes(
        cls, context: bpy.types.Context, obj: bpy.types.Object
    ) -> Union[tuple[bpy.types.Object, list[float]], None]:
        rv3d = context.region_data
        assert rv3d
        view_location = rv3d.view_matrix.inverted().translation
        view_normal = rv3d.view_rotation @ mathutils.Vector((0.0, 0.0, -1.0))
        obj_matrix = obj.matrix_world.copy()
        bbox = [obj_matrix @ Vector(v) for v in obj.bound_box]
        bbox_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

        transposed_bbox: list[Vector] = []
        bbox_2d: list[float] = []

        assert context.region
        assert isinstance(context.space_data, bpy.types.SpaceView3D)
        assert context.space_data.region_3d

        # Do not include objects too far from camera view
        if rv3d.view_perspective == "PERSP":
            threshold = 200
            min_distance = float("inf")
            closest_distance: float = None
            for point in bbox:
                distance = (view_location - point).length
                if distance < min_distance:
                    min_distance = distance
                    closest_distance = distance
            if closest_distance > threshold:
                return None

        for v in bbox:
            coord_2d = tool.Cad.location_3d_to_region_2d_np(context.region, context.space_data.region_3d, v)
            transposed_bbox.append(coord_2d)

        if not any(transposed_bbox):
            transposed_bbox = []
        # If there are None values in transposed_bbox it means that there are vertices behind the camera
        # so we get the intersection of the edge with the region border
        # new_bbox = []
        if any(transposed_bbox) and not all(transposed_bbox):
            new_bbox = transposed_bbox.copy()
            new_bbox = [x for x in new_bbox if x is not None]
            for edge in bbox_edges:
                if (transposed_bbox[edge[0]] is None) ^ (transposed_bbox[edge[1]] is None):
                    point, _ = cls.intersect_edge_region_border(
                        context.region, context.space_data, rv3d, bbox[edge[0]], bbox[edge[1]]
                    )
                    if point:
                        new_bbox.append(point)
            if new_bbox:
                transposed_bbox = new_bbox

        region = context.region
        borders = (0, region.width, 0, region.height)
        for i, axis in enumerate(zip(*transposed_bbox)):
            axis: tuple[float, ...]
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

    def intersect_edge_region_border(region, space, rv3d, v1, v2):
        def segment_intersect_near_plane(view_matrix, clip_start, p_world_a, p_world_b):
            a_view = view_matrix @ p_world_a
            b_view = view_matrix @ p_world_b
            z_near = -clip_start
            za = a_view.z
            zb = b_view.z
            denom = zb - za
            if denom == 0.0:
                return None, None
            t = (z_near - za) / denom
            if t < 0.0 or t > 1.0:
                return None, None
            p_view = a_view.lerp(b_view, t)
            cam_world = view_matrix.inverted()
            p_world = cam_world @ p_view
            return p_world, t

        def is_inside_region(pt2d, region):
            return 0.0 <= pt2d.x <= region.width and 0.0 <= pt2d.y <= region.height

        def clamp_to_region_border(point2d, region):
            x, y = point2d
            x_clamped = max(0.0, min(region.width, x))
            y_clamped = max(0.0, min(region.height, y))
            return Vector((x_clamped, y_clamped))

        def find_nearby_onscreen_point(region, rv3d, p1, p2, initial_t_on_segment, max_iters=40, step=0.05):
            """
            Use iterative approach: move t toward 0. Returns the first point that is inside region border
            """
            t = initial_t_on_segment
            for i in range(max_iters):
                test_3d = p1.lerp(p2, t)
                test_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, test_3d)
                if test_2d is not None and is_inside_region(test_2d, region):
                    return test_3d, test_2d, t
                # move t toward 0 by reducing it by a fraction of its current value
                t -= step
                # if t is already very small, break
                if t <= 1e-6:
                    break

            return None, None, None

        # Ensures that all the calculation uses the same direction based on which point is on the screen
        if view3d_utils.location_3d_to_region_2d(region, rv3d, v1):
            onscreen_vert = v1
            offscreen_vert = v2
        else:
            onscreen_vert = v2
            offscreen_vert = v1
            # v2, v1 = v1, v2

        clip_start = space.clip_start
        view_mat = rv3d.view_matrix
        inter_world, t_on_ab = segment_intersect_near_plane(view_mat, clip_start, onscreen_vert, offscreen_vert)

        if inter_world is None:
            print("No intersection with viewport near plane found for the segment.")
            return None, None

        init_2d = view3d_utils.location_3d_to_region_2d(region, rv3d, inter_world)

        if init_2d is not None and is_inside_region(init_2d, region):
            final_world = inter_world
            final_2d = init_2d
            final_t = t_on_ab
        else:
            found_world, found_2d, found_t = find_nearby_onscreen_point(
                region, rv3d, onscreen_vert, offscreen_vert, t_on_ab, max_iters=600, step=0.01
            )
            if found_world is None:
                if init_2d is None:
                    print("Initial projection invalid and iterative search failed.")
                    return None, None
                # fallback: clamp projected point to border via manual mapping
                final_2d = clamp_to_region_border(init_2d, region)
                final_world = None
                final_t = None
                # print("Iterative search failed; using clamped 2D:", final_2d)
            else:
                final_world = found_world
                final_2d = found_2d
                final_t = found_t
                # print(f"Found onscreen point at t={final_t:.4f}")

        # print("Final 2D:", final_2d)
        return final_2d, v2

    @classmethod
    def intersect_mouse_2d_bounding_box(cls, mouse_pos: tuple[int, int], bbox: list[float]):
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
    def object_is_visible_in_clipping_plane(cls, obj):
        is_visible = True
        if obj.type == "EMPTY":
            vertex = obj.location
            is_visible = cls.point_is_visible_in_clipping_plane(vertex)

        if obj.type == "CURVE":
            obj = bpy.data.objects.new("new_object", obj.to_mesh().copy())

        if obj.type == "MESH":
            for v in obj.data.vertices:
                vertex = obj.matrix_world @ v.co
                is_visible = cls.point_is_visible_in_clipping_plane(vertex)
                if is_visible:
                    break
        return is_visible

    @classmethod
    def point_is_visible_in_clipping_plane(cls, vertex):
        normals = tool.Project.get_clipping_planes_normals()
        if not normals:
            return True
        for normal in normals:
            t = (vertex - normal[0]).normalized()
            result = normal[1].dot(t)
            if result < 0:
                return False
        return True

    @classmethod
    def get_viewport_ray_data(
        cls, context: bpy.types.Context, event: bpy.types.Event, mouse_pos: tuple[int, int] = None
    ):
        region = context.region
        rv3d = context.region_data
        assert rv3d and region
        original_perspective = rv3d.view_perspective

        # TODO The raycast was working for orthographic view, but not when you are inside a camera view. This solution feels hacky,
        # but it temporarily switches the perspective_matrix from camera to the perspective_matrix from ortho view.
        if original_perspective == "CAMERA":
            rv3d.view_perspective = "ORTHO"
        if not mouse_pos:
            mouse_pos = event.mouse_region_x, event.mouse_region_y

        view_vector = tool.Cad.region_2d_to_vector_3d_np(region, rv3d, mouse_pos)
        ray_origin = tool.Cad.region_2d_to_origin_3d_np(
            region, rv3d, mouse_pos, clamp=10
        )  # TODO clamp is hardcoded but might be necessary to adapt

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
    def ray_cast_by_proximity_2d(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        snap_obj: SnapObj,
    ):

        def divide_vector(start, end, n):
            points = []
            delta = (end - start) / n
            for i in range(1, n):
                point = start + i * delta
                points.append(point)
            return points

        region = context.region
        rv3d = context.region_data
        mouse_pos = event.mouse_region_x, event.mouse_region_y
        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)
        points = []

        try:
            loc = tool.Cad.region_2d_to_location_3d_np(region, rv3d, mouse_pos, ray_direction)
        except:
            loc = Vector((0, 0, 0))

        snap_obj._ensure_bvh()
        intersected = snap_obj.raycast_boxes(
            context, event, snap_obj.root, intersected=[], rays=(ray_origin, ray_direction)
        )

        # Collect edges from intersected BVH boxes
        edges = []
        for it in intersected:
            edges.extend(it.edges)
        edges = set(edges)

        # Build only the vertices indices that belong to these edges
        verts_idx: set[int] = set()
        for e in edges:
            ev = snap_obj.obj.data.edges[e].vertices
            verts_idx.add(ev[0])
            verts_idx.add(ev[1])

        # Lazily project only the needed vertices to 2D screen space
        verts_2d: dict[int, Vector] = {}
        for idx in verts_idx:
            v2d = view3d_utils.location_3d_to_region_2d(region, rv3d, snap_obj.verts_3d[idx])
            if v2d is not None:
                verts_2d[idx] = v2d

        edge_verts = {}
        for e in edges:
            verts_idx = snap_obj.obj.data.edges[e].vertices
            v1 = snap_obj.verts_3d[verts_idx[0]]
            v2 = snap_obj.verts_3d[verts_idx[1]]
            v1_2d = verts_2d.get(verts_idx[0])
            v2_2d = verts_2d.get(verts_idx[1])
            if (v1_2d is None) ^ (v2_2d is None):
                point, _ = cls.intersect_edge_region_border(region, context.space_data, rv3d, v1, v2)
                if v1_2d is None:
                    edge_verts[e] = (point, v2_2d)
                else:
                    edge_verts[e] = (v1_2d, point)
            else:
                edge_verts[e] = (v1_2d, v2_2d)

        snap_threshold = 10.0

        # Check all vertices for proximity to mouse position.
        # Re-use the 2D projections already computed for edge endpoints.
        for i, v3d in enumerate(snap_obj.verts_3d):
            if i in verts_2d:
                v2d = verts_2d[i]
            else:
                v2d = view3d_utils.location_3d_to_region_2d(region, rv3d, v3d)
                if v2d is None:
                    continue
            distance = (Vector(mouse_pos) - v2d).length
            if distance <= snap_threshold:
                snap_point = {
                    "object": snap_obj.obj,
                    "type": "Vertex",
                    "point": snap_obj.verts_3d[i],
                    "distance": distance / 10,
                }
                points.append(snap_point)

        count = 0
        selected_edges = {}
        for e in edges:
            p0, p1 = edge_verts[e]
            p0x, p0y = p0
            p1x, p1y = p1
            px, py = mouse_pos

            # segment vector = p1 - p0
            sx = p1x - p0x
            sy = p1y - p0y

            # seg length squared
            seg_len_sq = sx * sx + sy * sy

            if seg_len_sq == 0.0:
                # degenerate segment: skip it
                continue

            # project (p - p0) onto seg: t = dot(p-p0, seg) / |seg|^2
            apx = px - p0x
            apy = py - p0y
            t = (apx * sx + apy * sy) / seg_len_sq

            # clamp to segment
            if t <= 0.0:
                t_clamped = 0.0
                cx, cy = p0x, p0y
            elif t >= 1.0:
                t_clamped = 1.0
                cx, cy = p1x, p1y
            else:
                t_clamped = t
                cx = p0x + sx * t_clamped
                cy = p0y + sy * t_clamped

            dx = px - cx
            dy = py - cy
            dist = math.hypot(dx, dy)
            if dist <= snap_threshold:
                selected_edges[dist] = e

        if selected_edges:
            min_dist = float("inf")
            for key in selected_edges:
                if key < min_dist:
                    min_dist = key

            idx = snap_obj.obj.data.edges[selected_edges[min_dist]].vertices
            edge_verts = (snap_obj.verts_3d[idx[0]], snap_obj.verts_3d[idx[1]])
            division_points = divide_vector(
                edge_verts[0], edge_verts[1], 2
            )  # TODO Make it work for different divisions
            for division_point in division_points:
                intersection = tool.Cad.point_on_edge(division_point, (ray_target, loc))
                distance = (division_point - intersection).length
                if distance < snap_threshold:
                    snap_point = {
                        "object": snap_obj.obj,
                        "type": "Edge Center",
                        "point": division_point.copy(),
                        "distance": distance,
                    }
                    points.append(snap_point)

            intersection = tool.Cad.intersect_edges_v2((ray_target, loc), edge_verts)
            if intersection[0]:
                if tool.Cad.is_point_on_edge(intersection[1], edge_verts):
                    distance = (intersection[1] - intersection[0]).length
                    if distance < snap_threshold:
                        snap_point = {
                            "object": snap_obj.obj,
                            "type": "Edge",
                            "point": intersection[1].copy(),
                            "edge_verts": edge_verts,
                            "distance": distance,
                        }
                        points.append(snap_point)

        return points

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

        snap_threshold = cls.calculate_snap_threshold(rv3d.view_distance)

        try:
            loc = tool.Cad.region_2d_to_location_3d_np(region, rv3d, mouse_pos, ray_direction)
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
            mw = obj.matrix_world.copy()
            obj = bpy.data.objects.new("new_object", obj.to_mesh().copy())
            obj.matrix_world = mw @ obj.matrix_world

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
        snap_threshold = cls.calculate_snap_threshold(rv3d.view_distance)

        try:
            loc = tool.Cad.region_2d_to_location_3d_np(region, rv3d, mouse_pos, ray_direction)
        except:
            loc = Vector((0, 0, 0))

        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline[0]
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
            loc = tool.Cad.region_2d_to_location_3d_np(region, rv3d, mouse_pos, ray_direction)
            intersection = tool.Cad.intersect_edge_plane_v2(ray_target, loc, plane_origin, plane_normal)
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
        snap_threshold = cls.calculate_snap_threshold(rv3d.view_distance)

        try:
            loc = tool.Cad.region_2d_to_location_3d_np(region, rv3d, mouse_pos, ray_direction)
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
                    if tool.Raycast.object_is_visible_in_clipping_plane(obj):
                        snap_obj = cls.create_snap_obj(obj)
                        if snap_obj is not None:
                            objs_to_raycast.append(snap_obj)

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

        for snap_obj in objs_to_raycast:
            if not include_wireframes and (
                snap_obj.obj.type in {"EMPTY", "CURVE"}
                or (hasattr(snap_obj.obj.data, "polygons") and len(snap_obj.obj.data.polygons) == 0)
            ):
                continue

            hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj.obj)

            if hit is not None:
                length_squared = (hit - ray_origin).length_squared
                if best_obj is None or length_squared < best_length_squared:
                    best_length_squared = length_squared
                    best_obj = hit_obj
                    best_hit = hit
                    best_face_index = face_index

        if best_obj is not None:
            return best_obj, best_hit, best_face_index

        else:
            return None, None, None

    @classmethod
    def process_wireframe_snap_obj(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        snap_obj,
        ray_origin: Vector,
        closest_snaps: list,
    ):
        snap_points = tool.Raycast.ray_cast_by_proximity_2d(context, event, snap_obj)
        hit_obj = None
        hit = None
        if snap_points:
            closest_length_squared = float("inf")
            for point in snap_points:
                point["group"] = "Wireframe"
                closest_snaps.append(point)
                length = (point["point"] - ray_origin).length_squared
                if length < closest_length_squared:
                    closest_length_squared = length
                    hit = point["point"]
                    hit_obj = point["object"]
        return hit_obj, hit

    @classmethod
    def ray_cast_and_get_closest_to_camera_snaps(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        objs_to_raycast: list[bpy.types.Object],
    ) -> Union[tuple[bpy.types.Object, Vector, int], tuple[None, None, None]]:
        closest_length_squared = 1.0
        closest_obj = None
        closest_hit = None
        closest_face_index = None

        ray_origin, ray_target, ray_direction = cls.get_viewport_ray_data(context, event)

        space = context.space_data
        xray_mode = (space.shading.type == "SOLID" and space.shading.show_xray) or (
            space.shading.type == "WIREFRAME" and space.shading.show_xray_wireframe
        )

        closest_snaps = []

        if not xray_mode and objs_to_raycast:
            # Non-xray - only the closest solid object's Face snap is kept by
            # the caller (detect_snapping_points).  Process solids in distance
            # order and stop at the first hit to minimise raycasts.
            wireframe_objs = []
            solid_objs = []
            for snap_obj in objs_to_raycast:
                if snap_obj.obj.type in {"EMPTY", "CURVE"} or (
                    hasattr(snap_obj.obj.data, "polygons") and len(snap_obj.obj.data.polygons) == 0
                ):
                    wireframe_objs.append(snap_obj)
                else:
                    solid_objs.append(snap_obj)

            # Rough distance - object origin to ray origin
            solid_objs.sort(key=lambda so: (so.obj.matrix_world.translation - ray_origin).length_squared)

            # Process wireframe objects first (all of them, always collected)
            for snap_obj in wireframe_objs:
                hit_obj, hit = cls.process_wireframe_snap_obj(context, event, snap_obj, ray_origin, closest_snaps)
                if hit is not None:
                    length_squared = (hit - ray_origin).length_squared
                    if closest_obj is None or length_squared < closest_length_squared:
                        closest_length_squared = length_squared
                        closest_obj = hit_obj
                        closest_hit = hit
                        closest_face_index = None

            # Process solid objects in distance order, stop at first hit
            for snap_obj in solid_objs:
                hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj.obj)

                if hit:
                    snap_point = {
                        "point": hit,
                        "type": "Face",
                        "group": "Object",
                        "object": hit_obj,
                        "face_index": face_index,
                        "distance": 9,  # High value so it has low priority
                    }
                    closest_snaps.append(snap_point)

                    length_squared = (hit - ray_origin).length_squared
                    if closest_obj is None or length_squared < closest_length_squared:
                        closest_length_squared = length_squared
                        closest_obj = hit_obj
                        closest_hit = hit
                        closest_face_index = face_index

                    break

        else:
            # Xray mode - process all objects (all snaps are kept by the caller)
            for snap_obj in objs_to_raycast:
                if snap_obj.obj.type in {"EMPTY", "CURVE"} or (
                    hasattr(snap_obj.obj.data, "polygons") and len(snap_obj.obj.data.polygons) == 0
                ):
                    hit_obj, hit = cls.process_wireframe_snap_obj(context, event, snap_obj, ray_origin, closest_snaps)
                    face_index = None
                else:
                    # Solid objects
                    hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj.obj)

                    if hit:
                        snap_point = {
                            "point": hit,
                            "type": "Face",
                            "group": "Object",
                            "object": hit_obj,
                            "face_index": face_index,
                            "distance": 9,  # High value so it has low priority
                        }
                        closest_snaps.append(snap_point)

                if hit is not None:
                    length_squared = (hit - ray_origin).length_squared
                    if closest_obj is None or length_squared < closest_length_squared:
                        closest_length_squared = length_squared
                        closest_obj = hit_obj
                        closest_hit = hit
                        closest_face_index = face_index

        # Label snaps from the closest object
        if closest_obj is not None:
            for snap in closest_snaps:
                if snap["object"] == closest_obj:
                    snap["is_closest_to_camera"] = True

        return closest_snaps

    @classmethod
    def calculate_snap_threshold(cls, view_distance):
        snap_threshold = view_distance / 100
        area = tool.Blender.get_view3d_area()
        lens = area.spaces.active.lens
        xp = np.array([1, 10, 50])
        fp = np.array([50, 10, 1])
        value = np.interp(lens, xp, fp)
        if lens < 50:
            snap_threshold *= value
        return snap_threshold

    @classmethod
    def create_snap_obj(cls, obj):
        if obj.data is None or not isinstance(obj.data, bpy.types.Mesh):
            return None
        for i, snap_obj in enumerate(cls.snap_objs):
            if obj.name == snap_obj.obj.name:
                # Handle objects modified while a modal operator is active.
                # Example: adding a door or window alters the wall geometry.
                if len(obj.data.vertices) != len(snap_obj.verts_3d):
                    cls.snap_objs.pop(i)
                    snap_obj = SnapObj(obj)
                    cls.snap_objs.append(snap_obj)
                for v1, v2 in zip(obj.data.vertices, snap_obj.verts_3d):
                    if (obj.matrix_world @ v1.co) != v2:
                        cls.snap_objs.pop(i)
                        snap_obj = SnapObj(obj)
                        cls.snap_objs.append(snap_obj)
                return snap_obj
        snap_obj = SnapObj(obj)
        cls.snap_objs.append(snap_obj)
        return snap_obj

    @classmethod
    def clear_snap_objs(cls):
        TreeNode.__clear_all__()
        SnapObj.__clear_all__()
        cls.snap_objs.clear()


class TreeNode:
    all = []

    def __init__(self, box: tuple):
        self.__class__.all.append(self)
        self.box = box
        self.child_a = None
        self.child_b = None
        self.edges = []

    def __clear_all__():
        for instance in TreeNode.all:
            del instance
        TreeNode.all.clear()


class SnapObj:
    max_depth = 9
    all = []

    def __init__(self, obj: bpy.types.Object):
        self.__class__.all.append(self)
        self.obj = obj
        self.root = None
        self._bvh_built = False
        self.verts_3d = [obj.matrix_world @ v.co for v in obj.data.vertices]
        self.snap_points = []

    def _ensure_bvh(self):
        if self._bvh_built:
            return
        self.root = self._create_root_node()
        self.root.edges = [e.index for e in self.obj.data.edges]
        self.split_box(self.root, 0)
        self._bvh_built = True

    def __clear_all__():
        for instance in SnapObj.all:
            del instance
        SnapObj.all.clear()

    def _create_root_node(self) -> TreeNode:
        bbox = tool.Blender.get_object_bounding_box(self.obj)
        min_point = self.obj.matrix_world @ bbox["min_point"]
        max_point = self.obj.matrix_world @ bbox["max_point"]
        new_bbox = self.expand_bounding_box((min_point, max_point))
        return TreeNode(new_bbox)

    def divide_bounding_box_along_longest_axis(
        self, min_pt: Vector, max_pt: Vector
    ) -> Union[tuple[Vector, Vector], tuple[Vector, Vector]]:
        """
        Divide a bounding box into two equal parts along the axis with the longest dimension.

        Args:
            min_pt: The minimum point of the bounding box.
            max_pt: The maximum point of the bounding box.

        Returns:
            list: A list of two tuples, each containing the minimum and maximum points of the divided boxes.
        """

        # Calculate the dimensions of the box
        dx = max_pt.x - min_pt.x
        dy = max_pt.y - min_pt.y
        dz = max_pt.z - min_pt.z

        # Determine the axis with the longest dimension
        if dx >= dy and dx >= dz:
            # Divide along the x-axis
            mid_x = min_pt.x + dx / 2
            box1 = (min_pt, Vector((mid_x, max_pt.y, max_pt.z)))
            box2 = (Vector((mid_x, min_pt.y, min_pt.z)), max_pt)
        elif dy >= dx and dy >= dz:
            # Divide along the y-axis
            mid_y = min_pt.y + dy / 2
            box1 = (min_pt, Vector((max_pt.x, mid_y, max_pt.z)))
            box2 = (Vector((min_pt.x, mid_y, min_pt.z)), max_pt)
        else:
            # Divide along the z-axis
            mid_z = min_pt.z + dz / 2
            box1 = (min_pt, Vector((max_pt.x, max_pt.y, mid_z)))
            box2 = (Vector((min_pt.x, min_pt.y, mid_z)), max_pt)

        return [box1, box2]

    def expand_bounding_box(self, box: tuple[Vector, Vector], offset: float = 0.1) -> tuple[Vector, Vector]:
        """
        Expand a 3D bounding box by a given offset.

        Args:
            min_pt: The minimum point of the bounding box.
            max_pt: The maximum point of the bounding box.
            offset: The offset to expand the bounding box by.

        Returns:
            tuple: A tuple containing the new minimum and maximum points of the expanded bounding box.
        """

        min_pt, max_pt = box
        # Calculate the new minimum and maximum points
        new_min_pt = Vector((min_pt.x - offset, min_pt.y - offset, min_pt.z - offset))
        new_max_pt = Vector((max_pt.x + offset, max_pt.y + offset, max_pt.z + offset))

        return new_min_pt, new_max_pt

    def split_box(self, parent: TreeNode, depth: int):
        """
        Splits the bounding box creating two child nodes to compose a BVH Tree recursively.

        Args:
            parent: the TreeNode instance that represents the parent node of a BVH Tree.
            depth: the depth of the BVH Tree no be used in recursion.
        """
        if depth > self.max_depth:
            return
        box_a, box_b = self.divide_bounding_box_along_longest_axis(parent.box[0], parent.box[1])
        parent.child_a = TreeNode(box_a)
        parent.child_b = TreeNode(box_b)
        edges_a = []
        edges_b = []
        for e in parent.edges:
            verts_idx = [v for v in self.obj.data.edges[e].vertices]
            verts_coords = []
            for idx in verts_idx:
                if idx < len(self.obj.data.vertices):
                    verts_coords.append(self.obj.matrix_world @ self.obj.data.vertices[idx].co)
            if self.line_intersects_box(verts_coords[0], verts_coords[1], parent.child_a.box):
                edges_a.append(e)
            if self.line_intersects_box(verts_coords[0], verts_coords[1], parent.child_b.box):
                edges_b.append(e)
        parent.child_a.edges = edges_a
        parent.child_b.edges = edges_b
        self.split_box(parent.child_a, depth + 1)
        self.split_box(parent.child_b, depth + 1)

    def raycast_box(
        self, context: bpy.types.Context, event: bpy.types.Event, node: TreeNode, rays: tuple[Vector, Vector]
    ) -> bool:
        """
        Raycast bounding box.

        Args:
            context: Blender context.
            event: Blender event.
            node: a TreeNode instance.
            rays: tuple containing ray origin and ray direction

        Returns:
            True if hits the box or False otherwise.
        """
        box = node.box
        min_v = box[0]
        max_v = box[1]
        t_min = 0.0
        t_max = float("inf")
        ray_origin, ray_dir = rays
        inv_dir = Vector((1.0 / r if r != 0.0 else 1e32) for r in (ray_dir.x, ray_dir.y, ray_dir.z))
        # X
        tx1 = (min_v.x - ray_origin.x) * inv_dir[0]
        tx2 = (max_v.x - ray_origin.x) * inv_dir[0]
        tmin = min(tx1, tx2)
        tmax = max(tx1, tx2)
        # Y
        ty1 = (min_v.y - ray_origin.y) * inv_dir[1]
        ty2 = (max_v.y - ray_origin.y) * inv_dir[1]
        tmin = max(tmin, min(ty1, ty2))
        tmax = min(tmax, max(ty1, ty2))
        # Z
        tz1 = (min_v.z - ray_origin.z) * inv_dir[2]
        tz2 = (max_v.z - ray_origin.z) * inv_dir[2]
        tmin = max(tmin, min(tz1, tz2))
        tmax = min(tmax, max(tz1, tz2))
        return (tmax >= max(tmin, t_min)) and (tmin <= t_max)

    def line_intersects_box(self, v1: mathutils.Vector, v2: mathutils.Vector, box: tuple) -> bool:
        """
        Check if a line segment intersects an axis-aligned bounding box (AABB).

        Args:
            v1: The first endpoint of the line segment as a mathutils.Vector.
            v2: The second endpoint of the line segment as a mathutils.Vector.
            box: A tuple containing the minimum and maximum points of the AABB, where each point is a mathutils.Vector.

        Returns:
            bool: True if the segment [v1, v2] intersects the AABB; otherwise, False.
        """
        bmin, bmax = box
        dir = v2 - v1
        tmin = 0.0
        tmax = 1.0

        for i in range(3):
            if abs(dir[i]) < 1e-12:
                # Line is parallel to slab. If origin not within slab -> no hit.
                if v1[i] < bmin[i] or v1[i] > bmax[i]:
                    return False
            else:
                ood = 1.0 / dir[i]
                t1 = (bmin[i] - v1[i]) * ood
                t2 = (bmax[i] - v1[i]) * ood
                if t1 > t2:
                    t1, t2 = t2, t1
                if t1 > tmin:
                    tmin = t1
                if t2 < tmax:
                    tmax = t2
                if tmin > tmax:
                    return False

        # If any overlap in [0,1] exists, there's intersection
        return (tmax >= 0.0) and (tmin <= 1.0)

    def raycast_boxes(
        self,
        context: bpy.types.Context,
        event: bpy.Types.Event,
        node: TreeNode,
        intersected: Union[TreeNode] = [],
        rays: tuple[Vector, Vector] = (),
    ) -> Union[TreeNode]:
        """
        Raycast bounding box subdivisions recursively.

        Args:
            context: Blender context.
            event: Blender event.
            node: a TreeNode instance.
            intersected: list of intersected boxes to use in recursion.
            rays: tuple containing ray origin and ray direction

        Returns:
            tuple: a list of TreeNode instances that represent the subdivided boxes hit by the ray cast.
        """
        if not node.child_a:
            intersected.append(node)
            return intersected

        intersects_a = self.raycast_box(context, event, node.child_a, rays)
        intersects_b = self.raycast_box(context, event, node.child_b, rays)
        if intersects_a:
            intersected = self.raycast_boxes(context, event, node.child_a, intersected, rays)

        if intersects_b:
            intersected = self.raycast_boxes(context, event, node.child_b, intersected, rays)

        return intersected
