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

"""Cache-invalidation tests for ``cached_compute_bend_preview_polylines``.

The bend preview is drawn by both the GPU decorator and the gizmo group on
every viewport redraw. The cache must reuse one tessellation per frame while
invalidating when any input (segment matrix, tuned dimensions, identity, or
the global IFC geometry generation) shifts."""

from unittest.mock import Mock, patch

import pytest
from mathutils import Matrix

pytestmark = pytest.mark.model


def _mock_obj(name: str, matrix: Matrix) -> Mock:
    obj = Mock()
    obj.name = name
    obj.matrix_world = matrix
    return obj


@pytest.fixture(autouse=True)
def _clear_memo():
    from bonsai.bim.module.model import mep

    mep._bend_preview_memo = None
    yield
    mep._bend_preview_memo = None


def _patches(call_count_sentinel: dict):
    from bonsai import tool
    from bonsai.bim.module.model import mep

    def counting_compute(*args, **kwargs):
        call_count_sentinel["calls"] += 1
        return {"valid": True, "leg_a": None, "leg_b": None, "arc": []}

    return (
        patch.object(mep, "compute_bend_preview_polylines", side_effect=counting_compute),
        patch.object(tool.Parametric, "get_geom_generation", return_value=call_count_sentinel.get("gen", 1)),
    )


def test_same_inputs_within_one_generation_share_one_compute():
    """Two callers (decorator + gizmo) with identical inputs in the same
    redraw frame must yield a single underlying compute."""
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 7}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)

    assert sentinel["calls"] == 1


def test_radius_change_invalidates_cache():
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 1}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.4)  # radius changed

    assert sentinel["calls"] == 2


def test_start_length_change_invalidates_cache():
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 1}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        cached_compute_bend_preview_polylines(a, b, 0.15, 0.2, 0.3)  # start_length changed

    assert sentinel["calls"] == 2


def test_end_length_change_invalidates_cache():
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 1}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.25, 0.3)  # end_length changed

    assert sentinel["calls"] == 2


def test_segment_matrix_change_invalidates_cache():
    """Moving either segment changes the bend geometry — the cache must
    recompute even when the IFC has not advanced."""
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 1}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        b.matrix_world = Matrix.Translation((2, 0, 0))
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)

    assert sentinel["calls"] == 2


def test_geom_generation_advance_invalidates_cache():
    """An IFC operator commit bumps ``tool.Parametric.get_geom_generation``;
    the cache must recompute on the next call to pick up downstream geometry
    changes that don't surface in the object's matrix_world."""
    from bonsai import tool
    from bonsai.bim.module.model import mep
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0}

    def counting_compute(*args, **kwargs):
        sentinel["calls"] += 1
        return {"valid": True, "leg_a": None, "leg_b": None, "arc": []}

    gen_state = {"gen": 1}
    with patch.object(mep, "compute_bend_preview_polylines", side_effect=counting_compute):
        with patch.object(tool.Parametric, "get_geom_generation", side_effect=lambda: gen_state["gen"]):
            cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
            gen_state["gen"] = 2
            cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)

    assert sentinel["calls"] == 2


def test_swapping_one_segment_invalidates_cache():
    """Selecting a different segment pair (different object identity) must
    recompute even when matrices coincidentally match."""
    from bonsai.bim.module.model.mep import cached_compute_bend_preview_polylines

    a = _mock_obj("seg_a", Matrix.Identity(4))
    b = _mock_obj("seg_b", Matrix.Translation((1, 0, 0)))
    c = _mock_obj("seg_c", Matrix.Translation((1, 0, 0)))

    sentinel = {"calls": 0, "gen": 1}
    p_compute, p_gen = _patches(sentinel)
    with p_compute, p_gen:
        cached_compute_bend_preview_polylines(a, b, 0.1, 0.2, 0.3)
        cached_compute_bend_preview_polylines(a, c, 0.1, 0.2, 0.3)

    assert sentinel["calls"] == 2
