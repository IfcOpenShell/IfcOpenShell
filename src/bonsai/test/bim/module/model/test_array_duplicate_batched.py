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

"""Tests for the batched array-duplicate path.

`tool.Geometry.duplicate_ifc_object_n_times` lifts the per-call overhead of
`duplicate_ifc_objects` (snapshot, UI refresh, decorator reload, select
flips) out of the per-child loop in `_regenerate_array_body`. These tests
pin three contracts:

1. N-way batched duplicate produces N distinct entities mapped from the
   source under `old_to_new[source_element]`, and the source object stays
   selected throughout (no per-iteration deselect).
2. Per-layer batching collapses the N independent UI refreshes into one.
3. End-to-end array regen still yields the same number and shape of
   children as the per-call baseline."""

import json
from unittest.mock import patch

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


def _build_actuator(name: str = "Actuator") -> tuple[bpy.types.Object, ifcopenshell.entity_instance]:
    """Minimal IfcActuator + cube — matches the test_array_batch_recut.py shape."""
    bpy.ops.bim.create_project()
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    obj.name = name
    rprops = tool.Root.get_root_props()
    rprops.ifc_product = "IfcElement"
    bpy.ops.bim.assign_class(ifc_class="IfcActuator", predefined_type="ELECTRICACTUATOR", userdefined_type="")
    element = tool.Ifc.get_entity(obj)
    return obj, element


def _build_actuator_with_array_pset(
    count: int, x: float = 1.0
) -> tuple[bpy.types.Object, ifcopenshell.entity_instance, list[dict]]:
    obj, element = _build_actuator()
    parent_data = [
        {
            "children": [],
            "count": count,
            "method": "OFFSET",
            "x": x,
            "y": 0.0,
            "z": 0.0,
            "use_local_space": False,
            "sync_children": False,
        }
    ]
    pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_Array")
    ifcopenshell.api.pset.edit_pset(
        tool.Ifc.get(),
        pset=pset,
        properties={"Data": json.dumps(parent_data), "Parent": element.GlobalId},
    )
    return obj, element, parent_data


class TestDuplicateIfcObjectNTimes(NewFile):
    def test_returns_empty_dict_for_zero_count(self):
        obj, _ = _build_actuator()
        result = tool.Geometry.duplicate_ifc_object_n_times(obj, 0)
        assert result == {}

    def test_returns_empty_dict_for_negative_count(self):
        obj, _ = _build_actuator()
        result = tool.Geometry.duplicate_ifc_object_n_times(obj, -3)
        assert result == {}

    def test_produces_n_distinct_entities(self):
        obj, element = _build_actuator()
        result = tool.Geometry.duplicate_ifc_object_n_times(obj, 5)
        new_entities = result.get(element)
        assert new_entities is not None
        assert len(new_entities) == 5
        assert len({e.id() for e in new_entities}) == 5
        for new_entity in new_entities:
            assert new_entity.is_a("IfcActuator")
            assert new_entity.GlobalId != element.GlobalId

    def test_source_stays_selected_after_batch(self):
        obj, _ = _build_actuator()
        obj.select_set(True)
        tool.Geometry.duplicate_ifc_object_n_times(obj, 4)
        assert obj in bpy.context.selected_objects, "source object must remain selected across batched duplicates"

    def test_each_new_entity_has_blender_object(self):
        obj, element = _build_actuator()
        result = tool.Geometry.duplicate_ifc_object_n_times(obj, 3)
        for new_entity in result[element]:
            new_obj = tool.Ifc.get_object(new_entity)
            assert new_obj is not None
            assert new_obj is not obj


class TestBatchedRefreshUIDataCallCount(NewFile):
    def test_n_times_calls_refresh_ui_data_once(self):
        obj, _ = _build_actuator()
        with patch("bonsai.bim.handler.refresh_ui_data") as refresh_mock:
            tool.Geometry.duplicate_ifc_object_n_times(obj, 8)
        assert (
            refresh_mock.call_count == 1
        ), f"batched 8-way duplicate must call refresh_ui_data once, got {refresh_mock.call_count}"

    def test_n_times_calls_reload_grid_decorator_once(self):
        obj, _ = _build_actuator()
        with patch.object(tool.Root, "reload_grid_decorator") as reload_mock:
            tool.Geometry.duplicate_ifc_object_n_times(obj, 8)
        assert reload_mock.call_count == 1


class TestRegenerateArrayEndToEnd(NewFile):
    def test_regenerate_array_creates_expected_children(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=8)
        bpy.context.view_layer.objects.active = obj
        tool.Model.regenerate_array(obj, parent_data)

        layer = parent_data[0]
        assert len(layer["children"]) == 7, "8-element array means 7 new children (parent + 7)"
        for child_guid in layer["children"]:
            child_element = tool.Ifc.get().by_guid(child_guid)
            assert child_element is not None
            assert child_element.is_a("IfcActuator")
            child_pset = ifcopenshell.util.element.get_pset(child_element, "BBIM_Array")
            assert child_pset is not None
            assert child_pset["Parent"] == element.GlobalId

    def test_regenerate_array_parent_stays_selected(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=4)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        tool.Model.regenerate_array(obj, parent_data)
        assert (
            obj in bpy.context.selected_objects
        ), "regenerate_array must leave parent_obj selected on return (post-condition)"

    def test_regen_operator_leaves_only_parent_selected_and_active(self):
        """Post-condition parity between grow and shrink for the user-facing
        ``bim.regenerate_array`` operator: only the parent is selected + active;
        every child is deselected. Pre-fix the grow path left new children
        selected, creating inconsistency with the shrink path.

        Scoped to the operator, not the tool method — ``remove_array`` and
        ``apply_array`` also invoke ``tool.Model.regenerate_array`` internally
        but expect a different post-selection state (children stay selected
        for user follow-up work)."""
        obj, element, parent_data = _build_actuator_with_array_pset(count=6)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.regenerate_array()

        assert obj in bpy.context.selected_objects
        assert bpy.context.view_layer.objects.active is obj
        parent_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        parent_data_after = json.loads(parent_pset["Data"])
        for child_guid in parent_data_after[0]["children"]:
            child_element = tool.Ifc.get().by_guid(child_guid)
            child_obj = tool.Ifc.get_object(child_element)
            assert (
                child_obj not in bpy.context.selected_objects
            ), f"child {child_obj.name} must be deselected on regenerate_array return"

    def test_regen_operator_after_shrink_still_leaves_only_parent_selected(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=6)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.bim.regenerate_array()

        parent_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        arrays = json.loads(parent_pset["Data"])
        arrays[0]["count"] = 3
        pset_entity = tool.Ifc.get().by_id(parent_pset["id"])
        ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset_entity, properties={"Data": json.dumps(arrays)})
        bpy.ops.bim.regenerate_array()

        assert obj in bpy.context.selected_objects
        assert bpy.context.view_layer.objects.active is obj
        parent_pset = ifcopenshell.util.element.get_pset(element, "BBIM_Array")
        arrays_after = json.loads(parent_pset["Data"])
        for child_guid in arrays_after[0]["children"]:
            child_element = tool.Ifc.get().by_guid(child_guid)
            child_obj = tool.Ifc.get_object(child_element)
            assert child_obj not in bpy.context.selected_objects

    def test_regenerate_array_child_positions_match_offset(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=4, x=2.5)
        bpy.context.view_layer.objects.active = obj
        parent_x = obj.matrix_world.translation.x
        tool.Model.regenerate_array(obj, parent_data)

        layer = parent_data[0]
        for i, child_guid in enumerate(layer["children"], start=1):
            child_element = tool.Ifc.get().by_guid(child_guid)
            child_obj = tool.Ifc.get_object(child_element)
            expected_x = parent_x + 2.5 * i
            assert child_obj.matrix_world.translation.x == pytest.approx(
                expected_x
            ), f"child {i}: expected x≈{expected_x}, got {child_obj.matrix_world.translation.x}"


class TestRegenerateArrayUIRefreshCoalesces(NewFile):
    def test_n_children_grow_calls_refresh_ui_data_once_per_layer(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=8)
        bpy.context.view_layer.objects.active = obj
        with patch("bonsai.bim.handler.refresh_ui_data") as refresh_mock:
            tool.Model.regenerate_array(obj, parent_data)
        assert refresh_mock.call_count == 1, (
            "growing an array layer from 0 to 7 children must call refresh_ui_data once, "
            f"got {refresh_mock.call_count}"
        )

    def test_n_children_grow_calls_reload_grid_decorator_once_per_layer(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=8)
        bpy.context.view_layer.objects.active = obj
        with patch.object(tool.Root, "reload_grid_decorator") as reload_mock:
            tool.Model.regenerate_array(obj, parent_data)
        assert reload_mock.call_count == 1


class TestRecreateAggregateIteratesAllNew(NewFile):
    """Pins the [0]-indexing sweep in tool/root.py recreate_aggregate. When the
    new-list has N>1 entries (the batched-duplicate shape), every entry must be
    aggregate-assigned, not just new[0]."""

    def test_iterates_assign_object_per_new_entity_when_old_has_aggregate(self):
        from unittest.mock import Mock

        old_assembly = Mock()
        old_assembly.is_a = lambda c: c == "IfcElementAssembly"
        old_parent_aggregate = Mock()
        old_parent_aggregate.is_a = lambda c: False

        new_assemblies = [Mock(), Mock(), Mock()]
        new_parent_aggregate = [Mock()]

        old_to_new = {old_assembly: new_assemblies, old_parent_aggregate: new_parent_aggregate}

        with patch(
            "ifcopenshell.util.element.get_aggregate",
            side_effect=lambda e: old_parent_aggregate if e is old_assembly else None,
        ), patch("bonsai.core.aggregate.assign_object") as assign_mock, patch(
            "ifcopenshell.util.element.get_pset", return_value=None
        ), patch.object(
            tool.Ifc, "get_object", side_effect=lambda e: Mock(spec=bpy.types.Object)
        ), patch.object(
            tool.Blender, "select_and_activate_single_object"
        ):
            tool.Root.recreate_aggregate(old_to_new)

        assert (
            assign_mock.call_count == 3
        ), f"recreate_aggregate must assign each of N new entities (not just new[0]); got {assign_mock.call_count}"

    def test_iterates_unassign_object_per_new_entity_when_aggregate_missing(self):
        from unittest.mock import Mock

        old_assembly = Mock()
        old_assembly.is_a = lambda c: c == "IfcElementAssembly"
        old_parent_aggregate = Mock()

        new_assemblies = [Mock(), Mock(), Mock()]
        old_to_new = {old_assembly: new_assemblies}  # parent aggregate NOT in old_to_new

        with patch(
            "ifcopenshell.util.element.get_aggregate",
            side_effect=lambda e: old_parent_aggregate if e is old_assembly else None,
        ), patch("bonsai.core.aggregate.unassign_object") as unassign_mock, patch.object(
            tool.Ifc, "get_object", side_effect=lambda e: Mock(spec=bpy.types.Object)
        ):
            tool.Root.recreate_aggregate(old_to_new)

        assert unassign_mock.call_count == 3, (
            f"recreate_aggregate must unassign each of N new entities when parent aggregate is missing; "
            f"got {unassign_mock.call_count}"
        )


class TestRecreateConnectionsZipsPairs(NewFile):
    """Pins the [0]-indexing sweep in tool/duplicate.py recreate_connections. When
    both sides of a connection are duplicated N times, zip-pair the N new
    relating with N new related; when only one side is duplicated, skip."""

    def _make_connection_data(self):
        from unittest.mock import Mock

        from bonsai.tool.duplicate import ConnectionRecord

        return ConnectionRecord(
            type="path",
            relating_element=Mock(),
            related_element=Mock(),
            relating_connection_type="ATSTART",
            related_connection_type="ATEND",
            relating_priorities=[],
            related_priorities=[],
        )

    def test_zips_n_pairs_when_both_sides_duplicated(self):
        from unittest.mock import Mock

        data = self._make_connection_data()
        old_to_new = {
            data.relating_element: [Mock(), Mock(), Mock()],
            data.related_element: [Mock(), Mock(), Mock()],
        }
        relationship = {Mock(): data}

        with patch.object(tool.Ifc, "run", return_value=None) as run_mock:
            tool.Duplicate.recreate_connections(relationship, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "geometry.connect_path"]
        assert (
            len(connect_calls) == 3
        ), f"zip-pair must create 3 connect_path calls for 3-vs-3 batched duplicate; got {len(connect_calls)}"

    def test_skips_when_other_side_not_duplicated(self):
        from unittest.mock import Mock

        data = self._make_connection_data()
        # Only relating side is in old_to_new; related side was NOT duplicated.
        old_to_new = {data.relating_element: [Mock(), Mock(), Mock()]}
        relationship = {Mock(): data}

        with patch.object(tool.Ifc, "run", return_value=None) as run_mock:
            tool.Duplicate.recreate_connections(relationship, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "geometry.connect_path"]
        assert (
            connect_calls == []
        ), "when only one side of a connection is in old_to_new, no connections should be recreated"

    def test_single_pair_case_unchanged(self):
        """Pre-sweep behavior (1 source -> 1 new) must still work — zip with two 1-element lists."""
        from unittest.mock import Mock

        data = self._make_connection_data()
        old_to_new = {
            data.relating_element: [Mock()],
            data.related_element: [Mock()],
        }
        relationship = {Mock(): data}

        with patch.object(tool.Ifc, "run", return_value=None) as run_mock:
            tool.Duplicate.recreate_connections(relationship, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "geometry.connect_path"]
        assert len(connect_calls) == 1


class TestRecalculateWallsWithNewConnections(NewFile):
    """Pins the post-connection wall recalc: after ``recreate_connections``
    wires new IfcRelConnectsPathElements onto duplicated walls, the wall
    bodies must be re-recalculated because the in-loop ``regenerate_wall``
    fired before the connections existed. Otherwise the junction geometry
    stays stale and the user has to manually regen."""

    def test_walls_with_new_connections_are_recalculated(self):
        from unittest.mock import Mock

        wall_new = Mock()
        wall_new.is_a = lambda c: c == "IfcWall"
        wall_new.ConnectedTo = [Mock()]
        wall_new.ConnectedFrom = []

        wall_obj = Mock(spec=bpy.types.Object)
        old_to_new = {Mock(): [wall_new]}

        with patch.object(tool.Ifc, "get_object", return_value=wall_obj), patch.object(
            tool.Model, "recalculate_walls"
        ) as recalc_mock:
            tool.Geometry._recalculate_walls_with_new_connections(old_to_new)

        assert recalc_mock.call_count == 1
        assert recalc_mock.call_args.args[0] == [wall_obj]

    def test_walls_without_connections_are_skipped(self):
        from unittest.mock import Mock

        wall_new = Mock()
        wall_new.is_a = lambda c: c == "IfcWall"
        wall_new.ConnectedTo = []
        wall_new.ConnectedFrom = []

        old_to_new = {Mock(): [wall_new]}

        with patch.object(tool.Ifc, "get_object", return_value=Mock(spec=bpy.types.Object)), patch.object(
            tool.Model, "recalculate_walls"
        ) as recalc_mock:
            tool.Geometry._recalculate_walls_with_new_connections(old_to_new)

        assert recalc_mock.call_count == 0, "walls with no new connections must not trigger a recalc pass"

    def test_non_wall_entities_are_skipped(self):
        from unittest.mock import Mock

        actuator_new = Mock()
        actuator_new.is_a = lambda c: c == "IfcActuator"
        actuator_new.ConnectedTo = [Mock()]

        old_to_new = {Mock(): [actuator_new]}

        with patch.object(tool.Ifc, "get_object", return_value=Mock(spec=bpy.types.Object)), patch.object(
            tool.Model, "recalculate_walls"
        ) as recalc_mock:
            tool.Geometry._recalculate_walls_with_new_connections(old_to_new)

        assert recalc_mock.call_count == 0

    def test_multiple_new_walls_collected_into_one_call(self):
        from unittest.mock import Mock

        wall_a_new = Mock()
        wall_a_new.is_a = lambda c: c == "IfcWall"
        wall_a_new.ConnectedTo = [Mock()]
        wall_a_new.ConnectedFrom = []
        wall_b_new = Mock()
        wall_b_new.is_a = lambda c: c == "IfcWall"
        wall_b_new.ConnectedTo = []
        wall_b_new.ConnectedFrom = [Mock()]

        objs = {wall_a_new: Mock(spec=bpy.types.Object), wall_b_new: Mock(spec=bpy.types.Object)}
        old_to_new = {Mock(): [wall_a_new], Mock(): [wall_b_new]}

        with patch.object(tool.Ifc, "get_object", side_effect=lambda e: objs.get(e)), patch.object(
            tool.Model, "recalculate_walls"
        ) as recalc_mock:
            tool.Geometry._recalculate_walls_with_new_connections(old_to_new)

        assert recalc_mock.call_count == 1
        assert set(recalc_mock.call_args.args[0]) == {objs[wall_a_new], objs[wall_b_new]}


class TestMEPActionGuardsAgainstArrayChildren(NewFile):
    """Pins the array-child guards on the three MEP-action visibility helpers.
    Writable MEP actions (add fitting, remove terminal, join, re-edit bend)
    applied to an array child get wiped by the next regen — gating the icons
    at the visibility layer prevents that footgun."""

    def test_active_is_flow_segment_returns_false_for_array_child(self):
        from unittest.mock import Mock

        from bonsai.bim.module.model.mep import _active_is_flow_segment

        obj = Mock(spec=bpy.types.Object)
        element = Mock()
        element.is_a = lambda c: c == "IfcFlowSegment"

        with patch.object(tool.Ifc, "get_entity", return_value=element), patch.object(
            tool.Array, "is_array_child", return_value=True
        ), patch.object(tool.System, "has_parametric_body", return_value=True):
            assert _active_is_flow_segment(obj) is False

    def test_active_is_flow_segment_true_for_non_array_parent(self):
        from unittest.mock import Mock

        from bonsai.bim.module.model.mep import _active_is_flow_segment

        obj = Mock(spec=bpy.types.Object)
        element = Mock()
        element.is_a = lambda c: c == "IfcFlowSegment"

        with patch.object(tool.Ifc, "get_entity", return_value=element), patch.object(
            tool.Array, "is_array_child", return_value=False
        ), patch.object(tool.System, "has_parametric_body", return_value=True):
            assert _active_is_flow_segment(obj) is True

    def test_active_is_bend_fitting_returns_false_for_array_child(self):
        from unittest.mock import Mock

        from bonsai.bim.module.model.mep import _active_is_bend_fitting

        obj = Mock(spec=bpy.types.Object)
        element = Mock()

        with patch.object(tool.Ifc, "get_entity", return_value=element), patch(
            "bonsai.bim.module.model.mep._is_bend_fitting", return_value=True
        ), patch.object(tool.Array, "is_array_child", return_value=True):
            assert _active_is_bend_fitting(obj) is False

    def test_n_mep_selected_returns_false_when_any_selected_is_array_child(self):
        from unittest.mock import Mock

        from bonsai.bim.module.model.mep import _n_mep_selected

        obj_a = Mock(spec=bpy.types.Object)
        obj_b = Mock(spec=bpy.types.Object)
        element_a = Mock()
        element_b = Mock()

        def is_array_child(el):
            return el is element_b

        with patch.object(tool.Blender, "get_selected_objects", return_value=[obj_a, obj_b]), patch.object(
            tool.Ifc, "get_entity", side_effect=lambda o: element_a if o is obj_a else element_b
        ), patch.object(tool.System, "is_mep_element", return_value=True), patch.object(
            tool.Array, "is_array_child", side_effect=is_array_child
        ):
            assert _n_mep_selected(2) is False


class TestSelectOnlyParent(NewFile):
    """Pins ``tool.Array.select_only_parent`` — the shared helper wired into
    both ``bim.regenerate_array`` and ``bim.finish_editing_array`` so the
    grow / shrink / edit-commit paths converge on the same post-condition:
    only the parent is selected + active."""

    def test_deselects_children_selects_and_activates_parent(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=4)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        tool.Model.regenerate_array(obj, parent_data)
        for child_guid in parent_data[0]["children"]:
            child_element = tool.Ifc.get().by_guid(child_guid)
            child_obj = tool.Ifc.get_object(child_element)
            child_obj.select_set(True)

        tool.Array.select_only_parent(obj, bpy.context)

        assert obj in bpy.context.selected_objects
        assert bpy.context.view_layer.objects.active is obj
        for child_guid in parent_data[0]["children"]:
            child_element = tool.Ifc.get().by_guid(child_guid)
            child_obj = tool.Ifc.get_object(child_element)
            assert child_obj not in bpy.context.selected_objects


class TestIsArrayChild(NewFile):
    """Pins ``tool.Array.is_array_child`` — the light helper used by the port
    decorator (and any future per-element guard) to skip array children."""

    def test_returns_false_when_no_bbim_array_pset(self):
        from unittest.mock import Mock

        element = Mock()
        with patch("ifcopenshell.util.element.get_pset", return_value=None):
            assert tool.Array.is_array_child(element) is False

    def test_returns_false_on_the_array_parent_itself(self):
        from unittest.mock import Mock

        element = Mock()
        element.GlobalId = "PARENT_GUID"
        with patch("ifcopenshell.util.element.get_pset", return_value={"Parent": "PARENT_GUID"}):
            assert tool.Array.is_array_child(element) is False

    def test_returns_true_when_parent_guid_points_elsewhere(self):
        from unittest.mock import Mock

        element = Mock()
        element.GlobalId = "CHILD_GUID"
        with patch("ifcopenshell.util.element.get_pset", return_value={"Parent": "PARENT_GUID"}):
            assert tool.Array.is_array_child(element) is True


class TestOrphanArrayChildPrune(NewFile):
    """Outliner / keyboard delete of a Bonsai-managed array child bypasses
    ``bim.delete``'s cascade, leaving the IFC entity and its opening / filling
    refs behind. Regen must prune these orphans before the main loop or the
    stale registry entry corrupts the ``batch_host_recut`` drain."""

    def test_orphan_ifc_entity_pruned_from_children_list(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=4)
        bpy.context.view_layer.objects.active = obj
        tool.Model.regenerate_array(obj, parent_data)
        assert len(parent_data[0]["children"]) == 3

        orphan_guid = parent_data[0]["children"][1]
        orphan_element = tool.Ifc.get().by_guid(orphan_guid)
        orphan_obj = tool.Ifc.get_object(orphan_element)
        assert orphan_obj is not None
        bpy.data.objects.remove(orphan_obj, do_unlink=True)

        tool.Model.regenerate_array(obj, parent_data)

        assert (
            orphan_guid not in parent_data[0]["children"]
        ), "orphan GUID must be pruned from array['children'] once its Blender object is dead"
        try:
            still_there = tool.Ifc.get().by_guid(orphan_guid)
        except RuntimeError:
            still_there = None
        assert still_there is None, "orphan IFC entity must be cascade-removed, not left as a leak"

    def test_regen_completes_when_child_deleted_outside_bim_cascade(self):
        obj, element, parent_data = _build_actuator_with_array_pset(count=6)
        bpy.context.view_layer.objects.active = obj
        tool.Model.regenerate_array(obj, parent_data)

        victim_guid = parent_data[0]["children"][2]
        victim_element = tool.Ifc.get().by_guid(victim_guid)
        victim_obj = tool.Ifc.get_object(victim_element)
        bpy.data.objects.remove(victim_obj, do_unlink=True)

        tool.Model.regenerate_array(obj, parent_data)

        assert len(parent_data[0]["children"]) == 5, "regen must rebuild to the target count after pruning the orphan"
        for guid in parent_data[0]["children"]:
            child = tool.Ifc.get().by_guid(guid)
            child_obj = tool.Ifc.get_object(child)
            assert child_obj is not None, "every surviving child must have a live Blender object"


class TestRecreatePortConnectionsZipsPairs(NewFile):
    """Pins the [0]-indexing sweep in tool/duplicate.py recreate_port_connections.
    When both sides of a port-to-port connection are duplicated N times, the
    connection must be recreated on every pair of new siblings — not just the
    first. Matters for arrayed MEP segments (pipes / ducts / cables) where each
    child in the array should stay connected to its neighbour after regen."""

    def _make_snapshot(self, relating_element, records, port_counts):
        from bonsai.tool.duplicate import PortConnectionSnapshot

        return PortConnectionSnapshot(
            by_element={relating_element: records},
            port_counts=port_counts,
        )

    def _make_record(self, related_element, relating_port_index=0, related_port_index=0, direction="SOURCE"):
        from bonsai.tool.duplicate import PortConnectionRecord

        return PortConnectionRecord(
            relating_port_index=relating_port_index,
            related_element=related_element,
            related_port_index=related_port_index,
            direction=direction,
        )

    def test_zips_n_pairs_when_both_sides_duplicated(self):
        from unittest.mock import Mock

        relating_old = Mock()
        related_old = Mock()
        record = self._make_record(related_old)
        snapshot = self._make_snapshot(relating_old, [record], port_counts={})

        old_to_new = {
            relating_old: [Mock(), Mock(), Mock()],
            related_old: [Mock(), Mock(), Mock()],
        }

        fake_ports = [Mock(), Mock()]
        with patch.object(tool.System, "get_ports", return_value=fake_ports), patch.object(
            tool.Ifc, "run", return_value=None
        ) as run_mock:
            tool.Duplicate.recreate_port_connections(snapshot, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "system.connect_port"]
        assert (
            len(connect_calls) == 3
        ), f"zip-pair must create 3 connect_port calls for 3-vs-3 batched MEP duplicate; got {len(connect_calls)}"

    def test_skips_when_other_side_not_duplicated(self):
        from unittest.mock import Mock

        relating_old = Mock()
        related_old = Mock()
        record = self._make_record(related_old)
        snapshot = self._make_snapshot(relating_old, [record], port_counts={})

        # Only relating side is in old_to_new.
        old_to_new = {relating_old: [Mock(), Mock(), Mock()]}

        with patch.object(tool.System, "get_ports", return_value=[Mock()]), patch.object(
            tool.Ifc, "run", return_value=None
        ) as run_mock:
            tool.Duplicate.recreate_port_connections(snapshot, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "system.connect_port"]
        assert connect_calls == [], "when only one side is in old_to_new, no port connections should be recreated"

    def test_single_pair_case_unchanged(self):
        """Pre-sweep behavior (1 source -> 1 new) must still work — zip with two 1-element lists."""
        from unittest.mock import Mock

        relating_old = Mock()
        related_old = Mock()
        record = self._make_record(related_old)
        snapshot = self._make_snapshot(relating_old, [record], port_counts={})

        old_to_new = {relating_old: [Mock()], related_old: [Mock()]}

        with patch.object(tool.System, "get_ports", return_value=[Mock()]), patch.object(
            tool.Ifc, "run", return_value=None
        ) as run_mock:
            tool.Duplicate.recreate_port_connections(snapshot, old_to_new)

        connect_calls = [c for c in run_mock.call_args_list if c.args and c.args[0] == "system.connect_port"]
        assert len(connect_calls) == 1
