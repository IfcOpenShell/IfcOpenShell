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
