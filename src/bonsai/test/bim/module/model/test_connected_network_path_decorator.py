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

"""Pin the template-method contract for the connected-network-path decorator
base. The base class defines three abstract hooks (`_is_seed_element`,
`_walk`, `_build_geometry`) and an `__init_subclass__` that rejects any
subclass which leaves a hook un-overridden. Without this guard, a forgotten
override would only surface as `NotImplementedError` on the first redraw
that hit the missing hook — long after the class declaration."""

import pytest

pytestmark = pytest.mark.model


_GOOD_HOOKS = {
    "_is_seed_element": lambda self, element: False,
    "_walk": lambda self, start_element: [],
    "_build_geometry": lambda self, connected: ([], [], []),
}


def _build_subclass(name, omit=()):
    from bonsai.bim.module.model.decorator import _ConnectedNetworkPathDecorator

    namespace = {name: fn for name, fn in _GOOD_HOOKS.items() if name not in omit}
    return type(name, (_ConnectedNetworkPathDecorator,), namespace)


@pytest.mark.parametrize("missing_hook", sorted(_GOOD_HOOKS))
def test_subclass_missing_any_single_hook_raises(missing_hook):
    with pytest.raises(TypeError, match="must override abstract hook"):
        _build_subclass(f"DecoratorMissing_{missing_hook}", omit=(missing_hook,))


def test_subclass_missing_all_hooks_raises_naming_each():
    with pytest.raises(TypeError) as excinfo:
        _build_subclass("DecoratorMissingEverything", omit=tuple(_GOOD_HOOKS))
    message = str(excinfo.value)
    for hook in _GOOD_HOOKS:
        assert hook in message, f"missing-hook error must name {hook!r}"


def test_fully_overridden_subclass_is_accepted():
    cls = _build_subclass("DecoratorWithAllHooks")
    assert cls.__name__ == "DecoratorWithAllHooks"


# ---------------------------------------------------------------------------
# Pure-geometry classifier contract.
#
# Pins the free/connection split that drives the dot colors. The classifier
# is plain Python (no bpy / no ifcopenshell), so it runs unconditionally —
# the autouse Blender skip in conftest still applies but doesn't bite here.

_EPS = 1e-5  # well under CONNECTION_EPS_SQ's sqrt (1e-4)


def _cls():
    from bonsai.bim.module.model.decorator import _ConnectedNetworkPathDecorator

    return _ConnectedNetworkPathDecorator


def test_classifier_empty_input_returns_two_empty_lists():
    free, conn = _cls()._partition_points_by_coincidence([])
    assert free == []
    assert conn == []


def test_classifier_single_point_is_free():
    p = (1.0, 2.0, 3.0)
    free, conn = _cls()._partition_points_by_coincidence([p])
    assert free == [p]
    assert conn == []


def test_classifier_coincident_pair_dedupes_to_one_connection():
    p = (1.0, 2.0, 3.0)
    near = (1.0 + _EPS, 2.0, 3.0)
    free, conn = _cls()._partition_points_by_coincidence([p, near])
    assert free == []
    assert len(conn) == 1


def test_classifier_far_points_stay_free():
    p1 = (0.0, 0.0, 0.0)
    p2 = (10.0, 0.0, 0.0)
    free, conn = _cls()._partition_points_by_coincidence([p1, p2])
    assert sorted(free) == sorted([p1, p2])
    assert conn == []


def test_classifier_t_junction_point_on_segment_interior_is_connection():
    a1, a2 = (0.0, 0.0, 0.0), (5.0, 0.0, 0.0)  # wall A endpoints (own segment)
    b1, b2 = (2.5, -2.0, 0.0), (2.5, 0.0, 0.0)  # wall B: T-meets A's midpoint
    points = [a1, a2, b1, b2]
    lines = [(a1, a2), (b1, b2)]
    free, conn = _cls()._partition_points_by_coincidence(points, lines)
    assert b2 in conn, "T-junction interior touch must be flagged as a connection"
    assert a1 in free and a2 in free, "wall A free endpoints must stay free"
    assert b1 in free, "wall B's far endpoint must stay free"


def test_classifier_endpoint_of_own_segment_is_not_a_t_junction():
    """A free endpoint sits exactly on its own segment's tip; the interior
    check must exclude segment endpoints, not just the line interior."""
    a1, a2 = (0.0, 0.0, 0.0), (5.0, 0.0, 0.0)
    free, conn = _cls()._partition_points_by_coincidence([a1, a2], [(a1, a2)])
    assert conn == [], "own-segment endpoints must not self-classify as connection"
    assert sorted(free) == sorted([a1, a2])


def test_classifier_zero_length_segment_does_not_match():
    """A segment whose two endpoints coincide has no interior; the interior
    check must skip it rather than divide by a near-zero seg_len_sq."""
    a = (0.0, 0.0, 0.0)
    p_far = (1.0, 1.0, 1.0)
    free, conn = _cls()._partition_points_by_coincidence([p_far], [(a, a)])
    assert free == [p_far]
    assert conn == []


# ---------------------------------------------------------------------------
# Wall topology classifier — IFC-rel-driven endpoint classification.
#
# Pins the rule "an endpoint is a connection iff an IfcRelConnectsPathElements
# rel says so", independent of geometric coincidence. Replaces the geometric
# classifier on the wall path because authoring tolerance routinely exceeds
# the 0.1 mm epsilon, leaving T-junction dots mis-coloured.

from unittest.mock import Mock, patch


def _stub_wall(wid, connected_to=(), connected_from=()):
    e = Mock()
    e.id.return_value = wid
    e.is_a = lambda kind: kind == "IfcWall"
    e.ConnectedTo = list(connected_to)
    e.ConnectedFrom = list(connected_from)
    return e


def _stub_rel(relating, related, relating_type, related_type):
    r = Mock()
    r.is_a = lambda kind: kind == "IfcRelConnectsPathElements"
    r.RelatingElement = relating
    r.RelatedElement = related
    r.RelatingConnectionType = relating_type
    r.RelatedConnectionType = related_type
    return r


def _wall_cls():
    from bonsai.bim.module.model.decorator import WallSystemPathDecorator

    return WallSystemPathDecorator


def test_wall_topology_single_wall_no_rels_both_endpoints_free():
    a = _stub_wall(1)
    refs = {1: ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))}
    free, conn = _wall_cls()._classify_endpoints_from_rels([a], refs)
    assert sorted(free) == sorted([(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])
    assert conn == []


def test_wall_topology_l_corner_atend_to_atstart_flags_both_endpoints():
    """Two walls meeting at a corner: A's ATEND joins B's ATSTART. Each wall's
    join-side endpoint flips to connection; the far endpoints stay free."""
    a = _stub_wall(1)
    b = _stub_wall(2)
    rel = _stub_rel(relating=a, related=b, relating_type="ATEND", related_type="ATSTART")
    a.ConnectedTo = [rel]
    b.ConnectedFrom = [rel]
    refs = {
        1: ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0)),
        2: ((5.0, 0.0, 0.0), (5.0, 5.0, 0.0)),
    }
    free, conn = _wall_cls()._classify_endpoints_from_rels([a, b], refs)
    assert (5.0, 0.0, 0.0) in conn, "A's ATEND endpoint at the corner must be connection"
    assert (5.0, 0.0, 0.0) in conn, "B's ATSTART endpoint at the corner must be connection"
    assert (0.0, 0.0, 0.0) in free, "A's far end must stay free"
    assert (5.0, 5.0, 0.0) in free, "B's far end must stay free"


def test_wall_topology_t_junction_atpath_emits_canonical_join_dot():
    """B's ATEND meets A's interior (ATPATH). A's two endpoints stay free,
    B's ATSTART stays free, B's ATEND is connection, and an extra connection
    dot is emitted at the T-meets point computed by
    ``tool.Wall.path_connection_location_world``."""
    a = _stub_wall(1)
    b = _stub_wall(2)
    rel = _stub_rel(relating=b, related=a, relating_type="ATEND", related_type="ATPATH")
    a.ConnectedFrom = [rel]
    b.ConnectedTo = [rel]
    refs = {
        1: ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0)),
        2: ((2.5, -2.0, 0.0), (2.5, 0.0, 0.0)),
    }
    t_meets = (2.5, 0.0, 0.0)
    with patch("bonsai.tool.Wall.path_connection_location_world", return_value=t_meets):
        free, conn = _wall_cls()._classify_endpoints_from_rels([a, b], refs)
    assert t_meets in conn, "T-meets canonical join must be a connection dot"
    assert (2.5, 0.0, 0.0) in conn, "B's ATEND at the junction must also be a connection"
    assert (0.0, 0.0, 0.0) in free and (5.0, 0.0, 0.0) in free, "A's endpoints stay free"
    assert (2.5, -2.0, 0.0) in free, "B's ATSTART (far end) stays free"


def test_wall_topology_rel_to_wall_outside_walked_set_is_ignored():
    """A rel pointing at a wall whose id is not in ``refs`` must not classify
    the participating endpoint as connection — only intra-set joins count."""
    a = _stub_wall(1)
    outside = _stub_wall(99)
    rel = _stub_rel(relating=a, related=outside, relating_type="ATEND", related_type="ATSTART")
    a.ConnectedTo = [rel]
    refs = {1: ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))}
    free, conn = _wall_cls()._classify_endpoints_from_rels([a], refs)
    assert sorted(free) == sorted([(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])
    assert conn == []


def test_wall_topology_non_path_rels_are_ignored():
    """``ConnectedTo`` can carry ``IfcRelConnectsElements`` (slab clip rels);
    only ``IfcRelConnectsPathElements`` contribute to wall endpoint topology."""
    a = _stub_wall(1)
    non_path_rel = Mock()
    non_path_rel.is_a = lambda kind: kind == "IfcRelConnectsElements"
    a.ConnectedTo = [non_path_rel]
    refs = {1: ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))}
    free, conn = _wall_cls()._classify_endpoints_from_rels([a], refs)
    assert sorted(free) == sorted([(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)])
    assert conn == []


def test_wall_topology_dedupe_collapses_overlapping_connection_dots():
    """Two connection dots at the same world point (within eps) collapse to
    one — used by ``_build_geometry`` to keep ATPATH joins from stacking on
    neighbour-wall endpoints."""
    p = (1.0, 2.0, 3.0)
    near = (1.0 + 1e-6, 2.0, 3.0)
    far = (10.0, 0.0, 0.0)
    result = _wall_cls()._dedupe_close_points([p, near, far], 1e-4 * 1e-4)
    assert len(result) == 2
    assert p in result and far in result
