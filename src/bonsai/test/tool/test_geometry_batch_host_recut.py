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

"""Coalescing tests for ``tool.Geometry.batch_host_recut``.

The opening/void/array recut paths fan out N host-mesh rebuilds per array of N
fillings — the CSG opening-subtraction inside ``switch_representation`` is the
most expensive geometry step in the addon. ``batch_host_recut`` queues
``recut_host`` + ``update_host_representation`` calls by voided element id and
drains each unique host once on the outermost exit. These tests pin the
queue/depth/drain contract that the call-site rewrites in subsequent phases
rely on."""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.geometry


@pytest.fixture(autouse=True)
def _reset_batch_state():
    from bonsai import tool

    saved_depth = tool.Geometry._host_batch_depth
    saved_recut = tool.Geometry._host_recut_queue
    saved_update = tool.Geometry._host_update_queue
    tool.Geometry._host_batch_depth = 0
    tool.Geometry._host_recut_queue = {}
    tool.Geometry._host_update_queue = {}
    yield
    tool.Geometry._host_batch_depth = saved_depth
    tool.Geometry._host_recut_queue = saved_recut
    tool.Geometry._host_update_queue = saved_update


def _mock_voided_obj(name: str, *, has_data: bool = True) -> Mock:
    obj = Mock()
    obj.name = name
    obj.data = Mock() if has_data else None
    return obj


def _mock_element(ifc_id: int) -> Mock:
    elem = Mock()
    elem.id.return_value = ifc_id
    return elem


def test_outside_batch_calls_switch_representation_directly():
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    representation = Mock()

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", return_value=_mock_element(42)
    ):
        tool.Geometry.recut_host(voided_obj, representation)

    assert recut.call_count == 1
    kwargs = recut.call_args.kwargs
    assert kwargs["obj"] is voided_obj
    assert kwargs["representation"] is representation


def test_inside_batch_queues_then_drains_once_on_exit():
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    representation = Mock()
    element = _mock_element(42)

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", return_value=element
    ), patch.object(tool.Geometry, "get_active_representation", return_value=representation):
        with tool.Geometry.batch_host_recut():
            for _ in range(5):
                tool.Geometry.recut_host(voided_obj, representation)
            assert recut.call_count == 0, "Inside the batch, no recuts should fire"
            assert tool.Geometry._host_batch_depth == 1
            assert len(tool.Geometry._host_recut_queue) == 1
        assert recut.call_count == 1, "Exactly one drain on outermost exit"


def test_two_different_hosts_drain_separately():
    from bonsai import tool

    obj_a = _mock_voided_obj("WallA")
    obj_b = _mock_voided_obj("WallB")
    elem_a = _mock_element(1)
    elem_b = _mock_element(2)
    rep = Mock()

    def get_entity(obj):
        return elem_a if obj is obj_a else elem_b

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", side_effect=get_entity
    ), patch.object(tool.Geometry, "get_active_representation", return_value=rep):
        with tool.Geometry.batch_host_recut():
            for _ in range(5):
                tool.Geometry.recut_host(obj_a, rep)
            for _ in range(3):
                tool.Geometry.recut_host(obj_b, rep)

    assert recut.call_count == 2
    drained_objs = [call.kwargs["obj"] for call in recut.call_args_list]
    assert set(drained_objs) == {obj_a, obj_b}


def test_nested_batches_only_outermost_drains():
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    rep = Mock()

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", return_value=_mock_element(1)
    ), patch.object(tool.Geometry, "get_active_representation", return_value=rep):
        with tool.Geometry.batch_host_recut():
            tool.Geometry.recut_host(voided_obj, rep)
            with tool.Geometry.batch_host_recut():
                tool.Geometry.recut_host(voided_obj, rep)
                assert recut.call_count == 0
            assert recut.call_count == 0, "Inner exit must not drain — outer batch still open"
        assert recut.call_count == 1


def test_stale_element_skipped_at_drain():
    """Host's IFC entity disappears between enqueue and drain. The dead entity
    must be skipped silently — not raise — so unrelated hosts in the same batch
    still get their recut."""
    from bonsai import tool

    dead_obj = _mock_voided_obj("Wall")
    rep = Mock()
    entity_state = {"alive": _mock_element(1)}

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", side_effect=lambda obj: entity_state["alive"]
    ), patch.object(tool.Geometry, "get_active_representation", return_value=rep):
        with tool.Geometry.batch_host_recut():
            tool.Geometry.recut_host(dead_obj, rep)
            entity_state["alive"] = None

    assert recut.call_count == 0


class _DeadStructRNA:
    """Simulates a Blender object whose StructRNA has been removed — every
    attribute access raises ReferenceError. Enqueue this as voided_obj to
    reproduce the outliner-mid-batch-delete crash."""

    def __getattr__(self, name):
        raise ReferenceError("StructRNA of type Object has been removed")

    def __bool__(self):
        raise ReferenceError("StructRNA of type Object has been removed")


def test_dead_structrna_recut_skipped_at_drain():
    """Blender object is deleted while the batch is open (outliner delete +
    manual DEL bypass the bim.delete cascade). The drain must skip it silently
    — not raise — so unrelated hosts in the same batch still get their recut."""
    from bonsai import tool

    dead_obj = _DeadStructRNA()
    live_obj = _mock_voided_obj("LiveWall")
    rep = Mock()

    def get_entity(obj):
        # Called only when the guard clears — for the dead ref, guard short-circuits first.
        return _mock_element(2)

    with patch("bonsai.core.geometry.switch_representation") as recut, patch.object(
        tool.Ifc, "get_entity", side_effect=get_entity
    ), patch.object(tool.Geometry, "get_active_representation", return_value=rep):
        with tool.Geometry.batch_host_recut():
            tool.Geometry._host_recut_queue[999] = (dead_obj, rep)
            tool.Geometry.recut_host(live_obj, rep)

    assert recut.call_count == 1, "live host must still get its recut despite a dead sibling in the queue"
    drained_obj = recut.call_args.kwargs["obj"]
    assert drained_obj is live_obj


def test_dead_structrna_update_skipped_at_drain():
    """Same guarantee for update_representation drain path."""
    from bonsai import tool

    dead_obj = _DeadStructRNA()
    live_obj = _mock_voided_obj("LiveWall")
    bpy_ops_mock = Mock()

    with patch("bonsai.tool.geometry.bpy.ops", new=bpy_ops_mock), patch.object(
        tool.Ifc, "get_entity", return_value=_mock_element(42)
    ), patch.object(tool.Geometry, "get_active_representation", return_value=Mock()):
        with tool.Geometry.batch_host_recut():
            tool.Geometry._host_update_queue[999] = dead_obj
            tool.Geometry.update_host_representation(live_obj)

    assert bpy_ops_mock.bim.update_representation.call_count == 1


def test_exception_inside_batch_still_resets_state():
    from bonsai import tool

    with patch("bonsai.core.geometry.switch_representation"):
        with pytest.raises(RuntimeError, match="boom"):
            with tool.Geometry.batch_host_recut():
                assert tool.Geometry._host_batch_depth == 1
                raise RuntimeError("boom")

    assert tool.Geometry._host_batch_depth == 0


def test_update_host_representation_outside_batch_fires_operator():
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    bpy_ops_mock = Mock()

    with patch("bonsai.tool.geometry.bpy.ops", new=bpy_ops_mock), patch.object(
        tool.Ifc, "get_entity", return_value=_mock_element(42)
    ):
        tool.Geometry.update_host_representation(voided_obj)

    assert bpy_ops_mock.bim.update_representation.call_count == 1
    assert bpy_ops_mock.bim.update_representation.call_args.kwargs["obj"] == voided_obj.name


def test_update_host_representation_coalesces_inside_batch():
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    bpy_ops_mock = Mock()

    with patch("bonsai.tool.geometry.bpy.ops", new=bpy_ops_mock), patch.object(
        tool.Ifc, "get_entity", return_value=_mock_element(42)
    ), patch.object(tool.Geometry, "get_active_representation", return_value=Mock()):
        with tool.Geometry.batch_host_recut():
            for _ in range(5):
                tool.Geometry.update_host_representation(voided_obj)
            assert bpy_ops_mock.bim.update_representation.call_count == 0

    assert bpy_ops_mock.bim.update_representation.call_count == 1


def test_drain_order_update_before_recut():
    """The same host has both pending update + recut. update_representation must
    fire first so the Blender-mesh edits land in IFC before switch_representation
    re-tessellates from IFC. Reversed order would silently drop user edits."""
    from bonsai import tool

    voided_obj = _mock_voided_obj("Wall")
    rep = Mock()
    fire_log: list[str] = []
    bpy_ops_mock = Mock()
    bpy_ops_mock.bim.update_representation.side_effect = lambda **kw: fire_log.append("update")

    with patch("bonsai.tool.geometry.bpy.ops", new=bpy_ops_mock), patch(
        "bonsai.core.geometry.switch_representation", side_effect=lambda *a, **kw: fire_log.append("recut")
    ), patch.object(tool.Ifc, "get_entity", return_value=_mock_element(42)), patch.object(
        tool.Geometry, "get_active_representation", return_value=rep
    ):
        with tool.Geometry.batch_host_recut():
            tool.Geometry.recut_host(voided_obj, rep)
            tool.Geometry.update_host_representation(voided_obj)

    assert fire_log == ["update", "recut"]


def test_mixed_hosts_drain_grouped_by_phase():
    from bonsai import tool

    obj_a = _mock_voided_obj("WallA")
    obj_b = _mock_voided_obj("WallB")
    obj_c = _mock_voided_obj("WallC")
    elem_a, elem_b, elem_c = _mock_element(1), _mock_element(2), _mock_element(3)
    rep = Mock()

    def get_entity(obj):
        return {obj_a: elem_a, obj_b: elem_b, obj_c: elem_c}[obj]

    update_targets: list[str] = []
    recut_targets: list[Mock] = []
    bpy_ops_mock = Mock()
    bpy_ops_mock.bim.update_representation.side_effect = lambda **kw: update_targets.append(kw["obj"])

    with patch("bonsai.tool.geometry.bpy.ops", new=bpy_ops_mock), patch(
        "bonsai.core.geometry.switch_representation",
        side_effect=lambda *a, **kw: recut_targets.append(kw["obj"]),
    ), patch.object(tool.Ifc, "get_entity", side_effect=get_entity), patch.object(
        tool.Geometry, "get_active_representation", return_value=rep
    ):
        with tool.Geometry.batch_host_recut():
            tool.Geometry.update_host_representation(obj_a)
            tool.Geometry.recut_host(obj_b, rep)
            tool.Geometry.update_host_representation(obj_c)
            tool.Geometry.recut_host(obj_c, rep)

    assert sorted(update_targets) == sorted([obj_a.name, obj_c.name])
    assert set(recut_targets) == {obj_b, obj_c}
