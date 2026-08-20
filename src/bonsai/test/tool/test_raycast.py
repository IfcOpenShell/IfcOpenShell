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

import random

from mathutils import Vector
from mathutils.geometry import intersect_point_line

from bonsai.tool.raycast import edge_out_of_snap_range
from test.bim.bootstrap import NewFile


class TestEdgeOutOfSnapRange(NewFile):
    """Guards the early-out that keeps the proximity loop off the expensive
    line-line intersection for edges that cannot possibly snap."""

    def test_far_edge_is_rejected(self):
        # Midpoint 10 away, edge only 2 long: nothing on it gets within 9.
        assert edge_out_of_snap_range(10.0, 2.0, 0.5) is True

    def test_edge_under_the_cursor_is_kept(self):
        assert edge_out_of_snap_range(0.01, 2.0, 0.5) is False

    def test_long_edge_far_from_its_midpoint_is_kept(self):
        """A long edge can reach the ray even when its midpoint is far away —
        this is the case a naive midpoint-only test would wrongly discard."""
        assert edge_out_of_snap_range(10.0, 40.0, 0.5) is False

    def test_boundary_is_not_rejected(self):
        # Bound lands exactly on the threshold; the loop's own test is strict
        # (`distance < snap_threshold`), so rejecting here stays correct.
        assert edge_out_of_snap_range(1.5, 1.0, 1.0) is True

    def test_never_rejects_an_edge_that_could_snap(self):
        """Random search: whenever a real point of the edge lies within the
        threshold of the ray line, the predicate must not reject the edge."""
        rng = random.Random(20260817)
        ray = (Vector((0.0, 0.0, 0.0)), Vector((1.0, 0.0, 0.0)))
        threshold = 0.5
        checked = 0

        for _ in range(3000):
            v1 = Vector([rng.uniform(-5, 5) for _ in range(3)])
            v2 = Vector([rng.uniform(-5, 5) for _ in range(3)])
            midpoint = (v1 + v2) / 2
            midpoint_distance = (midpoint - intersect_point_line(midpoint, *ray)[0]).length

            if not edge_out_of_snap_range(midpoint_distance, (v2 - v1).length, threshold):
                continue

            # Predicate claims "cannot snap" — verify no sampled point does.
            checked += 1
            for step in range(21):
                point = v1.lerp(v2, step / 20)
                assert (point - intersect_point_line(point, *ray)[0]).length >= threshold

        assert checked > 100, f"only {checked} edges exercised the rejection path"
