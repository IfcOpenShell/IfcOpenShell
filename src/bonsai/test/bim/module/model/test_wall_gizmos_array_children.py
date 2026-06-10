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

"""Behaviour contract: wall topology gizmos and operators reject any
selection that contains a Bonsai array child. Discovers gated gizmo
groups and guarded operators by source inspection so additions inherit
the rule automatically."""

from types import SimpleNamespace
from unittest.mock import patch

import bpy
import pytest

pytestmark = pytest.mark.model


def _wall_gizmo_groups_using_gate():
    """Wall-module ``bpy.types.GizmoGroup`` subclasses whose ``poll`` calls
    ``_wall_topology_gizmo_poll_gate``. Discovered by source inspection so
    the test tracks the gate's user set as the module grows."""
    import inspect

    from bonsai.bim.module.model import wall as wall_mod

    out = []
    for name in dir(wall_mod):
        obj = getattr(wall_mod, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, bpy.types.GizmoGroup) or obj is bpy.types.GizmoGroup:
            continue
        if obj.__module__ != wall_mod.__name__:
            continue
        poll = obj.__dict__.get("poll")
        if poll is None:
            continue
        try:
            src = inspect.getsource(poll)
        except (OSError, TypeError):
            continue
        if "_wall_topology_gizmo_poll_gate" not in src:
            continue
        out.append((name, obj))
    return out


def _wall_operators_with_array_child_guard():
    """Wall-module ``bpy.types.Operator`` subclasses whose ``poll`` rejects
    array-child selections, either by referencing the central predicate
    directly or by routing through the shared ``_poll_reject_array_children``
    helper that wraps it. The operator-level guard is defence in depth
    against keymap / F3 paths that bypass the gizmo entirely."""
    import inspect

    from bonsai.bim.module.model import wall as wall_mod

    out = []
    for name in dir(wall_mod):
        obj = getattr(wall_mod, name)
        if not isinstance(obj, type):
            continue
        if not issubclass(obj, bpy.types.Operator) or obj is bpy.types.Operator:
            continue
        if obj.__module__ != wall_mod.__name__:
            continue
        poll = obj.__dict__.get("poll")
        if poll is None:
            continue
        try:
            src = inspect.getsource(poll)
        except (OSError, TypeError):
            continue
        if "any_selected_is_array_child" not in src and "_poll_reject_array_children" not in src:
            continue
        out.append((name, obj))
    return out


class TestWallGizmoGroupsHideOnArrayChildSelection:
    def test_discovery_finds_wall_multi_object_gizmo_groups(self):
        groups = _wall_gizmo_groups_using_gate()
        assert groups, (
            "Expected at least one wall GizmoGroup whose poll calls "
            "_wall_gizmo_poll_gate — discovery walk drifted out of sync?"
        )

    def test_every_gated_wall_gizmo_hides_when_any_selection_is_array_child(self):
        """Mocks the central ``any_selected_is_array_child`` predicate to True
        and asserts every gizmo whose poll routes through
        ``_wall_gizmo_poll_gate`` returns False. The point is the BEHAVIOUR:
        a child wall in the selection must never surface a topology gizmo,
        regardless of which gate function the poll calls internally."""
        groups = _wall_gizmo_groups_using_gate()
        offenders = []
        with patch("bonsai.tool.Blender.are_viewport_gizmos_enabled", return_value=True):
            with patch("bonsai.bim.module.model.preview_base.any_preview_active", return_value=False):
                with patch(
                    "bonsai.tool.Blender.Modifier.any_selected_is_array_child",
                    return_value=True,
                ):
                    for name, cls in groups:
                        try:
                            result = cls.poll(bpy.context)
                        except Exception as exc:  # noqa: BLE001
                            offenders.append((name, f"poll raised: {type(exc).__name__}: {exc}"))
                            continue
                        if result:
                            offenders.append((name, "poll returned True with array child selected"))

        assert not offenders, (
            "Wall gizmo polls that surface on array-child selections: "
            + ", ".join(f"{n} — {why}" for n, why in offenders)
            + ". Route the poll through _wall_topology_gizmo_poll_gate so the "
            "central any_selected_is_array_child filter applies."
        )


class TestWallOperatorsRejectArrayChildSelection:
    def test_discovery_finds_wall_topology_operators(self):
        ops = _wall_operators_with_array_child_guard()
        assert ops, (
            "Expected at least one wall Operator whose poll rejects array-child "
            "selections (via any_selected_is_array_child or _poll_reject_array_children) "
            "— discovery walk drifted out of sync?"
        )

    def test_every_guarded_wall_operator_polls_false_on_array_child_selection(self):
        """Operators reachable from keymaps / F3 must reject array-child
        invocation independently of the gizmo gating, because not every
        invocation path goes through a gizmo. The shared predicate makes
        this a one-line guard per operator; this test pins it for every
        operator that opted in."""
        ops = _wall_operators_with_array_child_guard()
        offenders = []
        with patch(
            "bonsai.tool.Blender.Modifier.any_selected_is_array_child",
            return_value=True,
        ):
            with patch("bonsai.tool.Model.has_selected_ifc_objects", return_value=True):
                with patch("bonsai.tool.Model.get_selected_ifc_objects", return_value=[]):
                    for name, cls in ops:
                        try:
                            result = cls.poll(bpy.context)
                        except Exception as exc:  # noqa: BLE001
                            offenders.append((name, f"poll raised: {type(exc).__name__}: {exc}"))
                            continue
                        if result:
                            offenders.append((name, "poll returned True with array child selected"))

        assert not offenders, (
            "Wall topology operators that accept array-child selections: "
            + ", ".join(f"{n} — {why}" for n, why in offenders)
            + ". Route the poll through `_poll_reject_array_children(cls)` (the "
            "shared helper that sets the standard poll message and reuses the "
            "central `any_selected_is_array_child` predicate)."
        )


class TestAnySelectedIsArrayChildHelper:
    """Smoke checks on the central predicate. Returns ``False`` when nothing
    is selected; returns ``True`` when at least one selected element passes
    ``is_array_child``."""

    def test_returns_false_with_empty_selection(self):
        from bonsai import tool

        with patch.object(tool.Blender, "get_selected_objects", return_value=[]):
            assert tool.Blender.Modifier.any_selected_is_array_child() is False

    def test_returns_true_when_any_selected_passes_predicate(self):
        from bonsai import tool

        child_obj, child_element = SimpleNamespace(name="child"), object()
        parent_obj, parent_element = SimpleNamespace(name="parent"), object()

        def get_entity(obj):
            return {id(child_obj): child_element, id(parent_obj): parent_element}.get(id(obj))

        def is_array_child(element):
            return element is child_element

        with patch.object(tool.Blender, "get_selected_objects", return_value=[parent_obj, child_obj]):
            with patch.object(tool.Ifc, "get_entity", side_effect=get_entity):
                with patch.object(tool.Blender.Modifier, "is_array_child", side_effect=is_array_child):
                    assert tool.Blender.Modifier.any_selected_is_array_child() is True

    def test_returns_false_when_no_selected_passes_predicate(self):
        from bonsai import tool

        parent_obj, parent_element = SimpleNamespace(name="parent"), object()
        with patch.object(tool.Blender, "get_selected_objects", return_value=[parent_obj]):
            with patch.object(tool.Ifc, "get_entity", return_value=parent_element):
                with patch.object(tool.Blender.Modifier, "is_array_child", return_value=False):
                    assert tool.Blender.Modifier.any_selected_is_array_child() is False


class TestHostOpeningGizmoStaysAvailableOnArrayChildren:
    """Openings on array children are array-safe: ``regenerate_array``
    applies opening cuts after replicating child geometry, so an opening
    authored on a child survives regen and tracks with the replicated
    instance. The host-opening gizmos therefore route through the loose
    base wall gate, not the tighter topology gate that excludes
    children."""

    def test_host_opening_module_does_not_apply_topology_gate(self):
        import inspect

        from bonsai.bim.module.model import host_add_opening_gizmo

        src = inspect.getsource(host_add_opening_gizmo)
        assert "_wall_topology_gizmo_poll_gate" not in src, (
            "host-opening gizmo module references the topology gate; that "
            "would suppress add-opening on array-child hosts. Openings "
            "track with the regenerated child via the array regen pipeline."
        )
        assert "any_selected_is_array_child" not in src, (
            "host-opening gizmo module references any_selected_is_array_child; "
            "openings are array-safe, drop the filter."
        )
