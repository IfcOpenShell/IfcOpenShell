# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
# This file was generated with the assistance of an AI coding tool.

"""Generic face-quad resize gizmos for any axis-aligned local box.

This module contains the box-agnostic core of the interactive
face-resize gizmos: two Gizmo classes (a near-invisible click target
welded to each face, and a thin colored edge outline), a per-redraw
orchestrator that places six of each on a box, and the pure one-sided
resize arithmetic. None of it knows about IFC, clip boxes, or
``BIMSceneClipBoxProperties`` — a future camera-view-box adapter can
reuse the same classes and helpers.

Consumer contract — the adapter group must:

1. Create six ``BIM_GT_box_face_quad`` and six ``BIM_GT_box_face_outline``
   instances at ``setup()`` time, in :data:`FACE_ROUTES` order, and bind
   each quad's ``move_get_cb`` / ``move_set_cb`` to closures that read
   and mutate the box's host (e.g. an Empty's ``location`` / ``scale``).
2. Call :func:`apply_face_quad_layout` from ``refresh()`` /
   ``draw_prepare()`` with the box's local-frame ``bmin`` / ``bmax``,
   the host's ``matrix_world``, the OBB rotation as a 4x4
   (``Matrix.Identity(4)`` when the rotation rides in ``matrix_world``),
   and the current ``region`` / ``rv3d``.
3. Implement ``_lock_for(active_gz)`` / ``_unlock_all()`` on the group
   for drag mutual exclusion; the quad's ``invoke`` / ``exit`` call them.

The resize arithmetic in :func:`compute_face_resize` is pure: feed it
the modal scalar plus drag-start snapshots and it returns the host's
new scale-on-axis and new origin location.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import bpy
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from mathutils import Matrix, Vector

# ---------------------------------------------------------------------------
# Public iteration order
# ---------------------------------------------------------------------------

# (axis, is_max) pairs. The adapter group's ``setup()`` MUST create its
# six face-quad gizmos in this order so positional indexing into the
# layout helper stays correct.
FACE_ROUTES: tuple[tuple[int, bool], ...] = (
    (0, False),
    (0, True),
    (1, False),
    (1, True),
    (2, False),
    (2, True),
)


# ---------------------------------------------------------------------------
# Public visual constants (adapter reads these in setup())
# ---------------------------------------------------------------------------

# Standard XYZ axis colors (Blender convention).
AXIS_COLOR: dict[int, tuple[float, float, float]] = {
    0: (1.0, 0.2, 0.2),
    1: (0.2, 1.0, 0.2),
    2: (0.2, 0.4, 1.0),
}

# Documented "selectable but unpainted" trick: the GPU still writes the
# selection buffer at this alpha so clicks register, but no visible
# pixels are produced.
FACE_QUAD_ALPHA: float = 0.001

# Very faint hover tint — just enough to confirm "you're aiming at this
# face" without painting visibly over geometry behind it.
FACE_QUAD_ALPHA_HIGHLIGHT: float = 0.04

# Setup-time default for ``select_bias``; the layout helper overwrites
# it per frame to the front-facing or halo value below. Kept below the
# canonical arrow bias so a bailed frame can't let a front quad steal
# clicks meant for a hidden control.
FACE_QUAD_SELECT_BIAS: float = 0.5


# ---------------------------------------------------------------------------
# Internal constants
# ---------------------------------------------------------------------------

# Unit quad in the local XY plane spanning [-0.5, 0.5]^2 at z=0. Two
# CCW triangles viewed from +Z. matrix_basis stretches it onto the
# face's perpendicular extents.
_QUAD_TRIS: list[tuple[float, float, float]] = [
    (-0.5, -0.5, 0.0),
    (0.5, -0.5, 0.0),
    (0.5, 0.5, 0.0),
    (-0.5, -0.5, 0.0),
    (0.5, 0.5, 0.0),
    (-0.5, 0.5, 0.0),
]

# Unit-quad outline as 4 line segments in the local XY plane at z=0.
_QUAD_OUTLINE_LINES: list[tuple[float, float, float]] = [
    (-0.5, -0.5, 0.0),
    (0.5, -0.5, 0.0),
    (0.5, -0.5, 0.0),
    (0.5, 0.5, 0.0),
    (0.5, 0.5, 0.0),
    (-0.5, 0.5, 0.0),
    (-0.5, 0.5, 0.0),
    (-0.5, -0.5, 0.0),
]

# Degenerate zero-area triangle for hidden back-facing quads with no
# visible-adjacent neighbours (rare orientation). Blender tolerates
# this; the gizmo is hidden anyway so nothing renders.
_EMPTY_TRIS: list[tuple[float, float, float]] = [
    (0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0),
    (0.0, 0.0, 0.0),
]

# Rotates the gizmo's local +Z onto the outward face normal in the
# box's local frame. Right-hand rotation around the named axis.
_AXIS_ORIENT: dict[tuple[int, bool], Matrix] = {
    (0, False): Matrix.Rotation(-math.pi / 2, 4, "Y"),
    (0, True): Matrix.Rotation(math.pi / 2, 4, "Y"),
    (1, False): Matrix.Rotation(math.pi / 2, 4, "X"),
    (1, True): Matrix.Rotation(-math.pi / 2, 4, "X"),
    (2, False): Matrix.Rotation(math.pi, 4, "X"),
    (2, True): Matrix.Identity(4),
}

# Per-face mapping from face-quad local axes to local box axes for the
# perpendicular-extent scale. ``(w_axis, h_axis)`` — the box-local axis
# indices the quad's local X and Y span after the orientation rotation.
_QUAD_PERP_AXES: dict[tuple[int, bool], tuple[int, int]] = {
    (0, False): (2, 1),
    (0, True): (2, 1),
    (1, False): (0, 2),
    (1, True): (0, 2),
    (2, False): (0, 1),
    (2, True): (0, 1),
}

# Front-facing quad sits ABOVE the halo strips so the cursor on the
# visible face area always grabs the visible face, never accidentally
# routes to a back-face halo strip in an adjacent screen region.
_FACE_QUAD_FRONT_FACING_SELECT_BIAS: float = 1.5
_FACE_QUAD_HALO_FRAME_SELECT_BIAS: float = 1.0

# Target halo-strip thickness in screen pixels. The world-space margin
# is recomputed per frame so the rim stays a roughly constant on-screen
# size regardless of viewport zoom.
_FACE_QUAD_HALO_TARGET_PIXELS: float = 20.0

# Minimum world half-extent a face resize may shrink to. Stops a drag
# from collapsing the host to zero or negative scale.
_MIN_HALF_EXTENT: float = 1e-4


# ---------------------------------------------------------------------------
# Pure predicates (testable without Blender)
# ---------------------------------------------------------------------------

Vec3 = tuple[float, float, float]


def face_outward_axis_local(axis: int, is_max: bool) -> Vec3:
    """Un-rotated outward face normal in the box's local AABB coords.

    For ``(axis=0, is_max=True)`` returns ``(+1, 0, 0)``; for the −X
    face ``(-1, 0, 0)``; etc. The rotated world normal is obtained by
    applying the host's rotation and the OBB rotation:
    ``mw_rot @ cage_rotation @ this``.
    """
    sign = 1.0 if is_max else -1.0
    out = [0.0, 0.0, 0.0]
    out[axis] = sign
    return (out[0], out[1], out[2])


def front_facing_face_mask(
    face_normals_world: Sequence[Vec3],
    view_dir_world: Vec3,
    eps: float = 1e-6,
) -> tuple[bool, ...]:
    """Which of the 6 box faces point toward the camera.

    A face is front-facing iff its outward normal points AGAINST the
    view direction (``dot(normal, view_dir) < -eps``). The ``-eps``
    margin prevents flicker at grazing angles.

    ``face_normals_world`` must be in :data:`FACE_ROUTES` order; returns
    a 6-tuple of bool parallel to that order.
    """
    if len(face_normals_world) != 6:
        msg = f"expected 6 face normals, got {len(face_normals_world)}"
        raise ValueError(msg)
    vx, vy, vz = view_dir_world
    return tuple((n[0] * vx + n[1] * vy + n[2] * vz) < -eps for n in face_normals_world)


def view_axis_parallel_face_mask(
    face_normals_world: Sequence[Vec3],
    view_dir_world: Vec3,
    threshold: float = 0.95,
) -> tuple[bool, ...]:
    """Which faces have normals (anti-)parallel to the view direction.

    True iff ``abs(dot(normal, view_dir)) >= threshold`` — i.e. the
    face is nearly perpendicular to the screen plane. Provided as a
    pure predicate for callers that want to detect degenerate-drag
    conditions; the layout helper itself no longer gates on it.
    """
    if len(face_normals_world) != 6:
        msg = f"expected 6 face normals, got {len(face_normals_world)}"
        raise ValueError(msg)
    vx, vy, vz = view_dir_world
    return tuple(abs(n[0] * vx + n[1] * vy + n[2] * vz) >= threshold for n in face_normals_world)


# ---------------------------------------------------------------------------
# Pure resize arithmetic
# ---------------------------------------------------------------------------


def compute_face_resize(
    *,
    value: float,
    init_world_half: float,
    init_location: tuple[float, float, float],
    world_axis: tuple[float, float, float],
    display_size: float,
) -> tuple[float, tuple[float, float, float]]:
    """Pure one-sided face-resize arithmetic.

    Returns ``(new_scale_axis, new_location)`` — the host's new scale
    on the dragged axis and its new world origin — such that the
    dragged face moves by the modal's outward delta while the OPPOSITE
    face stays put.

    ``value`` is ``init + delta``, where ``init`` is the unsigned
    drag-start world half-extent and ``delta`` is the cursor projection
    onto the face's OUTWARD world normal. Realized half-extent is
    clamped to a small floor; the location shift uses the realized
    (post-clamp) delta so the opposite face stays fixed even at the
    clamp.
    """
    face_delta = value - init_world_half
    new_world_half = init_world_half + 0.5 * face_delta
    if new_world_half < _MIN_HALF_EXTENT:
        new_world_half = _MIN_HALF_EXTENT
    realized_delta = 2.0 * (new_world_half - init_world_half)

    ds = display_size if display_size != 0.0 else 1.0
    new_scale_axis = new_world_half / ds
    shift = 0.5 * realized_delta
    new_location = (
        init_location[0] + shift * world_axis[0],
        init_location[1] + shift * world_axis[1],
        init_location[2] + shift * world_axis[2],
    )
    return new_scale_axis, new_location


# ---------------------------------------------------------------------------
# Internal geometry helpers
# ---------------------------------------------------------------------------


def _compute_face_quad_scale(bmin: Any, bmax: Any, axis: int, is_max: bool) -> tuple[float, float]:
    """Return ``(w, h)`` for the face quad's scale matrix."""
    w_axis, h_axis = _QUAD_PERP_AXES[(axis, is_max)]
    w = float(bmax[w_axis] - bmin[w_axis])
    h = float(bmax[h_axis] - bmin[h_axis])
    return w, h


def _shared_edge_corner_keys(
    axis_a: int, is_max_a: bool, axis_b: int, is_max_b: bool
) -> tuple[tuple[int, int, int], tuple[int, int, int]] | None:
    """Return the 2 corner-bit triples shared by two adjacent faces.

    Corner keys are 3-tuples of bits (0 = bmin, 1 = bmax). The two
    returned corners are ordered with the free-axis bit ascending.
    """
    if axis_a == axis_b:
        return None
    free_axis = 3 - axis_a - axis_b
    bit_a = 1 if is_max_a else 0
    bit_b = 1 if is_max_b else 0
    corner_lo = [0, 0, 0]
    corner_hi = [0, 0, 0]
    corner_lo[axis_a] = bit_a
    corner_hi[axis_a] = bit_a
    corner_lo[axis_b] = bit_b
    corner_hi[axis_b] = bit_b
    corner_lo[free_axis] = 0
    corner_hi[free_axis] = 1
    return (
        (corner_lo[0], corner_lo[1], corner_lo[2]),
        (corner_hi[0], corner_hi[1], corner_hi[2]),
    )


def _face_corner_keys(axis: int, is_max: bool) -> tuple[
    tuple[int, int, int],
    tuple[int, int, int],
    tuple[int, int, int],
    tuple[int, int, int],
]:
    """Return the 4 corner-bit triples of a face in CCW order.

    Triangulation as ``[(0,1,2), (0,2,3)]`` covers the whole face with
    two non-overlapping triangles.
    """
    fixed_bit = 1 if is_max else 0
    free_axes = [a for a in (0, 1, 2) if a != axis]
    fa0, fa1 = free_axes
    corners = []
    for ka, kb in ((0, 0), (1, 0), (1, 1), (0, 1)):
        key = [0, 0, 0]
        key[axis] = fixed_bit
        key[fa0] = ka
        key[fa1] = kb
        corners.append((key[0], key[1], key[2]))
    return (corners[0], corners[1], corners[2], corners[3])


def _build_strip_tris_relative(
    edge_p0_local: tuple[float, float, float],
    edge_p1_local: tuple[float, float, float],
    extrusion_local: tuple[float, float, float],
) -> list[tuple[float, float, float]]:
    """Build two CCW triangles (6 vertices) for a thin halo strip.

    All inputs are in coords relative to the gizmo's ``matrix_basis``
    anchor. The strip runs along ``[edge_p0_local, edge_p1_local]`` and
    extrudes by ``extrusion_local`` perpendicular to the edge.
    """
    p0x, p0y, p0z = edge_p0_local
    p1x, p1y, p1z = edge_p1_local
    ex, ey, ez = extrusion_local
    p0e = (p0x + ex, p0y + ey, p0z + ez)
    p1e = (p1x + ex, p1y + ey, p1z + ez)
    return [
        (p0x, p0y, p0z),
        p0e,
        p1e,
        (p0x, p0y, p0z),
        p1e,
        (p1x, p1y, p1z),
    ]


def _strips_geometry_changed(quad_gz, face_quad_local, all_tris) -> bool:
    """True if the back-face quad's geometry differs from the cached upload.

    Pure orbit/pan doesn't change either the box pose or the cage
    rotation, so the computed strip vertices are byte-identical to the
    previous frame's. Hitting the cache lets the back-facing branch
    skip ``new_custom_shape`` and the GPU upload.
    """
    cached = getattr(quad_gz, "_strips_cache_key", None)
    last_state = getattr(quad_gz, "_last_geometry_state", None)
    key = (face_quad_local, all_tris)
    if cached is None or last_state != "strips" or cached != key:
        quad_gz._strips_cache_key = key
        quad_gz._last_geometry_state = "strips"
        return True
    return False


def _compute_face_basis(
    mw: Any,
    mw_rot: Any,
    cage_rotation: Any,
    pivot_local: Any,
    face_local: Any,
    orient: Any,
) -> tuple[Any, Any]:
    """World-space (translation, outward-normal-direction) for one face."""
    rotated_face_local = cage_rotation.to_3x3() @ (face_local - pivot_local) + pivot_local
    face_world = mw @ rotated_face_local
    world_axis = (mw_rot @ cage_rotation.to_3x3() @ (orient.to_3x3() @ Vector((0.0, 0.0, 1.0)))).normalized()
    return face_world, world_axis


def _compose_face_matrix_basis(
    face_world: Any,
    mw_rot_scale: Any,
    cage_rotation: Any,
    orient: Any,
    w: float,
    h: float,
) -> Any:
    """Compose the 5-term ``matrix_basis`` for a face-plane gizmo.

    Returns ``Translation @ mw_rot_scale @ cage_rotation @ orient @
    Diagonal((w, h, 1, 1))`` — maps a unit-square local quad onto the
    world-space face rectangle, including the host's scale.
    """
    quad_scale = Matrix.Diagonal((w, h, 1.0, 1.0))
    return Matrix.Translation(face_world) @ mw_rot_scale.to_4x4() @ cage_rotation @ orient @ quad_scale


def _compute_box_corners_world(
    bmin: Any,
    bmax: Any,
    pivot_local: Any,
    cage_rotation_3x3: Any,
    mw: Any,
) -> dict[tuple[int, int, int], Any]:
    """Return the 8 OBB corners in world space, keyed by bit-triple."""
    corners: dict[tuple[int, int, int], Any] = {}
    for ix in (0, 1):
        for iy in (0, 1):
            for iz in (0, 1):
                local = Vector(
                    (
                        float(bmax.x if ix else bmin.x),
                        float(bmax.y if iy else bmin.y),
                        float(bmax.z if iz else bmin.z),
                    )
                )
                rotated = cage_rotation_3x3 @ (local - pivot_local) + pivot_local
                corners[(ix, iy, iz)] = mw @ rotated
    return corners


def _abs_scale_matrix(mw: Any) -> Any:
    """Return a copy of ``mw`` with all scale components ``abs()``-ed.

    Without this, a negative-scale host produces a visible/clickable
    face inversion: ``mw @ local_vec`` flips the +axis face onto the
    -axis world side, while the rotation-only normal stays pointing
    in the +axis direction — so the gizmo for "the +X face" sits at
    world -X but reports its outward normal as +X.
    """
    loc, rot, scale = mw.decompose()
    abs_scale = Vector((abs(scale.x), abs(scale.y), abs(scale.z)))
    return Matrix.LocRotScale(loc, rot, abs_scale)


def _world_radius_to_screen_pixels(
    region: Any,
    rv3d: Any,
    center_world: Vector,
    world_radius: float,
    *,
    min_pixels: float = 0.0,
) -> float:
    """Return the on-screen pixel radius of a world-space circle.

    Projects ``center_world`` and a sample point offset by
    ``world_radius`` along the camera's view-aligned right axis to
    region pixels, and returns the screen-pixel distance between them.
    Falls back to ``min_pixels`` if either projection fails.
    """
    try:
        view_inv = rv3d.view_matrix.inverted()
        right = Vector((view_inv[0][0], view_inv[0][1], view_inv[0][2])).normalized()
    except (AttributeError, ValueError):
        right = Vector((1.0, 0.0, 0.0))
    sample_world = center_world + right * world_radius
    return _world_segment_to_screen_pixels(region, rv3d, center_world, sample_world, min_pixels=min_pixels)


def _world_segment_to_screen_pixels(
    region: Any,
    rv3d: Any,
    p0_world: Vector,
    p1_world: Vector,
    *,
    min_pixels: float = 0.0,
) -> float:
    """Return the on-screen pixel length of an arbitrary world segment.

    Unlike :func:`_world_radius_to_screen_pixels`, this measures the
    ACTUAL projected length of the segment — foreshortening included.
    Use this when the segment direction is known to be oblique to the
    screen plane (e.g. a back face's outward normal): a perpendicular
    radius measurement overestimates the on-screen length, leaving
    halo strips visually narrower than the requested pixel target.
    """
    p0 = location_3d_to_region_2d(region, rv3d, p0_world)
    p1 = location_3d_to_region_2d(region, rv3d, p1_world)
    if not p0 or not p1:
        return min_pixels
    dx = float(p1[0]) - float(p0[0])
    dy = float(p1[1]) - float(p0[1])
    return max(min_pixels, (dx * dx + dy * dy) ** 0.5)


# ---------------------------------------------------------------------------
# Gizmo classes
# ---------------------------------------------------------------------------


class BIM_GT_box_face_quad(bpy.types.Gizmo):  # noqa: N801 — Blender bl_idname convention
    """Near-invisible face-quad click target with drag-to-resize modal.

    Geometry: a unit quad in the local XY plane at z=0. The adapter
    group's layout helper rotates and scales it onto the face plane;
    the quad is welded to the world face (``use_draw_scale = False``).
    """

    bl_idname = "BIM_GT_box_face_quad"
    bl_target_properties = ({"id": "offset", "type": "FLOAT", "array_length": 1},)

    __slots__ = (
        "custom_shape",
        "custom_shape_select",
        "init_value",
        "move_get_cb",
        "move_set_cb",
        "axis",
        "start_location",
        "depth_point",
        "callback",
        "ctrl_click_cb",
        "_group",
        "_face_axis",
        "is_max",
        "_drag_snapshot",
        "_last_geometry_state",
        "_strips_cache_key",
    )

    def draw(self, context: Any) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: Any, select_id: int) -> None:
        # Back-facing quads bind ``custom_shape_select`` to the halo-strip
        # TRIS so clicks OUTSIDE the box silhouette catch the back face.
        # Front-facing quads leave it None and reuse ``custom_shape``.
        shape = getattr(self, "custom_shape_select", None) or self.custom_shape
        self.draw_custom_shape(shape, select_id=select_id)

    def setup(self) -> None:
        if not hasattr(self, "custom_shape_"):
            self.custom_shape = self.new_custom_shape("TRIS", _QUAD_TRIS)
        self.custom_shape_select = None
        # Quad welded to world geometry — clicks must align with the
        # visible face, not a screen-size widget. Disables Blender's
        # per-frame pixel-constant autoscale.
        self.use_draw_scale = False

    # ---- modal -------------------------------------------------------------

    def invoke(self, context: Any, event: Any) -> set[str]:
        # CTRL+click handoff: dispatch a host-defined callback (e.g.
        # align-view) instead of starting a drag.
        if event.ctrl and getattr(self, "ctrl_click_cb", None) is not None:
            self.ctrl_click_cb(context, event)
            return {"FINISHED"}

        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return {"CANCELLED"}
        self.init_value = self.move_get_cb()
        # Freeze the projection plane at invoke — projection-plane
        # drift on tilted axes causes exponential delta runaway.
        self.depth_point = self.matrix_basis.translation.copy()
        self.start_location = region_2d_to_location_3d(region, rv3d, (event.mouse_x, event.mouse_y), self.depth_point)

        if getattr(self, "_group", None) is not None:
            self._group._lock_for(self)
        return {"RUNNING_MODAL"}

    def exit(self, context: Any, cancel: bool) -> None:
        try:
            if context.area:
                context.area.header_text_set(None)
            if cancel:
                self.move_set_cb(self.init_value)
            if hasattr(self, "callback"):
                self.callback(self.move_get_cb())
        finally:
            self._drag_snapshot = None
            if getattr(self, "_group", None) is not None:
                self._group._unlock_all()

    def modal(self, context: Any, event: Any, tweak: set[str]) -> set[str]:
        if event.type == "ESC":
            return {"CANCELLED"}
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return {"CANCELLED"}
        end_location = region_2d_to_location_3d(region, rv3d, (event.mouse_x, event.mouse_y), self.depth_point)
        delta = (end_location - self.start_location).dot(self.axis)
        if "SNAP" in tweak:
            delta = round(delta, 1)
        if "PRECISE" in tweak:
            delta /= 10.0
        self.move_set_cb(self.init_value + delta)
        if context.area:
            context.area.header_text_set(f"Value: {self.move_get_cb():.3f} ({delta:.3f})")
        return {"RUNNING_MODAL"}


class BIM_GT_box_face_outline(bpy.types.Gizmo):  # noqa: N801 — Blender bl_idname convention
    """Thin non-interactive colored edge outline for one face.

    Drawn as 4 line segments in the face plane. The layout helper
    toggles its ``alpha`` between near-zero and ``1.0`` based on the
    sibling face-quad's ``is_highlight`` state — so hovering the quad
    lights up the matching outline. ``hide_select = True`` keeps the
    outline out of the GPU selection buffer.
    """

    bl_idname = "BIM_GT_box_face_outline"
    bl_target_properties = ()

    __slots__ = (
        "custom_shape",
        "_face_axis",
        "is_max",
        "_last_outline_state",
    )

    def draw(self, context: Any) -> None:
        self.draw_custom_shape(self.custom_shape)

    def draw_select(self, context: Any, select_id: int) -> None:
        return None

    def setup(self) -> None:
        if not hasattr(self, "custom_shape_"):
            self.custom_shape = self.new_custom_shape("LINES", _QUAD_OUTLINE_LINES)
        self.use_draw_scale = False
        self.hide_select = True
        self._last_outline_state = "unit"


# ---------------------------------------------------------------------------
# Per-redraw orchestrator
# ---------------------------------------------------------------------------


def apply_face_quad_layout(
    *,
    quad_gizmos,
    outline_gizmos,
    bmin: Any,
    bmax: Any,
    matrix_world: Any,
    cage_rotation: Any,
    region: Any,
    rv3d: Any,
    locked: bool,
) -> None:
    """Lay out 6 face quads + 6 outlines on the box for this redraw.

    ``quad_gizmos`` / ``outline_gizmos`` are length-6 sequences in
    :data:`FACE_ROUTES` order. ``bmin`` / ``bmax`` are the box corners
    in the host's local frame; ``matrix_world`` is the host's world
    matrix; ``cage_rotation`` is the OBB rotation as a 4x4 (use
    ``Matrix.Identity(4)`` when rotation rides in ``matrix_world``).
    ``region`` / ``rv3d`` drive the view-dependent front/back split and
    the screen-constant halo margin; passing ``rv3d = None`` bails.

    Negative scale on the host is normalized to positive internally so
    the visible cube and the clickable face gizmos stay aligned —
    callers don't need to pre-process ``matrix_world``.

    When ``locked`` (a drag is active), ``hide`` / ``select_bias``
    writes are skipped — the active quad's geometry is still refreshed
    so it tracks the moving box.
    """
    if rv3d is None or getattr(rv3d, "view_rotation", None) is None:
        return
    if len(quad_gizmos) != 6 or len(outline_gizmos) != 6:
        return

    mw = _abs_scale_matrix(matrix_world)
    mw_rot = mw.to_quaternion().to_matrix()
    mw_rot_scale = mw.to_3x3()
    cage_rotation_3x3 = cage_rotation.to_3x3()
    pivot_local = (bmin + bmax) * 0.5
    box_center_local = pivot_local
    face_midpoints_local = {
        (0, False): Vector((float(bmin.x), box_center_local.y, box_center_local.z)),
        (0, True): Vector((float(bmax.x), box_center_local.y, box_center_local.z)),
        (1, False): Vector((box_center_local.x, float(bmin.y), box_center_local.z)),
        (1, True): Vector((box_center_local.x, float(bmax.y), box_center_local.z)),
        (2, False): Vector((box_center_local.x, box_center_local.y, float(bmin.z))),
        (2, True): Vector((box_center_local.x, box_center_local.y, float(bmax.z))),
    }

    view_dir = (rv3d.view_rotation @ Vector((0.0, 0.0, -1.0))).normalized()
    view_dir_tuple = (float(view_dir.x), float(view_dir.y), float(view_dir.z))
    face_normals_world = []
    for route_axis, route_is_max in FACE_ROUTES:
        axis_local = Vector(face_outward_axis_local(route_axis, route_is_max))
        n_world = (mw_rot @ cage_rotation_3x3 @ axis_local).normalized()
        face_normals_world.append((float(n_world.x), float(n_world.y), float(n_world.z)))
    front = front_facing_face_mask(tuple(face_normals_world), view_dir_tuple)

    box_center_world = mw @ pivot_local
    corners_world = _compute_box_corners_world(bmin, bmax, pivot_local, cage_rotation_3x3, mw)
    route_to_index = {route: i for i, route in enumerate(FACE_ROUTES)}

    for i, route in enumerate(FACE_ROUTES):
        quad_gz = quad_gizmos[i]
        is_front = front[i]
        axis_b, is_max_b = route

        # Place the colored OUTLINE on every face using the same composed
        # face matrix the front-facing solid quad uses. Hidden/shown via
        # alpha at the end of the pass.
        outline_orient = _AXIS_ORIENT[route]
        outline_face_world, _outline_axis = _compute_face_basis(
            mw,
            mw_rot,
            cage_rotation,
            pivot_local,
            face_midpoints_local[route],
            outline_orient,
        )
        ow, oh = _compute_face_quad_scale(bmin, bmax, axis_b, is_max_b)
        outline_gizmos[i].matrix_basis = _compose_face_matrix_basis(
            outline_face_world, mw_rot_scale, cage_rotation, outline_orient, ow, oh
        )

        if is_front:
            if not locked:
                quad_gz.hide = False
                quad_gz.select_bias = _FACE_QUAD_FRONT_FACING_SELECT_BIAS
            orient = _AXIS_ORIENT[route]
            face_world, world_axis = _compute_face_basis(
                mw,
                mw_rot,
                cage_rotation,
                pivot_local,
                face_midpoints_local[route],
                orient,
            )
            w, h = _compute_face_quad_scale(bmin, bmax, axis_b, is_max_b)
            quad_gz.matrix_basis = _compose_face_matrix_basis(face_world, mw_rot_scale, cage_rotation, orient, w, h)
            quad_gz.axis = world_axis
            if getattr(quad_gz, "_last_geometry_state", None) != "solid":
                quad_gz.custom_shape = quad_gz.new_custom_shape("TRIS", _QUAD_TRIS)
                quad_gz.custom_shape_select = None
                quad_gz._last_geometry_state = "solid"
            continue

        # Back-facing: anchor at the back face centre; build halo strips
        # in the planes of the adjacent FRONT faces, extruded outside
        # the silhouette toward this face's outward normal.
        face_world = mw @ (cage_rotation_3x3 @ (face_midpoints_local[route] - pivot_local) + pivot_local)
        quad_gz.matrix_basis = Matrix.Translation(face_world)
        quad_gz.axis = (mw_rot @ cage_rotation_3x3 @ Vector(face_outward_axis_local(axis_b, is_max_b))).normalized()

        adjacent_front_routes = [
            (axis_a, is_max_a)
            for axis_a in range(3)
            if axis_a != axis_b
            for is_max_a in (False, True)
            if front[route_to_index[(axis_a, is_max_a)]]
        ]
        # Per-face world margin: measure the screen-projected length of
        # ONE world unit along THIS face's outward normal. The world
        # margin that yields ~N pixels on screen is then ``N / length``.
        # Foreshortening on oblique faces shortens the projected step,
        # so the world step must grow to keep the strip the same width
        # on screen.
        face_world_margin = 0.0
        if region is not None:
            sample_end = box_center_world + quad_gz.axis * 1.0
            screen_step = _world_segment_to_screen_pixels(region, rv3d, box_center_world, sample_end, min_pixels=0.0)
            if screen_step > 0.0:
                face_world_margin = _FACE_QUAD_HALO_TARGET_PIXELS / screen_step
        if face_world_margin <= 0.0 or not adjacent_front_routes:
            if not locked:
                quad_gz.hide = True
                quad_gz.select_bias = _FACE_QUAD_HALO_FRAME_SELECT_BIAS
            if getattr(quad_gz, "_last_geometry_state", None) != "empty":
                quad_gz.custom_shape = quad_gz.new_custom_shape("TRIS", _EMPTY_TRIS)
                quad_gz.custom_shape_select = None
                quad_gz._last_geometry_state = "empty"
            continue

        extrusion_world = quad_gz.axis * face_world_margin
        extrusion_local = (
            float(extrusion_world.x),
            float(extrusion_world.y),
            float(extrusion_world.z),
        )
        all_tris: list[tuple[float, float, float]] = []
        for axis_a, is_max_a in adjacent_front_routes:
            edge_keys = _shared_edge_corner_keys(axis_a, is_max_a, axis_b, is_max_b)
            if edge_keys is None:
                continue
            key0, key1 = edge_keys
            wp0 = corners_world[key0]
            wp1 = corners_world[key1]
            local_p0 = (
                float(wp0.x - face_world.x),
                float(wp0.y - face_world.y),
                float(wp0.z - face_world.z),
            )
            local_p1 = (
                float(wp1.x - face_world.x),
                float(wp1.y - face_world.y),
                float(wp1.z - face_world.z),
            )
            all_tris.extend(_build_strip_tris_relative(local_p0, local_p1, extrusion_local))

        if not locked:
            quad_gz.hide = False
            quad_gz.select_bias = _FACE_QUAD_HALO_FRAME_SELECT_BIAS

        corner_keys = _face_corner_keys(axis_b, is_max_b)
        wc_local = [
            (
                float(corners_world[k].x - face_world.x),
                float(corners_world[k].y - face_world.y),
                float(corners_world[k].z - face_world.z),
            )
            for k in corner_keys
        ]
        face_quad_local = [
            wc_local[0],
            wc_local[1],
            wc_local[2],
            wc_local[0],
            wc_local[2],
            wc_local[3],
        ]
        if _strips_geometry_changed(quad_gz, tuple(face_quad_local), tuple(all_tris)):
            quad_gz.custom_shape = quad_gz.new_custom_shape("TRIS", face_quad_local)
            quad_gz.custom_shape_select = quad_gz.new_custom_shape("TRIS", all_tris)
        quad_gz._last_geometry_state = "strips"

    # Outline alpha follows ONLY the hovered quad's own state — light
    # the outline of the face under the cursor, nothing else.
    if not locked:
        for outline_gz, quad_gz in zip(outline_gizmos, quad_gizmos, strict=True):
            lit = bool(getattr(quad_gz, "is_highlight", False))
            outline_gz.alpha = 1.0 if lit else 0.0
            outline_gz.alpha_highlight = 1.0 if lit else 0.0


__all__ = [
    "AXIS_COLOR",
    "FACE_QUAD_ALPHA",
    "FACE_QUAD_ALPHA_HIGHLIGHT",
    "FACE_QUAD_SELECT_BIAS",
    "FACE_ROUTES",
    "BIM_GT_box_face_outline",
    "BIM_GT_box_face_quad",
    "apply_face_quad_layout",
    "compute_face_resize",
    "face_outward_axis_local",
    "front_facing_face_mask",
    "view_axis_parallel_face_mask",
]
