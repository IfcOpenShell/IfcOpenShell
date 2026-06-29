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

"""Registration smoke test for `tool.Parametric.EDIT_TYPES`.

The registry is the single source of truth for which parametric element types
exist. Every consumer (auto-commit on save, finish/cancel chains, the
``PointerProperty`` attachment, the ``GizmoPreferences`` per-feature toggle)
derives identifiers from each entry's short ``name`` token. Forget any
downstream registration and the silent-desync the framework exists to prevent
will ship.

These tests pin the registry-to-runtime contract: for every entry the operator
``bl_idname``s resolve to registered ``bpy.ops.bim.*`` callables, the
``PropertyGroup`` class is attached to ``bpy.types.Object``, and the per-type
predicate exists on `tool.Parametric`."""

import types

import bpy
import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    if not isinstance(bpy, types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


@pytest.fixture
def registry():
    from bonsai import tool

    return tool.Parametric.EDIT_TYPES


def test_registry_is_non_empty(registry):
    assert len(registry) >= 1


def test_every_entry_has_enable_op_registered(registry):
    missing = [e.enable_op for e in registry if not hasattr(bpy.ops.bim, e.enable_op.removeprefix("bim."))]
    assert not missing, f"Missing enable operators: {missing}"


def test_every_entry_has_finish_op_registered(registry):
    missing = [e.finish_op for e in registry if not hasattr(bpy.ops.bim, e.finish_op.removeprefix("bim."))]
    assert not missing, f"Missing finish operators: {missing}"


def test_every_entry_has_cancel_op_registered(registry):
    missing = [e.cancel_op for e in registry if not hasattr(bpy.ops.bim, e.cancel_op.removeprefix("bim."))]
    assert not missing, f"Missing cancel operators: {missing}"


def test_every_entry_has_property_group_attached(registry):
    # ``register_object_properties`` runs at addon enable; if any entry's
    # PropertyGroup class is missing on prop module the attribute is skipped.
    missing = [e.props_attr for e in registry if not hasattr(bpy.types.Object, e.props_attr)]
    assert not missing, (
        f"bpy.types.Object missing attributes: {missing} — "
        f"verify the matching PropertyGroup classes exist in bim.module.model.prop"
    )


def test_every_entry_has_parametric_predicate(registry):
    from bonsai import tool

    missing = [e.name for e in registry if getattr(tool.Parametric, f"is_{e.name}", None) is None]
    assert not missing, f"tool.Parametric missing is_<name> predicates: {missing}"


def test_every_predicate_does_not_raise_on_non_matching_element(registry):
    """Each ``is_<name>`` predicate must be **total**: accept any IFC entity
    and return a truthy/falsy value, never raise.

    The registry iterates every predicate against the active IFC element on
    save; a raising predicate (e.g. ``AttributeError`` from a missing pset
    accessor when handed a non-matching element type) propagates upward and
    breaks the save path for *all* parametric types, not just its own.
    This test probes each predicate with an ``IfcAnnotation`` (an element
    that carries none of the BBIM_<Type> psets the predicates look up) and
    asserts the call does not raise. Falsy returns are acceptable — the
    registry treats them as 'no match'. What's forbidden is raising."""
    import ifcopenshell

    from bonsai import tool

    probe = ifcopenshell.file(schema="IFC4").create_entity("IfcAnnotation")

    raised = []
    for feature in registry:
        predicate = getattr(tool.Parametric, f"is_{feature.name}", None)
        if predicate is None:
            continue
        try:
            predicate(probe)
        except Exception as e:
            raised.append((feature.name, type(e).__name__, str(e)))
    assert not raised, (
        f"is_<name> predicates raised on a non-matching IfcAnnotation: {raised}. "
        f"Predicates must be total — return bool, never raise. Add an "
        f"`if not element.is_a('IfcXxx'): return False` short-circuit or guard the pset lookup."
    )


def test_default_parameters_field_per_registry_entry_with_defaults(registry):
    """Every entry flagged ``has_default_parameters=True`` must have a matching
    ``<name>: PointerProperty`` field on ``ui.DefaultParameters`` pointing at
    its ``BIM<Name>Properties`` class.

    The addon-preferences ``Default Parameters`` panel iterates flagged entries
    to render per-type defaults sections, and the matching create operator
    (``bim.add_door``, ``bim.add_window``, …) reads the field to seed new
    instances from the user's preset values. A missing field means the preset
    silently never reaches the operator.

    Entries WITHOUT the flag are not required to appear — the contract is
    one-directional: ``has_default_parameters=True`` implies a field, but
    ``False`` allows absence."""
    from bonsai.bim import ui

    annotations = getattr(ui.DefaultParameters, "__annotations__", {})
    missing = [e.name for e in registry if e.has_default_parameters and e.name not in annotations]
    assert not missing, (
        f"ui.DefaultParameters missing PointerProperty field(s) for: {missing} — "
        f"each EDIT_TYPES entry with has_default_parameters=True must have a matching "
        f"<name>: PointerProperty(type=BIM<Name>Properties) field"
    )


def test_gizmo_preferences_field_per_registry_entry(registry):
    """Every registry entry must have a matching ``<name>: BoolProperty`` field
    on ``ui.GizmoPreferences`` so the addon-preferences UI auto-renders a
    toggle for it and ``BaseParametricGizmoGroup.poll`` can gate the whole
    gizmo group on ``prefs.gizmos.<name>``.

    Checks ``__annotations__`` rather than ``hasattr`` because Blender's
    PropertyGroup syntax (``field: bpy.props.BoolProperty(...)``) is an
    annotation-only assignment — the attribute only materialises on the
    class after Blender's metaclass installs the bpy_struct descriptor,
    which depends on registration timing. Reading ``__annotations__``
    pins the source-level contract independently of when register() ran."""
    from bonsai.bim import ui

    annotations = getattr(ui.GizmoPreferences, "__annotations__", {})
    missing = [feature.name for feature in registry if feature.name not in annotations]
    assert not missing, (
        f"ui.GizmoPreferences missing BoolProperty field(s) for: {missing} — "
        f"each registry entry must have a matching ``<name>: BoolProperty(...)`` "
        f"field on ``ui.GizmoPreferences`` so the preferences UI surfaces a toggle"
    )
