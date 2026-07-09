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

"""Cache-invalidation tests for ``GizmoMEPActions.position_gizmos``.

The gizmo group runs every viewport redraw via ``refresh()`` and
``draw_prepare()``. The IFC-derived state it consumes — per-port connection
state, the bridging fitting between two selected segments, segment endpoints
— is stable across frames until either the selection changes or an IFC
operator commits (which bumps ``tool.Parametric.get_geom_generation``).
These tests pin that the per-frame redraw reuses the cached state."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest
from mathutils import Vector

pytestmark = pytest.mark.model


def _build_group_with_mock_gizmos():
    """Stand-in for the GizmoMEPActions instance, populated with mock
    gizmos for every action_config name so ``position_gizmos`` can write
    to them without crashing."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    class _Stand:
        pass

    inst = _Stand()
    inst.action_configs = GizmoMEPActions.action_configs
    inst.ENDPOINT_CONFIGS = GizmoMEPActions.ENDPOINT_CONFIGS
    inst.BEND_ANCHOR_CONFIGS = GizmoMEPActions.BEND_ANCHOR_CONFIGS
    inst.UNJOIN_CONFIGS = GizmoMEPActions.UNJOIN_CONFIGS
    inst.ICON_ROW_Z_OFFSET = GizmoMEPActions.ICON_ROW_Z_OFFSET
    inst.ICON_SPACING_X = GizmoMEPActions.ICON_SPACING_X
    inst.ICON_SCALE = GizmoMEPActions.ICON_SCALE
    inst.ENDPOINT_SCALE_RATIO = GizmoMEPActions.ENDPOINT_SCALE_RATIO
    inst._scale_for_config = GizmoMEPActions._scale_for_config.__get__(inst)
    inst.position_gizmos = GizmoMEPActions.position_gizmos.__get__(inst)
    for config in GizmoMEPActions.action_configs:
        gz = Mock()
        setattr(inst, f"action_{config.name}_gizmo", gz)
    return inst


def _mock_segment_obj(name: str = "Segment.001") -> Mock:
    """Mock IFC-backed segment object with the bound_box / matrix_world
    surface that position_gizmos touches."""
    obj = Mock()
    obj.name = name
    obj.bound_box = [
        (0.0, 0.0, 0.0),
        (1.0, 0.0, 0.0),
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
        (1.0, 0.0, 1.0),
        (1.0, 1.0, 1.0),
        (0.0, 1.0, 1.0),
    ]
    obj.matrix_world = Mock()
    obj.matrix_world.__matmul__ = lambda self, v: v
    return obj


def _make_context(active_obj):
    ctx = Mock()
    ctx.active_object = active_obj
    ctx.scene = Mock()
    ctx.scene.BIMPreviewProperties = None
    return ctx


def _silence_visibility_calls():
    """Force every action_config's visibility_condition to True so the
    cached fields actually get exercised. Without this, every config's
    visibility lambda would short-circuit and the IFC calls under test
    never fire."""
    from bonsai.bim.module.model.mep import GizmoMEPActions

    sentinel_lambdas = []
    for config in GizmoMEPActions.action_configs:
        sentinel_lambdas.append((config, config.visibility_condition))
        config.visibility_condition = lambda _obj: True
    return sentinel_lambdas


def _restore_visibility(saved):
    for config, original in saved:
        config.visibility_condition = original


@pytest.fixture
def _patched_visibility():
    saved = _silence_visibility_calls()
    yield
    _restore_visibility(saved)


def test_port_connection_state_cached_across_frames_within_generation(_patched_visibility):
    """Two back-to-back redraws with the same active object, same selection,
    and unchanged IFC generation must reuse the port-state lookup — the
    underlying IFC walk runs once, not once per redraw."""
    inst = _build_group_with_mock_gizmos()
    active = _mock_segment_obj("Segment.001")
    other = _mock_segment_obj("Segment.002")
    context = _make_context(active)

    element = Mock()
    element.is_a = lambda c: c == "IfcFlowSegment"

    call_counts = {"port_connection_state": 0, "find_bridging_fitting": 0, "compute_mep_join_location": 0}

    def counting_port_state(elem, at_start):
        call_counts["port_connection_state"] += 1
        return "FREE"

    def counting_find_fitting(a, b):
        call_counts["find_bridging_fitting"] += 1
        return None

    def counting_join_location():
        call_counts["compute_mep_join_location"] += 1
        return Vector((0.0, 0.0, 0.0))

    patches = [
        patch("bonsai.bim.module.model.mep.tool.Parametric.get_geom_generation", return_value=42),
        patch("bonsai.bim.module.model.mep.tool.Blender.get_selected_objects", return_value=[active, other]),
        patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=element),
        patch(
            "bonsai.bim.module.model.mep.tool.Model.get_flow_segment_axis",
            return_value=(Vector((0, 0, 0)), Vector((1, 0, 0))),
        ),
        patch("bonsai.bim.module.model.mep.port_connection_state", side_effect=counting_port_state),
        patch("bonsai.bim.module.model.mep.tool.System.find_bridging_fitting", side_effect=counting_find_fitting),
        patch("bonsai.bim.module.model.decorator.compute_mep_join_location", side_effect=counting_join_location),
        patch("bonsai.bim.module.model.mep.gizmo.get_billboard_rotation", return_value=Mock()),
        patch("bonsai.bim.module.model.mep.gizmo.billboarded_at", return_value=Mock()),
    ]

    with patches[0], patches[1], patches[2], patches[3], patches[4], patches[5], patches[6], patches[7], patches[8]:
        inst.position_gizmos(context)
        first = dict(call_counts)
        inst.position_gizmos(context)

    # Second frame must reuse the cached values — no second IFC walk.
    assert call_counts["port_connection_state"] == first["port_connection_state"]
    assert call_counts["find_bridging_fitting"] == first["find_bridging_fitting"]
    assert call_counts["compute_mep_join_location"] == first["compute_mep_join_location"]


def test_generation_advance_invalidates_cache(_patched_visibility):
    """An IFC operator commit bumps ``get_geom_generation`` — the next
    redraw must recompute port state and friends to pick up any
    downstream changes."""
    inst = _build_group_with_mock_gizmos()
    active = _mock_segment_obj("Segment.001")
    other = _mock_segment_obj("Segment.002")
    context = _make_context(active)

    element = Mock()
    element.is_a = lambda c: c == "IfcFlowSegment"

    port_call_count = {"n": 0}
    fitting_call_count = {"n": 0}

    def counting_port_state(elem, at_start):
        port_call_count["n"] += 1
        return "FREE"

    def counting_find_fitting(a, b):
        fitting_call_count["n"] += 1
        return None

    gen_state = {"gen": 1}

    with patch(
        "bonsai.bim.module.model.mep.tool.Parametric.get_geom_generation", side_effect=lambda: gen_state["gen"]
    ), patch("bonsai.bim.module.model.mep.tool.Blender.get_selected_objects", return_value=[active, other]), patch(
        "bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=element
    ), patch(
        "bonsai.bim.module.model.mep.tool.Model.get_flow_segment_axis",
        return_value=(Vector((0, 0, 0)), Vector((1, 0, 0))),
    ), patch(
        "bonsai.bim.module.model.mep.port_connection_state", side_effect=counting_port_state
    ), patch(
        "bonsai.bim.module.model.mep.tool.System.find_bridging_fitting", side_effect=counting_find_fitting
    ), patch(
        "bonsai.bim.module.model.decorator.compute_mep_join_location", return_value=Vector((0, 0, 0))
    ), patch(
        "bonsai.bim.module.model.mep.gizmo.get_billboard_rotation", return_value=Mock()
    ), patch(
        "bonsai.bim.module.model.mep.gizmo.billboarded_at", return_value=Mock()
    ):
        inst.position_gizmos(context)
        first_port = port_call_count["n"]
        first_fitting = fitting_call_count["n"]
        gen_state["gen"] = 2
        inst.position_gizmos(context)

    assert port_call_count["n"] > first_port, "port_connection_state must recompute after generation advance"
    assert fitting_call_count["n"] > first_fitting, "find_bridging_fitting must recompute after generation advance"


def test_selection_change_invalidates_cache(_patched_visibility):
    """Changing the selection (e.g. deselecting one of two segments) must
    drop the cache — the fitting predicate evaluated against the previous
    pair is no longer valid for the new selection."""
    inst = _build_group_with_mock_gizmos()
    active = _mock_segment_obj("Segment.001")
    other_a = _mock_segment_obj("Segment.002")
    other_b = _mock_segment_obj("Segment.003")
    context = _make_context(active)

    element = Mock()
    element.is_a = lambda c: c == "IfcFlowSegment"

    fitting_call_count = {"n": 0}

    def counting_find_fitting(a, b):
        fitting_call_count["n"] += 1
        return None

    selection_state = {"selected": [active, other_a]}

    with patch("bonsai.bim.module.model.mep.tool.Parametric.get_geom_generation", return_value=1), patch(
        "bonsai.bim.module.model.mep.tool.Blender.get_selected_objects", side_effect=lambda: selection_state["selected"]
    ), patch("bonsai.bim.module.model.mep.tool.Ifc.get_entity", return_value=element), patch(
        "bonsai.bim.module.model.mep.tool.Model.get_flow_segment_axis",
        return_value=(Vector((0, 0, 0)), Vector((1, 0, 0))),
    ), patch(
        "bonsai.bim.module.model.mep.port_connection_state", return_value="FREE"
    ), patch(
        "bonsai.bim.module.model.mep.tool.System.find_bridging_fitting", side_effect=counting_find_fitting
    ), patch(
        "bonsai.bim.module.model.decorator.compute_mep_join_location", return_value=Vector((0, 0, 0))
    ), patch(
        "bonsai.bim.module.model.mep.gizmo.get_billboard_rotation", return_value=Mock()
    ), patch(
        "bonsai.bim.module.model.mep.gizmo.billboarded_at", return_value=Mock()
    ):
        inst.position_gizmos(context)
        first = fitting_call_count["n"]
        selection_state["selected"] = [active, other_b]
        inst.position_gizmos(context)

    assert fitting_call_count["n"] > first, "find_bridging_fitting must recompute after selection change"
