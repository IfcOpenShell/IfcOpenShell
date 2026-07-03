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

"""Tests for pure-Python math helpers in bonsai.core.model used by the wall gizmo system.

These run in the core lane (``pytest test/core/``) — no Blender, no IFC file. The
helpers under test live in ``bonsai/core/model.py`` and are deliberately pure (tuple
in, tuple out) so they're exercisable without ``mathutils`` or ``bpy``."""

import math

import pytest

import bonsai.core.model as subject


class TestBaselineFromOffset:
    THICKNESS = 0.2

    def test_positive_direction_exterior(self):
        assert subject.baseline_from_offset(0.0, self.THICKNESS) == "EXTERIOR"

    def test_positive_direction_center(self):
        assert subject.baseline_from_offset(-self.THICKNESS / 2, self.THICKNESS) == "CENTER"

    def test_positive_direction_interior(self):
        assert subject.baseline_from_offset(-self.THICKNESS, self.THICKNESS) == "INTERIOR"

    def test_negative_direction_exterior(self):
        assert subject.baseline_from_offset(self.THICKNESS, self.THICKNESS) == "EXTERIOR"

    def test_negative_direction_center(self):
        assert subject.baseline_from_offset(self.THICKNESS / 2, self.THICKNESS) == "CENTER"

    def test_negative_direction_interior(self):
        assert subject.baseline_from_offset(0.0, self.THICKNESS) == "EXTERIOR"

    def test_within_tolerance_still_matches(self):
        # A 0.5mm jitter on a 200mm wall should still classify cleanly.
        assert subject.baseline_from_offset(-self.THICKNESS / 2 + 0.0005, self.THICKNESS) == "CENTER"

    def test_outside_tolerance_falls_back_to_center(self):
        # 50mm offset on a 200mm wall — not a canonical position.
        assert subject.baseline_from_offset(0.05, self.THICKNESS) == "CENTER"


class TestProjectAxisIntersection:
    PARALLEL_THRESHOLD = 0.9994  # cos(2°)

    def test_perpendicular_walls_meet_at_corner(self):
        # Wall A along +X from origin; wall B along +Y from (5, 0, 0).
        # Axes meet exactly at (5, 0).
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 0.0), (5.0, 3.0, 0.0))
        result = subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD)
        assert result is not None
        assert result[0] == pytest.approx(5.0)
        assert result[1] == pytest.approx(0.0)

    def test_offset_walls_intersect_at_extrapolated_point(self):
        # Wall A: y=0 from x=1 to x=6.
        # Wall B: x=0 from y=1 to y=4.
        # Infinite-line intersection at (0, 0).
        seg_a = ((1.0, 0.0, 0.0), (6.0, 0.0, 0.0))
        seg_b = ((0.0, 1.0, 0.0), (0.0, 4.0, 0.0))
        result = subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD)
        assert result is not None
        assert result[0] == pytest.approx(0.0)
        assert result[1] == pytest.approx(0.0)

    def test_parallel_walls_return_none(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((0.0, 1.0, 0.0), (5.0, 1.0, 0.0))
        assert subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD) is None

    def test_anti_parallel_walls_return_none(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 1.0, 0.0), (0.0, 1.0, 0.0))  # opposite direction
        assert subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD) is None

    def test_nearly_parallel_walls_return_none(self):
        # 1° off parallel — within the ~2° dead-band.
        angle = math.radians(1)
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((0.0, 1.0, 0.0), (5.0 * math.cos(angle), 1.0 + 5.0 * math.sin(angle), 0.0))
        assert subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD) is None

    def test_zero_length_segment_returns_none(self):
        seg_a = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        seg_b = ((0.0, 0.0, 0.0), (1.0, 1.0, 0.0))
        assert subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD) is None

    def test_intersection_z_is_average_of_endpoint_zs(self):
        # Walls at different elevations; the icon-placement Z should be the average.
        seg_a = ((0.0, 0.0, 1.0), (5.0, 0.0, 1.0))  # at z=1
        seg_b = ((5.0, 0.0, 3.0), (5.0, 3.0, 3.0))  # at z=3
        result = subject.project_axis_intersection(seg_a, seg_b, self.PARALLEL_THRESHOLD)
        assert result is not None
        assert result[2] == pytest.approx(2.0)


class TestSlopeRoundTrip:
    def test_zero_angle_zero_displacement(self):
        assert subject.displacement_from_x_angle(3.0, 0.0) == pytest.approx(0.0)
        assert subject.x_angle_from_displacement(3.0, 0.0) == pytest.approx(0.0)

    def test_positive_angle_positive_displacement(self):
        # 30° slope on a 3m wall → top moves ~1.732m in +Y.
        displacement = subject.displacement_from_x_angle(3.0, math.radians(30))
        assert displacement == pytest.approx(3.0 * math.tan(math.radians(30)))

    def test_negative_angle_negative_displacement(self):
        displacement = subject.displacement_from_x_angle(3.0, math.radians(-15))
        assert displacement < 0

    def test_round_trip_preserves_angle(self):
        # Drag-to-angle-to-drag preserves the original.
        original_angle = math.radians(20)
        displacement = subject.displacement_from_x_angle(3.0, original_angle)
        recovered = subject.x_angle_from_displacement(3.0, displacement)
        assert recovered == pytest.approx(original_angle, abs=1e-9)

    def test_round_trip_handles_zero_height(self):
        # Walls of effectively zero height should not divide-by-zero.
        recovered = subject.x_angle_from_displacement(0.0, 1.0)
        assert recovered == pytest.approx(math.pi / 2, abs=1e-3)


class TestAreAxesCollinear:
    PARALLEL_THRESHOLD = 0.9994
    LINE_TOLERANCE = 0.05

    def test_end_to_end_walls_along_x_are_collinear(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 0.0), (10.0, 0.0, 0.0))
        assert subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_separated_collinear_walls_with_gap(self):
        # Walls with a 1m gap between them — still on the same line.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((6.0, 0.0, 0.0), (10.0, 0.0, 0.0))
        assert subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_perpendicular_walls_are_not_collinear(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((0.0, 0.0, 0.0), (0.0, 5.0, 0.0))
        assert not subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_parallel_walls_offset_perpendicular_are_not_collinear(self):
        # Two parallel walls 1m apart — same direction but not the same line.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((0.0, 1.0, 0.0), (5.0, 1.0, 0.0))
        assert not subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_anti_parallel_collinear_walls(self):
        # Reversed direction on the same line still counts as collinear.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((10.0, 0.0, 0.0), (6.0, 0.0, 0.0))
        assert subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_z_is_ignored_for_plan_collinearity(self):
        # Walls on different floors are still considered collinear in plan.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 3.0), (10.0, 0.0, 3.0))
        assert subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_zero_length_segment_is_not_collinear(self):
        seg_a = ((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        seg_b = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        assert not subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_slightly_off_line_within_tolerance(self):
        # 2cm perpendicular offset — still within the 5cm tolerance.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.02, 0.0), (10.0, 0.02, 0.0))
        assert subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)

    def test_too_far_off_line_fails_tolerance(self):
        # 10cm perpendicular offset — outside the 5cm tolerance.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.10, 0.0), (10.0, 0.10, 0.0))
        assert not subject.are_axes_collinear(seg_a, seg_b, self.PARALLEL_THRESHOLD, self.LINE_TOLERANCE)


class TestClosestEndpointMidpoint:
    def test_end_to_end_walls_midpoint_is_the_shared_corner(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 0.0), (10.0, 0.0, 0.0))
        result = subject.closest_endpoint_midpoint(seg_a, seg_b)
        assert result == (pytest.approx(5.0), pytest.approx(0.0), pytest.approx(0.0))

    def test_walls_with_gap_midpoint_is_in_the_gap(self):
        # Wall A ends at x=5; wall B starts at x=7. Boundary midpoint is at x=6.
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((7.0, 0.0, 0.0), (12.0, 0.0, 0.0))
        result = subject.closest_endpoint_midpoint(seg_a, seg_b)
        assert result == (pytest.approx(6.0), pytest.approx(0.0), pytest.approx(0.0))

    def test_perpendicular_walls_midpoint_is_between_nearest_endpoints(self):
        # Wall A's +X endpoint (5,0,0) and wall B's origin (5,0,0) → midpoint at (5,0,0).
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 0.0), (5.0, 3.0, 0.0))
        result = subject.closest_endpoint_midpoint(seg_a, seg_b)
        assert result == (pytest.approx(5.0), pytest.approx(0.0), pytest.approx(0.0))

    def test_z_averaged_when_walls_at_different_elevations(self):
        seg_a = ((0.0, 0.0, 0.0), (5.0, 0.0, 0.0))
        seg_b = ((5.0, 0.0, 3.0), (10.0, 0.0, 3.0))
        result = subject.closest_endpoint_midpoint(seg_a, seg_b)
        # Closest pair: (5,0,0) and (5,0,3); midpoint Z = 1.5.
        assert result[2] == pytest.approx(1.5)


class TestVerticalHeightFromExtrusionDepth:
    def test_vertical_wall_returns_depth_unchanged(self):
        assert subject.vertical_height_from_extrusion_depth(3.0, 0.0) == pytest.approx(3.0)

    def test_30_degree_slope(self):
        # cos(30°) ≈ 0.866 → vertical height of a 3m slanted extrusion ≈ 2.598m.
        result = subject.vertical_height_from_extrusion_depth(3.0, math.radians(30))
        assert result == pytest.approx(3.0 * math.cos(math.radians(30)))

    def test_negative_angle_yields_same_magnitude(self):
        positive = subject.vertical_height_from_extrusion_depth(3.0, math.radians(30))
        negative = subject.vertical_height_from_extrusion_depth(3.0, math.radians(-30))
        assert positive == pytest.approx(negative)
