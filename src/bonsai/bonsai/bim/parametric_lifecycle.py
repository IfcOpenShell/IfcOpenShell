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

"""Shared operator mixins for parametric-edit operators.

Edit-lifecycle mixins (Enable / Finish / Cancel):
    `FeatureModifierEditMixin` — door, window (BBIM_<Type> pset; nested
        lining/panel properties; Finish + Cancel route through
        ``ifcopenshell.api.feature``).
    `PathPreservingEditMixin` — railing, roof (path_data preserved across
        edit; only general kwargs are user-editable).

Pattern selection (which approach a new feature should adopt):
    Every parametric edit lifecycle commits to one of three patterns. Pick by
    answering "does the feature share the Enable→Finish→Cancel shape that
    one of the existing mixins already encodes?":

    A. Inherit one of the shared mixins below and route through
       `tool.Parametric.build_edit_lifecycle`:

       - `FeatureModifierEditMixin` when the feature stores its pset as
         `{general fields} + {lining_properties: {...}} + {panel_properties: {...}}`
         and Finish must call a per-type `update_<type>_modifier_representation`.

       - `PathPreservingEditMixin` when the feature's pset carries a
         `path_data` field that survives general-kwarg edits untouched, with
         a separate Enable/Finish/Cancel lifecycle for path editing itself.

    B. Write a per-feature mixin that subclasses `ParametricEditMixinBase`
       and provides `_enable_targets` / `_finish_targets` / `_cancel_targets`,
       then route through `build_edit_lifecycle`. Pick this when the
       feature's pset roundtrip or representation handling diverges from the
       shared mixins but the Enable→Finish→Cancel shape still fits.

    C. Declare standalone Enable/Finish/Cancel Operator subclasses (no
       factory) when the feature's parameter-change logic is sufficiently
       unique that even a per-feature mixin would force optional hooks or
       dead branches. Such operators MUST call the matrix_world drift
       helpers (`tool.Geometry.commit_placement_if_moved` on Enable/Finish,
       `tool.Geometry.restore_or_rebaseline_placement` on Cancel) — the
       drift contract is enforced uniformly regardless of which pattern the
       operators adopt.

    The authoritative list of registered parametric types — and which use
    `build_edit_lifecycle` vs. standalone operators — lives in
    `tool/parametric.py`'s `EDIT_TYPES` and is enforced by the registry
    contract tests.

This module hosts operator-side mixins that import ``bonsai.tool`` freely.
The lightweight parametric registry consumed at addon-enable time must stay
free of such imports and lives separately in ``tool/parametric.py``."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import ClassVar, get_args

import bpy
import ifcopenshell.util.element
from bpy.app.handlers import persistent
from ifcopenshell import entity_instance

import bonsai.core.geometry
import bonsai.tool as tool


class ParametricEditMixinBase:
    """Common scaffolding for parametric edit-lifecycle mixins.

    Each per-type subclass provides four hooks:

        ``pset_name``: BBIM_<Type> pset identifier
        ``_is_element_type(element)``: IFC element predicate
        ``_get_props(obj)``: PropertyGroup accessor
        ``_iter_targets(context)``: list of objects to act on (default: ``[active_object]``)

    Drift handling is built in: pre-edit matrix_world drift commits to IFC on
    Enable, in-edit drag commits on Finish, and Cancel restores the committed
    IFC placement. This prevents an uncommitted drag from disappearing on
    Finish or snapping back on Cancel.

    Operator subclasses call one of ``_enable_targets`` / ``_finish_targets`` /
    ``_cancel_targets`` from their ``_execute`` method."""

    pset_name: ClassVar[str]

    @classmethod
    def _iter_targets(cls, context: bpy.types.Context) -> list[bpy.types.Object]:
        obj = context.active_object
        return [obj] if obj else []

    @classmethod
    def _is_element_type(cls, element: entity_instance) -> bool:
        raise NotImplementedError

    @classmethod
    def _get_props(cls, obj: bpy.types.Object):
        raise NotImplementedError

    @classmethod
    def _resolve(cls, obj: bpy.types.Object):
        """Look up ``(element, props)`` for ``obj`` if it matches this type, else None.

        Common predicate guard for every lifecycle method — collapses the
        ``element = tool.Ifc.get_entity(obj); assert element; if not is_<type>(element): return``
        triplet into one call."""
        element = tool.Ifc.get_entity(obj)
        if not element or not cls._is_element_type(element):
            return None
        return element, cls._get_props(obj)

    @classmethod
    def _handle_drift_on_enable(cls, obj: bpy.types.Object) -> None:
        tool.Geometry.commit_placement_if_moved(obj, apply_scale=False)

    @classmethod
    def _handle_drift_on_finish(cls, obj: bpy.types.Object) -> None:
        tool.Geometry.commit_placement_if_moved(obj)

    @classmethod
    def _handle_drift_on_cancel(cls, obj: bpy.types.Object, element: entity_instance) -> None:
        tool.Geometry.restore_or_rebaseline_placement(obj, element)

    @classmethod
    def _mark_type_thumbnail_dirty(cls, element: entity_instance) -> None:
        """Mark the element's type's preview thumbnail for refresh so the
        property-panel preview reflects post-edit geometry. No-op for
        occurrences without a backing type."""
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            tool.Model.mark_thumbnail_for_update(element_type)


class FeatureModifierEditMixin(ParametricEditMixinBase):
    """Lifecycle for door- and window-style parametric modifier operators.

    Enable:
        Read BBIM_<Type> pset JSON → unwrap ``lining_properties`` and
        ``panel_properties`` → merge constituents data → set draft props →
        ``is_editing = True``.

    Finish:
        Gather ``general / lining / panel`` kwargs (project units) → nest →
        ``is_editing = False`` → call ``_update_modifier_representation`` →
        mark thumbnail → write back to BBIM_<Type> pset via
        ``ifcopenshell.api.pset.edit_pset``.

    Cancel:
        Read BBIM_<Type> pset JSON → unwrap → restore draft props →
        ``switch_representation`` to the Body representation →
        ``is_editing = False``."""

    @classmethod
    def _update_modifier_representation(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Hook: call the per-type ``update_<type>_modifier_representation``."""
        raise NotImplementedError

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        cls._handle_drift_on_enable(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, cls.pset_name, "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))
        data.update(tool.Model.get_constituents_props_data(element))
        # required since the pset can be loaded from .ifc and the PropertyGroup
        # would otherwise still hold its default values
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True

    @classmethod
    def _finish_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        data = props.get_general_kwargs(convert_to_project_units=True)
        data["lining_properties"] = props.get_lining_kwargs(convert_to_project_units=True)
        data["panel_properties"] = props.get_panel_kwargs(convert_to_project_units=True)
        cls._update_modifier_representation(obj, context)
        cls._mark_type_thumbnail_dirty(element)
        tool.Pset.write_bbim_data(element, cls.pset_name, data)
        cls._handle_drift_on_finish(obj)
        # Set only on success: if any IFC op above raised, the user's draft survives for retry.
        props.is_editing = False

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        # Cancel must always clear is_editing — leaving it True after a
        # restore-failure would block the user from re-entering edit mode and
        # the next save's stale-flag heal would silently roll back the
        # cancellation. Wrap the restore in try/finally so the flag flips
        # even on partial failure.
        try:
            data = json.loads(ifcopenshell.util.element.get_pset(element, cls.pset_name, "Data"))
            data.update(data.pop("lining_properties"))
            data.update(data.pop("panel_properties"))
            props.set_props_kwargs_from_ifc_data(data)
            body = tool.Geometry.get_body_representation(element)
            bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=body)
            cls._handle_drift_on_cancel(obj, element)
        finally:
            props.is_editing = False

    def _enable_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._enable_one(obj)
        return {"FINISHED"}

    def _finish_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._finish_one(obj, context)
        return {"FINISHED"}

    def _cancel_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._cancel_one(obj)
        return {"FINISHED"}


class PathPreservingEditMixin(ParametricEditMixinBase):
    """Lifecycle for railing- and roof-style parametric modifier operators.

    Distinctive: ``path_data`` is part of the BBIM_<Type> pset but is **not**
    user-editable through this lifecycle — it survives the edit untouched, only
    general kwargs are diffed. (Path editing has its own separate operator
    pair, ``Enable/Finish/CancelEditing<Type>Path``, out of scope here.)

    Enable:
        Fetch pset data via ``tool.Model.get_modeling_bbim_pset_data`` → set
        draft props → ``is_editing = True``. The subclass post-load hook
        can reshape the dict to fit the PropertyGroup's storage layout
        (e.g., pre-serialise a structured pset value to JSON for a
        ``StringProperty`` field).

    Finish:
        Read fresh pset → keep ``path_data`` → gather ``general`` kwargs
        (project units) → reassemble → ``is_editing = False`` → call
        ``_update_pset`` (per-type pset writer) → call ``_update_modifier_ifc_data``
        (per-type geometry commit).

    Cancel:
        Read fresh pset → restore draft props → call
        ``_restore_viewport_after_cancel`` (per-type viewport restore — typically
        rebuilds the bmesh preview, but subclasses may load a different
        representation entirely) → ``is_editing = False``."""

    @classmethod
    def _post_load_data(cls, data: dict) -> dict:
        """Hook: optionally transform the pset data dict after loading and before
        passing to ``set_props_kwargs_from_ifc_data``. Default: pass-through.

        Override when the PropertyGroup stores a structured pset field as a
        serialised primitive — e.g., a list/dict value mapped onto a
        ``StringProperty`` requires JSON-encoding here."""
        return data

    @classmethod
    def _update_pset(cls, element: entity_instance, data: dict) -> None:
        """Hook: per-type pset writer (``update_bbim_<type>_pset``)."""
        raise NotImplementedError

    @classmethod
    def _update_modifier_ifc_data(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Hook: per-type ``update_<type>_modifier_ifc_data`` — commits the
        modified geometry to IFC. Signature accepts ``(obj, context)`` so
        subclasses can forward either argument to their existing helper."""
        raise NotImplementedError

    @classmethod
    def _restore_viewport_after_cancel(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Hook: restore the viewport mesh to match the just-restored draft props.

        Most subclasses rebuild a bmesh preview from props. Subclasses whose
        committed IFC representation diverges from the preview may switch
        the mesh back to the committed representation instead."""
        raise NotImplementedError

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        _element, props = resolved
        cls._handle_drift_on_enable(obj)
        data = tool.Model.get_modeling_bbim_pset_data(obj, cls.pset_name)["data_dict"]
        data = cls._post_load_data(data)
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True

    @classmethod
    def _finish_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        pset_data = tool.Model.get_modeling_bbim_pset_data(obj, cls.pset_name)
        stored = pset_data["data_dict"]
        data = props.get_general_kwargs(convert_to_project_units=True)
        data["path_data"] = stored["path_data"]
        # Skip the pset commit when the draft is identical to the stored pset:
        # an Enable → Finish-without-changes cycle should not pollute the
        # representation list or burn an undo entry. Drift commit still runs
        # unconditionally — matrix_world drift is independent of pset content.
        if data != stored:
            cls._update_pset(element, data)
            cls._update_modifier_ifc_data(obj, context)
            cls._mark_type_thumbnail_dirty(element)
        cls._handle_drift_on_finish(obj)
        # Set only on success: if any IFC op above raised, the user's draft survives for retry.
        props.is_editing = False

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        try:
            pset_data = tool.Model.get_modeling_bbim_pset_data(obj, cls.pset_name)
            stored = pset_data["data_dict"]
            draft = props.get_general_kwargs(convert_to_project_units=True)
            draft["path_data"] = stored["path_data"]
            nothing_changed = draft == stored
            data = cls._post_load_data(stored)
            props.set_props_kwargs_from_ifc_data(data)
            # Skip the viewport rebuild on a no-op cancel: the mesh on screen is
            # still the committed representation, and the per-type viewport-restore
            # hook may be expensive (some subclasses reload a high-poly IFC
            # representation rather than rebuild a preview mesh).
            if not nothing_changed:
                cls._restore_viewport_after_cancel(obj, context)
            cls._handle_drift_on_cancel(obj, element)
        finally:
            # Always clear the flag — see ``FeatureModifierEditMixin._cancel_one``
            # for the rationale.
            props.is_editing = False

    def _enable_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._enable_one(obj)
        return {"FINISHED"}

    def _finish_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._finish_one(obj, context)
        return {"FINISHED"}

    def _cancel_targets(self, context: bpy.types.Context) -> set[str]:
        for obj in self._iter_targets(context):
            self._cancel_one(obj, context)
        return {"FINISHED"}


# --- Type-selection mixins (Cycle / Pick) ------------------------------------


class TypeAccessorBase:
    """Shared contract for operators that resolve and write a Literal type
    attribute on a Bonsai PropertyGroup.

    Subclasses define ``element_checker``, ``props_getter``, ``type_literal``,
    ``type_attr``; ``skip_element_check`` bypasses element validation. Concrete
    subclasses (``CycleTypeMixin``, ``PickTypeMixin``) add the interaction
    shape on top.

    Test doubles must be set on the operator instance — the predicates are
    bound at class-definition time, so patching the underlying tool module
    has no effect."""

    element_checker: Callable[[entity_instance], bool]
    props_getter: Callable[[bpy.types.Object], bpy.types.PropertyGroup]
    type_literal: type
    type_attr: str
    skip_element_check: bool = False

    def _resolve_target(self, context: bpy.types.Context) -> bpy.types.Object | None:
        """Return the active object iff it passes ``element_checker`` (or the
        check is skipped). ``None`` signals the operator should bail with
        ``{'CANCELLED'}``."""
        obj = context.active_object
        if not obj:
            return None
        if not self.skip_element_check:
            element = tool.Ifc.get_entity(obj)
            if not element or not self.element_checker(element):
                return None
        return obj


class CycleTypeMixin(TypeAccessorBase):
    """Operator mixin that cycles through ``type_literal``'s values.

    Shift-click reverses direction."""

    reverse: bpy.props.BoolProperty(name="Reverse", default=False, options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        self.reverse = event.shift
        return self.execute(context)

    def _cycle_type(self, context: bpy.types.Context) -> set[str]:
        obj = self._resolve_target(context)
        if obj is None:
            return {"CANCELLED"}

        props = self.props_getter(obj)
        types = get_args(self.type_literal)
        current = getattr(props, self.type_attr)
        idx = types.index(current) if current in types else 0
        direction = -1 if self.reverse else 1
        setattr(props, self.type_attr, types[(idx + direction) % len(types)])

        return {"FINISHED"}


class PickTypeMixin(TypeAccessorBase):
    """Operator mixin that opens a popup menu listing ``type_literal``'s values.

    Empty ``value`` ⇒ ``invoke`` opens the popup; non-empty ⇒ the user picked
    an item and ``_pick_type`` applies it.

    When invoked mid-click (e.g. from a gizmo's ``target_set_operator``), the
    menu opens only after the originating ``LEFTMOUSE`` releases. Otherwise
    the still-pressed click flows straight into Blender's drag-through-pick
    gesture and the menu commits whichever item the cursor drifts over on
    release. Other invocation paths (command-palette / F3, EXEC_DEFAULT, F6
    redo) bypass the wait and open the menu immediately.

    The ``value`` StringProperty is declared on this mixin but registered via
    the concrete Operator subclass's MRO scan — do not instantiate the mixin
    standalone."""

    # Carries the picked value through invoke→execute; empty default
    # distinguishes "open popup" from "apply".
    value: bpy.props.StringProperty(default="", options={"HIDDEN", "SKIP_SAVE"})

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        """Open the picker menu, or apply a value that was preset by a
        menu-item click.

        Routing through ``execute()`` keeps subclass IFC-transaction wrapping
        in the loop and means F6 redo / ``EXEC_DEFAULT`` reach the apply path."""
        if self.value:
            return self.execute(context)

        if self._resolve_target(context) is None:
            return {"CANCELLED"}

        if event.value == "PRESS":
            context.window_manager.modal_handler_add(self)
            return {"RUNNING_MODAL"}
        return self._open_picker(context)

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:
        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            self._open_picker(context)
            # INTERFACE does not remove a modal handler; only FINISHED /
            # CANCELLED do.
            return {"CANCELLED"}
        if event.type in {"RIGHTMOUSE", "ESC"}:
            return {"CANCELLED"}
        return {"RUNNING_MODAL"}

    def _open_picker(self, context: bpy.types.Context) -> set[str]:
        bl_idname = self.bl_idname
        values = list(get_args(self.type_literal))

        def draw(menu_self, _menu_context):
            layout = menu_self.layout
            for v in values:
                op = layout.operator(bl_idname, text=v)
                op.value = v

        context.window_manager.popup_menu(draw, title=self.bl_label, icon="MENU_PANEL")
        # The type change is a two-step interaction: this invocation just OPENS
        # the menu (no state change yet); a SECOND invocation fires when the
        # user clicks a menu item — that one writes ``props.<type_attr>`` and
        # returns FINISHED. By returning INTERFACE here (and not FINISHED), the
        # menu-open step is excluded from Blender's undo stack so the user
        # gets exactly ONE undo entry per type change. If we returned FINISHED
        # here too, the stack would gain a no-op "opened the menu" entry that
        # Ctrl+Z would dismiss before reverting the actual type change —
        # confusing UX where the first Ctrl+Z appears to do nothing.
        return {"INTERFACE"}

    def _pick_type(self, context: bpy.types.Context) -> set[str]:
        if not self.value:
            # No-op rather than re-open the menu, so command-palette misuse
            # doesn't infinite-loop.
            return {"CANCELLED"}

        obj = self._resolve_target(context)
        if obj is None:
            return {"CANCELLED"}

        if self.value not in get_args(self.type_literal):
            self.report({"WARNING"}, f"Unknown {self.type_attr}: {self.value!r}")
            return {"CANCELLED"}

        props = self.props_getter(obj)
        setattr(props, self.type_attr, self.value)
        return {"FINISHED"}


class IntegerInputDialogMixin:
    """Operator mixin that mirrors a per-feature ``IntProperty`` on the
    operator into a draft attribute on the active object's parametric props,
    via Blender's ``invoke_props_dialog`` popup.

    Subclasses declare:

    - ``attr_name`` — name of the IntProperty on the subclass AND of the
      attribute on the resolved props (same name on both sides).
    - ``props_getter`` — ``staticmethod(tool.Model.get_<feature>_props)``.
    - ``requires_editing`` — True iff the operator must no-op outside an
      active edit lifecycle. Default False.
    - ``value_min`` — minimum value to clamp to. Default 1."""

    attr_name: ClassVar[str] = ""
    props_getter: ClassVar[Callable[[bpy.types.Object], bpy.types.PropertyGroup]]
    requires_editing: ClassVar[bool] = False
    value_min: ClassVar[int] = 1

    def _resolve_props(self, context: bpy.types.Context) -> bpy.types.PropertyGroup | None:
        """Return the active object's parametric props if the operator is
        allowed to fire, ``None`` otherwise (caller bails with ``CANCELLED``)."""
        obj = context.active_object
        if not obj:
            return None
        props = self.props_getter(obj)
        if self.requires_editing and not props.is_editing:
            return None
        return props

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> set[str]:  # noqa: ARG002
        props = self._resolve_props(context)
        if props is None:
            return {"CANCELLED"}
        setattr(self, self.attr_name, max(self.value_min, getattr(props, self.attr_name)))
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context: bpy.types.Context) -> set[str]:
        props = self._resolve_props(context)
        if props is None:
            return {"CANCELLED"}
        setattr(props, self.attr_name, max(self.value_min, getattr(self, self.attr_name)))
        return {"FINISHED"}


# --- Undo-resync registry ----------------------------------------------------
#
# Per-type regenerators called from ``resync_parametric_drafts_after_undo``
# (wired into ``bim/handler.py:undo_post`` and ``redo_post``) so the preview
# mesh of an in-progress parametric draft repaints after Ctrl+Z / Ctrl+Shift+Z.
#
# Each regenerator is a one-line lazy-import + call. Lazy imports because
# ``bonsai.bim.parametric_lifecycle`` loads before ``bim/module/model/*``
# at addon enable; a module-level import would cycle. Each function-local
# import lands at first call, after the feature module has registered.
#
# Types with no entry — door, window, railing, etc. — are IFC-derived: undo
# of an IFC mutation already restores the entity, and ``switch_representation``
# repaints the mesh as a side effect of the next refresh. They don't need a
# bespoke preview regenerator.


def _wall_undo_regenerator(obj: bpy.types.Object) -> None:
    from bonsai.bim.module.model.wall import regenerate_wall_mesh_from_props

    regenerate_wall_mesh_from_props(obj)


def _stair_undo_regenerator(obj: bpy.types.Object) -> None:
    from bonsai.bim.module.model.stair import regenerate_stair_mesh

    regenerate_stair_mesh(obj)


def _roof_undo_regenerator(obj: bpy.types.Object) -> None:
    from bonsai.bim.module.model.roof import update_roof_modifier_bmesh

    update_roof_modifier_bmesh(obj)


UNDO_REGENERATORS: dict[str, Callable[[bpy.types.Object], None]] = {
    "wall": _wall_undo_regenerator,
    "stair": _stair_undo_regenerator,
    "roof": _roof_undo_regenerator,
}


def resync_parametric_drafts_after_undo() -> None:
    """Re-render preview meshes for every parametric draft currently active.

    Walks all objects, skips any not in a registered parametric edit,
    dispatches to the per-type regenerator in ``UNDO_REGENERATORS``. A type
    without an entry is left alone — its preview is either already correct
    (IFC-derived) or has no draft preview mesh."""
    for obj in bpy.data.objects:
        feature = tool.Parametric.is_object_editing(obj)
        if feature is None:
            continue
        regenerator = UNDO_REGENERATORS.get(feature.name)
        if regenerator is None:
            continue
        regenerator(obj)
    tool.Blender.update_all_viewports()


@persistent
def _resync_on_undo(scene: bpy.types.Scene) -> None:
    resync_parametric_drafts_after_undo()


def install_parametric_lifecycle_handlers() -> None:
    """Append the undo-resync callback to undo_post and redo_post; idempotent.

    Caller must invoke this AFTER appending the central undo/redo handlers so
    regenerators see restored IFC state — bpy.app.handlers fire in append order."""
    for hook in (bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        if _resync_on_undo not in hook:
            hook.append(_resync_on_undo)


def uninstall_parametric_lifecycle_handlers() -> None:
    for hook in (bpy.app.handlers.undo_post, bpy.app.handlers.redo_post):
        try:
            hook.remove(_resync_on_undo)
        except ValueError:
            pass
