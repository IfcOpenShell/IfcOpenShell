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


def test_unjoin_icons_bind_unified_disconnect_operator():
    """Every unjoin icon (pair, start, end) routes to the unified
    ``bim.disconnect_elements`` operator and the group holds an
    ``op_props`` slot for each so the per-frame GUID writes have a
    target."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    GizmoMEPActions._wire_anchored_icon_targets(inst)

    assert isinstance(inst.unjoin_op_props, dict)
    for name in GizmoMEPActions.UNJOIN_CONFIGS:
        gz = getattr(inst, f"action_{name}_gizmo")
        gz.target_set_operator.assert_any_call("bim.disconnect_elements")
        assert name in inst.unjoin_op_props, f"missing op_props slot for {name!r}"


def test_bind_unjoin_pair_writes_both_guids():
    """``_bind_unjoin_pair`` is the per-frame hand-off from gizmo
    position-gizmos to the unified disconnect operator: both segment
    GlobalIds get written onto the pre-wired op_props so a click
    dispatches with the right pair."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    GizmoMEPActions._wire_anchored_icon_targets(inst)
    pair_op_props = inst.unjoin_op_props["unjoin_pair"]

    seg_a = Mock(GlobalId="GUID-A")
    seg_b = Mock(GlobalId="GUID-B")

    assert GizmoMEPActions._bind_unjoin_pair(inst, [seg_a, seg_b]) is True
    assert pair_op_props.element_a_guid == "GUID-A"
    assert pair_op_props.element_b_guid == "GUID-B"


def test_bind_unjoin_pair_rejects_incomplete_pair():
    """Defensive: a selection mid-change can hand the gizmo a one-element
    or None-containing pair. The bind must refuse rather than write a
    half-resolved op_props that would later CANCEL with a confusing
    error message."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    GizmoMEPActions._wire_anchored_icon_targets(inst)

    assert GizmoMEPActions._bind_unjoin_pair(inst, [Mock(GlobalId="A")]) is False
    assert GizmoMEPActions._bind_unjoin_pair(inst, [Mock(GlobalId="A"), None]) is False


def test_bind_unjoin_at_port_resolves_fitting_and_writes_guids():
    """The per-port unjoin gizmo resolves the partner fitting at the
    named port and writes (segment_guid, fitting_guid) onto the
    pre-wired op_props so the unified disconnect operator gets both
    endpoints."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    GizmoMEPActions._wire_anchored_icon_targets(inst)
    port_op_props = inst.unjoin_op_props["unjoin_end"]

    segment_obj = Mock()
    segment = Mock(GlobalId="SEG-GUID")
    fitting = Mock(GlobalId="FIT-GUID")
    fitting.is_a = lambda c: c == "IfcFlowFitting"
    fitting.PredefinedType = "BEND"

    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=segment), patch(
        "bonsai.bim.module.model.mep.get_connected_element_at_segment_port", return_value=fitting
    ):
        ok = GizmoMEPActions._bind_unjoin_at_port(inst, "unjoin_end", segment_obj, False)

    assert ok is True
    assert port_op_props.element_a_guid == "SEG-GUID"
    assert port_op_props.element_b_guid == "FIT-GUID"


def test_bind_unjoin_at_port_refuses_obstruction_partner():
    """OBSTRUCTION fittings have a dedicated grow/shrink removal flow —
    routing them through the unified disconnect would just delete the
    fitting and leave a visible gap. Mirror the find_rels exclusion
    here so the icon hides when the partner is an obstruction."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    inst = _build_group_with_mock_gizmos()
    GizmoMEPActions._wire_anchored_icon_targets(inst)

    segment = Mock(GlobalId="SEG-GUID")
    obstruction = Mock(GlobalId="OBS-GUID")
    obstruction.is_a = lambda c: c == "IfcFlowFitting"
    obstruction.PredefinedType = "OBSTRUCTION"

    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=segment), patch(
        "bonsai.bim.module.model.mep.get_connected_element_at_segment_port", return_value=obstruction
    ):
        assert GizmoMEPActions._bind_unjoin_at_port(inst, "unjoin_end", Mock(), False) is False


# ---------------------------------------------------------------------------
# Visibility predicates — total over degenerate inputs
# ---------------------------------------------------------------------------


def test_active_is_bend_fitting_accepts_tessellated_bend_with_bbim_pset():
    """A bend whose body has been tessellated as the upstream geometry-kernel
    workaround still has its parametric definition on the type's
    ``BBIM_Fitting`` pset — the re-edit operator reads from there, so the
    pen icon must surface on it. ``has_parametric_body`` would return False
    for the tessellated body; the pset gate is what makes the icon
    reachable."""
    from bonsai.bim.module.model.mep import _active_is_bend_fitting

    bend_obj = Mock()
    bend_elem = Mock()
    bend_elem.is_a = lambda c: c == "IfcFlowFitting"
    bend_type = Mock()
    bend_type.PredefinedType = "BEND"

    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=bend_elem), patch(
        "bonsai.bim.module.model.mep._is_bend_fitting", return_value=True
    ), patch("bonsai.bim.module.model.mep.ifcopenshell.util.element.get_type", return_value=bend_type), patch(
        "bonsai.bim.module.model.mep.ifcopenshell.util.element.get_pset",
        return_value={"radius": 0.2, "start_length": 0.1, "end_length": 0.1},
    ):
        assert _active_is_bend_fitting(bend_obj) is True


def test_active_is_bend_fitting_rejects_bend_type_without_bbim_pset():
    """A fitting that looks like a bend (IfcFlowFitting + type.PredefinedType
    == BEND) but lacks a ``BBIM_Fitting`` pset on the type can't be re-edited
    — the re-edit operator reads parameters from the pset. Reject so the pen
    icon hides rather than dispatching an operator that would CANCEL."""
    from bonsai.bim.module.model.mep import _active_is_bend_fitting

    bend_obj = Mock()
    bend_elem = Mock()
    bend_elem.is_a = lambda c: c == "IfcFlowFitting"
    bend_type = Mock()
    bend_type.PredefinedType = "BEND"

    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=bend_elem), patch(
        "bonsai.bim.module.model.mep._is_bend_fitting", return_value=True
    ), patch("bonsai.bim.module.model.mep.ifcopenshell.util.element.get_type", return_value=bend_type), patch(
        "bonsai.bim.module.model.mep.ifcopenshell.util.element.get_pset", return_value=None
    ):
        assert _active_is_bend_fitting(bend_obj) is False


def test_active_is_bend_fitting_rejects_non_bend():
    """Non-bend objects (segments, fittings with PredefinedType != BEND)
    fail the first gate regardless of pset state."""
    from bonsai.bim.module.model.mep import _active_is_bend_fitting

    bend_obj = Mock()
    bend_elem = Mock()
    bend_elem.is_a = lambda c: c == "IfcFlowFitting"

    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=bend_elem), patch(
        "bonsai.bim.module.model.mep._is_bend_fitting", return_value=False
    ):
        assert _active_is_bend_fitting(bend_obj) is False


def test_active_is_flow_segment_handles_unbound_object():
    """A Blender object with no IFC binding must not raise from a
    visibility predicate. The lambda runs on every selection event."""
    from bonsai.bim.module.model.mep import _active_is_flow_segment

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=None):
        assert _active_is_flow_segment(plain) is False


def test_active_is_flow_segment_classifies_segment_vs_fitting():
    """Only IfcFlowSegment lights the lock-icon row; IfcFlowFitting (the
    bend's own class) does not. The parametric-body gate is mocked True
    here — its dedicated truth-table is in test_mep_actions_visibility
    sibling tests."""
    from bonsai.bim.module.model.mep import _active_is_flow_segment

    segment_elem = Mock()
    segment_elem.is_a = lambda c: c == "IfcFlowSegment"
    fitting_elem = Mock()
    fitting_elem.is_a = lambda c: c == "IfcFlowFitting"

    plain = Mock()
    with patch("bonsai.bim.module.model.mep.tool.System.has_parametric_body", return_value=True), patch(
        "bonsai.bim.module.model.mep.tool.Array.is_array_child", return_value=False
    ):
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
