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

"""Registration smoke test for :attr:`tool.Parametric.EDIT_TYPES`.

The registry is the single source of truth for which parametric element types
exist. Every consumer (auto-commit on save, finish/cancel chains, the
``PointerProperty`` attachment, the ``GizmoPreferences<X>`` registration) derives
identifiers from each entry's short ``name`` token. Forget any downstream
registration and the silent-desync the framework exists to prevent will ship.

These tests pin the registry-to-runtime contract: for every entry the operator
``bl_idname``s resolve to registered ``bpy.ops.bim.*`` callables, the
``PropertyGroup`` class is attached to ``bpy.types.Object``, and the per-type
predicate exists on :class:`tool.Blender.Modifier`."""

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


def test_every_entry_has_modifier_predicate(registry):
    from bonsai import tool

    missing = [e.name for e in registry if getattr(tool.Blender.Modifier, f"is_{e.name}", None) is None]
    assert not missing, f"tool.Blender.Modifier missing is_<name> predicates: {missing}"


def test_gizmo_preferences_attached_when_class_exists(registry):
    """For every registry entry whose ``GizmoPreferences<Name>`` class exists in
    ``bonsai.bim.ui``, the matching sub-PointerProperty must be attached to
    ``ui.GizmoPreferences`` under the registry entry's ``name`` token.

    Catches the silent-skip behaviour of
    ``Parametric.iter_gizmo_preference_classes``: a typo in the class name
    or a dropped registration would otherwise produce a missing sub-panel at
    runtime with no error. Entries without a ``GizmoPreferences<Name>``
    class are allowed — not every parametric type ships gizmo prefs."""
    from bonsai.bim import ui

    missing = []
    for feature in registry:
        prefs_class_name = f"GizmoPreferences{feature.name.capitalize()}"
        if not hasattr(ui, prefs_class_name):
            continue
        if not hasattr(ui.GizmoPreferences, feature.name):
            missing.append((feature.name, prefs_class_name))
    assert not missing, (
        f"ui.GizmoPreferences missing sub-PointerProperty field(s) for: {missing} — "
        f"each registered ``GizmoPreferences<Name>`` class must have a matching "
        f"``<name>: PointerProperty(type=GizmoPreferences<Name>)`` field on "
        f"``ui.GizmoPreferences``"
    )
