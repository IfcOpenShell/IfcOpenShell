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
from typing import TYPE_CHECKING, Literal, Optional

if TYPE_CHECKING:
    import bpy
    from mathutils import Vector

    import bonsai.tool as tool
    from bonsai.bim.module.model.wall import DumbWallAligner, DumbWallJoiner

    AlignType = Literal["CENTER", "EXTERIOR", "INTERIOR"]
    OffsetType = Literal["CENTER", "EXTERIOR", "INTERIOR"]


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


def extend_wall_to_slab(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    model: type[tool.Model],
    slab_obj: bpy.types.Object,
    wall_objs: list[bpy.types.Object],
) -> None:
    if not (clip := model.get_slab_clipping_bmesh(slab_obj)):
        return  # Nothing to clip?
    slab = ifc.get_entity(slab_obj)
    for obj in wall_objs:
        if ifc.is_moved(obj):
            geometry.run_edit_object_placement(obj=obj)
        wall = ifc.get_entity(obj)
        model.clip_wall_to_slab(wall, clip)
        model.connect_wall_to_slab(wall, slab)
    model.reload_body_representation(wall_objs)


class RequireTwoWallsError(Exception):
    pass


class RequireAtLeastTwoLayeredElements(Exception):
    pass


class RequireAtLeastTwoElements(Exception):
    pass


class RequireLayeredElement(Exception):
    pass


# --- Wall geometry math (pure) ------------------------------------------------
# Tuple in / tuple out so these helpers run under ``pytest test/core/`` without
# ``bpy`` or ``mathutils``. Callers convert ``mathutils.Vector`` at the boundary.


def baseline_from_offset(offset: float, thickness: float, tolerance: float = 0.001) -> str:
    """Classify a numeric layer offset as EXTERIOR / CENTER / INTERIOR.

    Mirrors the math in ``tool.Model.offset_wall`` for both POSITIVE and NEGATIVE
    direction_sense walls. Returns the closest canonical baseline; falls back to
    ``"CENTER"`` when nothing is within ``tolerance``."""
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
    threshold — e.g. ``cos(2°) ≈ 0.9994`` treats walls within 2° of parallel as parallel)."""
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


def displacement_from_x_angle(height: float, x_angle: float) -> float:
    """Top-edge horizontal displacement for a wall of given vertical ``height`` and
    slope ``x_angle`` (radians). Drives the slope dimension gizmo's display value.

    Inverse of :func:`x_angle_from_displacement`."""
    return height * math.tan(x_angle)


def x_angle_from_displacement(height: float, displacement: float) -> float:
    """Recover slope ``x_angle`` (radians) from a top-edge horizontal displacement.

    ``height`` is clamped to ``max(height, 1e-6)`` so vertical walls of effectively
    zero height map cleanly to ``±π/2`` via ``atan2`` rather than dividing by zero.

    Inverse of :func:`displacement_from_x_angle`."""
    return math.atan2(displacement, max(height, 1e-6))


def vertical_height_from_extrusion_depth(extrusion_depth: float, x_angle: float) -> float:
    """Vertical height of a wall given its slanted extrusion depth and slope.

    ``IfcExtrudedAreaSolid.Depth`` measures along the (possibly slanted) extrusion
    direction. The vertical height the user thinks of is ``depth * cos(x_angle)``.
    Unit-agnostic: the result is in the same units as ``extrusion_depth``."""
    return extrusion_depth * abs(math.cos(x_angle))


def are_axes_collinear(
    seg_a: tuple[tuple[float, float, float], tuple[float, float, float]],
    seg_b: tuple[tuple[float, float, float], tuple[float, float, float]],
    parallel_threshold: float = 0.9994,
    line_tolerance: float = 0.05,
) -> bool:
    """True if both axis segments lie on the same infinite line in plan.

    Two conditions: directions must be (anti-)parallel within ``parallel_threshold``
    (``cos(2°) ≈ 0.9994``), AND any endpoint of B must lie on A's infinite line
    within ``line_tolerance``. Plan-only (Z ignored) — two parallel walls at
    different elevations are still considered collinear because the merge operator
    handles Z resolution itself.

    Used by the wall-join gizmo's state machine: collinear pair → Merge icon at the
    boundary, perpendicular pair → Join icon at the intersection."""
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
    """Midpoint of the closest pair of endpoints between two segments.

    For walls that meet end-to-end this is the shared corner; for walls with a
    small gap it's the midpoint of the gap. Either way it's the user-meaningful
    "boundary" where a merge would graft the two segments together."""
    endpoints_a = (seg_a[0], seg_a[1])
    endpoints_b = (seg_b[0], seg_b[1])

    def _distance_sq(p: tuple[float, float, float], q: tuple[float, float, float]) -> float:
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 + (p[2] - q[2]) ** 2

    closest_pair = min(((a, b) for a in endpoints_a for b in endpoints_b), key=lambda pair: _distance_sq(*pair))
    a, b = closest_pair
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
