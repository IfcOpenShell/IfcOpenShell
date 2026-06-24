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

"""Interactive face-quad resize gizmos for the active clip box.

Adapter group that binds the generic :mod:`face_quad` core to a Bonsai
clip-box Empty: six near-invisible click quads + six edge outlines on
the cube's faces. Dragging a face does a ONE-SIDED resize — the dragged
face moves along its outward world normal while the opposite face stays
put — by writing the empty's ``location`` and ``scale``. Bonsai's
depsgraph handler then re-arms the clip planes from the new matrix.
"""

from __future__ import annotations

import contextlib
from typing import Any

import bpy
from mathutils import Matrix, Vector

import bonsai.tool as tool

from . import face_quad

# Local-frame bounds of the empty's CUBE display. The display spans
# ``[-empty_display_size, +empty_display_size]^3``; Bonsai always sets
# ``empty_display_size = 1.0`` on clip-box hosts, so the local box is
# the unit cube. The empty's per-axis scale + rotation + translation
# ride in ``matrix_world``, which the layout helper applies.
_LOCAL_BMIN = Vector((-1.0, -1.0, -1.0))
_LOCAL_BMAX = Vector((1.0, 1.0, 1.0))


def _world_axis(empty: bpy.types.Object, axis: int, is_max: bool) -> Vector:
    """Outward world-space unit normal of the ``(axis, is_max)`` face.

    Uses the rotation-only matrix so a negative-scale empty doesn't
    flip the resulting direction — the visible "+X face" then stays
    associated with world +X (transformed through rotation).
    """
    rot_mat = empty.matrix_world.to_quaternion().to_matrix()
    n = Vector(rot_mat.col[axis])
    if n.length <= 0.0:
        return Vector((0.0, 0.0, 0.0))
    n.normalize()
    return n if is_max else -n


def _world_half_extent(empty: bpy.types.Object, axis: int) -> float:
    """The empty's box half-extent along local ``axis`` in WORLD units.

    A CUBE empty's local cube is ``±empty_display_size``; ``matrix_world``
    stretches it by the column length on ``axis``. So the world
    half-extent is ``|column[axis]| * empty_display_size``.
    """
    col_len = empty.matrix_world.to_3x3().col[axis].length
    display_size = abs(float(getattr(empty, "empty_display_size", 1.0) or 1.0))
    return float(col_len) * display_size


def _make_face_get_cb(gz: Any, group: Any, axis: int, is_max: bool):
    """Closure returning the world half-extent at drag start and
    snapshotting the empty's full transform on the gizmo instance.

    The snapshot lives on the gizmo (not the group) so a PERSISTENT
    group servicing multiple clip boxes can't bleed one drag's state
    onto another. Cleared on ``exit`` by the shared face-quad hook.
    """

    def getter() -> float:
        empty = group._empty
        if empty is None:
            return 0.0
        existing = getattr(gz, "_drag_snapshot", None)
        if existing is not None and existing.get("empty_name") == getattr(empty, "name", None):
            return float(existing["world_half"])

        world_half = _world_half_extent(empty, axis)
        display_size = abs(float(getattr(empty, "empty_display_size", 1.0) or 1.0))
        gz._drag_snapshot = {
            "empty_name": getattr(empty, "name", None),
            "world_half": world_half,
            "location": tuple(float(v) for v in empty.location),
            "scale": tuple(float(v) for v in empty.scale),
            "display_size": display_size if display_size != 0.0 else 1.0,
            "world_axis": tuple(_world_axis(empty, axis, is_max)),
        }
        return float(world_half)

    return getter


def _make_ctrl_click_cb(axis: int, is_max: bool):
    """Closure that dispatches CTRL+click on a face to the align-view operator.

    Routing through an operator (rather than mutating ``rv3d`` here)
    keeps the action F3-searchable and undoable.
    """

    def _callback(_context: Any, _event: Any) -> None:
        bpy.ops.bim.align_view_to_clip_face("INVOKE_DEFAULT", axis=axis, is_max=is_max)

    return _callback


def _make_face_set_cb(gz: Any, group: Any, axis: int, is_max: bool):
    """Closure that applies a one-sided face resize by writing the
    empty's ``location`` + ``scale``.

    The modal calls this with ``value = init + delta`` where ``delta``
    is the cursor's projection onto the face's OUTWARD world normal.
    Both reads come from ``gz._drag_snapshot`` so every frame is
    relative to drag start, never compounding.
    """
    del is_max  # snapshot's world_axis carries the direction

    def setter(value: float) -> None:
        empty = group._empty
        if empty is None:
            return
        snap = getattr(gz, "_drag_snapshot", None)
        if snap is None or snap.get("empty_name") != getattr(empty, "name", None):
            return

        new_scale_axis, new_location = face_quad.compute_face_resize(
            value=value,
            init_world_half=snap["world_half"],
            init_location=snap["location"],
            world_axis=snap["world_axis"],
            display_size=snap["display_size"],
        )
        new_scale = list(snap["scale"])
        # Preserve the sign of the original scale so a user-flipped empty
        # stays flipped after the resize — compute_face_resize returns a
        # positive magnitude, the sign is the user's intent to keep.
        sign = -1.0 if snap["scale"][axis] < 0.0 else 1.0
        new_scale[axis] = sign * new_scale_axis

        empty.scale = new_scale
        empty.location = Vector(new_location)

    return setter


class OBJECT_GGT_bim_clip_box(bpy.types.GizmoGroup):  # noqa: N801 — Blender bl_idname convention
    """Face-quad resize handles on the active clip box.

    Renders six near-invisible click-target quads and six colored edge
    outlines on the active clip-box empty whenever clipping is enabled.
    Click-and-drag a face to resize one-sided; the opposite face stays
    put. CTRL+click and plain click fall through to selection.
    """

    bl_idname = "OBJECT_GGT_bim_clip_box"
    bl_label = "Bonsai Clip Box Faces"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT", "SHOW_MODAL_ALL"}

    @classmethod
    def poll(cls, context: Any) -> bool:
        scene = getattr(context, "scene", None)
        if scene is None:
            return False
        scene_props = tool.ClipBox.get_scene_props(scene)
        if not scene_props.enabled or not scene_props.enable_gizmos:
            return False
        active_clip_box = tool.ClipBox.get_active_clip_box(scene)
        if active_clip_box is None:
            return False
        # Only render when the user has the active clip box itself
        # selected — otherwise the face handles would intercept clicks
        # meant for the geometry behind them.
        return getattr(context, "active_object", None) is active_clip_box

    @classmethod
    def setup_keymap(cls, keyconfig):
        # Bind CLICK_DRAG so plain LEFTMOUSE PRESS passes through to
        # selection — the user can still click through a near-invisible
        # face quad to pick a mesh behind it.
        km = keyconfig.keymaps.new(
            name=cls.bl_idname,
            space_type=cls.bl_space_type,
            region_type=cls.bl_region_type,
        )
        km.keymap_items.new("gizmogroup.gizmo_tweak", type="LEFTMOUSE", value="CLICK_DRAG")
        km.keymap_items.new("gizmogroup.gizmo_tweak", type="LEFTMOUSE", value="PRESS", ctrl=True)
        return km

    def setup(self, context: Any) -> None:
        # ``_empty`` is resolved each refresh so the PERSISTENT group
        # follows whichever clip box is active in the scene PG.
        self._empty: bpy.types.Object | None = None
        self._locked = False
        self._face_routes: list[tuple[int, bool]] = []

        for axis, is_max in face_quad.FACE_ROUTES:
            gz = self.gizmos.new(face_quad.BIM_GT_box_face_quad.bl_idname)
            gz._group = self
            gz._face_axis = axis
            gz.is_max = is_max
            gz._drag_snapshot = None
            gz._last_geometry_state = "solid"
            gz._strips_cache_key = None
            gz.color = face_quad.AXIS_COLOR[axis]
            gz.color_highlight = tuple(min(1.0, c + 0.3) for c in face_quad.AXIS_COLOR[axis])
            gz.alpha = face_quad.FACE_QUAD_ALPHA
            gz.alpha_highlight = face_quad.FACE_QUAD_ALPHA_HIGHLIGHT
            gz.use_draw_modal = True
            gz.scale_basis = 1.0
            gz.select_bias = face_quad.FACE_QUAD_SELECT_BIAS
            gz.move_get_cb = _make_face_get_cb(gz, self, axis, is_max)
            gz.move_set_cb = _make_face_set_cb(gz, self, axis, is_max)
            # CTRL+click on a face aligns the viewport to look at it.
            gz.ctrl_click_cb = _make_ctrl_click_cb(axis, is_max)
            self._face_routes.append((axis, is_max))

        # Outlines added last so they composite on top of the quad
        # fills (Blender draws gizmos in creation order).
        for axis, is_max in face_quad.FACE_ROUTES:
            ol = self.gizmos.new(face_quad.BIM_GT_box_face_outline.bl_idname)
            ol._face_axis = axis
            ol.is_max = is_max
            ol.color = face_quad.AXIS_COLOR[axis]
            ol.color_highlight = face_quad.AXIS_COLOR[axis]
            ol.alpha = 0.0
            ol.alpha_highlight = 0.0
            ol.line_width = 2.5

    def _quad_gizmos(self):
        return self.gizmos[: len(self._face_routes)]

    def _outline_gizmos(self):
        n = len(self._face_routes)
        return self.gizmos[n : 2 * n]

    def refresh(self, context: Any) -> None:
        """State-change path: resolve the active empty, then run the
        shared face-quad layout so the quads aren't stale for a frame
        after a selection or active-index change."""
        empty = tool.ClipBox.get_active_clip_box(context.scene)
        self._empty = empty
        if empty is None:
            for gz in self.gizmos:
                gz.hide = True
            return
        self._layout(context, empty)

    def draw_prepare(self, context: Any) -> None:
        """Per-redraw — fires on orbit — re-run the layout so the
        front/back split, halo strips, and outline highlights track
        the camera and any live G/R/S on the empty."""
        empty = self._empty
        if empty is None:
            return
        self._layout(context, empty)

    def _layout(self, context: Any, empty: bpy.types.Object) -> None:
        face_quad.apply_face_quad_layout(
            quad_gizmos=self._quad_gizmos(),
            outline_gizmos=self._outline_gizmos(),
            bmin=_LOCAL_BMIN,
            bmax=_LOCAL_BMAX,
            matrix_world=empty.matrix_world,
            # The empty's rotation rides in matrix_world, so the
            # box-local OBB rotation is identity.
            cage_rotation=Matrix.Identity(4),
            region=getattr(context, "region", None),
            rv3d=getattr(context, "region_data", None),
            locked=self._locked,
        )

    # ---- mutual exclusion (lock siblings during a drag) ------------------

    def _lock_for(self, active_gizmo) -> None:
        self._locked = True
        for gz in self.gizmos:
            if gz is not active_gizmo:
                with contextlib.suppress(ReferenceError, RuntimeError):
                    gz.hide = True

    def _unlock_all(self) -> None:
        self._locked = False
        for gz in self.gizmos:
            with contextlib.suppress(ReferenceError, RuntimeError):
                gz.hide = False
        # Rebuild caps synchronously so the cross-section overlay
        # re-forms the instant the user releases the handle, rather
        # than waiting for the depsgraph's debounced rebuild path.
        with contextlib.suppress(RuntimeError, ReferenceError):
            tool.ClipBox.rebuild_caps_now()
        # Push an undo step so the user can revert a face drag with Ctrl+Z.
        with contextlib.suppress(RuntimeError):
            bpy.ops.ed.undo_push(message="Resize Clip Box")
