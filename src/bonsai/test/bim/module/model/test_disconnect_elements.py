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

"""Behaviour tests for the unified ``bim.disconnect_elements`` operator and
``tool.Connection.find_rels`` registry.

Pin the dispatch contract: rels are found in either orientation; the kind
label drives cleanup (``path`` recreates both walls + resyncs drafts;
``element-top`` runs ``regenerate_wall_to_underside``); missing endpoints
report ERROR rather than crashing."""

from unittest.mock import MagicMock, Mock, patch

import pytest

import bonsai.tool as tool

pytestmark = pytest.mark.model


def _rel(klass: str, *, relating=None, related=None, description=None, rel_id: int = 0):
    rel = Mock()
    rel.is_a = lambda c: c == klass
    rel.RelatingElement = relating
    rel.RelatedElement = related
    rel.Description = description
    rel.id = lambda: rel_id
    return rel


def _elem(*, connected_to=(), connected_from=()):
    e = Mock()
    # Default is_a to False so the MEP-pair-fitting branch of find_rels
    # (which calls ``elem.is_a("IfcFlowSegment")``) early-outs on the
    # generic _elem stubs used by the wall-side dispatch tests. Test
    # cases that want is_a("IfcWall")-True explicitly override e.is_a.
    e.is_a = lambda _c: False
    e.ConnectedTo = list(connected_to)
    e.ConnectedFrom = list(connected_from)
    e.GlobalId = "GUID"
    return e


# ---------------------------------------------------------------------------
# tool.Connection.find_rels — registry behaviour
# ---------------------------------------------------------------------------


def test_find_rels_returns_path_rel_in_either_orientation():
    """The same wall pair can carry path rels authored with either orientation;
    find_rels must catch both."""
    elem_a = _elem()
    elem_b = _elem()
    rel_ab = _rel("IfcRelConnectsPathElements", related=elem_b, rel_id=1)
    rel_ba = _rel("IfcRelConnectsPathElements", relating=elem_b, rel_id=2)
    elem_a.ConnectedTo = [rel_ab]
    elem_a.ConnectedFrom = [rel_ba]

    rels = tool.Connection.find_rels(elem_a, elem_b)

    assert {r.id() for r, _ in rels} == {1, 2}
    assert all(k == "path" for _, k in rels)


def test_find_rels_classifies_top_element_rel_specifically():
    """IfcRelConnectsElements with Description=='TOP' is the rel kind
    extend_walls_to_underside creates. Tag it ``element-top`` so the
    operator can dispatch the regenerate-wall-to-underside cleanup."""
    wall = _elem()
    slab = _elem()
    rel = _rel("IfcRelConnectsElements", relating=slab, description="TOP", rel_id=1)
    wall.ConnectedFrom = [rel]

    rels = tool.Connection.find_rels(wall, slab)

    assert rels == [(rel, "element-top")]


def test_find_rels_classifies_non_top_element_rel_generically():
    """Other IfcRelConnectsElements descriptions don't get the TOP-specific
    cleanup. Tag as plain ``element`` so the operator just removes the rel."""
    elem_a = _elem()
    elem_b = _elem()
    rel = _rel("IfcRelConnectsElements", relating=elem_b, description="ATTACHMENT", rel_id=1)
    elem_a.ConnectedFrom = [rel]

    rels = tool.Connection.find_rels(elem_a, elem_b)

    assert rels == [(rel, "element")]


def test_find_rels_returns_empty_when_disconnected():
    elem_a = _elem()
    elem_b = _elem()
    assert tool.Connection.find_rels(elem_a, elem_b) == []


def test_find_rels_dedups_by_id():
    """A rel that surfaces on both ConnectedTo and ConnectedFrom (in
    pathological IFC files) should not be returned twice."""
    elem_a = _elem()
    elem_b = _elem()
    rel = _rel("IfcRelConnectsPathElements", related=elem_b, relating=elem_b, rel_id=1)
    elem_a.ConnectedTo = [rel]
    elem_a.ConnectedFrom = [rel]

    rels = tool.Connection.find_rels(elem_a, elem_b)

    assert len(rels) == 1


# ---------------------------------------------------------------------------
# tool.Connection.find_rels_for_element — single-element entry point
# ---------------------------------------------------------------------------


def test_find_rels_for_element_returns_kind_and_partner_per_rel():
    """Cascade-on-delete needs every rel touching one element plus the partner
    element on the other side of each rel — that's the cleanup target."""
    elem = _elem()
    partner_a = _elem()
    partner_b = _elem()
    rel_path = _rel("IfcRelConnectsPathElements", related=partner_a, rel_id=1)
    rel_top = _rel("IfcRelConnectsElements", relating=partner_b, description="TOP", rel_id=2)
    elem.ConnectedTo = [rel_path]
    elem.ConnectedFrom = [rel_top]

    result = tool.Connection.find_rels_for_element(elem)

    assert (rel_path, "path", partner_a) in result
    assert (rel_top, "element-top", partner_b) in result
    assert len(result) == 2


def test_find_rels_for_element_dedups_by_rel_id():
    elem = _elem()
    partner = _elem()
    rel = _rel("IfcRelConnectsPathElements", related=partner, relating=partner, rel_id=1)
    elem.ConnectedTo = [rel]
    elem.ConnectedFrom = [rel]

    result = tool.Connection.find_rels_for_element(elem)

    assert len(result) == 1


def test_find_rels_for_element_skips_rels_without_partner():
    """Defensive: a malformed rel missing the opposite-side attribute should not
    crash — record nothing for it rather than emit a (rel, kind, None) triple
    that would later trip a None-deref in the dispatch."""
    elem = _elem()
    bad = _rel("IfcRelConnectsPathElements", related=None, rel_id=1)
    elem.ConnectedTo = [bad]

    assert tool.Connection.find_rels_for_element(elem) == []


# ---------------------------------------------------------------------------
# tool.Connection.find_rels — MEP pair-fitting detection
# ---------------------------------------------------------------------------


def _mep(elem_id, *, klasses=("IfcFlowSegment",), predefined_type=None, ports=()):
    """Stand-in IFC element with port mocks and ``is_a`` short-circuits."""
    e = Mock()
    e.id = lambda: elem_id
    e.is_a = lambda c: c in klasses
    e.PredefinedType = predefined_type
    # Empty path / element rels so the find_rels prologue iterates cleanly
    # before reaching the MEP port-walk branch.
    e.ConnectedTo = []
    e.ConnectedFrom = []
    e._ports = list(ports)
    return e


def _port(port_id, owner, connected_to=None):
    p = Mock()
    p.id = lambda: port_id
    p._owner = owner
    p._connected_to = connected_to
    return p


def _patch_port_walk():
    """Patch the port helpers ``tool.System.find_bridging_fitting`` consumes
    so the mep-pair-fitting detection in ``find_rels`` can be exercised
    without a real IFC fixture. Three patches: ``get_ports`` and
    ``get_connected_port`` are ``tool.System`` classmethods that delegate
    to ``ifcopenshell.util.system``; ``get_port_element`` is called
    directly on ``ifcopenshell.util.system`` inside ``neighbours_at_ports``."""
    return (
        patch("bonsai.tool.system.System.get_ports", side_effect=lambda e: e._ports),
        patch(
            "bonsai.tool.system.System.get_connected_port",
            side_effect=lambda p: p._connected_to,
        ),
        patch(
            "bonsai.tool.system.ifcopenshell.util.system.get_port_element",
            side_effect=lambda p: p._owner,
        ),
    )


def test_find_rels_detects_segment_segment_bridging_fitting():
    """Two flow segments joined by a single bridging fitting must surface
    as ``(fitting, 'mep-pair-fitting')`` — the fitting whose deletion
    effects the disconnect."""
    fitting = _mep(99, klasses=("IfcFlowFitting", "IfcDistributionFlowElement"), predefined_type="BEND")
    seg_a = _mep(1)
    seg_b = _mep(2)

    a_port = _port(101, seg_a)
    b_port = _port(102, seg_b)
    f_port_a = _port(201, fitting, connected_to=a_port)
    f_port_b = _port(202, fitting, connected_to=b_port)
    a_port._connected_to = f_port_a
    b_port._connected_to = f_port_b

    seg_a._ports = [a_port]
    seg_b._ports = [b_port]
    fitting._ports = [f_port_a, f_port_b]

    with _patch_port_walk()[0], _patch_port_walk()[1], _patch_port_walk()[2]:
        rels = tool.Connection.find_rels(seg_a, seg_b)

    assert rels == [(fitting, "mep-pair-fitting")]


def test_find_rels_detects_segment_fitting_direct():
    """A segment + its directly-connected fitting also surface as the
    same kind, with the fitting itself as the deletion target."""
    fitting = _mep(99, klasses=("IfcFlowFitting", "IfcDistributionFlowElement"), predefined_type="BEND")
    seg = _mep(1)
    seg_port = _port(101, seg)
    f_port = _port(201, fitting, connected_to=seg_port)
    seg_port._connected_to = f_port
    seg._ports = [seg_port]
    fitting._ports = [f_port]

    with _patch_port_walk()[0], _patch_port_walk()[1], _patch_port_walk()[2]:
        rels = tool.Connection.find_rels(seg, fitting)

    assert rels == [(fitting, "mep-pair-fitting")]


def test_find_rels_skips_obstruction_fitting():
    """OBSTRUCTION fittings have a dedicated grow/shrink removal flow —
    they must not surface as a disconnect target."""
    obstruction = _mep(99, klasses=("IfcFlowFitting", "IfcDistributionFlowElement"), predefined_type="OBSTRUCTION")
    seg_a = _mep(1)
    seg_b = _mep(2)
    a_port = _port(101, seg_a)
    b_port = _port(102, seg_b)
    o_port_a = _port(201, obstruction, connected_to=a_port)
    o_port_b = _port(202, obstruction, connected_to=b_port)
    a_port._connected_to = o_port_a
    b_port._connected_to = o_port_b
    seg_a._ports = [a_port]
    seg_b._ports = [b_port]
    obstruction._ports = [o_port_a, o_port_b]

    with _patch_port_walk()[0], _patch_port_walk()[1], _patch_port_walk()[2]:
        assert tool.Connection.find_rels(seg_a, seg_b) == []


def test_find_rels_returns_empty_for_two_unrelated_mep_segments():
    """No bridging fitting, no detection."""
    seg_a = _mep(1)
    seg_b = _mep(2)
    seg_a._ports = []
    seg_b._ports = []
    with _patch_port_walk()[0], _patch_port_walk()[1], _patch_port_walk()[2]:
        assert tool.Connection.find_rels(seg_a, seg_b) == []


def test_find_rels_skips_non_mep_pair():
    """Walls don't have ports — find_rels must early-out before walking
    them as if they were MEP."""
    wall_a = Mock()
    wall_a.is_a = lambda c: c == "IfcWall"
    wall_a.ConnectedTo = []
    wall_a.ConnectedFrom = []
    wall_b = Mock()
    wall_b.is_a = lambda c: c == "IfcWall"
    wall_b.ConnectedTo = []
    wall_b.ConnectedFrom = []

    assert tool.Connection.find_rels(wall_a, wall_b) == []


# ---------------------------------------------------------------------------
# tool.Connection.find_rel — first-match convenience
# ---------------------------------------------------------------------------


def test_find_rel_returns_first_match_or_none_none():
    elem_a = _elem()
    elem_b = _elem()
    rel = _rel("IfcRelConnectsPathElements", related=elem_b, rel_id=1)
    elem_a.ConnectedTo = [rel]

    assert tool.Connection.find_rel(elem_a, elem_b) == (rel, "path")
    assert tool.Connection.find_rel(elem_a, _elem()) == (None, None)


# ---------------------------------------------------------------------------
# tool.Connection.orient_element_top — wall / slab orientation recovery
# ---------------------------------------------------------------------------


def test_orient_element_top_returns_wall_then_slab():
    """The TOP rel stores slab as relating + wall as related; orient_element_top
    figures out which input is which regardless of argument order."""
    wall = _elem()
    slab = _elem()
    rel = _rel("IfcRelConnectsElements", relating=slab, related=wall, description="TOP")

    assert tool.Connection.orient_element_top(rel, wall, slab) == (wall, slab)
    assert tool.Connection.orient_element_top(rel, slab, wall) == (wall, slab)


# ---------------------------------------------------------------------------
# bim.disconnect_elements — dispatch + cleanup
# ---------------------------------------------------------------------------


def _make_op(*, a_guid="A", b_guid="B"):
    op = Mock()
    op.element_a_guid = a_guid
    op.element_b_guid = b_guid
    op.report = Mock()
    return op


def test_disconnect_dispatches_one_call_per_rel():
    """Operator forwards every rel returned by find_rels to disconnect_rel,
    in order — the operator is a thin wrapper; per-kind cleanup logic lives
    in core.connection.disconnect_rel and is tested separately."""
    from bonsai.bim.module.model.wall import DisconnectElements

    elem_a = Mock()
    elem_b = Mock()
    rel1 = Mock()
    rel2 = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": elem_a, "B": elem_b}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels",
        return_value=[(rel1, "path"), (rel2, "element-top")],
    ), patch("bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel") as dispatch, patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=Mock()
    ), patch(
        "bonsai.bim.module.model.wall._resync_walls_after_mutation"
    ), patch(
        "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall", return_value=False
    ):
        DisconnectElements._perform(op, context=MagicMock())

    assert dispatch.call_count == 2
    # Both rels dispatch with elem=elem_a, partner=elem_b regardless of orientation
    # — orient_element_top inside disconnect_rel recovers the wall/slab roles.
    for call, expected_subject, expected_kind in zip(dispatch.call_args_list, [rel1, rel2], ["path", "element-top"]):
        kw = call.kwargs
        assert kw["subject"] is expected_subject
        assert kw["kind"] == expected_kind
        assert kw["elem"] is elem_a
        assert kw["partner"] is elem_b
    op.report.assert_not_called()


def test_disconnect_resyncs_path_objs_once_for_path_kind():
    """For path rels the operator collects both endpoint objects and resyncs
    drafts once at the end — a Blender-side concern that doesn't belong in
    the core dispatch."""
    from bonsai.bim.module.model.wall import DisconnectElements

    elem_a = Mock()
    elem_b = Mock()
    obj_a = Mock()
    obj_b = Mock()
    rel = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": elem_a, "B": elem_b}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "path")]
    ), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object",
        side_effect=lambda e: {elem_a: obj_a, elem_b: obj_b}[e],
    ), patch(
        "bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel"
    ), patch(
        "bonsai.bim.module.model.wall._resync_walls_after_mutation"
    ) as resync, patch(
        "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall", return_value=False
    ):
        DisconnectElements._perform(op, context=MagicMock())

    resync.assert_called_once_with([obj_a, obj_b])


def test_disconnect_skips_resync_for_non_path_kind():
    """element-top / element kinds don't need wall-draft resync — that's a
    path-specific concern (DumbWallJoiner geometry refresh)."""
    from bonsai.bim.module.model.wall import DisconnectElements

    elem_a = Mock()
    elem_b = Mock()
    rel = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": elem_a, "B": elem_b}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "element-top")]
    ), patch("bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=Mock()), patch(
        "bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel"
    ), patch(
        "bonsai.bim.module.model.wall._resync_walls_after_mutation"
    ) as resync, patch(
        "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall", return_value=False
    ):
        DisconnectElements._perform(op, context=MagicMock())

    resync.assert_not_called()


def test_disconnect_gizmo_direction_symmetry():
    """The wall-selected gizmo dispatches with element_a=wall, element_b=slab.
    The slab-selected gizmo dispatches with element_a=slab, element_b=wall.
    Both routes hit disconnect_rel with the same (rel, kind) pair — orientation
    recovery happens inside the dispatch, not at the operator layer."""
    from bonsai.bim.module.model.wall import DisconnectElements

    wall = Mock(name="wall")
    slab = Mock(name="slab")
    rel = Mock()

    ifc_file = MagicMock()
    op = _make_op()

    def _run_with_guids(a, b):
        ifc_file.by_guid.side_effect = lambda g: {a: wall if a == "WALL" else slab, b: slab if b == "SLAB" else wall}[g]
        op.element_a_guid = a
        op.element_b_guid = b
        with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
            "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "element-top")]
        ), patch("bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=Mock()), patch(
            "bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel"
        ) as dispatch, patch(
            "bonsai.bim.module.model.wall._resync_walls_after_mutation"
        ), patch(
            "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall", return_value=False
        ):
            DisconnectElements._perform(op, context=MagicMock())
        return dispatch.call_args.kwargs

    wall_first = _run_with_guids("WALL", "SLAB")
    slab_first = _run_with_guids("SLAB", "WALL")

    # disconnect_rel sees (rel, "element-top") in both runs; elem/partner swap
    # by argument order but orient_element_top inside disconnect_rel resolves
    # the wall/slab roles symmetrically.
    assert wall_first["subject"] is rel and slab_first["subject"] is rel
    assert wall_first["kind"] == slab_first["kind"] == "element-top"
    assert {wall_first["elem"], wall_first["partner"]} == {wall, slab}
    assert {slab_first["elem"], slab_first["partner"]} == {wall, slab}


def test_disconnect_reports_on_unknown_guids():
    from bonsai.bim.module.model.wall import DisconnectElements

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = RuntimeError("missing")
    op = _make_op(a_guid="MISSING_A", b_guid="MISSING_B")

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels"
    ) as find:
        DisconnectElements._perform(op, context=MagicMock())

    find.assert_not_called()
    op.report.assert_called_once()
    args, _ = op.report.call_args
    assert args[0] == {"ERROR"}


def test_disconnect_reports_when_no_rel_found():
    from bonsai.bim.module.model.wall import DisconnectElements

    elem_a = Mock()
    elem_b = Mock()
    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": elem_a, "B": elem_b}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[]
    ):
        DisconnectElements._perform(op, context=MagicMock())

    op.report.assert_called_once()


def test_disconnect_operator_is_registered():
    from bonsai.bim.module import model

    assert any(
        getattr(cls, "bl_idname", None) == "bim.disconnect_elements" for cls in model.classes
    ), "DisconnectElements is not in the model classes tuple"


def test_disconnect_refuses_path_kind_when_either_side_is_fillet():
    """The fillet corner's join with its source walls defines its identity
    — unjoining there would tear down the chord axis reference. The
    operator reports an INFO directing the user to delete the corner
    wall and skips the dispatch entirely."""
    from bonsai.bim.module.model.wall import DisconnectElements

    fillet = Mock(name="fillet_corner")
    wall = Mock(name="source_wall")
    rel = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": fillet, "B": wall}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "path")]
    ), patch(
        "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall",
        side_effect=lambda e: e is fillet,
    ), patch(
        "bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel"
    ) as dispatch:
        DisconnectElements._perform(op, context=MagicMock())

    dispatch.assert_not_called()
    op.report.assert_called_once()
    args, _ = op.report.call_args
    assert args[0] == {"INFO"}


def test_disconnect_allows_slab_kind_even_when_wall_is_fillet():
    """The fillet ↔ slab underside clip is a different relationship from
    the fillet ↔ source-wall path join. Slab disconnect must remain
    available while the corner is in preview."""
    from bonsai.bim.module.model.wall import DisconnectElements

    fillet = Mock(name="fillet_corner")
    slab = Mock(name="slab")
    rel = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": fillet, "B": slab}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "element-top")]
    ), patch(
        "bonsai.bim.module.model.wall.tool.Parametric.is_fillet_corner_wall",
        side_effect=lambda e: e is fillet,
    ), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=Mock()
    ), patch(
        "bonsai.bim.module.model.wall.bonsai.core.connection.disconnect_rel"
    ) as dispatch, patch(
        "bonsai.bim.module.model.wall._resync_walls_after_mutation"
    ):
        DisconnectElements._perform(op, context=MagicMock())

    dispatch.assert_called_once()
