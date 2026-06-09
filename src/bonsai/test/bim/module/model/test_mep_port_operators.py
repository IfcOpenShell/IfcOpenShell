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

"""Behaviour tests for the MEP port operators.

Pins the dispatch contract each operator carries — which IFC mutation
runs, which user-error path returns CANCELLED, and which fitting types
are deliberately refused by each entry point. Each test mocks the
``tool.*`` and ``MEPGenerator`` boundaries so no IFC fixture is needed."""

from unittest.mock import MagicMock, Mock, patch

import bpy
import pytest

pytestmark = pytest.mark.model


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


def _segment(predefined_type=None):
    """Stand-in IFC entity that reports ``is_a("IfcFlowSegment")`` True."""
    e = Mock()
    e.is_a = lambda c: c == "IfcFlowSegment"
    e.PredefinedType = predefined_type
    return e


def _fitting(predefined_type=None):
    """Stand-in IFC fitting entity with an arbitrary ``PredefinedType``."""
    e = Mock()
    e.is_a = lambda c: c in ("IfcFlowFitting", "IfcDistributionFlowElement")
    e.PredefinedType = predefined_type
    return e


def _make_op(_cls, **fields):
    """Return a Mock standing in for an Operator ``self``. Subclassing a
    ``bpy.types.Operator`` outside Blender's registration machinery raises
    a ``bpy_struct.__new__`` error, so each test calls the operator
    method as an unbound function with this Mock as the first argument."""
    op = Mock()
    for k, v in fields.items():
        setattr(op, k, v)
    op.report = MagicMock()
    return op


# ---------------------------------------------------------------------------
# MEPUnjoinAtPort
# ---------------------------------------------------------------------------


def test_unjoin_at_port_deletes_joining_fitting():
    """Happy path: port state is JOINED, fitting is non-OBSTRUCTION →
    delete the bridging fitting via the standard delete path."""
    from bonsai.bim.module.model import mep

    segment = _segment()
    fitting = _fitting(predefined_type="JUNCTION")
    fitting_obj = Mock()

    op = _make_op(mep.MEPUnjoinAtPort, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep.tool.Ifc, "get_object", return_value=fitting_obj
    ), patch.object(mep, "port_connection_state", return_value="JOINED"), patch.object(
        mep, "get_connected_element_at_segment_port", return_value=fitting
    ), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPUnjoinAtPort._execute(op, context=MagicMock())

    assert result == {"FINISHED"}
    delete.assert_called_once_with(fitting_obj)


def test_unjoin_at_port_refuses_obstruction_fitting():
    """OBSTRUCTION fittings route through ``bim.mep_add_obstruction``
    (mode=REMOVE) which extends the segment to absorb the freed length —
    using unjoin here would leave a gap."""
    from bonsai.bim.module.model import mep

    segment = _segment()
    obstruction = _fitting(predefined_type="OBSTRUCTION")

    op = _make_op(mep.MEPUnjoinAtPort, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep, "port_connection_state", return_value="JOINED"
    ), patch.object(mep, "get_connected_element_at_segment_port", return_value=obstruction), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPUnjoinAtPort._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    delete.assert_not_called()
    op.report.assert_called()


def test_unjoin_at_port_cancels_when_port_is_free():
    """Port has no connection at all → no fitting to delete → CANCELLED
    with a user-facing error rather than a silent no-op."""
    from bonsai.bim.module.model import mep

    segment = _segment()

    op = _make_op(mep.MEPUnjoinAtPort, segment_id=42, position="START")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep, "port_connection_state", return_value="FREE"
    ), patch.object(mep.tool.Geometry, "delete_ifc_object") as delete:
        result = mep.MEPUnjoinAtPort._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    delete.assert_not_called()
    op.report.assert_called()


def test_unjoin_at_port_cancels_when_active_is_not_segment():
    """The operator only operates on flow segments; non-segment active
    objects must fail loud rather than mutate something unexpected."""
    from bonsai.bim.module.model import mep

    fitting = _fitting()  # IfcFlowFitting, not IfcFlowSegment

    op = _make_op(mep.MEPUnjoinAtPort, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = fitting

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file):
        result = mep.MEPUnjoinAtPort._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    op.report.assert_called()


# ---------------------------------------------------------------------------
# MEPRemoveTerminalFitting
# ---------------------------------------------------------------------------


def test_remove_terminal_dispatches_obstruction_via_remove_obstruction():
    """OBSTRUCTION fittings extend the segment to absorb the freed length;
    the operator routes through ``MEPGenerator().remove_obstruction``
    rather than the plain delete path."""
    from bonsai.bim.module.model import mep

    segment = _segment()
    obstruction = _fitting(predefined_type="OBSTRUCTION")

    op = _make_op(mep.MEPRemoveTerminalFitting, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep, "port_connection_state", return_value="TERMINAL"
    ), patch.object(mep, "get_connected_element_at_segment_port", return_value=obstruction), patch.object(
        mep, "MEPGenerator"
    ) as gen_cls, patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        gen_cls.return_value.remove_obstruction.return_value = (obstruction, None)
        result = mep.MEPRemoveTerminalFitting._execute(op, context=MagicMock())

    assert result == {"FINISHED"}
    gen_cls.return_value.remove_obstruction.assert_called_once_with(segment, False)
    delete.assert_not_called()


def test_remove_terminal_dispatches_non_obstruction_via_delete():
    """A standard terminal fitting (cap, isolated terminal) goes through
    the plain delete path — the segment is not resized."""
    from bonsai.bim.module.model import mep

    segment = _segment()
    fitting = _fitting(predefined_type=None)
    fitting_obj = Mock()

    op = _make_op(mep.MEPRemoveTerminalFitting, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep.tool.Ifc, "get_object", return_value=fitting_obj
    ), patch.object(mep, "port_connection_state", return_value="TERMINAL"), patch.object(
        mep, "get_connected_element_at_segment_port", return_value=fitting
    ), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPRemoveTerminalFitting._execute(op, context=MagicMock())

    assert result == {"FINISHED"}
    delete.assert_called_once_with(fitting_obj)


def test_remove_terminal_cancels_on_non_terminal_port():
    """Port state must be TERMINAL for this operator; FREE / JOINED are
    routed through other operators."""
    from bonsai.bim.module.model import mep

    segment = _segment()

    op = _make_op(mep.MEPRemoveTerminalFitting, segment_id=42, position="END")
    ifc_file = MagicMock()
    ifc_file.by_id.return_value = segment

    with patch.object(mep.tool.Ifc, "get", return_value=ifc_file), patch.object(
        mep, "port_connection_state", return_value="JOINED"
    ):
        result = mep.MEPRemoveTerminalFitting._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    op.report.assert_called()


# ---------------------------------------------------------------------------
# MEPUnjoinPair
# ---------------------------------------------------------------------------


def test_unjoin_pair_deletes_bridging_fitting():
    """Happy path: two selected segments share a single non-OBSTRUCTION
    bridging fitting → delete it."""
    from bonsai.bim.module.model import mep

    segment_a = _segment()
    segment_b = _segment()
    fitting = _fitting(predefined_type="JUNCTION")
    fitting_obj = Mock()

    op = _make_op(mep.MEPUnjoinPair)
    selected = [Mock(), Mock()]

    with patch.object(mep.tool.Blender, "get_selected_objects", return_value=selected), patch.object(
        mep.tool.Ifc, "get_entity", side_effect=[segment_a, segment_b]
    ), patch.object(mep, "find_fitting_between_segments", return_value=fitting), patch.object(
        mep.tool.Ifc, "get_object", return_value=fitting_obj
    ), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPUnjoinPair._execute(op, context=MagicMock())

    assert result == {"FINISHED"}
    delete.assert_called_once_with(fitting_obj)


def test_unjoin_pair_refuses_obstruction_bridging():
    """Same defence-in-depth as ``MEPUnjoinAtPort`` — obstructions go
    through the dedicated REMOVE path; this operator surfaces the
    redirect rather than silently doing the wrong thing."""
    from bonsai.bim.module.model import mep

    segment_a = _segment()
    segment_b = _segment()
    obstruction = _fitting(predefined_type="OBSTRUCTION")

    op = _make_op(mep.MEPUnjoinPair)
    selected = [Mock(), Mock()]

    with patch.object(mep.tool.Blender, "get_selected_objects", return_value=selected), patch.object(
        mep.tool.Ifc, "get_entity", side_effect=[segment_a, segment_b]
    ), patch.object(mep, "find_fitting_between_segments", return_value=obstruction), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPUnjoinPair._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    delete.assert_not_called()
    op.report.assert_called()


def test_unjoin_pair_reports_when_no_bridging_fitting_found():
    """The pair is selected but no single fitting bridges them — the
    user is told instead of getting a silent no-op."""
    from bonsai.bim.module.model import mep

    segment_a = _segment()
    segment_b = _segment()

    op = _make_op(mep.MEPUnjoinPair)
    selected = [Mock(), Mock()]

    with patch.object(mep.tool.Blender, "get_selected_objects", return_value=selected), patch.object(
        mep.tool.Ifc, "get_entity", side_effect=[segment_a, segment_b]
    ), patch.object(mep, "find_fitting_between_segments", return_value=None), patch.object(
        mep.tool.Geometry, "delete_ifc_object"
    ) as delete:
        result = mep.MEPUnjoinPair._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    delete.assert_not_called()
    op.report.assert_called()


def test_unjoin_pair_cancels_when_selection_is_not_two_segments():
    """The poll filters the gizmo, but a programmatic invocation could
    still hand the operator an invalid selection. The execute path
    independently verifies both inputs are IfcFlowSegment."""
    from bonsai.bim.module.model import mep

    not_a_segment = _fitting()  # IfcFlowFitting, not IfcFlowSegment

    op = _make_op(mep.MEPUnjoinPair)
    selected = [Mock(), Mock()]

    with patch.object(mep.tool.Blender, "get_selected_objects", return_value=selected), patch.object(
        mep.tool.Ifc, "get_entity", side_effect=[not_a_segment, not_a_segment]
    ):
        result = mep.MEPUnjoinPair._execute(op, context=MagicMock())

    assert result == {"CANCELLED"}
    op.report.assert_called()


# ---------------------------------------------------------------------------
# SelectMEPPathMembers
# ---------------------------------------------------------------------------


def test_select_path_replaces_selection_with_walked_members():
    """Happy path: walker returns a small connected network → every
    member gets ``select_set(True)``; the original active object stays
    active."""
    from bonsai.bim.module.model import mep

    active = Mock()
    element = Mock()
    member_elements = [Mock(), Mock(), Mock()]
    member_objs = [Mock(), Mock(), Mock()]

    context = MagicMock()
    context.active_object = active
    context.view_layer.objects.active = None

    op = _make_op(mep.SelectMEPPathMembers)

    with patch.object(mep.tool.Ifc, "get_entity", return_value=element), patch.object(
        mep.tool.System, "walk_connected_mep_elements", return_value=member_elements
    ), patch.object(mep.tool.Ifc, "get_object", side_effect=member_objs), patch.object(
        mep.bpy.ops.object, "select_all"
    ):
        result = mep.SelectMEPPathMembers.execute(op, context)

    assert result == {"FINISHED"}
    for obj in member_objs:
        obj.select_set.assert_called_once_with(True)


def test_select_path_reports_when_walker_returns_empty():
    """An MEP element with no connected neighbours produces an empty
    walk; report INFO so the user knows the click registered, return
    FINISHED so the operator doesn't surface as an error."""
    from bonsai.bim.module.model import mep

    active = Mock()
    element = Mock()

    context = MagicMock()
    context.active_object = active

    op = _make_op(mep.SelectMEPPathMembers)

    with patch.object(mep.tool.Ifc, "get_entity", return_value=element), patch.object(
        mep.tool.System, "walk_connected_mep_elements", return_value=[]
    ):
        result = mep.SelectMEPPathMembers.execute(op, context)

    assert result == {"FINISHED"}
    op.report.assert_called()


def test_select_path_handles_walker_exception():
    """The walker can raise on malformed port graphs; the operator must
    catch and surface as ERROR rather than crashing the operator harness."""
    from bonsai.bim.module.model import mep

    active = Mock()
    element = Mock()

    context = MagicMock()
    context.active_object = active

    op = _make_op(mep.SelectMEPPathMembers)

    with patch.object(mep.tool.Ifc, "get_entity", return_value=element), patch.object(
        mep.tool.System, "walk_connected_mep_elements", side_effect=RuntimeError("malformed port graph")
    ):
        result = mep.SelectMEPPathMembers.execute(op, context)

    assert result == {"CANCELLED"}
    op.report.assert_called()
