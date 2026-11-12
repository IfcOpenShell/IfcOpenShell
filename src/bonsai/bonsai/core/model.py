# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
#
# This file was modified with the assistance of an AI coding tool.

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any, Literal, Optional

if TYPE_CHECKING:
    import bpy
    from mathutils import Vector

    import bonsai.tool as tool
    from bonsai.bim.module.model.wall import DumbWallAligner, DumbWallJoiner

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    OffsetType = Literal["CENTER", "EXTERIOR", "INTERIOR"]


# Arc sample count for fillet preview polylines. 24 samples produces a visually
# smooth arc at common viewport scales without bloating the GPU batch.
FILLET_DEFAULT_ARC_RESOLUTION = 24
# Dot-product floor for treating two wall-axis segments as parallel — below
# this the projected intersection is too sensitive to floating-point noise
# to be useful as a junction apex. Calibrated to ~2° from parallel.
PARALLEL_DOT_THRESHOLD = 0.9994
# Perpendicular distance (SI metres) under which two parallel wall axes are
# considered to share the same infinite line. Calibrated to absorb sub-50mm
# placement drift between authored-joined walls without merging genuinely
# offset parallel walls.
COLLINEAR_LINE_TOLERANCE = 0.05
# Default proximity (SI metres) for classifying a layer offset against the
# canonical EXTERIOR / CENTER / INTERIOR baselines. Tight enough that ordinary
# millimetre-scale modelling intent always falls into the nearest baseline.
BASELINE_OFFSET_TOLERANCE = 0.001


def unjoin_walls(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    geometry: type[tool.Geometry],
    joiner: DumbWallJoiner,
    model: type[tool.Model],
) -> None:
    """Unjoin selected walls."""
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        joiner.unjoin(obj)


def extend_walls(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    geometry: type[tool.Geometry],
    joiner: DumbWallJoiner,
    model: type[tool.Model],
    target: Vector,
    connection: Optional[str] = None,
) -> None:
    """Extend selected walls to the target."""
    for obj in blender.get_selected_objects():
        if not (element := ifc.get_entity(obj)) or model.get_usage_type(element) != "LAYER2":
            continue
        geometry.clear_scale(obj)
        joiner.extend(obj, target, connection)


def join_walls_LV(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    geometry: type[tool.Geometry],
    joiner: DumbWallJoiner,
    model: type[tool.Model],
    join_type: Literal["L", "V"] = "L",
) -> None:
    selected_objs = [
        o for o in blender.get_selected_objects() if (e := ifc.get_entity(o)) and model.get_usage_type(e) == "LAYER2"
    ]
    if len(selected_objs) != 2:
        raise RequireTwoWallsError("Two vertically layered elements must be selected to connect their paths together")

    if active_obj := blender.get_active_object():
        another_selected_object = next(o for o in selected_objs if o != active_obj)
    else:
        active_obj, another_selected_object = selected_objs

    for obj in selected_objs:
        geometry.clear_scale(obj)

    joiner.connect(another_selected_object, active_obj)


def offset_walls(ifc: type[tool.Ifc], blender: type[tool.Blender], model: type[tool.Model], offset_type: OffsetType):
    objs = [
        obj
        for obj in blender.get_selected_objects()
        if (element := ifc.get_entity(obj)) and model.get_usage_type(element) == "LAYER2"
    ]
    for obj in objs:
        model.offset_wall(obj, offset_type)
    model.recalculate_walls(objs)


def align_walls(
    ifc: type[tool.Ifc],
    blender: type[tool.Blender],
    model: type[tool.Model],
    aligner: DumbWallAligner,
    align_type: AlignType,
):
    reference_obj = blender.get_active_object(is_selected=True)
    if not reference_obj or not (e := ifc.get_entity(reference_obj)) or not model.get_usage_type(e) == "LAYER2":
        reference_obj = None
    objs = [
        o
        for o in blender.get_selected_objects()
        if o != reference_obj and (e := ifc.get_entity(o)) and model.get_usage_type(e) == "LAYER2"
    ]
    if not reference_obj or not objs:
        raise RequireAtLeastTwoLayeredElements(
            "At least two vertically layered elements must be selected to match alignments."
        )
    aligner.set_reference_wall(reference_obj)
    for obj in objs:
        if align_type == "CENTER":
            aligner.align_centerline(obj)
        elif align_type == "EXTERIOR":
            aligner.align_first_layer(obj)
        elif align_type == "INTERIOR":
            aligner.align_last_layer(obj)


def align_objects(
    blender: type[tool.Blender], model: type[tool.Model], align_type: Literal["CENTER", "POSITIVE", "NEGATIVE"]
):
    reference_obj = blender.get_active_object(is_selected=True)
    objs = [o for o in blender.get_selected_objects() if o != reference_obj]
    if not reference_obj or not objs:
        raise RequireAtLeastTwoElements("At least two objects must be selected to match alignments.")
    model.align_objects(reference_obj, objs, align_type)


def regenerate_wall_to_underside(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    model: type[tool.Model],
    wall_objs: list[bpy.types.Object],
) -> None:
    """Re-clip walls to their connected underside objects after the slab has moved.

    When a wall has no remaining slab connections — the case reached after the
    last TOP rel is severed (via disconnect or via cascade-on-slab-delete) — the
    stale trim booleans are cleaned up so the wall reverts to its pre-clip
    extrusion instead of holding orphan ``IfcBooleanResult`` items and a dead
    ``BBIM_Boolean`` pset.
    """
    clipped_objs = []
    reverted_objs = []
    for obj in wall_objs:
        wall = ifc.get_entity(obj)
        slab_objs = model.get_connected_slab_objs(wall)
        if not slab_objs:
            model.remove_wall_to_underside_booleans(wall)
            reverted_objs.append(obj)
            continue
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        # Sync each slab's Blender mesh to its current IFC representation before
        # reading face geometry, so a changed profile is picked up correctly.
        model.reload_body_representation(slab_objs)
        model.remove_wall_to_underside_booleans(wall)
        for slab_obj in slab_objs:
            clip = model.get_slab_clipping_bmesh(slab_obj)
            if clip:
                model.clip_wall_to_slab(wall, clip)
        clipped_objs.append(obj)
    refresh_objs = clipped_objs + reverted_objs
    if refresh_objs:
        model.reload_body_representation(refresh_objs)


def extend_wall_to_slab(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    model: type[tool.Model],
    slab_objs: list[bpy.types.Object],
    wall_objs: list[bpy.types.Object],
) -> None:
    # If any wall is currently in item mode, exit it before modifying the
    # representation. Leaving stale item objects around causes delete_ifc_item
    # to later remove the extrusion (or other pre-boolean items) from inside
    # the boolean chain, corrupting the IFC model.
    geom_props = geometry.get_geometry_props()
    if geom_props.representation_obj in wall_objs:
        geometry.disable_item_mode()
    clipped_walls = []
    for obj in wall_objs:
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        wall = ifc.get_entity(obj)
        # Merge previously connected slabs with newly requested ones so that
        # re-running the operator never produces duplicate booleans and never
        # silently discards clips that were applied in an earlier call.
        existing = model.get_connected_slab_objs(wall)
        seen = {id(s) for s in existing}
        all_slab_objs = list(existing) + [s for s in slab_objs if id(s) not in seen]
        # Remove stale booleans once, then re-clip against the full set.
        model.remove_wall_to_underside_booleans(wall)
        did_clip = False
        for slab_obj in all_slab_objs:
            clip = model.get_slab_clipping_bmesh(slab_obj)
            if not clip:
                continue
            model.clip_wall_to_slab(wall, clip)
            model.connect_wall_to_slab(wall, ifc.get_entity(slab_obj))
            did_clip = True
        if did_clip:
            clipped_walls.append(obj)
    if clipped_walls:
        model.reload_body_representation(clipped_walls)


class RequireTwoWallsError(Exception):
    pass


class RequireAtLeastTwoLayeredElements(Exception):
    pass


class RequireAtLeastTwoElements(Exception):
    pass


class RequireLayeredElement(Exception):
    pass


# --- Wall geometry math (pure) ------------------------------------------------
# Tuple in / tuple out so these helpers run without ``bpy`` or ``mathutils``.
# Callers convert ``mathutils.Vector`` at the boundary.


def baseline_from_offset(offset: float, thickness: float, tolerance: float = BASELINE_OFFSET_TOLERANCE) -> str:
    """Classify a numeric layer offset as EXTERIOR / CENTER / INTERIOR.

    Handles both POSITIVE and NEGATIVE direction_sense walls. Returns the
    closest canonical baseline; falls back to ``"CENTER"`` when nothing is
    within ``tolerance``."""
    candidates = (
        ("EXTERIOR", 0.0),
        ("CENTER", -thickness / 2),
        ("INTERIOR", -thickness),
        ("EXTERIOR", thickness),
        ("CENTER", thickness / 2),
        ("INTERIOR", 0.0),
    )
    best = min(candidates, key=lambda c: abs(offset - c[1]))
    return best[0] if abs(offset - best[1]) < tolerance else "CENTER"


def project_axis_intersection(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    parallel_threshold: float,
) -> Optional[tuple[float, float, float]]:
    """Compute the 2D (X,Y plane) intersection of two world-space axis segments.

    Each segment is a pair of 3-tuples. Returns the intersection as a 3-tuple
    (Z is the average of the four input Zs, for visual placement) or ``None`` if
    the segments are parallel within ``parallel_threshold`` (a dot-product magnitude
    threshold — see ``PARALLEL_DOT_THRESHOLD`` for the calibrated value)."""
    p1, p2 = seg_a
    p3, p4 = seg_b
    d1x, d1y = p2[0] - p1[0], p2[1] - p1[1]
    d2x, d2y = p4[0] - p3[0], p4[1] - p3[1]
    d1_len = (d1x * d1x + d1y * d1y) ** 0.5
    d2_len = (d2x * d2x + d2y * d2y) ** 0.5
    if d1_len < 1e-9 or d2_len < 1e-9:
        return None
    dot = (d1x * d2x + d1y * d2y) / (d1_len * d2_len)
    if abs(dot) >= parallel_threshold:
        return None
    denom = d1x * d2y - d1y * d2x
    if abs(denom) < 1e-9:
        return None
    t = ((p3[0] - p1[0]) * d2y - (p3[1] - p1[1]) * d2x) / denom
    ix = p1[0] + t * d1x
    iy = p1[1] + t * d1y
    iz = (p1[2] + p2[2] + p3[2] + p4[2]) / 4
    return (ix, iy, iz)


def opening_is_past_cut(min_t: float, cut_percentage: float) -> bool:
    """True when the opening's near edge sits past the cut on the t axis.

    Strict inequality is load-bearing: a boundary touch or NaN keeps the
    opening on both walls — the safe default when extent resolution fails."""
    return min_t > cut_percentage


def opening_is_before_cut(max_t: float, cut_percentage: float) -> bool:
    """True when the opening's far edge sits before the cut on the t axis."""
    return max_t < cut_percentage


def opening_straddles_cut(min_t: float, max_t: float, cut_percentage: float) -> bool:
    """True when the opening's extent crosses the cut on the t axis."""
    return min_t < cut_percentage < max_t


WallJoinState = Literal["joined", "collinear", "intersect", "none"]


def classify_wall_join_state(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    are_joined: bool,
    parallel_threshold: float,
    collinear_tolerance: float,
) -> tuple[WallJoinState, Optional[tuple[float, float, float]]]:
    """Classify a wall pair's geometric state — ``(state, intersection)``.

    Priority: ``"joined"`` (caller-supplied flag) → ``"collinear"`` →
    ``"intersect"`` (projected point returned) → ``"none"`` (parallel,
    non-collinear)."""
    if are_joined:
        return "joined", None
    if are_axes_collinear(seg_a, seg_b, parallel_threshold, collinear_tolerance):
        return "collinear", None
    intersection = project_axis_intersection(seg_a, seg_b, parallel_threshold)
    if intersection is None:
        return "none", None
    return "intersect", intersection


def wall_join_preview_lines(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    intersection: tuple[float, float, float],
) -> list[tuple[tuple[float, float, float], tuple[float, float, float]]]:
    """Two segments showing each wall axis extending to ``intersection``.

    Each segment runs from the input axis's nearest endpoint to the
    intersection, held at that wall's own Z. Returned in input order
    ``[floor_a, floor_b]``."""
    ix, iy, _ = intersection

    def _nearest(seg: tuple[tuple[float, float, float], tuple[float, float, float]]) -> tuple[float, float, float]:
        return min(seg, key=lambda p: (p[0] - ix) ** 2 + (p[1] - iy) ** 2)

    near_a = _nearest(seg_a)
    near_b = _nearest(seg_b)
    return [
        (near_a, (ix, iy, near_a[2])),
        (near_b, (ix, iy, near_b[2])),
    ]


def resolve_extend_walls_target(
    target_obj: Any,
    objs: list[Any],
    reverse: bool,
) -> tuple[Any, list[Any]]:
    """Pick which object is the extend-target and which are extended.

    Default direction: ``objs`` are extended to meet ``target_obj``.
    Reversed direction (``reverse=True``) swaps the pair — equivalent to
    having passed them in the opposite order. The swap is well-defined only
    for the 1+1 case (one target + one other); for ``n>1`` it would be
    ambiguous, so the default direction is preserved instead."""
    if reverse and target_obj is not None and len(objs) == 1:
        return objs[0], [target_obj]
    return target_obj, objs


def displacement_from_x_angle(height: float, x_angle: float) -> float:
    """Top-edge horizontal displacement for a wall of given vertical ``height``
    and slope ``x_angle`` (radians). Inverse of ``x_angle_from_displacement``."""
    return height * math.tan(x_angle)


def x_angle_from_displacement(height: float, displacement: float) -> float:
    """Recover slope ``x_angle`` (radians) from a top-edge horizontal displacement.

    ``height`` is clamped to ``max(height, 1e-6)`` so zero-height walls map
    cleanly to ``±π/2`` instead of dividing by zero."""
    return math.atan2(displacement, max(height, 1e-6))


def vertical_height_from_extrusion_depth(extrusion_depth: float, x_angle: float) -> float:
    """Vertical height of a wall given its slanted extrusion depth and slope.

    ``IfcExtrudedAreaSolid.Depth`` measures along the (possibly slanted) extrusion
    direction. The vertical height the user thinks of is ``depth * cos(x_angle)``.
    Unit-agnostic: the result is in the same units as ``extrusion_depth``."""
    return extrusion_depth * abs(math.cos(x_angle))


def extrusion_depth_from_vertical_height(vertical_height: float, x_angle: float) -> float:
    """``vertical_height / cos(x_angle)`` with ``cos`` clamped at ``1e-6`` to
    stay finite near ``±π/2``."""
    return vertical_height / max(abs(math.cos(x_angle)), 1e-6)


def length_and_height_from_extrusion(
    extrusion_depth: float,
    x_angle: float,
    reference_line_x_extent: float,
    unit_scale: float,
) -> tuple[float, float]:
    """SI ``(length, vertical_height)`` of a LAYER2 wall.

    Height is the *vertical* projection of the slanted depth, not the
    slanted depth itself."""
    length = reference_line_x_extent * unit_scale
    height = vertical_height_from_extrusion_depth(extrusion_depth * unit_scale, x_angle)
    return length, height


def are_axes_collinear(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    parallel_threshold: float = PARALLEL_DOT_THRESHOLD,
    line_tolerance: float = COLLINEAR_LINE_TOLERANCE,
) -> bool:
    """True if both axis segments lie on the same infinite line in plan.

    Two conditions: directions must be (anti-)parallel within ``parallel_threshold``,
    AND any endpoint of B must lie on A's infinite line within ``line_tolerance``.
    Plan-only (Z ignored)."""
    d1x, d1y = seg_a[1][0] - seg_a[0][0], seg_a[1][1] - seg_a[0][1]
    d2x, d2y = seg_b[1][0] - seg_b[0][0], seg_b[1][1] - seg_b[0][1]
    d1_len = (d1x * d1x + d1y * d1y) ** 0.5
    d2_len = (d2x * d2x + d2y * d2y) ** 0.5
    if d1_len < 1e-9 or d2_len < 1e-9:
        return False
    if abs((d1x * d2x + d1y * d2y) / (d1_len * d2_len)) < parallel_threshold:
        return False
    # Project seg_b[0] onto the infinite line through seg_a; the perpendicular
    # distance to the original point tells us how far off the line B sits.
    nx, ny = d1x / d1_len, d1y / d1_len
    dx, dy = seg_b[0][0] - seg_a[0][0], seg_b[0][1] - seg_a[0][1]
    t = dx * nx + dy * ny
    proj_x = seg_a[0][0] + nx * t
    proj_y = seg_a[0][1] + ny * t
    perp_x = seg_b[0][0] - proj_x
    perp_y = seg_b[0][1] - proj_y
    return (perp_x * perp_x + perp_y * perp_y) ** 0.5 < line_tolerance


def closest_endpoint_midpoint(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
) -> tuple[float, float, float]:
    """Midpoint of the closest endpoint pair between two segments."""
    endpoints_a = (seg_a[0], seg_a[1])
    endpoints_b = (seg_b[0], seg_b[1])

    def _distance_sq(p: tuple[float, float, float], q: tuple[float, float, float]) -> float:
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2

    closest_pair = min(((a, b) for a in endpoints_a for b in endpoints_b), key=lambda pair: _distance_sq(*pair))
    a, b = closest_pair
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)


def compute_path_connection_location(
    seg_self: tuple[tuple[float, float, float], tuple[float, float, float]],
    self_conn_type: str,
    seg_other: tuple[tuple[float, float, float], tuple[float, float, float]],
    other_conn_type: str,
    parallel_threshold: float = PARALLEL_DOT_THRESHOLD,
) -> tuple[float, float, float]:
    """World-space location of a single ``IfcRelConnectsPathElements`` between
    two wall axes.

    Priority: ``self``'s ATSTART/ATEND endpoint → ``other``'s ATSTART/ATEND
    endpoint → axis intersection → closest-endpoint midpoint fallback."""
    if self_conn_type == "ATSTART":
        return seg_self[0]
    if self_conn_type == "ATEND":
        return seg_self[1]
    if other_conn_type == "ATSTART":
        return seg_other[0]
    if other_conn_type == "ATEND":
        return seg_other[1]
    intersection = project_axis_intersection(seg_self, seg_other, parallel_threshold)
    if intersection is not None:
        return intersection
    return closest_endpoint_midpoint(seg_self, seg_other)


def _vec_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vec_cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _vec_length(v: tuple[float, float, float]) -> float:
    return (v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) ** 0.5


def _rotate_around_axis(
    v: tuple[float, float, float],
    axis: tuple[float, float, float],
    angle: float,
) -> tuple[float, float, float]:
    """Rotate ``v`` around unit-length ``axis`` by ``angle`` radians."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dot = _vec_dot(axis, v)
    cross = _vec_cross(axis, v)
    k = 1.0 - cos_a
    return (
        v[0] * cos_a + cross[0] * sin_a + axis[0] * dot * k,
        v[1] * cos_a + cross[1] * sin_a + axis[1] * dot * k,
        v[2] * cos_a + cross[2] * sin_a + axis[2] * dot * k,
    )


def compute_fillet_polylines(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    radius: float,
    arc_resolution: int = FILLET_DEFAULT_ARC_RESOLUTION,
    parallel_threshold: float = PARALLEL_DOT_THRESHOLD,
) -> dict:
    """Preview polylines for a circular fillet at the junction of two axes.

    Returns a dict with ``valid``, ``reason``, ``intersection``, ``tangent_a``
    / ``tangent_b``, ``arc`` (``arc_resolution + 1`` samples), ``arc_center``,
    ``arc_radius``, ``sweep_angle``, ``sweep_axis``, ``tangent_offset``,
    ``wall_a_join_side`` / ``wall_b_join_side`` (ATSTART/ATEND/None),
    ``invalid_radius`` (tangent overshoots — arc + tangents still populated
    for warning rendering), and ``invalid_axes`` (set on parallel)."""
    blank: dict = {
        "valid": False,
        "reason": None,
        "intersection": None,
        "tangent_a": None,
        "tangent_b": None,
        "arc": [],
        "arc_center": None,
        "arc_radius": radius,
        "sweep_angle": 0.0,
        "sweep_axis": None,
        "tangent_offset": 0.0,
        "wall_a_join_side": None,
        "wall_b_join_side": None,
        "invalid_radius": False,
        "invalid_axes": None,
    }

    intersection = project_axis_intersection(seg_a, seg_b, parallel_threshold)
    if intersection is None:
        return {**blank, "reason": "parallel", "invalid_axes": [seg_a, seg_b]}

    def _classify(seg, ipt):
        d0 = (seg[0][0] - ipt[0]) ** 2 + (seg[0][1] - ipt[1]) ** 2 + (seg[0][2] - ipt[2]) ** 2
        d1 = (seg[1][0] - ipt[0]) ** 2 + (seg[1][1] - ipt[1]) ** 2 + (seg[1][2] - ipt[2]) ** 2
        if d0 <= d1:
            return seg[0], seg[1], "ATSTART"
        return seg[1], seg[0], "ATEND"

    near_a, far_a, side_a = _classify(seg_a, intersection)
    near_b, far_b, side_b = _classify(seg_b, intersection)

    # Direction along each segment AWAY from the corner. ``far - intersection``
    # handles both the shared-corner and extended-axes cases uniformly.
    dir_a_raw = _vec_sub(far_a, intersection)
    dir_b_raw = _vec_sub(far_b, intersection)
    far_len_a = _vec_length(dir_a_raw)
    far_len_b = _vec_length(dir_b_raw)
    if far_len_a < 1e-9 or far_len_b < 1e-9:
        return {**blank, "reason": "near_collinear", "intersection": intersection}
    dir_a = (dir_a_raw[0] / far_len_a, dir_a_raw[1] / far_len_a, dir_a_raw[2] / far_len_a)
    dir_b = (dir_b_raw[0] / far_len_b, dir_b_raw[1] / far_len_b, dir_b_raw[2] / far_len_b)

    cos_angle = max(-1.0, min(1.0, _vec_dot(dir_a, dir_b)))
    angle = math.acos(cos_angle)
    sweep_angle = math.pi - angle
    if sweep_angle < 1e-3 or sweep_angle > math.pi - 1e-3:
        return {
            **blank,
            "reason": "near_collinear",
            "intersection": intersection,
            "sweep_angle": sweep_angle,
            "wall_a_join_side": side_a,
            "wall_b_join_side": side_b,
        }

    tangent_offset = radius * math.tan(sweep_angle / 2)
    tangent_a = (
        intersection[0] + dir_a[0] * tangent_offset,
        intersection[1] + dir_a[1] * tangent_offset,
        intersection[2] + dir_a[2] * tangent_offset,
    )
    tangent_b = (
        intersection[0] + dir_b[0] * tangent_offset,
        intersection[1] + dir_b[1] * tangent_offset,
        intersection[2] + dir_b[2] * tangent_offset,
    )

    plane_normal_raw = _vec_cross(dir_a, dir_b)
    pn_len = _vec_length(plane_normal_raw)
    if pn_len < 1e-9:
        return {**blank, "reason": "near_collinear", "intersection": intersection}
    plane_normal = (
        plane_normal_raw[0] / pn_len,
        plane_normal_raw[1] / pn_len,
        plane_normal_raw[2] / pn_len,
    )

    perp_a = _vec_cross(plane_normal, dir_a)
    if _vec_dot(perp_a, dir_b) < 0:
        perp_a = (-perp_a[0], -perp_a[1], -perp_a[2])

    arc_center = (
        tangent_a[0] + perp_a[0] * radius,
        tangent_a[1] + perp_a[1] * radius,
        tangent_a[2] + perp_a[2] * radius,
    )

    v_a = _vec_sub(tangent_a, arc_center)
    v_b = _vec_sub(tangent_b, arc_center)
    sweep_axis = plane_normal
    if _vec_dot(_vec_cross(v_a, v_b), plane_normal) < 0:
        sweep_axis = (-plane_normal[0], -plane_normal[1], -plane_normal[2])

    arc_points: list[tuple[float, float, float]] = []
    for i in range(arc_resolution + 1):
        t = i / arc_resolution
        rotated = _rotate_around_axis(v_a, sweep_axis, sweep_angle * t)
        arc_points.append(
            (
                arc_center[0] + rotated[0],
                arc_center[1] + rotated[1],
                arc_center[2] + rotated[2],
            )
        )

    # Overshoot check only for convex fillets (positive ``tangent_offset``);
    # the inverted-fillet case puts tangents past the intersection.
    invalid_radius = tangent_offset > 0 and (tangent_offset > far_len_a or tangent_offset > far_len_b)

    return {
        "valid": not invalid_radius,
        "reason": "invalid_radius" if invalid_radius else None,
        "intersection": intersection,
        "tangent_a": tangent_a,
        "tangent_b": tangent_b,
        "arc": arc_points,
        "arc_center": arc_center,
        "arc_radius": radius,
        "sweep_angle": sweep_angle,
        "sweep_axis": sweep_axis,
        "tangent_offset": tangent_offset,
        "wall_a_join_side": side_a,
        "wall_b_join_side": side_b,
        "leg_a_available": far_len_a,
        "leg_b_available": far_len_b,
        "invalid_radius": invalid_radius,
        "invalid_axes": None,
    }
