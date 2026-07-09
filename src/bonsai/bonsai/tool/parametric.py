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

"""Registry and save-time auto-commit for parametric draft edits.

The registry is consumed along two orthogonal axes:

- **Predicate axis**: every entry carries an ``is_<name>`` total predicate. Used
  by ``find_for_element``, save-flow auto-commit, and per-feature gizmo polls.
- **Lifecycle axis**: a subset of entries flagged ``supports_build_edit_lifecycle=True``
  share the ``Enable/Finish/CancelEditing<Type>`` operator shape and are wired
  through ``build_edit_lifecycle``. The remainder declare their edit operators
  directly because their lifecycle (per-attribute diff dispatch, layer-stack
  editing, mid-spline gizmo drag, …) does not fit the shared mixin contract.

Adding a new parametric element type is a single entry in ``EDIT_TYPES``;
flag ``supports_build_edit_lifecycle`` only if the type's edit lifecycle matches
one of the shared mixins in ``bim/parametric_lifecycle.py``."""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar, Optional

import bpy

import bonsai.core.tool
import bonsai.tool as tool

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ifcopenshell import entity_instance


# Lowercase ASCII snake_case token; each segment a non-empty letter/digit
# sequence starting with a letter. ``"pipe_segment"`` → ``"BIMPipeSegmentProperties"``.
_VALID_NAME_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def _camel_case(name: str) -> str:
    return "".join(part.capitalize() for part in name.split("_"))


@dataclass(frozen=True)
class ParametricObject:
    """One parametric element type's draft + enable + finish + cancel edit lifecycle.

    The ``name`` token drives every derived identifier: the
    ``BIM<Name>Properties`` attribute on ``bpy.types.Object``, the
    ``bim.enable_editing_<name>`` / ``bim.finish_editing_<name>`` /
    ``bim.cancel_editing_<name>`` operator ``bl_idname``s, and the
    ``tool.Parametric.is_<name>`` runtime predicate.

    The predicate is part of the contract and MUST be total — accept any IFC
    entity, return a bool, never raise. A raising predicate breaks the save
    path for every parametric type, not just its own.

    ``supports_build_edit_lifecycle`` marks entries whose edit lifecycle fits the
    shared mixin contract (``_enable_targets`` / ``_finish_targets`` /
    ``_cancel_targets``) and that therefore wire their operators through
    ``build_edit_lifecycle``. Entries with bespoke edit lifecycles (per-attribute
    diff dispatch, layer-stack editing, mid-spline gizmo drag) leave this
    False and declare their operator classes directly.

    ``has_default_parameters`` marks entries whose ``BIM<Name>Properties``
    class exposes ``get_general_kwargs`` / ``copy_to`` and a matching
    ``draw_<name>_properties`` UI helper, so the addon-preferences panel can
    surface a per-type defaults section and the create operator can seed new
    instances from the preset. Entries without that machinery leave this False
    and don't appear in the preferences ``Default Parameters`` panel."""

    name: str
    has_non_editable_path: bool = False
    supports_build_edit_lifecycle: bool = False
    has_default_parameters: bool = False

    def __post_init__(self) -> None:
        if not _VALID_NAME_RE.match(self.name):
            raise ValueError(
                f"ParametricObject name {self.name!r} must match "
                f"{_VALID_NAME_RE.pattern!r} — lowercase letters / digits, "
                f"optionally split by single underscores (e.g. ``door`` or "
                f"``pipe_segment``). Leading / trailing underscores and "
                f"consecutive underscores are rejected because they produce "
                f"empty CamelCase segments in derived class names."
            )

    @property
    def props_attr(self) -> str:
        return f"BIM{_camel_case(self.name)}Properties"

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
    class GenerationKeyedCache:
        """A dict-keyed cache stamped with the parametric generation counter
        at fill time. Reads at a later generation drop the whole dict and
        re-run the loader. Any IFC commit bumps the generation, invalidating
        all entries en bloc.

        ``None`` values are stored verbatim; only "key not in dict" counts as
        a miss."""

        def __init__(self) -> None:
            self._gen: int | None = None
            self._data: dict = {}

        def get_or_compute(self, key, loader):
            current = Parametric.get_geom_generation()
            if self._gen != current:
                self._data.clear()
                self._gen = current
            if key not in self._data:
                self._data[key] = loader()
            return self._data[key]

        def clear(self) -> None:
            """Explicit drop. Use from ``load_post`` so a fresh file starts clean."""
            self._data.clear()
            self._gen = None

    EDIT_TYPES: list[ParametricObject] = [
        ParametricObject(
            "door", has_non_editable_path=True, supports_build_edit_lifecycle=True, has_default_parameters=True
        ),
        ParametricObject(
            "window", has_non_editable_path=True, supports_build_edit_lifecycle=True, has_default_parameters=True
        ),
        ParametricObject(
            "stair", has_non_editable_path=True, supports_build_edit_lifecycle=True, has_default_parameters=True
        ),
        ParametricObject("railing", supports_build_edit_lifecycle=True, has_default_parameters=True),
        ParametricObject("roof", supports_build_edit_lifecycle=True, has_default_parameters=True),
        ParametricObject("array", supports_build_edit_lifecycle=True),
        ParametricObject("pipe_segment", supports_build_edit_lifecycle=True),
        ParametricObject("duct_segment", supports_build_edit_lifecycle=True),
        ParametricObject("wall"),
        ParametricObject("slab"),
    ]

    # Annotations for the uppercase constants populated from ``EDIT_TYPES`` by
    # the binding loop at module bottom. Declared here so IDEs and type
    # checkers see the attributes without running the loop.
    DOOR: ClassVar[ParametricObject]
    WINDOW: ClassVar[ParametricObject]
    STAIR: ClassVar[ParametricObject]
    RAILING: ClassVar[ParametricObject]
    ROOF: ClassVar[ParametricObject]
    ARRAY: ClassVar[ParametricObject]
    PIPE_SEGMENT: ClassVar[ParametricObject]
    DUCT_SEGMENT: ClassVar[ParametricObject]
    WALL: ClassVar[ParametricObject]
    SLAB: ClassVar[ParametricObject]

    _geom_generation: int = 0

    @classmethod
    def get_geom_generation(cls) -> int:
        return cls._geom_generation

    @classmethod
    def refresh_post_commit(cls, operator: bpy.types.Operator) -> None:
        """Post-commit hook for ``tool.Ifc.Operator``: bumps the geometry
        generation counter so caches keyed off it drop stale entries on
        the next draw, and tags viewports for redraw.

        Additionally refreshes the BIM Tool header floats for the
        validate-gizmo path — operators whose ``bl_idname`` is the
        ``finish_op`` of an entry in ``EDIT_TYPES``. That is the only
        commit class where selection didn't change but the header
        values displayed did. Other operators skip the refresh: they
        don't target an active-object header edit, and their commit
        context may lack the view-layer attributes the refresh reads."""
        cls._geom_generation += 1
        tool.Blender.update_all_viewports()
        if operator.bl_idname in {feature.finish_op for feature in cls.EDIT_TYPES}:
            import bonsai.bim.handler  # late import: bim.handler imports tool.*

            bonsai.bim.handler.refresh_bim_tool_headers()

    @classmethod
    def find_by_name(cls, name: str) -> Optional[ParametricObject]:
        return next((f for f in cls.EDIT_TYPES if f.name == name), None)

    @classmethod
    def _safe_predicate(cls, feature: ParametricObject, element: entity_instance) -> bool:
        """Resolve and invoke ``is_<feature.name>`` defensively. The contract is
        that predicates are total (see ``ParametricObject`` docstring); a
        regression that turns one predicate raising would otherwise break the
        save path for every parametric type, not just its own."""
        predicate = getattr(cls, f"is_{feature.name}", None)
        if predicate is None:
            return False
        try:
            return bool(predicate(element))
        except Exception:
            logger.warning(
                "parametric predicate is_%s raised on %r",
                feature.name,
                element,
                exc_info=True,
            )
            return False

    @classmethod
    def find_for_element(cls, element: entity_instance) -> Optional[ParametricObject]:
        """Return the registry entry whose IFC type predicate matches ``element``."""
        for feature in cls.EDIT_TYPES:
            if cls._safe_predicate(feature, element):
                return feature
        return None

    @classmethod
    def is_object_editing(cls, obj: bpy.types.Object, skip_name: Optional[str] = None) -> Optional[ParametricObject]:
        """Return the registry entry whose edit lifecycle is active on ``obj``, or None.

        ``skip_name`` excludes one entry from the scan, for callers that want
        to know if a *different* type is editing."""
        for feature in cls.EDIT_TYPES:
            if feature.name == skip_name:
                continue
            if feature.is_editing(obj):
                return feature
        return None

    @classmethod
    def _validated_editing_feature(cls, obj: bpy.types.Object) -> Optional[ParametricObject]:
        """Return the active registry entry on ``obj``, validated against the
        per-type predicate. Returns None when no ``is_editing`` flag is set
        or when the flag is stale.

        Self-heals: a predicate mismatch clears the flag in place so the
        finish dispatch never re-picks up a phantom edit."""
        feature = cls.is_object_editing(obj)
        if feature is None:
            return None
        element = tool.Ifc.get_entity(obj)
        if element is None or not cls._safe_predicate(feature, element):
            getattr(obj, feature.props_attr).is_editing = False
            return None
        return feature

    @classmethod
    def heal_stale_edit_flags(cls) -> None:
        """Validate every scene object's ``is_editing`` flag against the
        per-type predicate, clearing stale flags in place.

        Run from ``load_post`` so a ``.blend`` saved with phantom flags
        (e.g. a save that bypassed the auto-commit flush) is consistent the
        moment it opens."""
        for obj in bpy.data.objects:
            cls._validated_editing_feature(obj)

    @classmethod
    def on_load_post(cls, scene: bpy.types.Scene) -> None:
        """Drain load-transient parametric state on a freshly opened scene
        so no draft edit flag, preview flag, or cache entry persists from
        the saved file."""
        from bonsai.bim.module.model import wall_offset_gizmos
        from bonsai.bim.module.model.preview_base import discard_pending_previews

        cls.heal_stale_edit_flags()
        discard_pending_previews(scene)
        wall_offset_gizmos.clear_caches()

    @classmethod
    def get_pending_edits(cls) -> list[tuple[bpy.types.Object, str]]:
        """``(object, finish_operator_bl_idname)`` pairs for every object
        with an in-progress parametric draft. Stale flags are cleared in
        place and excluded."""
        pending: list[tuple[bpy.types.Object, str]] = []
        for obj in bpy.data.objects:
            feature = cls._validated_editing_feature(obj)
            if feature is not None:
                pending.append((obj, feature.finish_op))
        return pending

    @classmethod
    def run_bim_op(cls, bl_idname: str) -> None:
        """Invoke a ``bim.*`` operator by ``bl_idname``.

        Asserts the operator is a ``tool.Ifc.Operator`` subclass — bypassing
        that wrap would mutate IFC outside Bonsai's transaction system."""
        verb = bl_idname.removeprefix("bim.")
        op_cls = getattr(bpy.types, f"BIM_OT_{verb}", None)
        if op_cls is None or not issubclass(op_cls, tool.Ifc.Operator):
            raise RuntimeError(
                f"{bl_idname!r} must be a registered tool.Ifc.Operator subclass for undo-safe IFC mutation"
            )
        getattr(bpy.ops.bim, verb)()

    @classmethod
    def commit_object_draft(cls, obj: bpy.types.Object, finish_op: str) -> bool:
        """Run ``finish_op`` scoped to ``obj`` alone. Returns False (with
        traceback printed) if the operator raised.

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
                except Exception:
                    logger.warning(
                        "commit of %r via %s failed",
                        obj.name,
                        finish_op,
                        exc_info=True,
                    )
                    return False
        finally:
            view_layer.objects.active = original_active

    @classmethod
    def commit_pending_edits(cls) -> tuple[int, list[bpy.types.Object]]:
        """Run each pending draft's finish operator scoped to its object.

        A per-object failure does not abort the loop — remaining drafts
        still flush, otherwise the auto-commit would ship the exact silent
        desync it exists to prevent."""
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
        """Selection-scoped variant. ``names`` filters which registry entries
        to consider; ``None`` considers every type."""
        committed = 0
        failed: list[bpy.types.Object] = []
        for obj in tool.Blender.get_selected_objects():
            feature = cls._validated_editing_feature(obj)
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
    def _assert_predicates_registered(cls) -> None:
        """Loud at addon-enable if any ``EDIT_TYPES`` entry has no matching
        ``is_<name>`` classmethod. Without this, a typo in the registry entry
        produces a silent-False predicate that never matches — every
        parametric draft of that type bypasses save-flow auto-commit."""
        missing = [feature.name for feature in cls.EDIT_TYPES if not callable(getattr(cls, f"is_{feature.name}", None))]
        if missing:
            raise RuntimeError(
                f"tool.Parametric.EDIT_TYPES has entries with no is_<name> predicate: {missing}. "
                f"Add `is_<name>(cls, element) -> bool` classmethods on tool.Parametric, "
                f"or remove the entries from EDIT_TYPES."
            )

    @classmethod
    def register_object_properties(cls, prop_module) -> None:
        """Attach ``bpy.types.Object.BIM<Name>Properties`` for every registered
        parametric type. Skips entries whose ``PropertyGroup`` is absent."""
        cls._assert_predicates_registered()
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

    # --- Feature-kind predicates ------------------------------------------------
    # One predicate per registered parametric type. Each is total: accepts any
    # IFC entity (or None), returns a bool, never raises. Predicates live with
    # the registry rather than ``tool.Blender.Modifier`` because they ARE the
    # registry contract — ``find_for_element`` and ``_validated_editing_feature``
    # resolve them by name. Coupling them on the same class makes a typo at
    # registration time an immediate AttributeError instead of a silent None
    # predicate that never matches.

    @classmethod
    def is_array(cls, element: entity_instance) -> bool:
        """True if element is the PARENT of a Bonsai parametric array.

        Array children also carry a ``BBIM_Array`` pset (their ``Parent``
        field points back to the original), so checking pset presence alone
        would falsely match them. The parent is distinguished by
        ``pset.Parent == element.GlobalId``."""
        import ifcopenshell.util.element

        if element is None:
            return False
        pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        if not pset:
            return False
        return pset.get("Parent") == element.GlobalId

    @classmethod
    def is_railing(cls, element: entity_instance) -> bool:
        if element is None:
            return False
        return tool.Pset.get_element_pset(element, "BBIM_Railing") is not None

    @classmethod
    def is_roof(cls, element: entity_instance) -> bool:
        if element is None:
            return False
        return tool.Pset.get_element_pset(element, "BBIM_Roof") is not None

    @classmethod
    def is_window(cls, element: entity_instance) -> bool:
        if element is None:
            return False
        return tool.Pset.get_element_pset(element, "BBIM_Window") is not None

    @classmethod
    def is_door(cls, element: entity_instance) -> bool:
        if element is None:
            return False
        return tool.Pset.get_element_pset(element, "BBIM_Door") is not None

    @classmethod
    def is_stair(cls, element: entity_instance) -> bool:
        if element is None:
            return False
        return tool.Pset.get_element_pset(element, "BBIM_Stair") is not None

    @classmethod
    def is_slab(cls, element: entity_instance) -> bool:
        """``True`` for any ``IfcSlab``. The slab edit lifecycle only gates
        the connection-disconnect UI — no IFC mutation — so we don't narrow
        further (e.g. by checking for wall connections). Per-gizmo polls
        layer the "has wall connections" check on top via
        ``tool.Wall.iter_slab_wall_connections``."""
        return element is not None and element.is_a("IfcSlab")

    @classmethod
    def is_wall(cls, element: entity_instance) -> bool:
        """A wall is editable by the parametric gizmo if it is an IfcWall with LAYER2 usage.

        Unlike doors/windows/stairs, walls do not carry a proprietary BBIM_Wall pset —
        their parametric state lives in standard IFC (axis polyline, IfcMaterialLayerSetUsage,
        IfcExtrudedAreaSolid). Any LAYER2 wall qualifies."""
        if element is None or not element.is_a("IfcWall"):
            return False
        return tool.Model.get_usage_type(element) == "LAYER2"

    @classmethod
    def is_path_connectable_wall(cls, element: entity_instance) -> bool:
        """An IfcWall that may participate in IfcRelConnectsPathElements joins —
        either a LAYER2 parametric wall, or a fillet-corner wall whose body is
        hand-built but whose axis still drives path connections.

        Distinct from ``is_wall``: that predicate gates parametric edits that
        would regenerate the body and flatten a curved fillet. Unjoin / join
        gizmo polls and path-connection partner enumeration use this looser
        predicate so fillet corners (which have no LAYER2 usage by spec) still
        surface their join icons."""
        if element is None or not element.is_a("IfcWall"):
            return False
        if tool.Model.get_usage_type(element) == "LAYER2":
            return True
        return cls.is_fillet_corner_wall(element)

    @classmethod
    def is_fillet_corner_wall(cls, element: entity_instance) -> bool:
        """``True`` if the wall carries the ``BBIM_Wall.IsFilletCorner`` flag,
        marking it as a curved corner whose banana body is hand-built rather
        than regenerated from the wall's axis + layer set."""
        import ifcopenshell.util.element

        return bool(ifcopenshell.util.element.get_pset(element, "BBIM_Wall", "IsFilletCorner"))

    @classmethod
    def is_pipe_segment(cls, element: entity_instance) -> bool:
        return element is not None and element.is_a("IfcPipeSegment")

    @classmethod
    def is_duct_segment(cls, element: entity_instance) -> bool:
        return element is not None and element.is_a("IfcDuctSegment")

    @classmethod
    def build_edit_lifecycle(
        cls,
        feature_name: str,
        mixin: type,
        labels: tuple[tuple[str, str], tuple[str, str], tuple[str, str]],
        bl_options: Optional[set[str]] = None,
        enable_extra_props: Optional[dict[str, Any]] = None,
        enable_extra_kwargs: Optional[Callable[[Any], dict[str, Any]]] = None,
        module_name: Optional[str] = None,
    ) -> tuple[type, type, type]:
        """Generate (Enable, Finish, Cancel) operator classes for a parametric type.

        ``mixin`` provides ``_enable_targets`` / ``_finish_targets`` /
        ``_cancel_targets`` (i.e. inherits from ``ParametricEditMixinBase`` or
        a sibling). ``labels`` is ``((enable_label, enable_desc), …)`` in
        Enable / Finish / Cancel order.

        ``bl_idname`` and the Python class name come from the registry entry —
        ``feature_name`` MUST already be in ``EDIT_TYPES``, otherwise a typo
        produces an unregistered operator. Anchoring bl_idnames to the registry
        eliminates the silent-mismatch failure mode where a hand-typed
        ``bl_idname = "bim.enable_editing_dor"`` produces a class that
        ``find_for_element`` never resolves to.

        ``enable_extra_props`` declares extra ``bpy.props.*`` descriptors to
        attach to the Enable class only (e.g. array's ``item: IntProperty``
        carrying the target layer index across redo). When set,
        ``enable_extra_kwargs`` must also be supplied: it receives the Enable
        operator instance and returns a kwargs dict forwarded to
        ``_enable_targets`` so the mixin's enable phase sees the extras.

        ``module_name`` sets ``__module__`` on the generated classes — pass
        ``__name__`` from the calling feature module so Blender's right-click
        → Edit Source resolves to the feature module rather than the factory
        site. Defaults to the factory's module, which is sub-optimal for
        debugging but harmless."""
        import bonsai.tool as _tool  # late import: tool/__init__.py wires this module last

        feature = cls.find_by_name(feature_name)
        if feature is None:
            raise RuntimeError(
                f"build_edit_lifecycle: {feature_name!r} not in EDIT_TYPES — add a "
                f"ParametricObject entry before declaring its operators"
            )
        if not feature.supports_build_edit_lifecycle:
            raise RuntimeError(
                f"build_edit_lifecycle: {feature_name!r} has supports_build_edit_lifecycle=False — "
                f"its edit lifecycle is bespoke. Either declare "
                f"Enable/Finish/CancelEditing{_camel_case(feature_name)} as direct Operator "
                f"subclasses, or flip the flag on the EDIT_TYPES entry if the type does fit "
                f"the shared mixin contract."
            )
        if (enable_extra_props is None) != (enable_extra_kwargs is None):
            raise RuntimeError(
                f"build_edit_lifecycle({feature_name!r}): enable_extra_props and "
                f"enable_extra_kwargs must be supplied together — extras with no "
                f"kwargs builder are unreachable, kwargs with no extras have nothing to forward"
            )
        options = bl_options if bl_options is not None else {"REGISTER", "UNDO"}
        base_classes = (mixin, bpy.types.Operator, _tool.Ifc.Operator)
        capitalised = _camel_case(feature_name)

        def _build(
            action: str, bl_idname: str, label: str, desc: str, target_method: str, extras: Optional[dict]
        ) -> type:
            if extras and target_method == "_enable_targets":
                assert enable_extra_kwargs is not None
                kwargs_builder = enable_extra_kwargs

                def _execute(self, context: bpy.types.Context) -> set[str]:
                    return getattr(self, target_method)(context, **kwargs_builder(self))

            else:

                def _execute(self, context: bpy.types.Context) -> set[str]:
                    return getattr(self, target_method)(context)

            attrs: dict[str, Any] = {
                "bl_idname": bl_idname,
                "bl_label": label,
                "bl_description": desc,
                "bl_options": options,
                "_execute": _execute,
            }
            if module_name is not None:
                attrs["__module__"] = module_name
            if extras:
                # Blender's PropertyGroup machinery reads __annotations__ for bpy.props descriptors.
                attrs["__annotations__"] = dict(extras)
            return type(f"{action}Editing{capitalised}", base_classes, attrs)

        return (
            _build("Enable", feature.enable_op, labels[0][0], labels[0][1], "_enable_targets", enable_extra_props),
            _build("Finish", feature.finish_op, labels[1][0], labels[1][1], "_finish_targets", None),
            _build("Cancel", feature.cancel_op, labels[2][0], labels[2][1], "_cancel_targets", None),
        )


_edit_type_names = [entry.name for entry in Parametric.EDIT_TYPES]
if len(set(_edit_type_names)) != len(_edit_type_names):
    raise RuntimeError(
        f"EDIT_TYPES name collision: {_edit_type_names}. Each name is the primary key "
        f"for derived bl_idnames, BIM<Name>Properties attributes, is_<name> predicates, "
        f"and the uppercase constant — a duplicate silently shadows the first entry."
    )
del _edit_type_names

# Bind every registered ParametricObject as an uppercase class attribute so
# call sites can reference ``tool.Parametric.ROOF`` directly. Renaming a
# registry entry renames the constant; a typo at the call site surfaces as
# AttributeError at module load.
for _entry in Parametric.EDIT_TYPES:
    setattr(Parametric, _entry.name.upper(), _entry)
del _entry
