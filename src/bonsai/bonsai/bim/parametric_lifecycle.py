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

"""Shared Enable / Finish / Cancel lifecycle mixins for parametric-edit operators.

Two mixins fit the parametric-edit triads in ``bim/module/model/``:

`FeatureModifierEditMixin`
    Door, Window — BBIM_<Type> pset with nested ``lining_properties`` /
    ``panel_properties``; Finish calls ``update_<type>_modifier_representation``
    via ``ifcopenshell.api.feature``; Cancel restores via ``switch_representation``.

`PathPreservingEditMixin`
    Railing, Roof — BBIM_<Type> pset whose ``path_data`` is preserved through
    edit (only general kwargs are user-editable); Finish calls
    ``update_<type>_modifier_bmesh`` / ``update_<type>_modifier_ifc_data``;
    Cancel re-reads the pset and rebuilds the bmesh preview.

Stair and Wall stay standalone — their lifecycles diverge in ways that don't
fit either mixin without optional escape hatches (Stair has a unique
``update_ifc_stair_props`` post-Finish step + a separate ``get_props_kwargs_for_ifc_export``;
Wall is validation-first, snapshot-driven, no preview regen in operators).

This module sits separately from `bonsai.tool.Parametric` (the registry +
auto-commit) because it imports ``bonsai.tool`` freely, while the registry
itself must stay light — ``tool/blender.py`` consumes the registry at module load."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, ClassVar

import bpy
import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.representation

import bonsai.core.geometry
import bonsai.tool as tool

if TYPE_CHECKING:
    from ifcopenshell import entity_instance


class _ParametricEditMixinBase:
    """Common scaffolding for parametric edit-triad mixins.

    Each per-type subclass provides four hooks:

        ``pset_name``: BBIM_<Type> pset identifier
        ``_is_element_type(element)``: IFC element predicate
        ``_get_props(obj)``: PropertyGroup accessor
        ``_iter_targets(context)``: list of objects to act on (default: ``[active_object]``)

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


class FeatureModifierEditMixin(_ParametricEditMixinBase):
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
        """Hook: call the per-type ``update_<type>_modifier_representation``.

        Door's helper takes ``obj``; window's takes ``context``. The hook lets
        each subclass forward to its existing helper without unifying signatures."""
        raise NotImplementedError

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
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
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            tool.Model.mark_thumbnail_for_update(element_type)
        pset = tool.Pset.get_element_pset(element, cls.pset_name)
        data_text = tool.Ifc.get().createIfcText(json.dumps(data, default=list))
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": data_text})
        # Set only on success: if any IFC op above raised, the user's draft survives for retry.
        props.is_editing = False

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        element, props = resolved
        data = json.loads(ifcopenshell.util.element.get_pset(element, cls.pset_name, "Data"))
        data.update(data.pop("lining_properties"))
        data.update(data.pop("panel_properties"))
        props.set_props_kwargs_from_ifc_data(data)
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=body)
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


class PathPreservingEditMixin(_ParametricEditMixinBase):
    """Lifecycle for railing- and roof-style parametric modifier operators.

    Distinctive: ``path_data`` is part of the BBIM_<Type> pset but is **not**
    user-editable through this triad — it survives the edit untouched, only
    general kwargs are diffed. (Path editing has its own separate operator
    pair, ``Enable/Finish/CancelEditing<Type>Path``, out of scope here.)

    Enable:
        Fetch pset data via ``tool.Model.get_modeling_bbim_pset_data`` → set
        draft props → ``is_editing = True``. The subclass post-load hook
        lets railing JSON-serialise ``path_data`` for the PropertyGroup
        string field.

    Finish:
        Read fresh pset → keep ``path_data`` → gather ``general`` kwargs
        (project units) → reassemble → ``is_editing = False`` → call
        ``_update_pset`` (per-type pset writer) → call ``_update_modifier_ifc_data``
        (per-type geometry commit).

    Cancel:
        Read fresh pset → restore draft props → call
        ``_update_modifier_bmesh`` (per-type bmesh preview) →
        ``is_editing = False``."""

    @classmethod
    def _post_load_data(cls, data: dict) -> dict:
        """Hook: optionally transform the pset data dict after loading and before
        passing to ``set_props_kwargs_from_ifc_data``. Default: pass-through.

        Railing overrides to JSON-serialise ``path_data`` (its
        BIMRailingProperties.path_data is a ``StringProperty`` holding JSON)."""
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
    def _update_modifier_bmesh(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        """Hook: per-type ``update_<type>_modifier_bmesh`` — rebuilds the
        bmesh preview to match the current draft props (used by Cancel)."""
        raise NotImplementedError

    @classmethod
    def _enable_one(cls, obj: bpy.types.Object) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        _element, props = resolved
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
        path_data = pset_data["data_dict"]["path_data"]
        data = props.get_general_kwargs(convert_to_project_units=True)
        data["path_data"] = path_data
        cls._update_pset(element, data)
        cls._update_modifier_ifc_data(obj, context)
        # Set only on success: if any IFC op above raised, the user's draft survives for retry.
        props.is_editing = False

    @classmethod
    def _cancel_one(cls, obj: bpy.types.Object, context: bpy.types.Context) -> None:
        resolved = cls._resolve(obj)
        if resolved is None:
            return
        _element, props = resolved
        data = tool.Model.get_modeling_bbim_pset_data(obj, cls.pset_name)["data_dict"]
        data = cls._post_load_data(data)
        props.set_props_kwargs_from_ifc_data(data)
        cls._update_modifier_bmesh(obj, context)
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
