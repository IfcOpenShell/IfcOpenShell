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
# Cache invalidation — the load-bearing crash guard.
#
# Without geom-generation gating, the walk cache holds entity_instance
# references that outlive their backing IFC entities after an
# ifcopenshell.api mutation. The next _build_geometry pass calls .is_a
# on a freed SWIG handle and segfaults Blender. The gate must fire
# whenever tool.Parametric.get_geom_generation bumps — which is on
# every tool.Ifc.Operator commit (via refresh_post_commit), covering
# every disconnect path.

from types import SimpleNamespace
from unittest.mock import Mock, patch


def _seed_cache(decorator, *, start_guid, ifc_file, geom_gen, walk_ids):
    decorator._cached_start_guid = start_guid
    decorator._cached_ifc_file = ifc_file
    decorator._cached_geom_gen = geom_gen
    decorator._cached_walk_ids = list(walk_ids)


def test_walk_cache_reuses_when_seed_file_and_geom_gen_unchanged():
    """Cache hit: same seed, same ifc_file, same geom_gen → reuse the
    stored walk. Steady-state path while the IFC is idle."""
    cls = _build_subclass("DecoratorCacheReuse")
    dec = cls()

    ifc_file = SimpleNamespace()
    _seed_cache(dec, start_guid="GUID", ifc_file=ifc_file, geom_gen=5, walk_ids=[101, 102])

    current_geom_gen = 5
    start_guid = "GUID"
    hit = (
        start_guid == dec._cached_start_guid
        and ifc_file is dec._cached_ifc_file
        and current_geom_gen == dec._cached_geom_gen
        and dec._cached_walk_ids
    )
    assert hit, "Cache must hit when seed, file, and geom_gen are unchanged"


def test_walk_cache_invalidates_on_geom_generation_bump():
    """Cache must miss when geom_gen bumps so entities removed by an
    ``ifcopenshell.api`` mutation never survive in the cached walk
    list into the next draw pass."""
    cls = _build_subclass("DecoratorCacheGenInvalidates")
    dec = cls()

    ifc_file = SimpleNamespace()
    _seed_cache(dec, start_guid="GUID", ifc_file=ifc_file, geom_gen=5, walk_ids=[101])

    current_geom_gen = 6  # IFC mutation has bumped the counter
    start_guid = "GUID"
    hit = (
        start_guid == dec._cached_start_guid
        and ifc_file is dec._cached_ifc_file
        and current_geom_gen == dec._cached_geom_gen
        and dec._cached_walk_ids
    )
    assert not hit, "Cache must miss when geom_gen bumps so the walk re-runs against live entities"


def test_walk_cache_invalidates_on_seed_change():
    """Selecting a different network seed forces a re-walk even if
    geom_gen is unchanged."""
    cls = _build_subclass("DecoratorCacheSeedChange")
    dec = cls()

    ifc_file = SimpleNamespace()
    _seed_cache(dec, start_guid="OLD-GUID", ifc_file=ifc_file, geom_gen=5, walk_ids=[101])

    hit = (
        "NEW-GUID" == dec._cached_start_guid
        and ifc_file is dec._cached_ifc_file
        and 5 == dec._cached_geom_gen
        and dec._cached_walk_ids
    )
    assert not hit


def test_walk_cache_invalidates_on_ifc_file_swap():
    """Loading a different IFC file must invalidate even if the new
    seed happens to share the GUID (different IfcOpenShell file
    objects → different identity)."""
    cls = _build_subclass("DecoratorCacheFileSwap")
    dec = cls()

    old_file = SimpleNamespace()
    new_file = SimpleNamespace()
    _seed_cache(dec, start_guid="GUID", ifc_file=old_file, geom_gen=5, walk_ids=[101])

    hit = (
        "GUID" == dec._cached_start_guid
        and new_file is dec._cached_ifc_file
        and 5 == dec._cached_geom_gen
        and dec._cached_walk_ids
    )
    assert not hit


def test_walk_cache_stores_ids_not_entity_references():
    """Structural safety: the cache stores STEP integer ids, not raw
    ``entity_instance`` references — re-resolved via ``ifc_file.by_id``
    on each cache hit. Eliminates the dangling-SWIG-handle class entirely:
    even if geom_gen mistakenly fails to bump, a deleted entity's id won't
    resolve, the cache-hit branch returns ``None``, and the next draw
    re-walks against live entities."""
    cls = _build_subclass("DecoratorCacheStoresIds")
    dec = cls()
    _seed_cache(dec, start_guid="GUID", ifc_file=SimpleNamespace(), geom_gen=5, walk_ids=[42])
    assert dec._cached_walk_ids == [42]
    assert all(isinstance(eid, int) for eid in dec._cached_walk_ids)


def test_geom_cache_key_includes_geom_generation():
    """``TokenCache.get_or_compute`` keys that include geom_gen flush
    the cached world-space geometry on IFC mutations the depsgraph
    token doesn't observe — without that key component, a re-walk
    would feed a fresh list to the lambda while the cache still
    returned the prior result."""
    import bonsai.bim.decorator_cache as decorator_cache
    from bonsai.bim.module.model.decorator import MEPSystemPathDecorator

    decorator_cache.reset_for_test()
    dec = MEPSystemPathDecorator()

    builds: list[int] = []

    def _build():
        builds.append(1)
        return ([], [], [])

    ifc_file = SimpleNamespace()
    dec._geom_cache.get_or_compute(("GUID", id(ifc_file), 1), _build)
    dec._geom_cache.get_or_compute(("GUID", id(ifc_file), 1), _build)
    assert len(builds) == 1, "Same key (same gen) should reuse the cached value"

    dec._geom_cache.get_or_compute(("GUID", id(ifc_file), 2), _build)
    assert len(builds) == 2, "Bumping geom_gen in the key must invalidate the cached value"


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
