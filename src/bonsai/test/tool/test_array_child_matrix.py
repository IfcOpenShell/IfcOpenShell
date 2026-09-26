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

"""Placement math for parametric arrays — ``tool.Array.child_matrix``.

This is the single source of truth both the regenerator
(``tool.Model._regenerate_array_body``) and the drag-time ghost preview
(``ArrayPreviewDecorator``) place instances from, so it is worth pinning
hard. The cases below cover three contracts:

1. **Linear parity.** Layers written before radial arrays existed carry no
   ``type`` key and must place byte-for-byte as they always did.
2. **Multi-turn integrity.** A sweep past 360 degrees must not fold back.
   This is the contract a future refactor is most likely to break, because
   the natural-looking "normalise the angle" or "round-trip through a
   quaternion" both destroy it silently — the array still looks plausible,
   it is just missing turns.
3. **Helix coupling.** ``rise`` climbs along the rotation axis, and under
   DISTRIBUTE shares the angle's divisor so "N treads over S degrees and
   H metres" reads the way a stair is actually specified.

Tolerances are 1e-5, not something tighter: ``mathutils`` is
single-precision (``Vector((1/3,))`` stores 0.3333333432674408), and a
composed rotate-about-a-pivot accumulates ~1e-6 of float32 round-off.
"""

import math

import pytest
from mathutils import Matrix, Vector

import bonsai.tool as tool

pytestmark = pytest.mark.model

# Float32 round-off ceiling for a composed translate/rotate/translate.
EPS = 1e-5

IDENTITY = Matrix.Identity(4)


def assert_vec(actual, expected, eps=EPS):
    assert all(abs(a - b) < eps for a, b in zip(actual, expected)), f"{tuple(actual)} != {tuple(expected)}"


def assert_rotation(actual: Matrix, expected: Matrix, eps=EPS):
    """Compare rotation parts element-wise. Deliberately NOT via euler or
    quaternion comparison — those normalise, which is exactly the failure
    mode the multi-turn tests exist to catch."""
    a = [c for row in actual.to_3x3().row for c in row]
    b = [c for row in expected.to_3x3().row for c in row]
    assert all(abs(x - y) < eps for x, y in zip(a, b)), f"{a} != {b}"


def linear_layer(**overrides) -> dict:
    layer = {
        "type": "LINEAR",
        "count": 5,
        "method": "OFFSET",
        "x": 2.0,
        "y": 0.0,
        "z": 0.0,
        "use_local_space": True,
    }
    layer.update(overrides)
    return layer


def radial_layer(**overrides) -> dict:
    layer = {
        "type": "RADIAL",
        "count": 4,
        "method": "OFFSET",
        "angle": math.radians(90),
        "rise": 0.0,
        "center": [-1.0, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "use_local_space": True,
        "rotate_children": True,
    }
    layer.update(overrides)
    return layer


class TestLinearParity:
    def test_offset_steps_by_a_fixed_amount(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 3, 1.0).translation, (6, 0, 0))

    def test_distribute_spreads_across_a_fixed_span(self):
        layer = linear_layer(method="DISTRIBUTE")
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 4, 1.0).translation, (2, 0, 0))
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 1, 1.0).translation, (0.5, 0, 0))

    def test_layer_without_type_key_places_as_linear(self):
        """Pre-radial pset data has no ``type``; it must not change meaning."""
        legacy = {k: v for k, v in linear_layer().items() if k != "type"}
        assert_vec(tool.Array.child_matrix(IDENTITY, legacy, 3, 1.0).translation, (6, 0, 0))

    def test_unit_scale_converts_project_units_to_si(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 1, 0.001).translation, (0.002, 0, 0))

    def test_index_zero_is_the_source_itself(self):
        assert_vec(tool.Array.child_matrix(IDENTITY, linear_layer(), 0, 1.0).translation, (0, 0, 0))


class TestRadialPlacement:
    def test_quarter_turns_about_an_offset_pivot(self):
        layer = radial_layer()
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 1, 1.0).translation, (-1, 1, 0))
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 2, 1.0).translation, (-2, 0, 0))
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 3, 1.0).translation, (-1, -1, 0))

    def test_copies_are_turned_to_face_along_the_sweep(self):
        result = tool.Array.child_matrix(IDENTITY, radial_layer(), 1, 1.0)
        assert_rotation(result, Matrix.Rotation(math.radians(90), 4, "Z"))

    def test_rotate_children_off_orbits_without_turning(self):
        source = Matrix.Rotation(math.radians(37), 4, "Z")
        turned = tool.Array.child_matrix(source, radial_layer(), 1, 1.0)
        upright = tool.Array.child_matrix(source, radial_layer(rotate_children=False), 1, 1.0)
        assert_vec(upright.translation, turned.translation)
        assert_rotation(upright, source)

    def test_axis_need_not_be_normalised(self):
        unit = tool.Array.child_matrix(IDENTITY, radial_layer(axis=[0, 0, 1]), 1, 1.0)
        scaled = tool.Array.child_matrix(IDENTITY, radial_layer(axis=[0, 0, 7]), 1, 1.0)
        assert_vec(scaled.translation, unit.translation)

    def test_rotation_about_a_non_z_axis(self):
        layer = radial_layer(axis=[1, 0, 0], center=[0, -2, 0], rise=1.0)
        # The climb follows the rotation axis, so an X-axis sweep climbs in X.
        assert_vec(tool.Array.child_matrix(IDENTITY, layer, 1, 1.0).translation[:1], (1.0,))

    def test_degenerate_axis_leaves_the_copy_on_the_source(self):
        result = tool.Array.child_matrix(IDENTITY, radial_layer(axis=[0, 0, 0]), 3, 1.0)
        assert_vec(result.translation, (0, 0, 0))


class TestMultiTurn:
    """A sweep past one full turn must stay unwrapped.

    The regression these guard against is silent: normalising the angle (or
    decomposing the matrix to an euler/quaternion and back) folds 630 degrees
    to -90, so later instances stack onto earlier ones and the array simply
    loses turns while still looking like a plausible array.
    """

    # 22 treads at 30 degrees = 630 degrees = 1.75 turns, climbing 180mm each.
    STAIR = {
        "type": "RADIAL",
        "count": 22,
        "method": "OFFSET",
        "angle": math.radians(30),
        "rise": 0.18,
        "center": [-1.5, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "use_local_space": True,
        "rotate_children": True,
    }

    def test_final_instance_is_a_true_630_degree_rotation(self):
        result = tool.Array.child_matrix(IDENTITY, self.STAIR, 21, 1.0)
        assert_rotation(result, Matrix.Rotation(math.radians(630), 4, "Z"))

    def test_final_instance_position_is_a_true_630_degree_sweep(self):
        result = tool.Array.child_matrix(IDENTITY, self.STAIR, 21, 1.0)
        pivot = Vector((-1.5, 0.0, 0.0))
        expected = pivot + Matrix.Rotation(math.radians(630), 3, "Z") @ Vector((1.5, 0.0, 0.0))
        assert_vec(result.translation.xy, expected.xy)

    def test_instances_a_full_turn_apart_are_separated_by_the_climb(self):
        """Treads 9 and 21 share a compass bearing (270 vs 630 degrees) but
        must be a full turn of rise apart — 12 treads x 180mm = 2.16m. If the
        angle were wrapped they would land on top of each other."""
        lower = tool.Array.child_matrix(IDENTITY, self.STAIR, 9, 1.0)
        upper = tool.Array.child_matrix(IDENTITY, self.STAIR, 21, 1.0)
        assert_vec(upper.translation.xy, lower.translation.xy, eps=1e-4)
        assert abs((upper.translation.z - lower.translation.z) - 2.16) < EPS

    def test_climb_is_monotonic_across_every_tread(self):
        heights = [tool.Array.child_matrix(IDENTITY, self.STAIR, i, 1.0).translation.z for i in range(22)]
        assert all(b > a for a, b in zip(heights, heights[1:]))
        assert abs(heights[-1] - 3.78) < EPS

    def test_no_two_treads_share_a_position(self):
        seen = [tool.Array.child_matrix(IDENTITY, self.STAIR, i, 1.0).translation.copy() for i in range(22)]
        for i, a in enumerate(seen):
            for b in seen[i + 1 :]:
                assert (a - b).length > 1e-3


class TestDistributeDivisor:
    """DISTRIBUTE spreads a fixed total across the copies.

    The angle and the rise decide this independently (see
    ``TestIndependentRiseMethod``); when a layer sets only ``method`` they
    move together, which is the coherent reading of a partial spec."""

    SPEC = {
        "type": "RADIAL",
        "count": 17,
        "method": "DISTRIBUTE",
        "angle": math.radians(540),
        "rise": 3.0,
        "center": [-1.2, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "use_local_space": True,
        "rotate_children": True,
    }

    def test_last_instance_consumes_the_whole_sweep(self):
        result = tool.Array.child_matrix(IDENTITY, self.SPEC, 16, 1.0)
        assert_rotation(result, Matrix.Rotation(math.radians(540), 4, "Z"))

    def test_intermediate_instance_proves_the_sweep_was_not_wrapped(self):
        """The load-bearing multi-turn assertion for DISTRIBUTE.

        Checking the LAST instance cannot detect a wrapped sweep: rotations are
        periodic, so ``Rotation(540)`` and ``Rotation(180)`` are the identical
        matrix and a sweep normalised to 180 still lands the final copy in the
        right place. The damage shows up in the STEP — 540/16 = 33.75 degrees
        versus a wrapped 180/16 = 11.25 — so only an intermediate instance
        reveals it."""
        first = tool.Array.child_matrix(IDENTITY, self.SPEC, 1, 1.0)
        assert_rotation(first, Matrix.Rotation(math.radians(33.75), 4, "Z"))
        # Guard the guard: the wrapped step really would look different here.
        wrapped_step = math.radians(180) / 16
        assert abs(math.radians(33.75) - wrapped_step) > math.radians(20)

    def test_two_full_turns_distribute_evenly(self):
        """720 degrees is the worst case — wrapping it yields a zero step and
        collapses every copy onto the original."""
        layer = dict(self.SPEC, angle=math.radians(720), count=9)
        assert_rotation(tool.Array.child_matrix(IDENTITY, layer, 1, 1.0), Matrix.Rotation(math.radians(90), 4, "Z"))
        positions = [tool.Array.child_matrix(IDENTITY, layer, i, 1.0).translation.copy() for i in range(9)]
        assert all((positions[0] - p).length > 1e-3 for p in positions[1:4])

    def test_last_instance_consumes_the_whole_rise(self):
        assert abs(tool.Array.child_matrix(IDENTITY, self.SPEC, 16, 1.0).translation.z - 3.0) < EPS

    def test_midpoint_is_at_half_the_rise(self):
        assert abs(tool.Array.child_matrix(IDENTITY, self.SPEC, 8, 1.0).translation.z - 1.5) < EPS

    def test_count_of_one_does_not_divide_by_zero(self):
        layer = radial_layer(count=1, method="DISTRIBUTE")
        assert tool.Array.step_divisor(layer) == 1
        tool.Array.child_matrix(IDENTITY, layer, 0, 1.0)

    def test_count_of_zero_does_not_divide_by_zero(self):
        assert tool.Array.step_divisor({"count": 0, "method": "DISTRIBUTE"}) == 1


class TestIndependentRiseMethod:
    """``rise_method`` is independent of ``method``.

    A spiral stair is normally known as one total and one per-copy quantity:
    the floor-to-floor height is fixed by the building while the tread angle
    is a design choice, or the sweep is fixed by the plan while the riser is
    set by code. Forcing both quantities into the same mode makes the ordinary
    specification unstatable, so each carries its own.
    """

    # 17 treads, 30 degrees each (per copy), climbing to exactly 3.0m (total).
    STAIR = {
        "type": "RADIAL",
        "count": 17,
        "method": "OFFSET",
        "rise_method": "DISTRIBUTE",
        "angle": math.radians(30),
        "rise": 3.0,
        "center": [-1.4, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "use_local_space": True,
        "rotate_children": True,
    }

    def test_per_copy_angle_with_total_rise(self):
        """ "30 degrees a tread, 3 metres floor to floor"."""
        last = tool.Array.child_matrix(IDENTITY, self.STAIR, 16, 1.0)
        # Angle is per copy: 16 steps of 30 degrees = 480 degrees, past a full turn.
        assert_rotation(last, Matrix.Rotation(math.radians(480), 4, "Z"))
        # Rise is a total: the last tread lands exactly at floor-to-floor.
        assert abs(last.translation.z - 3.0) < EPS
        # ...and the implied riser is the total spread over the gaps.
        first = tool.Array.child_matrix(IDENTITY, self.STAIR, 1, 1.0)
        assert abs(first.translation.z - 3.0 / 16) < EPS

    def test_total_angle_with_per_copy_rise(self):
        """ "540 degrees of sweep, 180mm risers" — the mirror-image spec."""
        layer = dict(self.STAIR, method="DISTRIBUTE", rise_method="OFFSET", angle=math.radians(540), rise=0.18)
        last = tool.Array.child_matrix(IDENTITY, layer, 16, 1.0)
        assert_rotation(last, Matrix.Rotation(math.radians(540), 4, "Z"))
        assert abs(last.translation.z - 0.18 * 16) < EPS
        first = tool.Array.child_matrix(IDENTITY, layer, 1, 1.0)
        assert_rotation(first, Matrix.Rotation(math.radians(540) / 16, 4, "Z"))
        assert abs(first.translation.z - 0.18) < EPS

    def test_absent_rise_method_inherits_the_layer_method(self):
        """A layer specifying only ``method`` keeps both quantities coherent."""
        for method in ("OFFSET", "DISTRIBUTE"):
            layer = {k: v for k, v in self.STAIR.items() if k != "rise_method"}
            layer["method"] = method
            assert tool.Array.rise_method(layer) == method
            coupled = dict(layer, rise_method=method)
            assert_vec(
                tool.Array.child_matrix(IDENTITY, layer, 5, 1.0).translation,
                tool.Array.child_matrix(IDENTITY, coupled, 5, 1.0).translation,
            )

    def test_empty_rise_method_falls_back_rather_than_breaking(self):
        assert tool.Array.rise_method(dict(self.STAIR, rise_method="")) == "OFFSET"

    def test_rise_divisor_ignores_the_closed_loop_branch(self):
        """``step_divisor`` can divide by ``count`` for a closed ring, but a
        closed ring requires zero rise, so the climb never takes that path."""
        layer = dict(self.STAIR, full_circle=True, count=6)
        assert tool.Array.rise_divisor(layer) == 5

    def test_all_four_mode_combinations_are_distinct(self):
        """Guards against a refactor quietly re-coupling the two modes."""
        seen = []
        for method in ("OFFSET", "DISTRIBUTE"):
            for rise_method in ("OFFSET", "DISTRIBUTE"):
                layer = dict(self.STAIR, method=method, rise_method=rise_method)
                result = tool.Array.child_matrix(IDENTITY, layer, 5, 1.0)
                seen.append((result.translation.copy(), result.to_3x3().copy()))
        for i, (pos_a, _) in enumerate(seen):
            for pos_b, _ in seen[i + 1 :]:
                assert (pos_a - pos_b).length > 1e-3


class TestResolvedValues:
    """``resolved_rise`` / ``resolved_angle`` report both halves of each
    (per-copy, total) pair so the panel can show whichever the user did not
    type. The derived riser is the number building code constrains, and it
    exists nowhere else — without this it is only discoverable by rebuilding
    the array and measuring it.

    These feed a read-only display, so the contract that matters is that they
    agree with what ``child_matrix`` actually builds.
    """

    STAIR = {
        "type": "RADIAL",
        "count": 17,
        "method": "OFFSET",
        "rise_method": "DISTRIBUTE",
        "angle": math.radians(30),
        "rise": 3.0,
        "center": [-1.4, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "use_local_space": True,
        "rotate_children": True,
    }

    def test_total_rise_yields_the_derived_riser(self):
        per_copy, total = tool.Array.resolved_rise(self.STAIR)
        assert abs(total - 3.0) < EPS
        assert abs(per_copy - 3.0 / 16) < EPS

    def test_per_copy_rise_yields_the_derived_total(self):
        layer = dict(self.STAIR, rise_method="OFFSET", rise=0.18)
        per_copy, total = tool.Array.resolved_rise(layer)
        assert abs(per_copy - 0.18) < EPS
        assert abs(total - 0.18 * 16) < EPS

    def test_derived_riser_matches_what_child_matrix_builds(self):
        """The readout must not be able to disagree with the geometry."""
        for rise_method, rise in (("DISTRIBUTE", 3.0), ("OFFSET", 0.18)):
            layer = dict(self.STAIR, rise_method=rise_method, rise=rise)
            per_copy, total = tool.Array.resolved_rise(layer)
            first = tool.Array.child_matrix(IDENTITY, layer, 1, 1.0)
            last = tool.Array.child_matrix(IDENTITY, layer, 16, 1.0)
            assert abs(first.translation.z - per_copy) < EPS
            assert abs(last.translation.z - total) < EPS

    def test_total_sweep_is_reported_unwrapped(self):
        """Reporting 480 rather than 120 degrees is the entire point — the
        turn count is exactly what a bare heading hides."""
        per_copy, total = tool.Array.resolved_angle(self.STAIR)
        assert abs(math.degrees(per_copy) - 30) < 1e-4
        assert abs(math.degrees(total) - 480) < 1e-4

    def test_distribute_sweep_yields_the_derived_step(self):
        layer = dict(self.STAIR, method="DISTRIBUTE", angle=math.radians(540))
        per_copy, total = tool.Array.resolved_angle(layer)
        assert abs(math.degrees(per_copy) - 540 / 16) < 1e-4
        assert abs(math.degrees(total) - 540) < 1e-4

    def test_single_instance_spans_nothing(self):
        """A lone instance has no gaps. The display count is honest about that
        rather than borrowing ``step_divisor``'s floor of 1, which exists only
        to keep the division safe."""
        offset = dict(self.STAIR, count=1, method="OFFSET", rise_method="OFFSET")
        assert tool.Array.rise_gap_count(offset) == 0
        assert tool.Array.angle_gap_count(offset) == 0
        # Per-copy in, so the total climb across zero gaps is zero.
        assert tool.Array.resolved_rise(offset)[1] == 0.0
        assert tool.Array.resolved_angle(offset)[1] == 0.0

        distribute = dict(self.STAIR, count=1, method="DISTRIBUTE", rise_method="DISTRIBUTE")
        # Total in, but nothing to divide it between — report zero rather than
        # dividing by the safety floor and inventing a step.
        assert tool.Array.resolved_rise(distribute)[0] == 0.0
        assert tool.Array.resolved_angle(distribute)[0] == 0.0

    def test_closed_ring_counts_the_wrapping_gap(self):
        """A closed ring has ``count`` gaps, not ``count - 1`` — the last one
        wraps back onto the first."""
        ring = dict(self.STAIR, count=6, full_circle=True, rise=0.0, method="DISTRIBUTE")
        assert tool.Array.angle_gap_count(ring) == 6
        # The climb never takes that branch: a closed loop requires zero rise.
        assert tool.Array.rise_gap_count(ring) == 5

    def test_gap_counts_agree_with_the_divisors_above_one_instance(self):
        """The display counts and the safe divisors may only differ at count<=1."""
        for count in range(2, 8):
            layer = dict(self.STAIR, count=count)
            assert tool.Array.angle_gap_count(layer) == tool.Array.step_divisor(layer)
            assert tool.Array.rise_gap_count(layer) == tool.Array.rise_divisor(layer)


class TestClosedLoop:
    RING = {
        "type": "RADIAL",
        "count": 6,
        "method": "DISTRIBUTE",
        "angle": 2 * math.pi,
        "center": [-1.0, 0.0, 0.0],
        "axis": [0.0, 0.0, 1.0],
        "full_circle": True,
        "use_local_space": True,
        "rotate_children": True,
    }

    def test_closed_ring_divides_by_count_not_count_minus_one(self):
        """Otherwise the last copy lands on top of the first."""
        assert tool.Array.step_divisor(self.RING) == 6
        assert tool.Array.is_closed_loop(self.RING)

    def test_ring_spacing_is_an_even_sixth(self):
        result = tool.Array.child_matrix(IDENTITY, self.RING, 1, 1.0)
        expected = (-1 + math.cos(math.radians(60)), math.sin(math.radians(60)), 0)
        assert_vec(result.translation, expected)

    def test_rise_cancels_full_circle(self):
        """A helix never returns to its start, so the endpoint is a real
        instance, not a duplicate — dropping it would lose a tread."""
        helix = dict(self.RING, rise=0.2)
        assert not tool.Array.is_closed_loop(helix)
        assert tool.Array.step_divisor(helix) == 5

    def test_full_circle_is_ignored_for_linear_layers(self):
        assert tool.Array.step_divisor(linear_layer(method="DISTRIBUTE", full_circle=True)) == 4


class TestPivotIsParentRelative:
    """The pivot is stored relative to the source instance, never as an
    absolute world point. Children track the parent through the BBIM_Array
    CHILD_OF constraint, so an absolute pivot would stay behind when the
    parent moved and tear the ring away from its own contents."""

    def test_result_is_rigid_under_parent_motion(self):
        moved = Matrix.Translation((10, 20, 30)) @ Matrix.Rotation(math.radians(45), 4, "Z")
        relative = moved.inverted() @ tool.Array.child_matrix(moved, radial_layer(), 1, 1.0)
        at_origin = tool.Array.child_matrix(IDENTITY, radial_layer(), 1, 1.0)
        assert_vec(relative.translation, at_origin.translation, eps=1e-4)
        assert_rotation(relative, at_origin, eps=1e-4)

    def test_world_space_pivot_is_measured_from_the_object(self):
        """World space fixes the axes, not the origin — matching how the
        linear offsets have always treated ``use_local_space=False``."""
        moved = Matrix.Translation((10, 20, 30)) @ Matrix.Rotation(math.radians(45), 4, "Z")
        result = tool.Array.child_matrix(moved, radial_layer(use_local_space=False), 1, 1.0)
        assert_vec(result.translation, (9, 21, 30), eps=1e-4)

    def test_local_space_pivot_follows_parent_rotation(self):
        turned = Matrix.Rotation(math.radians(90), 4, "Z")
        result = tool.Array.child_matrix(turned, radial_layer(), 1, 1.0)
        # Pivot (-1,0,0) in the parent's frame is (0,-1,0) in world once the
        # parent is turned 90 degrees; the copy lands a quarter turn on from there.
        assert_vec(result.translation, (-1, -1, 0), eps=1e-4)
