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

"""Behaviour tests for the wall-slab connection helpers on tool.Wall.

Pins the rel-shape contract (IfcRelConnectsElements with Description=="TOP")
the underside-extension feature creates, and the icon placement contract the
new wall-slab connection gizmo group reads."""

from unittest.mock import Mock, patch

import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool

pytestmark = pytest.mark.model


def _rel(klass: str = "IfcRelConnectsElements", description: str = "TOP", relating=None, related=None):
    rel = Mock()
    rel.is_a = lambda c: c == klass
    rel.Description = description
    rel.RelatingElement = relating
    rel.RelatedElement = related
    return rel


def _wall_with_rels(*rels) -> Mock:
    wall = Mock()
    wall.ConnectedFrom = list(rels)
    return wall


def _slab_with_rels(*rels) -> Mock:
    slab = Mock()
    slab.ConnectedTo = list(rels)
    return slab


# ---------------------------------------------------------------------------
# iter_wall_slab_connections — yields (slab, rel) for TOP rels
# ---------------------------------------------------------------------------


def test_iter_wall_slab_connections_yields_top_rels():
    slab_a = Mock(name="slab_a")
    slab_b = Mock(name="slab_b")
    wall = _wall_with_rels(
        _rel(relating=slab_a),
        _rel(relating=slab_b),
    )

    result = list(tool.Wall.iter_wall_slab_connections(wall))

    assert result == [(slab_a, wall.ConnectedFrom[0]), (slab_b, wall.ConnectedFrom[1])]


def test_iter_wall_slab_connections_skips_non_top_description():
    """Only TOP-described rels count; BOTTOM / SIDE / arbitrary strings are
    skipped so other RelConnectsElements semantics aren't confused with the
    underside-extension contract."""
    slab = Mock()
    wall = _wall_with_rels(
        _rel(description="BOTTOM", relating=slab),
        _rel(description="TOP", relating=slab),
    )

    result = list(tool.Wall.iter_wall_slab_connections(wall))

    assert len(result) == 1
    assert result[0][0] is slab


def test_iter_wall_slab_connections_skips_non_connectselements_rels():
    """Path-connections to other walls show up on ConnectedFrom too — the
    helper must filter on rel class, not just presence."""
    slab = Mock()
    wall = _wall_with_rels(
        _rel(klass="IfcRelConnectsPathElements", relating=slab),
        _rel(klass="IfcRelConnectsElements", relating=slab),
    )

    result = list(tool.Wall.iter_wall_slab_connections(wall))

    assert len(result) == 1


def test_iter_wall_slab_connections_handles_none_relating():
    """A malformed rel with RelatingElement=None is skipped rather than
    raising — defensive against partially-loaded IFC files."""
    wall = _wall_with_rels(_rel(relating=None))

    result = list(tool.Wall.iter_wall_slab_connections(wall))

    assert result == []


def test_iter_wall_slab_connections_empty_when_no_connectedfrom():
    wall = Mock()
    wall.ConnectedFrom = []

    assert list(tool.Wall.iter_wall_slab_connections(wall)) == []


# ---------------------------------------------------------------------------
# iter_slab_wall_connections — mirror, walks slab.ConnectedTo
# ---------------------------------------------------------------------------


def test_iter_slab_wall_connections_yields_top_rels():
    wall_a = Mock()
    wall_b = Mock()
    slab = _slab_with_rels(
        _rel(related=wall_a),
        _rel(related=wall_b),
    )

    result = list(tool.Wall.iter_slab_wall_connections(slab))

    assert [w for w, _ in result] == [wall_a, wall_b]


def test_iter_slab_wall_connections_skips_non_top():
    wall = Mock()
    slab = _slab_with_rels(
        _rel(description="BOTTOM", related=wall),
        _rel(description="TOP", related=wall),
    )

    result = list(tool.Wall.iter_slab_wall_connections(slab))

    assert len(result) == 1


# ---------------------------------------------------------------------------
# find_wall_slab_rel — locate specific rel between wall + slab
# ---------------------------------------------------------------------------


def test_find_wall_slab_rel_returns_match():
    slab_a = Mock(name="slab_a")
    slab_b = Mock(name="slab_b")
    rel_a = _rel(relating=slab_a)
    rel_b = _rel(relating=slab_b)
    wall = _wall_with_rels(rel_a, rel_b)

    assert tool.Wall.find_wall_slab_rel(wall, slab_b) is rel_b


def test_find_wall_slab_rel_returns_none_when_unconnected():
    slab_a = Mock(name="slab_a")
    other_slab = Mock(name="other_slab")
    wall = _wall_with_rels(_rel(relating=slab_a))

    assert tool.Wall.find_wall_slab_rel(wall, other_slab) is None


# ---------------------------------------------------------------------------
# wall_slab_connection_location_world — icon anchor point
# ---------------------------------------------------------------------------


def test_wall_slab_connection_location_perches_above_wall_top():
    """Icon X/Y comes from the wall axis midpoint; Z from the wall's mesh
    bbox top in world space plus WALL_SLAB_CONNECTION_Z_CLEARANCE so the
    icon sits above the extend-vertical / slope gizmo at the wall top."""
    wall_obj = Mock()
    wall_obj.matrix_world = Matrix.Identity(4)
    wall_obj.bound_box = [
        (-0.1, -0.1, 0.0),
        (0.1, -0.1, 0.0),
        (-0.1, 0.1, 0.0),
        (0.1, 0.1, 0.0),
        (-0.1, -0.1, 3.0),
        (0.1, -0.1, 3.0),
        (-0.1, 0.1, 3.0),
        (0.1, 0.1, 3.0),
    ]
    slab_obj = Mock()

    ref_line = (Vector((1.0, 0.0, 0.0)), Vector((3.0, 0.0, 0.0)))
    with patch.object(tool.Wall, "get_world_reference_line", return_value=ref_line):
        loc = tool.Wall.wall_slab_connection_location_world(wall_obj, slab_obj)

    expected_z = 3.0 + tool.Wall.WALL_SLAB_CONNECTION_Z_CLEARANCE
    assert loc == Vector((2.0, 0.0, expected_z))


def test_wall_slab_connection_location_returns_none_for_axisless_wall():
    """A wall without an IFC Axis representation has no reference line; the
    helper returns None so callers can skip rather than guess a location."""
    wall_obj = Mock()
    slab_obj = Mock()
    with patch.object(tool.Wall, "get_world_reference_line", return_value=None):
        assert tool.Wall.wall_slab_connection_location_world(wall_obj, slab_obj) is None
