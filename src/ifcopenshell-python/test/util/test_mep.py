# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import pytest

from ifcopenshell.util.mep import calculate_orthogonal_path


def _segments_are_axis_aligned(path: list[tuple[float, float, float]]) -> bool:
    for (x0, y0, z0), (x1, y1, z1) in zip(path, path[1:]):
        differing = sum(1 for a, b in zip((x0, y0, z0), (x1, y1, z1)) if abs(a - b) > 1e-9)
        if differing > 1:
            return False
    return True


class TestCalculateOrthogonalPath:
    def test_coincident_points_return_a_single_waypoint(self):
        path = calculate_orthogonal_path((1.0, 2.0, 3.0), (1.0, 2.0, 3.0))
        assert path == [(1.0, 2.0, 3.0)]

    def test_same_axis_offset_is_a_direct_run_with_no_bends(self):
        path = calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        assert path == [(0.0, 0.0, 0.0), (5.0, 0.0, 0.0)]
        assert _segments_are_axis_aligned(path)

    def test_offset_on_two_axes_needs_exactly_one_bend(self):
        path = calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0))
        assert len(path) == 3
        assert path[0] == (0.0, 0.0, 0.0)
        assert path[-1] == (5.0, 3.0, 0.0)
        assert _segments_are_axis_aligned(path)

    def test_offset_on_three_axes_needs_exactly_two_bends(self):
        path = calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 2.0))
        assert len(path) == 4
        assert path[0] == (0.0, 0.0, 0.0)
        assert path[-1] == (5.0, 3.0, 2.0)
        assert _segments_are_axis_aligned(path)
        # every coordinate is fixed to its final value one axis at a time
        axes_fixed_at = set()
        point = path[0]
        for next_point in path[1:]:
            changed = [i for i in range(3) if abs(point[i] - next_point[i]) > 1e-9]
            assert len(changed) == 1
            axes_fixed_at.add(changed[0])
            point = next_point
        assert axes_fixed_at == {0, 1, 2}

    def test_start_direction_picks_which_axis_is_travelled_first(self):
        # forcing the first leg along +Y instead of the default +X first.
        path = calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0), start_direction=(0.0, 1.0, 0.0))
        assert path[1] == (0.0, 3.0, 0.0)
        assert path[-1] == (5.0, 3.0, 0.0)

    def test_end_direction_picks_which_axis_is_travelled_last(self):
        path = calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0), end_direction=(1.0, 0.0, 0.0))
        assert path[1] == (0.0, 3.0, 0.0)
        assert path[-1] == (5.0, 3.0, 0.0)

    def test_start_and_end_direction_together_fix_the_whole_order(self):
        path = calculate_orthogonal_path(
            (0.0, 0.0, 0.0),
            (5.0, 3.0, 2.0),
            start_direction=(0.0, 0.0, 1.0),
            end_direction=(1.0, 0.0, 0.0),
        )
        assert path[1] == (0.0, 0.0, 2.0)
        assert path[2] == (0.0, 3.0, 2.0)
        assert path[-1] == (5.0, 3.0, 2.0)

    def test_negative_direction_matching_the_delta_sign_is_honoured(self):
        path = calculate_orthogonal_path((5.0, 0.0, 0.0), (0.0, 3.0, 0.0), start_direction=(-1.0, 0.0, 0.0))
        assert path[1] == (0.0, 0.0, 0.0)

    def test_direction_along_a_shared_axis_is_rejected(self):
        # start and end already agree on Z, so a Z-facing start direction
        # cannot be honoured by a direct orthogonal path.
        with pytest.raises(ValueError):
            calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0), start_direction=(0.0, 0.0, 1.0))

    def test_direction_pointing_away_from_the_target_is_rejected(self):
        with pytest.raises(ValueError):
            calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0), start_direction=(-1.0, 0.0, 0.0))

    def test_non_axis_aligned_direction_is_rejected(self):
        with pytest.raises(ValueError):
            calculate_orthogonal_path((0.0, 0.0, 0.0), (5.0, 3.0, 0.0), start_direction=(1.0, 1.0, 0.0))

    def test_contradictory_start_and_end_direction_on_the_same_axis_is_rejected(self):
        with pytest.raises(ValueError):
            calculate_orthogonal_path(
                (0.0, 0.0, 0.0),
                (5.0, 3.0, 2.0),
                start_direction=(1.0, 0.0, 0.0),
                end_direction=(1.0, 0.0, 0.0),
            )
