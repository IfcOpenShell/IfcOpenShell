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

"""Registry + save-time auto-commit for parametric draft edits.

Single source of truth: adding a new parametric element type is one entry in
`Parametric.EDIT_TYPES`. Every consumer — save-time auto-commit, the
finish/cancel chains in ``tool.Blender.Modifier``, the ``PointerProperty``
attachment in ``bim/module/model/__init__.py``, and the per-type
``GizmoPreferences<X>`` registration in ``bim/__init__.py`` — derives the
class names, operator ``bl_idname``s, and predicates from the registry entry's
short ``name`` token.

Lives in ``tool/`` so both ``tool/`` (e.g. ``tool/blender.py``) and ``bim/``
modules can consume it without crossing the layer boundary. The orchestration
helpers (``commit_object_draft``, ``commit_pending_edits``) call
``bpy.ops.bim.*`` operators by name, which is runtime dispatch through Blender
rather than a Python import of ``bim/``.

----------------------------------------------------------------------
How to add a new parametric object
----------------------------------------------------------------------

End-to-end walkthrough for wiring a new IFC element type (e.g. ``IfcSlab``)
into the gizmo-driven parametric edit framework. Numbered steps are
**required** unless flagged OPTIONAL. Keep this section in sync with the
implementation files it references — if a step's example code stops matching
the real registration site, the step is out of date.

STEP 1 — Add the registry entry (this file)
    Append to `Parametric.EDIT_TYPES`::

        ParametricObject("slab", has_non_editable_path=False),

    The ``name`` token drives every derived identifier:
    ``BIMSlabProperties``, ``bim.enable_editing_slab`` /
    ``bim.finish_editing_slab`` / ``bim.cancel_editing_slab``, and the
    ``slab`` field on ``GizmoPreferences``. Set ``has_non_editable_path=True``
    if the modifier exposes no user-editable path (cf. door, window, stair).

STEP 2 — Define the ``PropertyGroup`` (``bim/module/model/prop.py``)
    Class name **must** be ``BIM<Name>Properties`` — capitalisation matches
    `ParametricObject.props_attr`::

        class BIMSlabProperties(bpy.types.PropertyGroup):
            is_editing: BoolProperty(...)
            # ... per-type draft fields, snapshots, mesh_dirty, etc. ...

    The ``is_editing`` flag is the single field every consumer of the registry
    expects.

STEP 3 — Register the PropertyGroup class
    Add it to the ``classes`` tuple in ``bim/module/model/__init__.py`` (near
    the existing ``prop.BIM<X>Properties`` entries). The
    ``bpy.types.Object.BIMSlabProperties`` attachment is automatic —
    `Parametric.register_object_properties` loops the registry.

STEP 4 — Implement the Enable / Finish / Cancel triad
    In ``bim/module/model/slab.py``, define three ``bpy.types.Operator``
    subclasses with the canonical ``bl_idname``\\s:

        - ``EnableEditingSlab``  → ``bl_idname = "bim.enable_editing_slab"``
        - ``FinishEditingSlab``  → ``bl_idname = "bim.finish_editing_slab"``
        - ``CancelEditingSlab``  → ``bl_idname = "bim.cancel_editing_slab"``

    **First, check if your new type fits one of the existing lifecycle
    shapes** in `bonsai.bim.parametric_lifecycle`. If it does, inherit
    the matching mixin and the triad collapses to ~25 lines total:

        - ``FeatureModifierEditMixin`` — BBIM_<Type> pset with nested
          ``lining_properties`` / ``panel_properties``; Finish via
          ``update_<type>_modifier_representation`` →
          ``ifcopenshell.api.feature``; Cancel via
          ``switch_representation`` to the Body rep. Reference samples:
          door (multi-object) and window (single-object).

        - ``PathPreservingEditMixin`` — BBIM_<Type> pset whose ``path_data``
          is preserved through edit; Finish via per-type
          ``update_bbim_<type>_pset`` + ``update_<type>_modifier_ifc_data``;
          Cancel rebuilds the bmesh preview. Reference samples: railing, roof.

    If neither shape fits (the type needs validation-first lifecycle, an
    explicit snapshot, delegate-to-sub-operators Finish, or a unique
    post-Finish step) implement the triad standalone — see ``wall.py``
    (validation/snapshot/delegate) or ``stair.py`` (raw pset JSON +
    ``update_ifc_stair_props``) as references. Register all three in the
    module's ``classes`` tuple.

STEP 5 — Implement the gizmo group (same file)
    Subclass ``BaseParametricGizmoGroup`` from
    ``bim/module/drawing/gizmos.py``::

        class GizmoSlabEdition(bpy.types.GizmoGroup, BaseParametricGizmoGroup):
            bl_idname = "OBJECT_GGT_bim_slab_edition"

            @classmethod
            def is_element_type(cls, element):
                return tool.Blender.Modifier.is_slab(element)

            dimension_gizmo_props = [DimensionGizmoConfig(...)]

    Register it in the ``classes`` tuple. The classmethod makes
    ``tool.Blender.Modifier.is_slab(element)`` testable via the gizmo's
    ``poll()``.

STEP 6 — Add the element-type predicate (``tool/blender.py``)
    Inside the ``Blender.Modifier`` class, alongside ``is_door`` / ``is_wall``::

        @classmethod
        def is_slab(cls, element: entity_instance) -> bool:
            return tool.Pset.get_element_pset(element, "BBIM_Slab")

    The method name **must** be ``is_<name>`` to match
    `ParametricObject.name` — `Parametric.find_for_element`
    looks it up by string.

STEP 7 — OPTIONAL: typed property accessor (``tool/model.py``)
    Convenience helper for call sites that statically know the IFC type::

        @classmethod
        def get_slab_props(cls, obj) -> BIMSlabProperties:
            return obj.BIMSlabProperties

    Call sites that work generically (registry-driven) can use
    ``getattr(obj, feature.props_attr)`` directly and skip this step.

STEP 8 — OPTIONAL: gizmo visibility preferences (``bim/ui.py``)
    For per-gizmo show/hide toggles, define::

        class GizmoPreferencesSlab(bpy.types.PropertyGroup):
            length: BoolProperty(name="Length", default=True, ...)
            # ... one BoolProperty per gizmo ...

    Then add a matching field on ``GizmoPreferences``::

        slab: bpy.props.PointerProperty(type=GizmoPreferencesSlab)

    Do **not** add ``GizmoPreferencesSlab`` to the ``classes`` list in
    ``bim/__init__.py`` — the registry-driven discovery in this module finds
    it by name (``GizmoPreferences`` + capitalised registry token) and
    registers it automatically.

STEP 9 — OPTIONAL: pure geometry helpers (``core/model.py``)
    Per-type math (collinearity checks, slope/displacement conversions,
    intersection helpers) lives here. The hard rule: no ``bpy`` /
    ``ifcopenshell`` imports at module load — wrap them in
    ``if TYPE_CHECKING:`` blocks only. Lets the helpers be unit-tested
    headless via ``pytest test/core/``.

STEP 10 — Verify
    From ``src/bonsai/``::

        ruff check .
        black --check .
        pytest test/core/ -x -q
        blender -b -P runpytest.py -- test/bim/ -x -q -m model

    The Blender-backed lane runs a registry smoke test that iterates the
    EDIT_TYPES list and asserts each entry's enable/finish/cancel operator
    resolves to a registered ``bpy.ops.bim.*``, that ``bpy.types.Object``
    carries the matching ``BIM<Name>Properties`` attribute, and that the
    ``is_<name>`` predicate exists on ``tool.Blender.Modifier``. Forget any
    of the steps above and that test fails with a precise pointer at
    what's missing.

    Then manually in Blender:

    1. Enable Bonsai → create an instance of the new IFC type.
    2. Run ``bim.enable_editing_<name>`` → confirm the gizmo group polls in
       and the dimension handles appear.
    3. Modify a draft field, save the file → confirm auto-commit fires
       (watch the console for the ``parametric_commit`` log line).
    4. Disable + re-enable the addon → no ``bpy_struct: unknown property
       type`` errors in the console (validates the register/unregister
       symmetry driven by the registry)."""

from __future__ import annotations

import re
import traceback
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

import bpy

import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from ifcopenshell import entity_instance


# ``name`` must be a single ASCII lowercase token starting with a letter:
# ``str.capitalize()`` only handles single-word names cleanly, so a compound
# token like ``"curtain_wall"`` would derive ``"BIMCurtain_wallProperties"`` —
# off the Bonsai naming convention and silently broken.
_VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9]*$")


@dataclass(frozen=True)
class ParametricObject:
    """One parametric element type's draft + enable + finish + cancel triad.

    The short ``name`` token ("door", "window", "stair", "railing", "roof",
    "wall", …) drives every derived identifier: the ``BIM<Name>Properties``
    attribute on ``bpy.types.Object`` and the ``bim.enable_editing_<name>`` /
    ``bim.finish_editing_<name>`` / ``bim.cancel_editing_<name>`` operator
    ``bl_idname``s. The ``name`` is validated at construction time — a
    multi-word IFC type would silently mis-derive through
    ``str.capitalize()`` and breaks the single-token assumption.

    ``has_non_editable_path`` flags element types whose modifier exposes no
    user-editable path (door, window, stair).

    The paired runtime predicate ``tool.Blender.Modifier.is_<name>(element)``
    is part of the registry contract: it MUST be **total** — accept any
    IFC entity and return a boolean, never raise. The registry iterates
    every predicate against the active element on save; a raising predicate
    propagates upward and breaks the save path for *all* parametric types,
    not just its own."""

    name: str
    has_non_editable_path: bool = False

    def __post_init__(self) -> None:
        if not _VALID_NAME_RE.match(self.name):
            raise ValueError(
                f"ParametricObject name {self.name!r} must be a single ASCII lowercase "
                f"token matching {_VALID_NAME_RE.pattern!r}. ``str.capitalize()`` only "
                f"handles single-word names — compound IFC types need an explicit "
                f"naming override (not yet supported)."
            )

    @property
    def props_attr(self) -> str:
        return f"BIM{self.name.capitalize()}Properties"

    @property
    def enable_op(self) -> str:
        return f"bim.enable_editing_{self.name}"

    @property
    def finish_op(self) -> str:
        return f"bim.finish_editing_{self.name}"

    @property
    def cancel_op(self) -> str:
        return f"bim.cancel_editing_{self.name}"

    def is_editing(self, obj: bpy.types.Object) -> bool:
        props = getattr(obj, self.props_attr, None)
        return bool(props and getattr(props, "is_editing", False))


class Parametric(bonsai.core.tool.Parametric):
    EDIT_TYPES: list[ParametricObject] = [
        ParametricObject("door", has_non_editable_path=True),
        ParametricObject("window", has_non_editable_path=True),
        ParametricObject("stair", has_non_editable_path=True),
        ParametricObject("railing"),
        ParametricObject("roof"),
        ParametricObject("wall"),
    ]

    _geom_generation: int = 0

    @classmethod
    def get_geom_generation(cls) -> int:
        return cls._geom_generation

    @classmethod
    def refresh_post_commit(cls) -> None:
        """Post-commit hook for ``tool.Ifc.Operator``: re-syncs scene-level
        ``BIMModelProperties`` (workspace tool header H/L/A fields) from current
        IFC state and bumps the geometry generation counter so per-gizmo-group
        caches keyed off it drop their stale entries on the next draw.

        Why this exists: ``update_bim_tool_props`` was historically only wired
        to the active-object msgbus, so in-place IFC mutations on the current
        selection (S_E, C_E, change_extrusion_*, …) left the header showing
        stale values until the user changed selection. Same shape of bug for
        the wall gizmo cache: ``GizmoGroup.refresh()`` only fires on Blender's
        own state-change events, not on every ``bpy.ops.bim.*`` mutation.

        Cheap when nothing parametric is active — ``update_bim_tool_props``
        early-returns when no Bonsai workspace tool is selected or the active
        object isn't an IFC element."""
        import bonsai.bim.handler  # late import: bim.handler imports tool.*

        cls._geom_generation += 1
        bonsai.bim.handler.update_bim_tool_props()
        screen = getattr(bpy.context, "screen", None)
        if screen is not None:
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    area.tag_redraw()

    @classmethod
    def find_by_name(cls, name: str) -> Optional[ParametricObject]:
        return next((f for f in cls.EDIT_TYPES if f.name == name), None)

    @classmethod
    def find_for_element(cls, element: entity_instance) -> Optional[ParametricObject]:
        """Return the registry entry whose IFC type predicate matches ``element``.

        The per-type predicate lives at ``tool.Blender.Modifier.is_<name>``;
        resolved here by attribute lookup at call time, which avoids a
        ``tool.parametric`` ↔ ``tool.blender`` import cycle."""
        for feature in cls.EDIT_TYPES:
            predicate = getattr(tool.Blender.Modifier, f"is_{feature.name}", None)
            if predicate is not None and predicate(element):
                return feature
        return None

    @classmethod
    def is_object_editing(cls, obj: bpy.types.Object) -> Optional[ParametricObject]:
        for feature in cls.EDIT_TYPES:
            if feature.is_editing(obj):
                return feature
        return None

    @classmethod
    def get_pending_edits(cls) -> list[tuple[bpy.types.Object, str]]:
        """``(object, finish_operator_bl_idname)`` pairs for every object with
        an in-progress parametric draft. The first registry match per object wins."""
        return [(obj, feature.finish_op) for obj in bpy.data.objects if (feature := cls.is_object_editing(obj))]

    @classmethod
    def run_bim_op(cls, bl_idname: str) -> None:
        """Invoke a ``bim.*`` operator by its ``bl_idname``.

        Constraint enforced via ``assert``: the operator MUST be a
        ``tool.Ifc.Operator`` subclass — its transaction wrap is what
        makes the IFC mutation undo-aware. Direct ``bpy.ops.bim.*`` invocation
        of a non-``Ifc.Operator`` would mutate IFC outside Bonsai's
        transaction system."""
        verb = bl_idname.removeprefix("bim.")
        op_cls = getattr(bpy.types, f"BIM_OT_{verb}", None)
        assert op_cls is not None and issubclass(
            op_cls, tool.Ifc.Operator
        ), f"{bl_idname!r} must be a registered tool.Ifc.Operator subclass for undo-safe IFC mutation"
        getattr(bpy.ops.bim, verb)()

    @classmethod
    def commit_object_draft(cls, obj: bpy.types.Object, finish_op: str) -> bool:
        """Run ``finish_op`` scoped to ``obj`` alone. Returns True on success, False if
        the operator raised (with traceback printed to the console).

        Both ``temp_override`` and ``view_layer.objects.active`` are set:
        ``temp_override`` does not rebind ``objects.active``, and some finish
        operators read it directly."""
        view_layer = bpy.context.view_layer
        original_active = view_layer.objects.active
        try:
            with bpy.context.temp_override(active_object=obj, selected_objects=[obj]):
                view_layer.objects.active = obj
                try:
                    cls.run_bim_op(finish_op)
                    return True
                except Exception as e:
                    print(f"Bonsai: commit of {obj.name!r} via {finish_op} failed: {e}")
                    traceback.print_exc()
                    return False
        finally:
            view_layer.objects.active = original_active

    @classmethod
    def commit_pending_edits(cls) -> tuple[int, list[bpy.types.Object]]:
        """Run each pending draft's finish operator scoped to its object.

        A per-object failure does not abort the loop — remaining drafts still
        flush, otherwise the auto-commit would ship the exact silent-desync
        it exists to prevent.

        Each finish op wraps its own IFC transaction, so N pending drafts
        produce N+1 undo entries (one per commit, plus the save). Ctrl+Z
        walks back through commits individually — intentional, each commit
        is reversible on its own."""
        committed = 0
        failed: list[bpy.types.Object] = []
        for obj, finish_op in cls.get_pending_edits():
            if cls.commit_object_draft(obj, finish_op):
                committed += 1
            else:
                failed.append(obj)
        return committed, failed

    @classmethod
    def commit_pending_edits_for_selection(
        cls, names: Optional[tuple[str, ...]] = None
    ) -> tuple[int, list[bpy.types.Object]]:
        """Selection-scoped variant of `commit_pending_edits`. ``names``
        filters which registry entries to consider — e.g. ``("wall",)`` to commit
        only wall drafts among selected objects; ``None`` considers every type.

        Used by multi-object operators (``bim.unjoin_walls``, ``bim.merge_wall``,
        ``bim.extend_walls_to_wall`` etc.) that must run against committed IFC
        state — running them with a wall whose draft hasn't been flushed leaves
        stale gizmos pointing at obsolete IFC numbers."""
        committed = 0
        failed: list[bpy.types.Object] = []
        for obj in tool.Blender.get_selected_objects():
            feature = cls.is_object_editing(obj)
            if feature is None:
                continue
            if names is not None and feature.name not in names:
                continue
            if cls.commit_object_draft(obj, feature.finish_op):
                committed += 1
            else:
                failed.append(obj)
        return committed, failed

    @classmethod
    def register_object_properties(cls, prop_module) -> None:
        """Attach ``bpy.types.Object.BIM<Name>Properties`` for every registered
        parametric type, looking up the matching ``PropertyGroup`` class on
        ``prop_module``. Skips entries whose ``PropertyGroup`` class is absent."""
        for feature in cls.EDIT_TYPES:
            prop_cls = getattr(prop_module, feature.props_attr, None)
            if prop_cls is None:
                continue
            setattr(bpy.types.Object, feature.props_attr, bpy.props.PointerProperty(type=prop_cls))

    @classmethod
    def unregister_object_properties(cls) -> None:
        for feature in cls.EDIT_TYPES:
            if hasattr(bpy.types.Object, feature.props_attr):
                delattr(bpy.types.Object, feature.props_attr)

    @classmethod
    def iter_gizmo_preference_classes(cls, ui_module) -> list[type]:
        """``GizmoPreferences<Name>`` classes that exist on ``ui_module`` for
        every registry entry. Order matches `EDIT_TYPES`. Used by
        ``bim/__init__.py`` to inject the per-type ``GizmoPreferences<X>``
        classes at the correct point — before ``ui.GizmoPreferences``, which
        references them via ``PointerProperty``."""
        out: list[type] = []
        for feature in cls.EDIT_TYPES:
            gpref = getattr(ui_module, f"GizmoPreferences{feature.name.capitalize()}", None)
            if gpref is not None:
                out.append(gpref)
        return out
