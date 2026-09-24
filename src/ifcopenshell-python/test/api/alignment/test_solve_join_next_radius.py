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

# This file was generated with the assistance of an AI coding tool.

"""
Pure-solver tests for solve_join_next_radius: given the tangent length a join_next junction's
joined-into curve must claim to close, solves for the radius that achieves it -- so a Bonsai user
enabling "Join to Next PI" no longer has to guess a closing radius by hand.

Verifies both that the solved radius is numerically close to a known-good one, and, more
importantly, that feeding the solved radius back into solve_horizontal_alignment_by_pi_method
actually produces a real, continuous, closing chain -- not just that bisection converged to
*something*.
"""

import math

import pytest

import ifcopenshell.api.alignment
from ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method import (
    _solve_spiral_curve,
    solve_join_next_radius,
    solve_joining_radius,
)
from test.api.alignment.test_solve_compound_reverse import _assert_chain_continuous


def test_plain_circular_matches_closed_form():
    """CIRCULAR has an exact closed form (T = R * tan(delta/2)); solve_join_next_radius should
    return exactly that, not an approximation."""
    delta2 = math.radians(40.0)
    r2 = 300.0
    target = abs(r2 * math.tan(delta2 / 2.0))
    solved = solve_join_next_radius(delta2, target)
    assert solved == pytest.approx(r2, abs=1.0e-9)


def test_plain_circular_closes_end_to_end_pcc():
    """Solved radius fed back into the real solver produces a genuine, continuous PCC."""
    r1, delta1_deg = 600.0, 60.0
    delta2_deg = 40.0
    delta1 = math.radians(delta1_deg)
    delta2 = math.radians(delta2_deg)
    t1 = abs(r1 * math.tan(delta1 / 2.0))

    # Build a PI-to-PI distance from a *known* r2, then solve blind and confirm it matches and closes.
    r2_known = 300.0
    t2_known = abs(r2_known * math.tan(delta2 / 2.0))
    pi_to_pi_distance = t1 + t2_known

    r2_solved = solve_join_next_radius(delta2, pi_to_pi_distance - t1)
    assert r2_solved == pytest.approx(r2_known, abs=1.0e-6)

    pob = (0.0, 0.0)
    pi1 = (1000.0, 0.0)
    pi2 = (pi1[0] + pi_to_pi_distance * math.cos(delta1), pi1[1] + pi_to_pi_distance * math.sin(delta1))
    poe = (pi2[0] + 800.0 * math.cos(delta1 + delta2), pi2[1] + 800.0 * math.sin(delta1 + delta2))
    hpoints = [pob, pi1, pi2, poe]
    radii = [(r1, 0.0, 0.0, "CLOTHOID", None, True), r2_solved]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == ["LINE", "CIRCULARARC", "CIRCULARARC", "LINE"]
    _assert_chain_continuous(segments)


def test_plain_circular_closes_end_to_end_prc():
    """Same as the PCC case, but the joined-into curve turns the opposite direction (PRC)."""
    r1, delta1_deg = 500.0, 55.0
    delta2_deg = -30.0  # opposite direction -> reverse curve
    delta1 = math.radians(delta1_deg)
    delta2 = math.radians(delta2_deg)
    t1 = abs(r1 * math.tan(delta1 / 2.0))

    r2_known = 250.0
    t2_known = abs(r2_known * math.tan(delta2 / 2.0))
    pi_to_pi_distance = t1 + t2_known

    r2_solved = solve_join_next_radius(delta2, pi_to_pi_distance - t1)
    assert r2_solved == pytest.approx(r2_known, abs=1.0e-6)

    pob = (0.0, 0.0)
    pi1 = (1000.0, 0.0)
    pi2 = (pi1[0] + pi_to_pi_distance * math.cos(delta1), pi1[1] + pi_to_pi_distance * math.sin(delta1))
    poe = (pi2[0] + 800.0 * math.cos(delta1 + delta2), pi2[1] + 800.0 * math.sin(delta1 + delta2))
    hpoints = [pob, pi1, pi2, poe]
    radii = [(r1, 0.0, 0.0, "CLOTHOID", None, True), r2_solved]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == ["LINE", "CIRCULARARC", "CIRCULARARC", "LINE"]
    arc1, arc2 = segments[1], segments[2]
    assert math.copysign(1.0, arc1.start_radius_of_curvature) != math.copysign(1.0, arc2.start_radius_of_curvature)
    _assert_chain_continuous(segments)


def test_spiral_circular_to_circular_spiral_closes_end_to_end():
    """The SPIRAL_CIRCULAR -> CIRCULAR_SPIRAL case has no closed form: the joined-into curve's
    exit spiral (outer side) still shifts its entry-side (joined) tangent claim as a function of
    radius, so this must bisect against the real spiral math, not a plain-circular approximation."""
    r1, delta1_deg, entry1 = 500.0, 50.0, 100.0
    delta2_deg, exit2 = 35.0, 70.0  # PCC (same direction), mirrored spiral length per the UI default
    delta1 = math.radians(delta1_deg)
    delta2 = math.radians(delta2_deg)

    sol1 = _solve_spiral_curve(delta1, r1, entry1, 0.0, "CLOTHOID", None, pi_number=1)
    t1_out = sol1.pi_to_st

    r2_known = 350.0
    sol2_known = _solve_spiral_curve(delta2, r2_known, 0.0, exit2, "CLOTHOID", None, pi_number=2)
    t2_known_in = sol2_known.ts_to_pi
    pi_to_pi_distance = t1_out + t2_known_in

    r2_solved = solve_join_next_radius(delta2, pi_to_pi_distance - t1_out, exit_length=exit2, family="CLOTHOID")
    assert r2_solved == pytest.approx(r2_known, abs=1.0e-3)

    pob = (0.0, 0.0)
    pi1 = (1000.0, 0.0)
    pi2 = (pi1[0] + pi_to_pi_distance * math.cos(delta1), pi1[1] + pi_to_pi_distance * math.sin(delta1))
    poe = (pi2[0] + 800.0 * math.cos(delta1 + delta2), pi2[1] + 800.0 * math.sin(delta1 + delta2))
    hpoints = [pob, pi1, pi2, poe]
    radii = [
        (r1, entry1, 0.0, "CLOTHOID", None, True),
        (r2_solved, 0.0, exit2, "CLOTHOID", None, False),
    ]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == [
        "LINE", "CLOTHOID", "CIRCULARARC", "CIRCULARARC", "CLOTHOID", "LINE",
    ]
    # Looser tolerance than the closed-form PCC/PRC tests: r2_solved is only as exact as
    # solve_join_next_radius's own bisection (see _assert_chain_continuous's docstring) -- still
    # far tighter than _check_pi_join_closure's own real-world 1e-4 relative tolerance.
    _assert_chain_continuous(segments, abs_tol=1.0e-5)


def test_three_curve_chain_solves_pairwise():
    """A chain of 3 joined curves: PI1's radius is fixed, PI2's radius is solved to close against
    PI1, then PI3's radius is solved to close against the (solved) PI2 -- pairwise along the chain,
    matching how a caller would apply this PI by PI down a longer join_next run."""
    r1, delta1_deg = 600.0, 20.0
    delta2_deg, delta3_deg = 15.0, 25.0  # all left turns -- a 3-arc PCC chain
    delta1 = math.radians(delta1_deg)
    delta2 = math.radians(delta2_deg)
    delta3 = math.radians(delta3_deg)

    t1 = abs(r1 * math.tan(delta1 / 2.0))

    # Choose an arbitrary target tangent claim for PI2's own joined side and solve for r2 from it.
    pi1_pi2_distance = t1 + 250.0  # leaves 250.0 for PI2's own tangent claim
    r2_solved = solve_join_next_radius(delta2, 250.0)
    t2 = abs(r2_solved * math.tan(delta2 / 2.0))
    assert t2 == pytest.approx(250.0, abs=1.0e-6)

    pi2_pi3_distance_share_for_pi3 = 180.0
    r3_solved = solve_join_next_radius(delta3, pi2_pi3_distance_share_for_pi3)
    t3 = abs(r3_solved * math.tan(delta3 / 2.0))
    assert t3 == pytest.approx(pi2_pi3_distance_share_for_pi3, abs=1.0e-6)

    pob = (0.0, 0.0)
    pi1 = (1000.0, 0.0)
    bearing12 = delta1
    pi2 = (pi1[0] + pi1_pi2_distance * math.cos(bearing12), pi1[1] + pi1_pi2_distance * math.sin(bearing12))
    bearing23 = bearing12 + delta2
    pi3_distance = t2 + pi2_pi3_distance_share_for_pi3
    pi3 = (pi2[0] + pi3_distance * math.cos(bearing23), pi2[1] + pi3_distance * math.sin(bearing23))
    bearing3poe = bearing23 + delta3
    poe = (pi3[0] + 800.0 * math.cos(bearing3poe), pi3[1] + 800.0 * math.sin(bearing3poe))
    hpoints = [pob, pi1, pi2, pi3, poe]
    radii = [
        (r1, 0.0, 0.0, "CLOTHOID", None, True),
        (r2_solved, 0.0, 0.0, "CLOTHOID", None, True),
        r3_solved,
    ]

    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == [
        "LINE", "CIRCULARARC", "CIRCULARARC", "CIRCULARARC", "LINE",
    ]
    _assert_chain_continuous(segments)


def test_rejects_non_positive_target():
    with pytest.raises(ValueError, match="not positive"):
        solve_join_next_radius(math.radians(30.0), -5.0)
    with pytest.raises(ValueError, match="not positive"):
        solve_join_next_radius(math.radians(30.0), 0.0)


def test_rejects_zero_deflection():
    with pytest.raises(ValueError, match="deflection angle is zero"):
        solve_join_next_radius(0.0, 100.0)


def _hpoints_for_join(delta1, delta2, pi_to_pi_distance):
    pob = (0.0, 0.0)
    pi1 = (1000.0, 0.0)
    pi2 = (pi1[0] + pi_to_pi_distance * math.cos(delta1), pi1[1] + pi_to_pi_distance * math.sin(delta1))
    poe = (pi2[0] + 800.0 * math.cos(delta1 + delta2), pi2[1] + 800.0 * math.sin(delta1 + delta2))
    return [pob, pi1, pi2, poe]


def test_joining_radius_plain_circular_matches_closed_form():
    delta1 = math.radians(60.0)
    r1 = 600.0
    target = abs(r1 * math.tan(delta1 / 2.0))
    assert solve_joining_radius(delta1, target) == pytest.approx(r1, abs=1.0e-9)


def test_joining_radius_spiral_circular_matches_known_radius():
    """SPIRAL_CIRCULAR's forward-side claim shifts with its outer entry spiral -- no closed form,
    so check the bisection recovers a known radius from its own pi_to_st."""
    delta1, entry1, r1_known = math.radians(50.0), 100.0, 500.0
    target = _solve_spiral_curve(delta1, r1_known, entry1, 0.0, "CLOTHOID", None, pi_number=1).pi_to_st
    solved = solve_joining_radius(delta1, target, entry_length=entry1, family="CLOTHOID")
    assert solved == pytest.approx(r1_known, abs=1.0e-3)


@pytest.mark.parametrize("delta2_deg", [40.0, -30.0])  # PCC, then PRC
def test_join_by_distance_closes_end_to_end(delta2_deg):
    """Distance mode: the junction is placed at a stated distance T1 from PI1 along the PI1-PI2 leg,
    and *both* radii are solved -- PI1's from T1, PI2's from the remainder."""
    delta1, delta2 = math.radians(60.0), math.radians(delta2_deg)
    pi_to_pi_distance = 450.0
    t1 = 300.0

    r1 = solve_joining_radius(delta1, t1)
    r2 = solve_join_next_radius(delta2, pi_to_pi_distance - t1)

    hpoints = _hpoints_for_join(delta1, delta2, pi_to_pi_distance)
    radii = [(r1, 0.0, 0.0, "CLOTHOID", None, True), r2]
    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == ["LINE", "CIRCULARARC", "CIRCULARARC", "LINE"]
    _assert_chain_continuous(segments)

    # the junction lands exactly T1 from PI1 along the leg
    junction = segments[2].start_point
    expected = (hpoints[1][0] + t1 * math.cos(delta1), hpoints[1][1] + t1 * math.sin(delta1))
    assert junction[0] == pytest.approx(expected[0], abs=1.0e-9)
    assert junction[1] == pytest.approx(expected[1], abs=1.0e-9)


@pytest.mark.parametrize("family", ["CLOTHOID", "BLOSSCURVE", "CUBIC"])
def test_join_by_distance_with_outer_spirals_closes_end_to_end(family):
    delta1, delta2 = math.radians(50.0), math.radians(35.0)
    entry1, exit2 = 100.0, 70.0
    pi_to_pi_distance = 520.0
    t1 = 300.0

    r1 = solve_joining_radius(delta1, t1, entry_length=entry1, family=family)
    r2 = solve_join_next_radius(delta2, pi_to_pi_distance - t1, exit_length=exit2, family=family)

    hpoints = _hpoints_for_join(delta1, delta2, pi_to_pi_distance)
    radii = [(r1, entry1, 0.0, family, None, True), (r2, 0.0, exit2, family, None, False)]
    segments = ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method(hpoints, radii)
    assert [s.predefined_type for s in segments] == ["LINE", family, "CIRCULARARC", "CIRCULARARC", family, "LINE"]
    _assert_chain_continuous(segments, abs_tol=1.0e-5)


def test_joining_radius_rejects_non_positive_target():
    with pytest.raises(ValueError, match="not positive"):
        solve_joining_radius(math.radians(30.0), 0.0)


def test_joining_radius_rejects_unreachable_target():
    """An entry spiral so long its smallest valid radius already claims more than the target."""
    with pytest.raises(ValueError, match="no radius closes"):
        solve_joining_radius(math.radians(10.0), 5.0, entry_length=200.0)
