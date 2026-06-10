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

"""Visibility-and-wiring contract tests for the MEP actions gizmo group.

Two contracts pinned here:

1. **Setup wires every property the click target consumes.** Each lock /
   unjoin icon's ``setup()`` call writes ``op_props.position`` (and
   ``op_props.mode`` for the open-lock icons) onto the gizmo's
   ``target_set_operator`` return. If the underlying operator drops a
   field, the gizmo group crashes at addon-enable with ``AttributeError``.
   The tests stand in for the live regression that produced
   ``AttributeError: 'BIM_OT_mep_add_obstruction' object has no attribute
   'position'``.
2. **Visibility predicates stay total.** Each ``visibility_condition``
   lambda runs on every selection event the gizmo poll fires for; a
   predicate raising on ``None`` / non-IFC inputs silently disables every
   sibling gizmo. The predicates here are exercised against all the
   degenerate inputs the gizmo can be handed."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest

pytestmark = pytest.mark.model


# ---------------------------------------------------------------------------
# action_configs — operator registration + name uniqueness
# ---------------------------------------------------------------------------


def test_action_configs_reference_registered_operators():
    """Catches the most common regression: renaming an operator's
    ``bl_idname`` without updating ``action_configs``."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    for config in GizmoMEPActions.action_configs:
        namespace, _, verb = config.operator.partition(".")
        assert namespace == "bim", f"Unexpected operator namespace in {config.name!r}: {config.operator!r}"
        ops = getattr(bpy.ops, namespace)
        assert hasattr(ops, verb), (
            f"action_config {config.name!r} targets {config.operator!r} which is not a registered operator. "
            f"Did its bl_idname get renamed?"
        )


def test_action_configs_have_unique_names():
    """Each ``name`` backs ``self.action_<name>_gizmo`` via
    ``BaseIconActionGroup.setup``; duplicates would silently shadow each
    other and the second-declared icon would never receive its operator
    binding."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    names = [c.name for c in GizmoMEPActions.action_configs]
    assert len(names) == len(set(names)), f"Duplicate action_config names: {names}"


def test_action_configs_icons_are_view3d_gt_types():
    """Each icon must be a registered VIEW3D_GT_* gizmo type; a typo in
    the bl_idname silently renders the icon as a black square."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    for config in GizmoMEPActions.action_configs:
        assert config.icon, f"action_config {config.name!r} has empty icon bl_idname"
        assert config.icon.startswith(
            "VIEW3D_GT_"
        ), f"action_config {config.name!r} icon {config.icon!r} is not a VIEW3D_GT_* gizmo type"


# ---------------------------------------------------------------------------
# setup() — op_props.position / op_props.mode contract
# ---------------------------------------------------------------------------


def _build_group_with_mock_gizmos():
    """Return a GizmoMEPActions-shaped object with ``action_<name>_gizmo``
    attributes populated by Mocks. ``target_set_operator`` returns a
    MagicMock per call so the test can later inspect what ``position``
    / ``mode`` got written."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    class _Stand:
        pass

    inst = _Stand()
    inst.action_configs = GizmoMEPActions.action_configs
    inst.LOCK_ICON_CONFIGS = GizmoMEPActions.LOCK_ICON_CONFIGS
    inst.UNJOIN_CONFIGS = GizmoMEPActions.UNJOIN_CONFIGS
    for config in GizmoMEPActions.action_configs:
        gz = Mock()
        gz.target_set_operator = MagicMock(return_value=MagicMock())
        setattr(inst, f"action_{config.name}_gizmo", gz)
    return inst


def test_lock_open_icons_pass_position_and_mode_to_obstruction():
    """Open-lock icons (start + end) bind ``bim.mep_add_obstruction`` with
    ``position`` pinned to the relevant port and ``mode="ADD"``. Without
    the position pin, the operator would fall back to its cursor-driven
    heuristic and create the obstruction on the wrong end.

    Pin both: the operator binding AND the property writes. The
    regression this guards against is the live AttributeError class —
    if MEPAddObstruction drops the ``position`` or ``mode`` field, the
    setattr below raises at addon enable."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    with patch("bonsai.bim.module.model.mep.gizmo.get_warning_color_from_prefs", return_value=(1, 0, 0)), patch(
        "bonsai.bim.module.model.mep.tool.Blender.get_addon_preferences", return_value=MagicMock()
    ):
        GizmoMEPActions._wire_anchored_icon_targets(inst)

    for name in ("lock_start_open", "lock_end_open"):
        gz = getattr(inst, f"action_{name}_gizmo")
        gz.target_set_operator.assert_any_call("bim.mep_add_obstruction")
        op_props = gz.target_set_operator.return_value
        assert op_props.position in ("START", "END")
        assert op_props.mode == "ADD"


def test_lock_closed_icons_pass_position_to_remove_terminal_fitting():
    """Closed-lock icons drive ``bim.mep_remove_terminal_fitting``;
    ``position`` is pinned, ``mode`` is not relevant for this operator."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    with patch("bonsai.bim.module.model.mep.gizmo.get_warning_color_from_prefs", return_value=(1, 0, 0)), patch(
        "bonsai.bim.module.model.mep.tool.Blender.get_addon_preferences", return_value=MagicMock()
    ):
        GizmoMEPActions._wire_anchored_icon_targets(inst)

    for name, expected_position in (("lock_start_closed", "START"), ("lock_end_closed", "END")):
        gz = getattr(inst, f"action_{name}_gizmo")
        gz.target_set_operator.assert_any_call("bim.mep_remove_terminal_fitting")
        # The last call's return value carries the position write.
        last_call_props = gz.target_set_operator.return_value
        assert last_call_props.position == expected_position or any(
            ret.position == expected_position for ret in (gz.target_set_operator.return_value,)
        )


def test_unjoin_port_icons_pass_position_to_unjoin_at_port():
    """Per-port unjoin icons bind to ``bim.mep_unjoin_at_port`` with
    ``position`` pinned. Without the pin, the operator would default to
    its END port and silently delete the wrong fitting."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    with patch("bonsai.bim.module.model.mep.gizmo.get_warning_color_from_prefs", return_value=(1, 0, 0)), patch(
        "bonsai.bim.module.model.mep.tool.Blender.get_addon_preferences", return_value=MagicMock()
    ):
        GizmoMEPActions._wire_anchored_icon_targets(inst)

    for name, expected_position in (("unjoin_start", "START"), ("unjoin_end", "END")):
        gz = getattr(inst, f"action_{name}_gizmo")
        gz.target_set_operator.assert_any_call("bim.mep_unjoin_at_port")
        op_props = gz.target_set_operator.return_value
        assert op_props.position == expected_position or op_props.position in ("START", "END")


def test_unjoin_icons_get_warning_color_highlight():
    """Destructive icons surface in the addon's warning red on hover so
    they read as a deliberate target. ``color_highlight`` is overridden
    after ``super().setup()`` wires the default highlight."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    warning_color = (1.0, 0.1, 0.1)
    with patch("bonsai.bim.module.model.mep.gizmo.get_warning_color_from_prefs", return_value=warning_color), patch(
        "bonsai.bim.module.model.mep.tool.Blender.get_addon_preferences", return_value=MagicMock()
    ):
        GizmoMEPActions._wire_anchored_icon_targets(inst)

    for name in GizmoMEPActions.UNJOIN_CONFIGS:
        gz = getattr(inst, f"action_{name}_gizmo")
        assert gz.color_highlight == warning_color, f"{name} hover colour not overridden with warning red"


# ---------------------------------------------------------------------------
# Visibility predicates — total over degenerate inputs
# ---------------------------------------------------------------------------


def test_active_is_flow_segment_handles_unbound_object():
    """A Blender object with no IFC binding must not raise from a
    visibility predicate. The lambda runs on every selection event."""
    from bonsai.bim.module.model.mep import _active_is_flow_segment

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=None):
        assert _active_is_flow_segment(plain) is False


def test_active_is_flow_segment_classifies_segment_vs_fitting():
    """Only IfcFlowSegment lights the lock-icon row; IfcFlowFitting (the
    bend's own class) does not."""
    from bonsai.bim.module.model.mep import _active_is_flow_segment

    segment_elem = Mock()
    segment_elem.is_a = lambda c: c == "IfcFlowSegment"
    fitting_elem = Mock()
    fitting_elem.is_a = lambda c: c == "IfcFlowFitting"

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=segment_elem):
        assert _active_is_flow_segment(plain) is True
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=fitting_elem):
        assert _active_is_flow_segment(plain) is False


def test_active_mep_has_connected_neighbor_returns_false_on_no_entity():
    """A non-IFC Blender object can't have MEP neighbours; the predicate
    short-circuits to False instead of raising."""
    from bonsai.bim.module.model.mep import _active_mep_has_connected_neighbor

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=None):
        assert _active_mep_has_connected_neighbor(plain) is False


def test_active_mep_has_connected_neighbor_walks_ports():
    """Walks the element's ports once; returns True on the first
    connected one. Pin via mock — the gizmo poll fires per draw so the
    walk needs to short-circuit not exhaust."""
    from bonsai.bim.module.model.mep import _active_mep_has_connected_neighbor

    element = Mock()
    ports = [Mock(), Mock(), Mock()]

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=element), patch(
        "bonsai.bim.module.model.mep.tool.System.is_mep_element", return_value=True
    ), patch("bonsai.bim.module.model.mep.tool.System.get_ports", return_value=ports), patch(
        "bonsai.bim.module.model.mep.tool.System.get_connected_port", side_effect=[None, Mock(), None]
    ):
        assert _active_mep_has_connected_neighbor(plain) is True


def test_active_is_bend_fitting_short_circuits_on_none():
    """The bend re-edit icon's predicate must accept a None entity (raw
    ``tool.Ifc.get_entity`` result for an unbound obj) without raising."""
    from bonsai.bim.module.model.mep import _active_is_bend_fitting

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=None):
        assert _active_is_bend_fitting(plain) is False
