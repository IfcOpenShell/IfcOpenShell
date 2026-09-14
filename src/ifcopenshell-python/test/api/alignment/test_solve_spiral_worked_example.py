# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

"""
Golden worked example for solve_horizontal_alignment_by_pi_method with a symmetric
spiral-curve-spiral (clothoid / circular arc / clothoid) transition.

Every expected value below is derived directly from the classic route-surveying spiral
formulas (see e.g. AASHTO "A Policy on Geometric Design of Highways and Streets", spiral
curve tables), independently of solve_horizontal_alignment_by_pi_method's own
implementation (which integrates the clothoid position functions with 32 point
Gauss-Legendre quadrature). The two methods agreeing to 1e-6 or better is the point of the
test: it is a check on solve_horizontal_alignment_by_pi_method, not a restatement of it.

Problem setup (units are arbitrary but consistent, e.g. feet or meters):

    Delta = 60 deg   total PI deflection angle
    R     = 500      circular curve radius
    Ls    = 150      spiral length, both entry and exit (equal-spiral case)

Derivation, step by step:

    theta_s = Ls / (2R)                                    spiral angle (deflection of one spiral)
            = 150 / 1000 = 0.15 rad

    X = Ls * (1 - theta_s^2/10 + theta_s^4/216)             local coordinates of the spiral's far end
    Y = Ls * (theta_s/3 - theta_s^3/42 + theta_s^5/1320)    (TS at the origin, tangent along +X)

    p = Y - R*(1 - cos(theta_s))                            shift: inward offset of the circular
                                                             curve from the tangent line
    k = X - R*sin(theta_s)                                  abscissa of the shifted PC, measured
                                                             from TS along the tangent

    Ts = (R + p)*tan(Delta/2) + k                           total tangent distance, PI to TS (or,
                                                             by symmetry of an equal-spiral curve,
                                                             PI to ST)

    Delta_c = Delta - 2*theta_s                              central angle left for the circular arc
    Lc      = R * Delta_c                                    circular arc length

Plugging in Delta = pi/3, R = 500, Ls = 150 (computed with Python's math module, which is
just a calculator here -- no call into ifcopenshell.api.alignment is involved):

    theta_s = 0.15
    X       = 149.6628515625
    Y       = 7.487955057832791
    p       = 1.8734940258539128
    k       = 74.9437853257004
    Ts      = 364.70058220066517
    Delta_c = 0.7471975511965976 rad  (=~ 42.809 deg)
    Lc      = 373.5987755982988

Geometry of the PI-method problem: POB at (0,0), PI1 at (D,0) with D = 1200 (comfortably
more than Ts so the back tangent run is a real segment), and POE at
(D + L*cos(-60deg), L*sin(-60deg)) with L = 1200, so PI1 deflects 60 degrees to the right.
Because the back tangent lies exactly on the world X axis (POB -> PI1 direction is 0 rad),
the offset of any point on the curve from the initial tangent line is simply that point's
world Y coordinate, and the spiral's local (X, Y) frame is the world frame translated to TS
(no rotation) -- which is what lets this example's numbers be checked directly against the
solver's segment start points without any extra transform.

    TS = (D - Ts, 0) = (835.2994177993348, 0.0)

The circular arc begins where the entry spiral ends. In the spiral's local frame that is
(X, Y); since the curve deflects right (s = -1 in the solver's sign convention) the spiral's
local Y is mirrored into world coordinates:

    circular arc start = TS + (X, -Y) = (984.9622693618348, -7.487955057832791)

By symmetry (equal spirals, same radius on both sides) the exit tangent run has the same
length as the entry tangent run, D - Ts = L - Ts = 835.2994177993348.
"""

import math

import pytest

import ifcopenshell.api.alignment

R = 500.0
Ls = 150.0
DELTA = math.pi / 3.0  # 60 degrees
D = 1200.0
L = 1200.0

# --- independently derived expected values (see module docstring for the derivation) ---
THETA_S = Ls / (2.0 * R)
assert THETA_S == pytest.approx(0.15)

EXPECTED_X = Ls * (1.0 - THETA_S**2 / 10.0 + THETA_S**4 / 216.0)
EXPECTED_Y = Ls * (THETA_S / 3.0 - THETA_S**3 / 42.0 + THETA_S**5 / 1320.0)
assert EXPECTED_X == pytest.approx(149.6628515625)
assert EXPECTED_Y == pytest.approx(7.487955057832791)

EXPECTED_P = EXPECTED_Y - R * (1.0 - math.cos(THETA_S))
EXPECTED_K = EXPECTED_X - R * math.sin(THETA_S)
assert EXPECTED_P == pytest.approx(1.8734940258539128)
assert EXPECTED_K == pytest.approx(74.9437853257004)

EXPECTED_TS = (R + EXPECTED_P) * math.tan(DELTA / 2.0) + EXPECTED_K
assert EXPECTED_TS == pytest.approx(364.70058220066517)

EXPECTED_DELTA_C = DELTA - 2.0 * THETA_S
EXPECTED_ARC_LENGTH = R * EXPECTED_DELTA_C
assert EXPECTED_DELTA_C == pytest.approx(0.7471975511965976)
assert EXPECTED_ARC_LENGTH == pytest.approx(373.5987755982988)

EXPECTED_TANGENT_RUN = D - EXPECTED_TS
assert EXPECTED_TANGENT_RUN == pytest.approx(835.2994177993348)

EXPECTED_TS_POINT = (D - EXPECTED_TS, 0.0)
EXPECTED_CIRCULARARC_START = (EXPECTED_TS_POINT[0] + EXPECTED_X, EXPECTED_TS_POINT[1] - EXPECTED_Y)
assert EXPECTED_CIRCULARARC_START == pytest.approx((984.9622693618348, -7.487955057832791))


def _pi_points() -> list[tuple[float, float]]:
    pi0 = (0.0, 0.0)
    pi1 = (D, 0.0)
    pi2 = (D + L * math.cos(math.radians(-60.0)), L * math.sin(math.radians(-60.0)))
    return [pi0, pi1, pi2]


def test_solve_spiral_worked_example_segment_types_and_lengths():
    hpoints = _pi_points()
    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(R, Ls, Ls)])

    expected_types = ["LINE", "CLOTHOID", "CIRCULARARC", "CLOTHOID", "LINE"]
    assert [s.predefined_type for s in segments] == expected_types

    back_tangent, entry_spiral, arc, exit_spiral, forward_tangent = segments

    # first tangent run: POB to TS, length D - Ts
    assert back_tangent.segment_length == pytest.approx(EXPECTED_TANGENT_RUN, rel=1.0e-6)

    # spiral lengths are exactly what was requested
    assert entry_spiral.segment_length == pytest.approx(Ls, rel=1.0e-6)
    assert exit_spiral.segment_length == pytest.approx(Ls, rel=1.0e-6)

    # circular arc length == R * Delta_c
    assert arc.segment_length == pytest.approx(EXPECTED_ARC_LENGTH, rel=1.0e-6)

    # by symmetry, the closing tangent run has the same length as the opening one
    assert forward_tangent.segment_length == pytest.approx(EXPECTED_TANGENT_RUN, rel=1.0e-6)


def test_solve_spiral_worked_example_spiral_end_offset():
    hpoints = _pi_points()
    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(R, Ls, Ls)])
    _, entry_spiral, arc, _, _ = segments

    # the back tangent (POB -> PI1) runs exactly along the world X axis, so TS is where the
    # entry spiral starts. EXPECTED_TS_POINT comes from the truncated power series formulas
    # for X and Y, while the solver integrates the same clothoid with Gauss-Legendre
    # quadrature; the two methods agree to a few parts in 1e-10 relative, well inside the
    # 1e-6 relative tolerance used throughout this test.
    assert entry_spiral.start_point == pytest.approx(EXPECTED_TS_POINT, rel=1.0e-6, abs=1.0e-9)

    # the circular arc starts where the entry spiral ends: TS + (X, -Y) in world coordinates
    # (Y is mirrored because the curve deflects to the right). this is the spiral end offset
    # from the initial tangent, expressed directly against the classic X, Y spiral formulas.
    assert arc.start_point == pytest.approx(EXPECTED_CIRCULARARC_START, rel=1.0e-6, abs=1.0e-9)
    offset_from_tangent = -arc.start_point[1]  # tangent line is world Y == 0
    assert offset_from_tangent == pytest.approx(EXPECTED_Y, rel=1.0e-6)


def test_solve_spiral_worked_example_is_continuous():
    hpoints = _pi_points()
    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, [(R, Ls, Ls)])

    max_position_gap = 0.0
    max_direction_gap = 0.0
    for segment, next_segment in zip(segments[:-1], segments[1:]):
        end_x, end_y, end_direction = ifcopenshell.api.alignment.compute_horizontal_segment_end(segment)
        position_gap = math.hypot(end_x - next_segment.start_point[0], end_y - next_segment.start_point[1])
        raw_direction_gap = end_direction - next_segment.start_direction
        direction_gap = abs(math.atan2(math.sin(raw_direction_gap), math.cos(raw_direction_gap)))
        max_position_gap = max(max_position_gap, position_gap)
        max_direction_gap = max(max_direction_gap, direction_gap)

    assert max_position_gap < 1.0e-9
    assert max_direction_gap < 1.0e-9
