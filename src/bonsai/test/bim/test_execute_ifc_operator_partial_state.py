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

"""Framework contract test for the partial-state recovery hint in
``IfcStore.execute_ifc_operator``.

The framework wraps every ``tool.Ifc.Operator._execute`` call between
``ifc_file.begin_transaction()`` and ``ifc_file.end_transaction()``. When
``_execute`` raises after at least one ``ifcopenshell.api.*`` mutation
has been captured, the user is in a partial state (IFC mutated, Blender
side stale) and the framework surfaces a WARNING naming Ctrl+Z so the
recovery path is discoverable instead of buried behind a raw traceback.

The contract has three parts pinned here:

1. ``ifcopenshell.file.Transaction.operations`` is a public list and is
   the introspection idiom the framework relies on.
2. The WARNING fires only when ``_execute`` raised AND the transaction
   captured at least one operation.
3. A successful ``_execute`` never emits the WARNING regardless of
   whether IFC was mutated."""

from unittest import mock

import pytest

pytestmark = pytest.mark.misc


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


@pytest.fixture
def fresh_ifc():
    """Set up a fresh ``ifcopenshell.file`` as ``IfcStore.file`` and tear
    it down afterwards. Each test gets a virgin transaction state."""
    import ifcopenshell

    from bonsai.bim.ifc import IfcStore

    previous = IfcStore.file
    previous_transaction = IfcStore.current_transaction
    IfcStore.file = ifcopenshell.file(schema="IFC4")
    IfcStore.current_transaction = ""
    try:
        yield IfcStore.file
    finally:
        IfcStore.file = previous
        IfcStore.current_transaction = previous_transaction


@pytest.fixture
def neutralised_framework():
    """Patch the side-effect-heavy helpers in ``IfcStore.execute_ifc_operator``
    so a bare unit test can drive it without a populated Scene / props /
    decorator handlers."""
    with mock.patch("bonsai.bim.ifc.tool.Blender.get_bim_props") as get_props, mock.patch(
        "bonsai.bim.handler.refresh_ui_data"
    ), mock.patch("bonsai.bim.ifc.tool.Parametric.refresh_post_commit"), mock.patch(
        "bonsai.bim.ifc.IfcStore.add_transaction_operation"
    ), mock.patch(
        "bonsai.bim.ifc.IfcStore.begin_transaction"
    ), mock.patch(
        "bonsai.bim.ifc.IfcStore.end_transaction"
    ), mock.patch(
        "bonsai.bim.ifc.IfcStore.get_ifc_file_undo_callback", return_value=lambda data: True
    ):
        get_props.return_value = mock.Mock(is_dirty=False)
        yield


def _make_operator(execute_callback):
    """Build a ``Mock`` operator that satisfies the attribute reads the
    framework performs (``bl_idname``, ``_execute``, ``report``, etc.)."""
    op = mock.Mock(spec=["bl_idname", "_execute", "_invoke", "_modal", "report", "transaction_key"])
    op.bl_idname = "bim.test_partial_state"
    op._execute = execute_callback
    return op


def _mutate_ifc():
    """Single ``ifcopenshell.api.*`` call so the transaction captures at
    least one operation. ``project.create_file`` would not work here since
    it replaces the file; pick a small entity mutation that always lands."""
    import ifcopenshell.api.owner

    from bonsai.bim.ifc import IfcStore

    ifcopenshell.api.owner.add_person(IfcStore.get_file())


def test_transaction_operations_is_empty_until_first_api_call(fresh_ifc):
    """Pin the introspection contract the framework relies on:
    ``Transaction.operations`` is empty after ``begin_transaction()`` and
    populated by any ``ifcopenshell.api.*`` call."""
    fresh_ifc.begin_transaction()
    assert fresh_ifc.transaction is not None
    assert fresh_ifc.transaction.operations == []

    _mutate_ifc()

    assert len(fresh_ifc.transaction.operations) > 0


def test_no_mutation_no_raise_no_warning(fresh_ifc, neutralised_framework):
    """Happy path: ``_execute`` does nothing, returns FINISHED.
    Framework MUST NOT emit the partial-state WARNING."""
    from bonsai.bim.ifc import IfcStore

    op = _make_operator(execute_callback=lambda context: {"FINISHED"})
    IfcStore.execute_ifc_operator(op, context=mock.Mock())

    for call in op.report.call_args_list:
        assert "Ctrl+Z" not in call.args[1], "partial-state WARNING fired on a clean success path"


def test_raise_before_mutation_no_warning(fresh_ifc, neutralised_framework):
    """``_execute`` raises before any IFC mutation. The transaction has no
    operations → no partial state → no WARNING."""
    from bonsai.bim.ifc import IfcStore

    def _raise_immediately(context):
        raise RuntimeError("kaboom")

    op = _make_operator(execute_callback=_raise_immediately)
    with pytest.raises(RuntimeError, match="kaboom"):
        IfcStore.execute_ifc_operator(op, context=mock.Mock())

    for call in op.report.call_args_list:
        assert "Ctrl+Z" not in call.args[1], "partial-state WARNING fired without any mutation"


def test_mutation_then_success_no_warning(fresh_ifc, neutralised_framework):
    """Real mutation, normal FINISHED return. WARNING is exception-path
    only and MUST NOT fire on a clean success."""
    from bonsai.bim.ifc import IfcStore

    def _mutate_and_finish(context):
        _mutate_ifc()
        return {"FINISHED"}

    op = _make_operator(execute_callback=_mutate_and_finish)
    IfcStore.execute_ifc_operator(op, context=mock.Mock())

    for call in op.report.call_args_list:
        assert "Ctrl+Z" not in call.args[1], "partial-state WARNING fired on a successful mutation"


def test_mutation_then_raise_emits_warning(fresh_ifc, neutralised_framework):
    """The contract this whole change exists for: mutate, then raise.
    Framework MUST emit a WARNING naming Ctrl+Z before the exception
    re-raises into Blender's normal operator error flow."""
    from bonsai.bim.ifc import IfcStore

    def _mutate_then_raise(context):
        _mutate_ifc()
        raise RuntimeError("rebuild failed after IFC mutation")

    op = _make_operator(execute_callback=_mutate_then_raise)
    with pytest.raises(RuntimeError, match="rebuild failed"):
        IfcStore.execute_ifc_operator(op, context=mock.Mock())

    warning_calls = [
        call
        for call in op.report.call_args_list
        if call.args and call.args[0] == {"WARNING"} and "Ctrl+Z" in call.args[1]
    ]
    assert (
        len(warning_calls) == 1
    ), f"expected exactly one partial-state WARNING with Ctrl+Z guidance, got: {op.report.call_args_list}"


def test_mutation_then_raise_pushes_blender_undo_step(fresh_ifc, neutralised_framework):
    """A raised operator does not get an automatic Blender undo step (same gap
    as the CANCELLED-modal path). The framework pushes one explicitly so the
    Ctrl+Z the WARNING advertises actually rewinds the partial mutation."""
    from bonsai.bim.ifc import IfcStore

    def _mutate_then_raise(context):
        _mutate_ifc()
        raise RuntimeError("rebuild failed after IFC mutation")

    op = _make_operator(execute_callback=_mutate_then_raise)
    with mock.patch("bonsai.bim.ifc.bpy.ops", new=mock.Mock()) as bpy_ops:
        undo_push = bpy_ops.ed.undo_push
        with pytest.raises(RuntimeError, match="rebuild failed"):
            IfcStore.execute_ifc_operator(op, context=mock.Mock())

    assert undo_push.call_count == 1, f"expected exactly one undo_push, got {undo_push.call_count}"
    pushed_message = undo_push.call_args.kwargs.get("message", "")
    assert op.bl_idname in pushed_message, f"undo step message should name the operator, got: {pushed_message!r}"


def test_raise_before_mutation_does_not_push_undo_step(fresh_ifc, neutralised_framework):
    """No mutation captured → nothing to recover → no recovery undo step.
    Avoids polluting the undo history with no-op recovery snapshots."""
    from bonsai.bim.ifc import IfcStore

    def _raise_immediately(context):
        raise RuntimeError("kaboom")

    op = _make_operator(execute_callback=_raise_immediately)
    with mock.patch("bonsai.bim.ifc.bpy.ops", new=mock.Mock()) as bpy_ops:
        undo_push = bpy_ops.ed.undo_push
        with pytest.raises(RuntimeError, match="kaboom"):
            IfcStore.execute_ifc_operator(op, context=mock.Mock())

    assert undo_push.call_count == 0, "undo_push fired on a non-partial-state raise"
