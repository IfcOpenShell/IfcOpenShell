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

"""Cache-invalidation tests for the wall-topology gizmo helpers.

``GizmoWallUnjoinSingle`` and ``GizmoWallJoinIntersection`` re-run
``_iter_path_connections``, ``_are_walls_joined``, ``_are_walls_collinear``,
and ``core.project_axis_intersection`` every viewport redraw without the
cache helpers wrapping them. These tests pin that:

- Repeat calls within one IFC generation reuse the cached result.
- An IFC-generation bump invalidates the cache.
- ``refresh()`` (the Blender state-change hook on the mixin) drops the cache."""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.model


def test_get_wall_connections_cached_returns_cached_within_generation():
    from bonsai.bim.module.model import wall

    group = Mock(spec=[])
    elem = Mock()
    elem.GlobalId = "0AAAAAAAAAAAAAAAAAAAAA"
    expected = [(Mock(), "ATEND", "ATSTART")]

    call_count = {"n": 0}

    def counting_iter(e):
        call_count["n"] += 1
        return expected

    with patch.object(wall, "_iter_path_connections", side_effect=counting_iter), patch(
        "bonsai.bim.module.model.wall.tool.Parametric.get_geom_generation", return_value=7
    ):
        first = wall._get_wall_connections_cached(group, elem)
        second = wall._get_wall_connections_cached(group, elem)

    assert first is second
    assert call_count["n"] == 1


def test_get_wall_connections_cached_invalidates_on_generation_bump():
    from bonsai.bim.module.model import wall

    group = Mock(spec=[])
    elem = Mock()
    elem.GlobalId = "0AAAAAAAAAAAAAAAAAAAAA"

    call_count = {"n": 0}

    def counting_iter(e):
        call_count["n"] += 1
        return []

    gen_state = {"gen": 1}
    with patch.object(wall, "_iter_path_connections", side_effect=counting_iter), patch(
        "bonsai.bim.module.model.wall.tool.Parametric.get_geom_generation", side_effect=lambda: gen_state["gen"]
    ):
        wall._get_wall_connections_cached(group, elem)
        gen_state["gen"] = 2
        wall._get_wall_connections_cached(group, elem)

    assert call_count["n"] == 2


def test_get_wall_pair_predicate_cached_reuses_value_within_generation():
    from bonsai.bim.module.model import wall

    group = Mock(spec=[])
    call_count = {"n": 0}

    def compute():
        call_count["n"] += 1
        return "result"

    with patch("bonsai.bim.module.model.wall.tool.Parametric.get_geom_generation", return_value=3):
        first = wall._get_wall_pair_predicate_cached(group, ("joined", ("guid_a", "guid_b")), compute)
        second = wall._get_wall_pair_predicate_cached(group, ("joined", ("guid_a", "guid_b")), compute)

    assert first == second == "result"
    assert call_count["n"] == 1


def test_get_wall_pair_predicate_cached_distinguishes_predicate_kind():
    """The cache key includes a tag string ("joined" vs "collinear" vs
    "intersection") so adding a second predicate for the same pair doesn't
    return the first predicate's value."""
    from bonsai.bim.module.model import wall

    group = Mock(spec=[])
    pair = ("guid_a", "guid_b")
    with patch("bonsai.bim.module.model.wall.tool.Parametric.get_geom_generation", return_value=3):
        a = wall._get_wall_pair_predicate_cached(group, ("joined", pair), lambda: "JOINED")
        b = wall._get_wall_pair_predicate_cached(group, ("collinear", pair), lambda: "COLLINEAR")

    assert a == "JOINED"
    assert b == "COLLINEAR"


def test_get_wall_pair_predicate_cached_invalidates_on_generation_bump():
    from bonsai.bim.module.model import wall

    group = Mock(spec=[])
    call_count = {"n": 0}

    def compute():
        call_count["n"] += 1
        return call_count["n"]

    gen_state = {"gen": 1}
    with patch(
        "bonsai.bim.module.model.wall.tool.Parametric.get_geom_generation", side_effect=lambda: gen_state["gen"]
    ):
        first = wall._get_wall_pair_predicate_cached(group, ("joined", ("a", "b")), compute)
        gen_state["gen"] = 2
        second = wall._get_wall_pair_predicate_cached(group, ("joined", ("a", "b")), compute)

    assert first == 1
    assert second == 2
    assert call_count["n"] == 2


def test_mixin_refresh_clears_pair_and_connection_caches():
    """``refresh()`` is Blender's "state changed" signal — typically a
    selection change. Both the connection list and pair predicate caches
    must drop alongside the geometry cache, otherwise the next frame would
    read predicates that targeted the previously-selected pair."""
    from bonsai.bim.module.model import wall

    class _Group(wall._WallGeomCachedBillboardingMixin):
        def position_gizmos(self, context):
            pass

    group = _Group()
    group._wall_geom_cache = {"x": "geom"}
    group._wall_connections_cache = {"guid": []}
    group._wall_pair_predicate_cache = {"key": "value"}

    group.refresh(context=Mock())

    assert group._wall_geom_cache is None
    assert group._wall_connections_cache is None
    assert group._wall_pair_predicate_cache is None
