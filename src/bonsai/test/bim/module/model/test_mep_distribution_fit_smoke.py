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

"""Smoke coverage for ``RegenerateDistributionElement`` and
``FitFlowSegments``.

Both operators carry substantial branching that the bend / port test
files don't reach. These tests pin:

- the operator-registration contract (bl_idname / bl_label / bl_options),
- ``FitFlowSegments`` dispatch table — 0 / 1 / mixed-class selections
  resolve to the documented no-op or operator dispatch without raising,
- ``RegenerateDistributionElement`` runs on a leaf element (no connected
  neighbours) without crashing on the recursion entry point.

Deeper geometry-tree behaviour (multi-branch traversal, port-aligned
translation, segment regrowth) is deferred to integration testing
against real IFC fixtures; the smoke tests are explicitly the
oversight-prevention floor, not the full contract."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest

pytestmark = pytest.mark.model


def _segment(ifc_class: str = "IfcFlowSegment"):
    """Stand-in for an IfcFlowSegment / subclass entity.

    ``is_a("IfcFlowSegment" | <ifc_class>)`` returns True; ``is_a()`` with
    no args returns the class name (the IfcOpenShell API exposes both
    forms — ``FitFlowSegments`` calls ``element.is_a()`` to record the
    selection's class for the mixed-class refusal check)."""

    def fake_is_a(c=None):
        if c is None:
            return ifc_class
        return c in {"IfcFlowSegment", ifc_class}

    e = Mock()
    e.is_a = fake_is_a
    return e


def _make_op(**fields):
    op = Mock()
    for k, v in fields.items():
        setattr(op, k, v)
    op.report = MagicMock()
    return op


# ---------------------------------------------------------------------------
# Registration smoke
# ---------------------------------------------------------------------------


def test_regenerate_distribution_element_is_registered():
    """``RegenerateDistributionElement`` is the entry point for the
    distribution-tree repropagation. Pin the bl_idname so a typo in the
    classes tuple wouldn't silently drop the operator."""
    from bonsai.bim.module.model import mep

    assert mep.RegenerateDistributionElement.bl_idname == "bim.regenerate_distribution_element"
    assert mep.RegenerateDistributionElement.bl_label == "Regenerate Distribution Element"
    assert mep.RegenerateDistributionElement.bl_options == {"REGISTER", "UNDO"}


def test_fit_flow_segments_is_registered():
    """``FitFlowSegments`` is the cursor-based "add a fitting from the
    current selection" entry point. Pin the registration contract so the
    operator stays callable from the workspace tool."""
    from bonsai.bim.module.model import mep

    assert mep.FitFlowSegments.bl_idname == "bim.fit_flow_segments"
    assert mep.FitFlowSegments.bl_label == "Fit Flow Segments"
    assert mep.FitFlowSegments.bl_options == {"REGISTER", "UNDO"}


# ---------------------------------------------------------------------------
# FitFlowSegments dispatch table
# ---------------------------------------------------------------------------


def test_fit_flow_segments_with_no_selection_is_noop():
    """Nothing selected → no fitting type resolved → operator returns
    without dispatching any ``bim.mep_add_*`` op. The user-facing
    contract is "this is a tool you fire with a selection"; the silent
    no-op on empty selection is intentional (no popup, no error)."""
    from bonsai.bim.module.model import mep

    context = MagicMock()
    context.selected_objects = []

    op = _make_op()
    with patch.object(mep.MEPAddObstruction, "_execute", return_value=None) as obstruction, patch.object(
        mep.MEPAddBend, "_execute", return_value=None
    ) as bend, patch.object(mep.MEPAddTransition, "_execute", return_value=None) as transition:
        mep.FitFlowSegments._execute(op, context=context)

    obstruction.assert_not_called()
    bend.assert_not_called()
    transition.assert_not_called()


def test_fit_flow_segments_with_single_segment_dispatches_obstruction():
    """Exactly one IfcFlowSegment selected → OBSTRUCTION fitting type,
    delegates to ``bim.mep_add_obstruction`` which handles the
    cursor-anchored placement.

    ``bpy.ops`` resolves operator dispatch through Blender's internal id
    table, not through Python attribute access, so a Python-level patch
    on ``bpy.ops.bim.mep_add_obstruction`` doesn't intercept the call.
    Patch the operator's ``_execute`` instead — same effect, exercises
    the real dispatch path that the user hits at runtime."""
    from bonsai.bim.module.model import mep

    segment_obj = MagicMock()
    segment_profile = MagicMock()
    segment_entity = _segment("IfcPipeSegment")

    context = MagicMock()
    context.selected_objects = [segment_obj]

    op = _make_op()
    with patch.object(mep.tool.Ifc, "get_entity", return_value=segment_entity), patch.object(
        mep.tool.Model, "get_flow_segment_profile", return_value=segment_profile
    ), patch.object(mep.MEPAddObstruction, "_execute", return_value=None) as obstruction, patch.object(
        mep.MEPAddBend, "_execute", return_value=None
    ) as bend, patch.object(
        mep.MEPAddTransition, "_execute", return_value=None
    ) as transition:
        mep.FitFlowSegments._execute(op, context=context)

    assert obstruction.call_count == 1
    bend.assert_not_called()
    transition.assert_not_called()


def test_fit_flow_segments_refuses_mixed_pipe_and_duct():
    """Selecting one IfcPipeSegment + one IfcDuctSegment → the operator
    bails out before any fitting dispatch. The user-facing path is
    "select segments of one kind"; mixing pipe + duct would create an
    invalid IFC fitting type."""
    from bonsai.bim.module.model import mep

    pipe_obj = MagicMock()
    duct_obj = MagicMock()
    pipe_entity = _segment("IfcPipeSegment")
    duct_entity = _segment("IfcDuctSegment")
    profile = MagicMock()

    context = MagicMock()
    context.selected_objects = [pipe_obj, duct_obj]

    def fake_get_entity(obj):
        return pipe_entity if obj is pipe_obj else duct_entity

    op = _make_op()
    with patch.object(mep.tool.Ifc, "get_entity", side_effect=fake_get_entity), patch.object(
        mep.tool.Model, "get_flow_segment_profile", return_value=profile
    ), patch.object(mep.MEPAddObstruction, "_execute", return_value=None) as obstruction, patch.object(
        mep.MEPAddBend, "_execute", return_value=None
    ) as bend, patch.object(
        mep.MEPAddTransition, "_execute", return_value=None
    ) as transition:
        mep.FitFlowSegments._execute(op, context=context)

    obstruction.assert_not_called()
    bend.assert_not_called()
    transition.assert_not_called()


# ---------------------------------------------------------------------------
# RegenerateDistributionElement
# ---------------------------------------------------------------------------


def test_regenerate_distribution_element_on_leaf_is_safe():
    """A distribution element with no connected neighbours → the inner
    queue stays empty → the operator returns cleanly without entering
    the per-branch processing path.

    This pins the safety floor: the recursion entry point should not
    crash on a single-element graph, which is the most common shape
    when a user fires this operator on an isolated segment."""
    from bonsai.bim.module.model import mep

    leaf_element = _segment("IfcPipeSegment")
    leaf_obj = MagicMock()

    context = MagicMock()
    context.active_object = leaf_obj

    fake_active = MagicMock()
    fake_active.is_a = lambda c: False  # bpy.context.active_object stub

    op = _make_op()
    with patch.object(mep.tool.Ifc, "get_entity", return_value=leaf_element), patch(
        "ifcopenshell.util.system.get_connected_to", return_value=[]
    ), patch("ifcopenshell.util.system.get_connected_from", return_value=[]), patch.object(
        mep.tool.Ifc, "get", return_value=MagicMock()
    ), patch(
        "ifcopenshell.util.unit.calculate_unit_scale", return_value=1.0
    ), patch.object(
        bpy, "context", new=context
    ):
        mep.RegenerateDistributionElement._execute(op, context=context)

    # The contract on a leaf is "nothing to do". No exception, no IFC
    # mutation. The bpy.ops dispatch table inside process_branch never
    # fires because queue is empty.
