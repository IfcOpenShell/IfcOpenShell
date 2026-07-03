# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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

"""Shared helpers for Bonsai's parametric preview flows.

Multiple Bonsai features follow the same Scene-level preview pattern:

    Enable<X>Preview   — validates a selection, populates draft state on
                         ``Scene.BIMPreviewProperties.<x>``, flips ``is_active``.
    Gizmo<X>Preview    — polls on ``is_active``, surfaces tunable widgets +
                         validate/cancel icons.
    <X>PreviewDecorator — GPU lines drawn while ``is_active`` is True.
    Finish<X>Preview   — direct ``bpy.ops.bim.<verb>(...)`` call with kwargs
                         read off the draft state, then clears it.
    Cancel<X>Preview   — pure state reset.

The MEP bend and wall fillet flows are the two current callers. They write
their Finish / Cancel operators directly, matching the convention used
throughout the rest of ``bim/module/model/`` for operator-to-operator
dispatch (explicit ``bpy.ops.bim.X(kwarg=value)`` at the call site, no
string indirection). This module hosts the cross-cutting accessors only;
no base class layer.

The GPU draw-handler lifecycle for ``<X>PreviewDecorator`` lives on the
feature-neutral ``tool.Blender.ViewportDecorator`` base, which every
viewport decorator (preview or otherwise) inherits from."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import bpy

import bonsai.tool as tool

# --- Props accessors ---------------------------------------------------------


def get_preview_props(context: bpy.types.Context, attr: str):
    """Resolve a child preview PropertyGroup under ``Scene.BIMPreviewProperties``.

    Returns ``None`` if the umbrella isn't attached yet — true briefly
    during addon register and during plug-out, so polls / draw callbacks
    must defend against ``None`` rather than assuming the prop is always
    available. Also tolerates contexts without a ``scene`` attribute
    (test mocks built from ``SimpleNamespace``)."""
    scene = getattr(context, "scene", None)
    if scene is None:
        return None
    preview = getattr(scene, "BIMPreviewProperties", None)
    return getattr(preview, attr, None) if preview is not None else None


def is_preview_active(context: bpy.types.Context, attr: str) -> bool:
    """``True`` while a specific preview is open. Used by sibling gizmo
    polls to hide themselves so the preview is the only interactive
    surface in the viewport (the bend / fillet preview groups take over
    the same selection's icon stack)."""
    props = get_preview_props(context, attr)
    return bool(props is not None and props.is_active)


def any_preview_active(context: bpy.types.Context) -> bool:
    """``True`` if any registered preview is currently open. Sister gizmo
    polls call this to hide themselves uniformly during ANY preview, so a
    new preview registered in ``PREVIEW_CANCEL_OPS`` automatically gates
    every parametric gizmo without each one growing a specific check."""
    for attr, _op_name in PREVIEW_CANCEL_OPS:
        if is_preview_active(context, attr):
            return True
    return False


# --- Lazy closure factories --------------------------------------------------
#
# Used by preview gizmo groups when wiring ``BIM_GT_gizmo_dimension``'s
# ``move_get_cb`` / ``move_set_cb`` callbacks. The closures re-resolve
# ``bpy.context.scene`` per CALL rather than capturing it at setup() time
# — the captured Scene's RNA struct can be freed on file open / undo, and
# referencing a freed struct crashes Blender. Lazy lookup survives the
# whole undo / reload lifecycle.


def make_props_callback(attr: str) -> Callable[[], Any]:
    """Return a zero-arg callable that lazily fetches the preview props.

    Equivalent to ``getattr(bpy.context.scene.BIMPreviewProperties, attr)``
    with full defensiveness against missing scene / missing umbrella."""

    def _props():
        scene = bpy.context.scene
        preview = getattr(scene, "BIMPreviewProperties", None) if scene else None
        return getattr(preview, attr, None) if preview is not None else None

    return _props


def make_dim_getter(props_callback: Callable[[], Any], field: str) -> Callable[[], float]:
    """Factory for ``BIM_GT_gizmo_dimension.move_get_cb`` reading a single
    FloatProperty off the live preview state. Returns ``0.0`` defensively
    when the props are temporarily unavailable so the widget doesn't crash
    Blender during plug-out / reload."""

    def _get() -> float:
        props = props_callback()
        return getattr(props, field) if props is not None else 0.0

    return _get


def make_dim_setter(
    props_callback: Callable[[], Any],
    field: str,
    min_value: float = 0.001,
) -> Callable[[float], None]:
    """Factory for ``BIM_GT_gizmo_dimension.move_set_cb`` writing a single
    FloatProperty + tagging viewport areas for redraw so the GPU preview
    decorator tracks the value live during drag. Clamps at ``min_value``
    to match the FloatProperty's declared lower bound."""

    def _set(value: float) -> None:
        props = props_callback()
        if props is None:
            return
        setattr(props, field, max(min_value, float(value)))
        tool.Blender.update_all_viewports()

    return _set


# --- Shared Enable lifecycle helpers -----------------------------------------


def sync_uncommitted_moves(objects: list) -> None:
    """Push any Blender-side translation / rotation of ``objects`` back to
    their IFC ``ObjectPlacement`` before a preview decorator starts reading
    ``obj.matrix_world`` per frame.

    Without this sync, a user who grabbed-moved an object but didn't commit
    the move sees the live preview at the dragged position while the final
    commit lands at the stale IFC position — a confusing "where did my
    preview go?" experience. Both bend and fillet enable paths call this
    on the relevant pair just before activating the preview."""
    for obj in objects:
        tool.Geometry.commit_placement_if_moved(obj, apply_scale=False)


def clear_preview_state(props: bpy.types.PropertyGroup) -> None:
    """Reset a preview PropertyGroup to its idle state on commit / cancel.

    Sets ``is_active`` to False and zeros every ``IntProperty`` whose name
    ends in ``_id`` (the entity-reference convention every preview follows).
    Other fields are left at their last value — defaults are re-applied on
    the next enable, so leaving them alone avoids a redundant write."""
    props.is_active = False
    for name, rna in props.bl_rna.properties.items():
        if name.endswith("_id") and rna.type == "INT":
            setattr(props, name, 0)


# --- Standard Finish flow ----------------------------------------------------


def commit_preview(
    operator: bpy.types.Operator,
    context: bpy.types.Context,
    attr: str,
    target_op_name: str,
    kwarg_names: tuple[str, ...],
) -> set[str]:
    """Standard Finish-Preview dispatch: validate context + active preview,
    read kwargs off the draft, call ``bpy.ops.bim.<target_op_name>(**kwargs)``,
    and clear the preview on success.

    The dispatched operator's own ``self.report({"ERROR"})`` paths are promoted
    by ``bpy.ops`` to ``RuntimeError`` — catching it here surfaces the message
    to the user via ``operator.report`` rather than leaving Blender's operator
    state half-broken (which silently disables downstream gizmo polls).

    Returns the dispatched operator's result set verbatim so callers can
    pass it straight back from their own ``execute``."""
    if context.screen is None:
        return {"CANCELLED"}
    props = get_preview_props(context, attr)
    if props is None or not props.is_active:
        return {"CANCELLED"}
    if tool.Ifc.get() is None:
        operator.report({"ERROR"}, "No IFC file loaded.")
        return {"CANCELLED"}
    kwargs = {name: getattr(props, name) for name in kwarg_names}
    try:
        result = getattr(bpy.ops.bim, target_op_name)(**kwargs)
    except RuntimeError as exc:
        operator.report({"ERROR"}, str(exc))
        return {"CANCELLED"}
    if "FINISHED" in result:
        clear_preview_state(props)
    return result


# --- Esc dispatch ------------------------------------------------------------

PREVIEW_CANCEL_OPS: tuple[tuple[str, str], ...] = (
    ("bend", "cancel_bend_preview"),
    ("wall_fillet", "cancel_wall_fillet_preview"),
)
"""Registry of ``(child PointerProperty on Scene.BIMPreviewProperties, bim
operator name)`` consulted by the Esc handler. Adding a new preview means
appending one tuple; the forward-compat test pins that every preview
PropertyGroup with ``is_active`` has an entry here."""


def try_cancel_active_preview(context: bpy.types.Context) -> bool:
    """Cancel every registered preview that is currently active.

    Returns ``True`` iff at least one preview was cancelled. Multiple
    previews can be simultaneously active (e.g. a stale bend preview opened
    just before the user starts a wall fillet) — one Esc must clear them
    all rather than forcing the user to tap Esc once per preview.

    Tags 3D viewports for redraw on success — the Esc keymap entry runs
    outside a viewport mouse event so the gizmo poll wouldn't re-evaluate
    until the next interaction without an explicit redraw."""
    cancelled = False
    for attr, op_name in PREVIEW_CANCEL_OPS:
        if is_preview_active(context, attr):
            getattr(bpy.ops.bim, op_name)()
            cancelled = True
    if cancelled:
        tool.Blender.update_all_viewports(context)
    return cancelled


def discard_pending_previews(scene: bpy.types.Scene) -> None:
    """Clear every active preview under ``Scene.BIMPreviewProperties`` so
    saved preview state never resurfaces on file load.

    Mirrors ``tool.Parametric.heal_stale_edit_flags`` for the object-level
    parametric-edit lifecycle — except previews are *discarded* rather than
    validated. A preview's only UI cue is its in-viewport widget; reloading
    a ``.blend`` saved mid-preview restores the flag but not the surrounding
    user attention, and a stuck ``is_active`` silently hides every sibling
    gizmo poll gated on it.

    Iterates ``PREVIEW_CANCEL_OPS`` so any preview registered for Esc
    cancellation is automatically covered here too. Sets ``is_active``
    directly rather than dispatching the cancel operator: load_post may
    fire before ``bpy.context.screen`` is reattached, and the cancel
    operators bail on ``context.screen is None``."""
    preview = getattr(scene, "BIMPreviewProperties", None)
    if preview is None:
        return
    for attr, _op_name in PREVIEW_CANCEL_OPS:
        child = getattr(preview, attr, None)
        if child is not None and getattr(child, "is_active", False):
            child.is_active = False
