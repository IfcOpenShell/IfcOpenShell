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


def test_disconnect_path_removes_all_rels_then_recreates_walls():
    from bonsai.bim.module.model.wall import DisconnectElements

    elem_a = Mock()
    elem_b = Mock()
    rel1 = Mock()
    rel2 = Mock()
    obj_a = Mock()
    obj_b = Mock()

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": elem_a, "B": elem_b}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels",
        return_value=[(rel1, "path"), (rel2, "path")],
    ), patch(
        "bonsai.bim.module.model.wall.tool.Ifc.get_object", side_effect=lambda e: {elem_a: obj_a, elem_b: obj_b}[e]
    ), patch("bonsai.bim.module.model.wall.bonsai.core.geometry.remove_connection") as remove, patch(
        "bonsai.bim.module.model.wall.tool.Model.recreate_wall"
    ) as recreate, patch("bonsai.bim.module.model.wall._resync_walls_after_mutation") as resync:
        DisconnectElements._perform(op, context=MagicMock())

    assert remove.call_count == 2
    assert recreate.call_count == 2
    resync.assert_called_once_with([obj_a, obj_b])
    op.report.assert_not_called()


def test_disconnect_element_top_calls_regenerate():
    from bonsai.bim.module.model.wall import DisconnectElements

    wall = Mock()
    slab = Mock()
    wall_obj = Mock()
    rel = Mock()
    rel.RelatedElement = wall

    ifc_file = MagicMock()
    ifc_file.by_guid.side_effect = lambda g: {"A": wall, "B": slab}[g]
    op = _make_op()

    with patch("bonsai.bim.module.model.wall.tool.Ifc.get", return_value=ifc_file), patch(
        "bonsai.bim.module.model.wall.tool.Connection.find_rels", return_value=[(rel, "element-top")]
    ), patch(
        "bonsai.bim.module.model.wall.tool.Connection.orient_element_top", return_value=(wall, slab)
    ), patch("bonsai.bim.module.model.wall.tool.Ifc.get_object", return_value=wall_obj), patch(
        "bonsai.bim.module.model.wall.ifcopenshell.api.geometry.disconnect_element"
    ) as disc, patch("bonsai.bim.module.model.wall.core.regenerate_wall_to_underside") as regen:
        DisconnectElements._perform(op, context=MagicMock())

    disc.assert_called_once_with(ifc_file, relating_element=slab, related_element=wall)
    regen.assert_called_once()
    op.report.assert_not_called()


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
