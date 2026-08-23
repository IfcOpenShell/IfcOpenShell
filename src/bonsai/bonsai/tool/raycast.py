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

from typing import Union

import bmesh
import bpy
import gpu
import mathutils
import numpy as np
from bpy_extras import view3d_utils
from gpu.types import (
    GPUBatch,
    GPUIndexBuf,
    GPUOffScreen,
    GPUShaderCreateInfo,
    GPUStageInterfaceInfo,
    GPUVertBuf,
    GPUVertFormat,
)
from mathutils import Matrix, Vector

import bonsai.core.tool
import bonsai.tool as tool
from bonsai.bim.module.drawing.data import DecoratorData
from bonsai.bim.module.drawing.decoration import CutDecorator


_wireframe_batch_cache: dict[int, dict[str, tuple[GPUBatch, int, list]]] = {}
_wireframe_vert_fmt: GPUVertFormat | None = None
_triangle_batch_cache: dict[int, tuple[GPUBatch, int]] = {}
_triangle_vert_fmt: GPUVertFormat | None = None
_encoding_shader: gpu.types.GPUShader | None = None
_offscreen: GPUOffScreen | None = None
_obj_list: list[[bpy.types.Object, bool]] = []

_SNAP_RADIUS_PX = 10  # half-size of the readback region around the cursor


def _create_encoding_shader() -> gpu.types.GPUShader:
    """Unlit flat-colour shader for encoding primitive IDs as RGBA."""
    iface = GPUStageInterfaceInfo("iface")
    iface.flat("FLOAT", "slot_id")

    shader_info = GPUShaderCreateInfo()
    shader_info.push_constant("MAT4", "MVP")
    shader_info.push_constant("FLOAT", "slot_base")
    shader_info.vertex_in(0, "VEC3", "pos")
    shader_info.vertex_in(1, "FLOAT", "vert_slot")
    shader_info.vertex_out(iface)
    shader_info.fragment_out(0, "VEC4", "FragColor")

    shader_info.vertex_source(
        "void main() {\n" "  slot_id = vert_slot;\n" "  gl_Position = MVP * vec4(pos, 1.0);\n" "}\n"
    )
    shader_info.fragment_source(
        "vec4 encode(float f) {\n"
        "  ivec4 c;\n"
        "  int fi = int(f);\n"
        "  c.r = (fi      ) & 0xFF;\n"
        "  c.g = (fi >> 8 ) & 0xFF;\n"
        "  c.b = (fi >> 16) & 0xFF;\n"
        "  c.a = (fi >> 24) & 0xFF;\n"
        "  return vec4(c) / 255.0;\n"
        "}\n"
        "void main() {\n"
        "  FragColor = encode(slot_base + slot_id);\n"
        "}\n"
    )
    s = gpu.shader.create_from_info(shader_info)
    del shader_info, iface
    return s


def _decode_wireframe_pixel(r: int, g: int, b: int, a: int) -> int:
    """Decode an RGBA pixel back to an integer slot ID."""
    return (a << 24) | (b << 16) | (g << 8) | r


def _create_vert_format() -> GPUVertFormat:
    """Attribute 0 = position (vec3), attribute 1 = primitive slot (float); solid faces use 0."""
    fmt = GPUVertFormat()
    fmt.attr_add(id="pos", comp_type="F32", len=3, fetch_mode="FLOAT")
    fmt.attr_add(id="vert_slot", comp_type="F32", len=1, fetch_mode="FLOAT")
    return fmt


def _find_closest_wireframe_pixel(buffer_data, cx, cy):
    """Scan *buffer_data* (list of rows) for the closest non-zero pixel
    to (cx, cy). Used for points a lines detection.  Returns ``(encoded_value, dx, dy)`` or None."""
    best_dist = float("inf")
    best = None
    for y, row in enumerate(buffer_data):
        for x, px in enumerate(row):
            r, g, b, a = px
            if r == 0 and g == 0 and b == 0 and a == 0:
                continue
            val = _decode_wireframe_pixel(r, g, b, a)
            if val > 0:
                dx = x - cx
                dy = y - cy
                d2 = dx * dx + dy * dy
                if d2 < best_dist:
                    best_dist = d2
                    best = (val, dx, dy)
    return best


def _get_solid_triangles(obj: bpy.types.Object) -> list[tuple[tuple, tuple, tuple]]:
    """Return the list of triangles for *obj* in **local** space.

    Uses evaluated mesh so that modifiers are respected.
    The world matrix is applied separately in the shader.

    Returns
        tris: list[tuple[tuple, tuple, tuple]] = []
    """
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    if not mesh or not mesh.vertices:
        if mesh:
            eval_obj.to_mesh_clear()
        return []

    mesh.calc_loop_triangles()

    tris: list[tuple[tuple, tuple, tuple]] = []
    for tri in mesh.loop_triangles:
        v0 = mesh.vertices[tri.vertices[0]].co
        v1 = mesh.vertices[tri.vertices[1]].co
        v2 = mesh.vertices[tri.vertices[2]].co
        tris.append(
            (
                (v0.x, v0.y, v0.z),
                (v1.x, v1.y, v1.z),
                (v2.x, v2.y, v2.z),
            )
        )

    eval_obj.to_mesh_clear()
    return tris

def _get_cut_object_solid_triangles(obj: bpy.types.Object) -> list[tuple[tuple, tuple, tuple]]:
    """
    Gets all the triangles from cut decorator fill, in local space

    Returns
    tris_co : list[tuple[tuple, tuple, tuple]]
        list of all triangle vertices
    """
    model_props = tool.Model.get_model_props()
    if not (element := tool.Ifc.get_entity(obj)):
        return []
    if model_props.show_cut_decorator_fill and element.id() in DecoratorData.fill_cache:
        tris_co: list[tuple[tuple, tuple, tuple]] = []
        for color, verts_and_tris in DecoratorData.fill_cache[element.id()].items():
            for verts, tris in verts_and_tris:
                verts = [tuple(obj.matrix_world.inverted() @ Vector(v)) for v in verts]  # local space
                for tri in tris:
                    new_verts = [verts[vi] for vi in tri]
                    tris_co.append(tuple(new_verts))

    return tris_co


def _ensure_triangle_batches(obj: bpy.types.Object) -> tuple[GPUBatch | None, bool]:
    """Build (or fetch from cache) a TRIANGLES batch for *obj*.

    When in drawing view, creates the triangles from cut decorator fill.
    In model view, creates the triangles from object face..
    Every triangle is rendered with a zeroed vertex slot since the
    GPU only encodes the object index; the face is found later via ray_cast.

    Returns
    batch : GPUBatch | None when the object has no faces.
        All triangles batch from the object
    is_cut_face : bool
        This is used later in snap. Indicates if bash comes from cut geometry. Tris from cut geometry are irregular, so we don't want to use them to create edges and vertices snaps. They are handled by wireframe snaps
    """

    global _triangle_vert_fmt, _triangle_batch_cache

    is_cut_face = False

    if _triangle_vert_fmt is None:
        _triangle_vert_fmt = _create_vert_format()

    cache_key = id(obj)
    if cache_key in _triangle_batch_cache:
        return _triangle_batch_cache[cache_key]

    tris = []
    if CutDecorator.installed:
        tris = _get_cut_object_solid_triangles(obj)
        if tris:
            is_cut_face = True
        if not tris and (hasattr(obj.data, "polygons") and len(obj.data.polygons) > 0):
            tris = _get_solid_triangles(obj)
            is_cut_face = False

    else:
        tris = _get_solid_triangles(obj)
    n_tris = len(tris)
    if n_tris == 0:
        return None, is_cut_face

    # Flatten: 3 verts per tri; the slot is unused for solid faces
    coords: list[tuple[float, float, float]] = []
    slot_ids: list[float] = []
    for tri in tris:
        for v in tri:
            coords.append(v)
            slot_ids.append(0.0)

    n_verts = len(coords)
    vbo = GPUVertBuf(len=n_verts, format=_triangle_vert_fmt)
    vbo.attr_fill(id="pos", data=coords)
    vbo.attr_fill(id="vert_slot", data=slot_ids)

    ibo = GPUIndexBuf(type="TRIS", seq=[(i * 3, i * 3 + 1, i * 3 + 2) for i in range(n_tris)])
    batch = GPUBatch(type="TRIS", buf=vbo, elem=ibo)

    _triangle_batch_cache[cache_key] = (batch, is_cut_face)
    return batch, is_cut_face


def _get_boundary_features(obj: bpy.types.Object) -> tuple[list[tuple[float, float, float]], list[tuple[tuple, tuple]]]:
    """
    Uses bmesh on the **evaluated** mesh so that modifiers are respected.
    Gets only edges that are not in a face and vertices that are not on and edge

    Returns
    verts : list[tuple[float, float, float]]
        Positions of unique vertices from boundary edges plus isolated
        vertices (vertices with **no** connected edges), in local space.
    edge_pairs : list[tuple[tuple[float,float,float], tuple[float,float,float]]]
        Pairs of vertex positions for edges that have **no** linked faces
        (boundary / wire edges), in local space.
    """

    if obj.type == "EMPTY":
        return [(0.0, 0.0, 0.0)], []

    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj = obj.evaluated_get(depsgraph)
    mesh = eval_obj.to_mesh()
    if not mesh or not mesh.vertices:
        if mesh:
            eval_obj.to_mesh_clear()
        return [], []

    bm = bmesh.new()
    bm.from_mesh(mesh)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # Collect unique vertices: isolated vertices + endpoints of boundary edges
    seen_verts: set[tuple[float, float, float]] = set()
    verts: list[tuple[float, float, float]] = []

    # Vertices that are not connected to any edge
    for v in bm.verts:
        if not v.link_edges:
            coord = (v.co.x, v.co.y, v.co.z)
            if coord not in seen_verts:
                seen_verts.add(coord)
                verts.append(coord)

    # Edges that are not part of any face (boundary / wire)
    edge_pairs: list[tuple[tuple, tuple]] = []
    for e in bm.edges:
        if not e.link_faces:
            v0, v1 = e.verts
            edge_pairs.append(
                (
                    (v0.co.x, v0.co.y, v0.co.z),
                    (v1.co.x, v1.co.y, v1.co.z),
                )
            )
            # Add unique endpoint vertices
            for v in (v0, v1):
                coord = (v.co.x, v.co.y, v.co.z)
                if coord not in seen_verts:
                    seen_verts.add(coord)
                    verts.append(coord)

    bm.free()
    eval_obj.to_mesh_clear()
    return verts, edge_pairs

def _get_cut_object_features(
    obj: bpy.types.Object,
) -> (list[tuple[float, float, float]], list[tuple[tuple[float, float, float], tuple[float, float, float]]]):
    """Return ``(all_vert_coords, edge_pairs)`` for *obj*.

    Gets vertices and edges from the cut decorator

    Returns
    verts : list[tuple[float, float, float]]
        Positions of unique vertices from cut decorator, in local space.
    edge_pairs : list[tuple[tuple[float,float,float], tuple[float,float,float]]]
        Pairs of vertex positions for edges from cut decorator, in local space.
    """
    model_props = tool.Model.get_model_props()
    if not (element := tool.Ifc.get_entity(obj)):
        return [], []
    if model_props.show_cut_decorator and element.id() in DecoratorData.cut_cache and (hasattr(obj.data, "polygons") and len(obj.data.polygons) > 0):
        verts, edges = DecoratorData.cut_cache[element.id()]
        if not verts or not edges:
            return {}, {}
        verts = [tuple(obj.matrix_world.inverted() @ Vector(v)) for v in verts]  # local space
        edge_pairs = [(verts[v0], verts[v1]) for v0, v1 in edges]

        return verts, edge_pairs
    else:
        return [], []


def _ensure_wireframe_batches(obj: bpy.types.Object) -> dict[str, tuple[GPUBatch, int, list]]:
    """Build (or fetch from cache) POINTS + LINES batches.

    When in drawing view, gets edges and vertices from the cut decorator.
    In model view, gets boundary edges (no faces) and their endpoint vertices plus any
    isolated vertices (no edges) are included.
    Returns ``{'POINTS': (batch, count, coords_list),
    'LINES': (batch, count, edge_pairs_list)}`` or an empty dict when
    there is nothing snappable.
    """

    global _wireframe_vert_fmt, _wireframe_batch_cache

    if _wireframe_vert_fmt is None:
        _wireframe_vert_fmt = _create_vert_format()

    cache_key = id(obj)

    # Cache hit
    if cache_key in _wireframe_batch_cache:
        return _wireframe_batch_cache[cache_key]

    if CutDecorator.installed:
        all_vert_coords, edge_pairs = [], []
        v, e = _get_cut_object_features(obj)
        if v and e:
            all_vert_coords, edge_pairs = v, e

        if hasattr(obj.data, "polygons") and len(obj.data.polygons) == 0:
            v, e = _get_boundary_features(obj)
            all_vert_coords.extend(v)
            edge_pairs.extend(e)
    else:
        # avoids creating batches for solid objects
        if hasattr(obj.data, "polygons") and len(obj.data.polygons) > 0:
            return {}

        all_vert_coords, edge_pairs = _get_boundary_features(obj)



    batches: dict[str, tuple[GPUBatch, int, list]] = {}

    # POINTS batch (all wireframe vertices)
    n_pts = len(all_vert_coords)
    if n_pts > 0:
        vbo = GPUVertBuf(len=n_pts, format=_wireframe_vert_fmt)
        vbo.attr_fill(id="pos", data=all_vert_coords)
        vbo.attr_fill(id="vert_slot", data=[float(i) for i in range(n_pts)])

        ibo = GPUIndexBuf(type="POINTS", seq=list(range(n_pts)))
        batches["POINTS"] = (GPUBatch(type="POINTS", buf=vbo, elem=ibo), n_pts, all_vert_coords)

    # LINES batch (boundary edges)
    n_lines = len(edge_pairs)
    if n_lines > 0:
        coords: list[tuple] = []
        prim_ids: list[float] = []
        for e_idx, (c0, c1) in enumerate(edge_pairs):
            coords.append(c0)
            coords.append(c1)
            prim_ids.append(float(e_idx))
            prim_ids.append(float(e_idx))

        n_line_verts = len(coords)
        vbo = GPUVertBuf(len=n_line_verts, format=_wireframe_vert_fmt)
        vbo.attr_fill(id="pos", data=coords)
        vbo.attr_fill(id="vert_slot", data=prim_ids)

        ibo = GPUIndexBuf(type="LINES", seq=[(i, i + 1) for i in range(0, n_line_verts, 2)])
        batches["LINES"] = (GPUBatch(type="LINES", buf=vbo, elem=ibo), n_lines, edge_pairs)

    if batches:
        _wireframe_batch_cache[cache_key] = batches
    return batches

def _get_tris_render_ops(objs_to_raycast: list[bpy.types.Object]) -> list[tuple[GPUBatch, Matrix, int]]:
    """Build render ops for solid (triangle) objects to raycast.

    Each mesh contributes a single TRIANGLES batch and a slot base that 
    encodes its index in the global ``_obj_list`` (slot 0 is reserved for 
    the background). The batch is drawn unlit so the object index can be
    read back from the framebuffer. 

    Args: 
        objs_to_raycast: iterable of candidate objects. 

    Returns:
        list[tuple[GPUBatch, Matrix, int]]: ``(batch, world_matrix, slot_base)``
        for every mesh with faces. Populates ``_obj_list`` as a side effect.
    """
    global _obj_list

    render_ops: list[tuple[GPUBatch, Matrix, int]] = []

    for snap_obj in objs_to_raycast:
        if snap_obj.type != "MESH":
            continue
        if not hasattr(snap_obj.data, "polygons"):
            continue
        if len(snap_obj.data.polygons) == 0:
            continue

        batch, is_cut_face = _ensure_triangle_batches(snap_obj)
        if batch is None:
            continue

        obj_index = len(_obj_list)
        _obj_list.append((snap_obj, is_cut_face))
        slot_base = obj_index + 1  # slot 0 = background
        render_ops.append((batch, snap_obj.matrix_world.copy(), slot_base))
    return render_ops
    
def _create_tris_snaps(context: bpy.types.Context, event: bpy.types.Event, mouse_read_rect, buffers_list, last_buf, xray_mode) -> tuple[list[dict], bpy.types.Object | None]:
    """Decode the triangle readback buffer(s) into face snaps.
 
    In xray mode each object is read back as a single pixel under the 
    cursor (``buffers_list``); otherwise the center pixel of the readback 
    region (``last_buf``) is decoded. Every hit object is then ray cast for 
    real to find the exact face, producing one ``Face`` snap per hit. 
 
    Args: 
        context: Blender context. 
        event: the event carrying the cursor position.
        mouse: ``(mx, read_x, my, read_y)`` cursor and readback origin. 
        buffers_list: per-object single-pixel buffers (xray mode only). 
        last_buf: full readback region buffer (non-xray mode).
        xray_mode: whether solid xray rendering is active.
 
    Returns:
        tuple[list[dict], bpy.types.Object | None]: the face snaps and the
        closest hit object, or ``([], None)`` when nothing was hit. 
    """
           
    global _obj_list

    w, h, mx, my, read_x, read_y = mouse_read_rect
    # Decode hits
    hits: set[int] = set()

    if xray_mode:
        vals_read: set[int] = set()
        # Each buffer is a single pixel read back right under the
        # cursor. When the cursor is outside the region there is
        # nothing to snap to, matching the previous bounds check.
        if not (0 <= mx < w and 0 <= my < h):
            return [], None
        for buf in buffers_list:
            pixel_data = buf.to_list()
            if not pixel_data or not pixel_data[0]:
                return [], None
            px = pixel_data[0][0]
            val = _decode_wireframe_pixel(px[0], px[1], px[2], px[3])
            if val in vals_read:  # avoid getting all the tris from the same object
                continue
            vals_read.add(val)
            if val > 0:
                obj_index = val - 1
                if obj_index < len(_obj_list):
                    hits.add(obj_index)
    else:
        pixel_data = last_buf.to_list()
        if not pixel_data or not pixel_data[0]:
            return [], None
        centre_x = mx - int(read_x)
        centre_y = my - int(read_y)
        if 0 <= centre_y < len(pixel_data) and 0 <= centre_x < len(pixel_data[0]):
            px = pixel_data[centre_y][centre_x]
            val = _decode_wireframe_pixel(px[0], px[1], px[2], px[3])
            if val > 0:
                obj_index = val - 1
                if obj_index < len(_obj_list):
                    hits.add(obj_index)

    if not hits:
        return [], None

    snaps: list[dict] = []
    closest_obj = None
    closest_dist = float("inf")
    ray_origin, _, _ = tool.Raycast.get_viewport_ray_data(context, event)
    for obj_index in hits:
        obj, is_cut_face = _obj_list[obj_index]
        hit_obj, hit, face_index = tool.Raycast.cast_rays_to_single_object(context, event, obj)
        if hit:
            snap: dict = {
                "point": hit,
                "type": "Face",
                "group": "Object",
                "object": hit_obj,
                "face_index": face_index,
                "is_cut": is_cut_face, # Used later in snap
                "distance": 9,  # High value so it has low priority
            }
            dist = (hit - ray_origin).length
            if dist < closest_dist:
                closest_dist = dist
                closest_obj = obj

            snaps.append(snap)

    return snaps, closest_obj
    
def _get_wireframe_render_ops(objs_to_raycast: list[bpy.types.Objects]) -> tuple[list[tuple[GPUBatch, Matrix, int]], list[tuple]]:
    """Build render ops for wireframe (non-solid) objects.

    Boundary points and lines of each object are assigned sequential slot 
    IDs across all objects, so every vertex and edge gets a unique encoded
    ID. Per-object slot ranges are recorded in ``obj_slots`` for decoding.

    Args: 
    objs_to_raycast: iterable of candidate objects. 

    Returns:
    tuple[list[tuple[GPUBatch, Matrix, int]], list[tuple]]: 
    ``(render_ops, obj_slots)`` where ``render_ops`` holds
    ``(batch, world_matrix, slot_base)`` and each ``obj_slots`` 
    entry is ``(snap_obj, pts_start, n_pts, lines_start, n_lines)``.
    """
       
    render_ops: list[tuple[GPUBatch, Matrix, int]] = []
    obj_slots: list[tuple] = []  # [(snap_obj, pts_start, n_pts, lines_start, n_lines), ...]

    slot = 1  # slot 0 = background

    for snap_obj in objs_to_raycast:
        batches = _ensure_wireframe_batches(snap_obj)
        if not batches:
            continue

        world_mat = snap_obj.matrix_world.copy()
        pts_start = 0
        n_pts = 0
        lines_start = 0
        n_lines = 0

        pts_data = batches.get("POINTS")
        if pts_data is not None:
            batch, n_pts, _ = pts_data
            pts_start = slot
            render_ops.append((batch, world_mat, slot))
            slot += n_pts

        lines_data = batches.get("LINES")
        if lines_data is not None:
            batch, n_lines, _ = lines_data
            lines_start = slot
            render_ops.append((batch, world_mat, slot))
            slot += n_lines

        if n_pts > 0 or n_lines > 0:
            obj_slots.append((snap_obj, pts_start, n_pts, lines_start, n_lines))

    return render_ops, obj_slots

def _create_wireframe_snaps(context: bpy.types.Context, event: bpy.types.Event, mouse_read_rect, obj_slots, last_buf) -> tuple[list[dict], None]:
    """Decode the wireframe readback buffer into vertex/edge snaps. 

    Finds the closest non-zero pixel to the cursor, maps its encoded slot ID
    back to a vertex or edge via ``obj_slots``, then builds the candidate 
    snaps (Vertex, Edge, Edge Center, plus endpoint Vertex snaps within the 
    snap threshold).

    Args: 
        context: Blender context. 
        event: the event carrying the cursor position.
        mouse: ``(mx, read_x, my, read_y)`` cursor and readback origin. 
        obj_slots: ``[(snap_obj, pts_start, n_pts, lines_start, n_lines), ...]``. 
        last_buf: full readback region buffer.

    Returns:
        tuple[list[dict], None]: the wireframe snaps, or ``([], None)`` when
        no non-zero pixel is found near the cursor. 
    """ 
    global _wireframe_batch_cache

    w, h, mx, my, read_x, read_y = mouse_read_rect
    centre = (mx - int(read_x), my - int(read_y))
    pixel_data = last_buf.to_list()
    best = _find_closest_wireframe_pixel(pixel_data, *centre)
    if best is None:
        return [], None
    encoded, dx, dy = best

    # Decode and build snap dicts

    rv3d = context.region_data
    snaps: list[dict] = []
    snap_threshold = tool.Raycast.calculate_snap_threshold(rv3d.view_distance)

    # Compute view ray for 3D proximity calculations
    _, ray_target, ray_direction = tool.Raycast.get_viewport_ray_data(context, event)
    try:
        loc = tool.Cad.region_2d_to_location_3d_np(context.region, rv3d, (mx, my), ray_direction)
    except Exception:
        loc = ray_target

    for snap_obj, pts_start, n_pts, lines_start, n_lines in obj_slots:
        if n_pts > 0 and pts_start <= encoded < pts_start + n_pts:
            vi = encoded - pts_start
            batches = _wireframe_batch_cache.get(id(snap_obj))
            if batches:
                pts_data = batches.get("POINTS")
                if pts_data:
                    _, _, coords = pts_data
                    if vi < len(coords):
                        local_pos = Vector(coords[vi])
                        world_pos = snap_obj.matrix_world @ local_pos
                        # Compute proper 3D distance from vertex to view ray
                        proj = tool.Cad.point_on_edge(world_pos, (ray_target, loc))
                        distance = (world_pos - proj).length
                        snaps.append(
                            {
                                "object": snap_obj,
                                "type": "Vertex",
                                "point": world_pos,
                                "distance": distance,
                                "group": "Wireframe",
                            }
                        )
            break

        if n_lines > 0 and lines_start <= encoded < lines_start + n_lines:
            ei = encoded - lines_start
            batches = _wireframe_batch_cache.get(id(snap_obj))
            if batches:
                lines_data = batches.get("LINES")
                if lines_data:
                    _, _, edge_pairs = lines_data
                    if ei < len(edge_pairs):
                        c0, c1 = edge_pairs[ei]
                        mw = snap_obj.matrix_world
                        v0 = mw @ Vector(c0)
                        v1 = mw @ Vector(c1)

                        # Compute closest point on edge to view ray
                        intersection = tool.Cad.intersect_edges_v2((ray_target, loc), (v0, v1))
                        if intersection[0] is not None and tool.Cad.is_point_on_edge(intersection[1], (v0, v1)):
                            edge_point = intersection[1].copy()
                            distance = (intersection[1] - intersection[0]).length
                        else:
                            # Fallback to midpoint if lines are parallel
                            edge_point = (v0 + v1) / 2
                            proj = tool.Cad.point_on_edge(edge_point, (ray_target, loc))
                            distance = (edge_point - proj).length

                        snaps.append(
                            {
                                "object": snap_obj,
                                "type": "Edge",
                                "point": edge_point,
                                "edge_verts": (v0, v1),
                                "distance": distance,
                                "group": "Wireframe",
                            }
                        )

                        # Edge Center snap (midpoint)
                        mid = (v0 + v1) / 2 # TODO Allow divisions by other values
                        mid_proj = tool.Cad.point_on_edge(mid, (ray_target, loc))
                        mid_dist = (mid - mid_proj).length
                        snaps.append(
                            {
                                "object": snap_obj,
                                "type": "Edge Center",
                                "point": mid,
                                "distance": mid_dist,
                                "group": "Wireframe",
                            }
                        )

                        # Also include vertex snaps for edge endpoints
                        for vtx in (v0, v1):
                            proj = tool.Cad.point_on_edge(vtx, (ray_target, loc))
                            vtx_dist = (vtx - proj).length
                            if vtx_dist < snap_threshold:
                                snaps.append(
                                    {
                                        "object": snap_obj,
                                        "type": "Vertex",
                                        "point": vtx,
                                        "distance": vtx_dist,
                                        "group": "Wireframe",
                                    }
                                )
            break

    return snaps, None

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
    def get_gpu_detection_snaps(
        cls,
        context: bpy.types.Context,
        event: bpy.types.Event,
        objs_to_raycast: list[bpy.types.Object],
        tris: bool = False,
    ) -> tuple[list[dict], bpy.types.Object | None]:
        """GPU-based solid face detection.

        Renders all solid objects' triangles to an offscreen buffer
        with per-face IDs encoded as colours, then reads the pixel(s)
        under the cursor to find which faces are hit.

        :return: ``(snaps, closest_obj)`` where *snaps* is a list of
            snap dicts (same format as the raycast-based version) and
            *closest_obj* is the single closest object (or None).
        """
        global _encoding_shader, _offscreen, _obj_list

        if bpy.app.background:
            return [], None

        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return [], None

        space = context.space_data
        xray_mode = (space.shading.type == "SOLID" and space.shading.show_xray) or (
            space.shading.type == "WIREFRAME" and space.shading.show_xray_wireframe
        )

        # Build the object index -> object lookup and collect render ops
        _obj_list.clear()
        render_ops: list[tuple[GPUBatch, Matrix, int]] = []
        obj_slots: list[tuple] = []  # [(snap_obj, pts_start, n_pts, lines_start, n_lines), ...]

        if tris:
            render_ops = _get_tris_render_ops(objs_to_raycast)
        else:
            render_ops, obj_slots = _get_wireframe_render_ops(objs_to_raycast)

        if not render_ops:
            return [], None

        # Render to offscreen buffer

        w, h = region.width, region.height
        mx = int(event.mouse_region_x)
        my = int(event.mouse_region_y)

        if _encoding_shader is None:
            _encoding_shader = _create_encoding_shader()  # same shader works for TRIS

        if _offscreen is None:
            _offscreen = GPUOffScreen(max(w, 1), max(h, 1), format="RGBA8")

        _encoding_shader.bind()

        if xray_mode:
            gpu.state.depth_mask_set(False)
            gpu.state.depth_test_set("NONE")
        else:
            gpu.state.depth_mask_set(True)
            gpu.state.depth_test_set("LESS")
        if not tris:
            gpu.state.depth_mask_set(False)
            gpu.state.depth_test_set("NONE")

        gpu.state.blend_set("NONE")
        gpu.state.face_culling_set("NONE")

        read_size = 2 * _SNAP_RADIUS_PX + 1
        read_x = max(0, min(mx - _SNAP_RADIUS_PX, w - read_size))
        read_y = max(0, min(my - _SNAP_RADIUS_PX, h - read_size))

        # For solid objects in xray_mode, when only need one pixel to detect tha face
        # So we change the read size for optimization
        read_per_object = xray_mode and tris
        if read_per_object:
            read_size = 1
            read_x = max(0, min(mx, w - 1))
            read_y = max(0, min(my, h - 1))

        buffers_list = []
        last_buf = None
        with _offscreen.bind():
            fb = gpu.state.active_framebuffer_get()
            fb.clear(color=(0.0, 0.0, 0.0, 0.0), depth=1.0)

            for batch, world_mat, slot_base in render_ops:
                mvp = rv3d.perspective_matrix @ world_mat
                _encoding_shader.uniform_float("MVP", mvp)
                _encoding_shader.uniform_float("slot_base", float(slot_base))
                with gpu.matrix.push_pop():
                    gpu.matrix.load_matrix(Matrix.Identity(4))
                    batch.draw(_encoding_shader)

                if read_per_object:  # gets all buffers
                    buf = fb.read_color(int(read_x), int(read_y), read_size, read_size, 4, 0, "UBYTE")
                    buffers_list.append(buf)
            if not read_per_object:
                last_buf = fb.read_color(int(read_x), int(read_y), read_size, read_size, 4, 0, "UBYTE")

        # Restore state
        gpu.state.depth_mask_set(True)
        gpu.state.depth_test_set("LESS")

        mouse_read_rect = (w, h, mx, my, read_x, read_y)
        if tris:
            return _create_tris_snaps(context, event, mouse_read_rect, buffers_list, last_buf, xray_mode)
        else:
            return _create_wireframe_snaps(context, event, mouse_read_rect, obj_slots, last_buf)

    @classmethod
    def get_gpu_solid_snaps(cls, context, event, objs_to_raycast):
        return cls.get_gpu_detection_snaps(context, event, objs_to_raycast, tris=True)

    @classmethod
    def get_gpu_wireframe_snaps(cls, context, event, objs_to_raycast):
        return cls.get_gpu_detection_snaps(context, event, objs_to_raycast)

    @classmethod
    def clear_cache(cls):
        global _wireframe_batch_cache, _wireframe_vert_fmt, _triangle_batch_cache, _triangle_vert_fmt, _encoding_shader, _offscreen, _obj_list
        _wireframe_batch_cache = {}
        _wireframe_vert_fmt= None
        _triangle_batch_cache= {}
        _triangle_vert_fmt= None
        _encoding_shader= None
        _offscreen= None
        _obj_list= []
        
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
                    if tool.Raycast.object_is_visible_in_clipping_plane(
                        obj
                    ):  # TODO Make this work only if clipping plane is active
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
                snap_obj.type in {"EMPTY", "CURVE"}
                or (hasattr(snap_obj.data, "polygons") and len(snap_obj.data.polygons) == 0)
            ):
                continue

            hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj)

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
        snap_points = tool.Raycast.ray_cast_by_proximity(context, event, snap_obj)
        hit_obj = None
        hit = None
        if snap_points:
            closest_length_squared = float("inf")
            for point in snap_points:
                point["group"] = "Wireframe"
                point["object"] = snap_obj
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
                if snap_obj.type in {"EMPTY", "CURVE"} or (
                    hasattr(snap_obj.data, "polygons") and len(snap_obj.data.polygons) == 0
                ):
                    wireframe_objs.append(snap_obj)
                else:
                    solid_objs.append(snap_obj)

            # Rough distance - object origin to ray origin
            solid_objs.sort(key=lambda so: (so.matrix_world.translation - ray_origin).length_squared)

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
                hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj)

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
                if snap_obj.type in {"EMPTY", "CURVE"} or (
                    hasattr(snap_obj.data, "polygons") and len(snap_obj.data.polygons) == 0
                ):
                    hit_obj, hit = cls.process_wireframe_snap_obj(context, event, snap_obj, ray_origin, closest_snaps)
                    face_index = None
                else:
                    # Solid objects
                    hit_obj, hit, face_index = cls.cast_rays_to_single_object(context, event, snap_obj)

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
