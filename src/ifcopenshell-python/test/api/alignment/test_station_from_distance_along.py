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

"""Tests for station_from_distance_along — the inverse of distance_along_from_station.

Each test exercises a distinct stationing configuration.  The expected values are derived from the
same referent tables used in the distance_along_from_station tests so the two functions are
verifiably inverse (within floating-point tolerance) where the mapping is one-to-one.
"""

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along

try:
    ifcopenshell.file(schema="IFC4X3_ADD2")
    IFC4X3_AVAILABLE = True
except RuntimeError:
    IFC4X3_AVAILABLE = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_file():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    ctx = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=ctx,
    )
    return file


def _short_alignment(file, start_station=None):
    """A compact horizontal-only alignment long enough for all tests (~1 300 ft)."""
    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0)]
    radii = [(1000.0)]
    return ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, start_station=start_station
    )


def _long_alignment(file, start_station=None):
    """A longer alignment (~8 000 ft), matching the fixture in test_distance_along_from_station."""
    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    return ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, start_station=start_station
    )


sfda = ifcopenshell.api.alignment.station_from_distance_along
dafs = ifcopenshell.api.alignment.distance_along_from_station


# ---------------------------------------------------------------------------
# Test 1 — no stationing nest (get_stationing_nest returns None)
# ---------------------------------------------------------------------------


def test_no_stationing_nest_returns_dist_along():
    # create_by_pi_method without start_station creates no referent; the
    # start station defaults to 0.0 and station == dist_along.
    file = _make_file()
    alignment = _short_alignment(file)  # no start_station arg

    assert sfda(file, alignment, 0.0) == pytest.approx(0.0)
    assert sfda(file, alignment, 300.0) == pytest.approx(300.0)
    assert sfda(file, alignment, 750.5) == pytest.approx(750.5)


# ---------------------------------------------------------------------------
# Test 2 — single referent at D 0 (start station, no equations)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(not IFC4X3_AVAILABLE, reason="IFC4X3 not available")
def test_single_start_station_referent():
    # Alignment with start station 10 000; one referent at D 0, S 10 000.
    # station = 10 000 + dist_along.
    file = _make_file()
    alignment = _long_alignment(file, start_station=10000.0)

    assert sfda(file, alignment, 0.0) == pytest.approx(10000.0)
    assert sfda(file, alignment, 3883.96) == pytest.approx(13883.96)
    assert sfda(file, alignment, 7525.36) == pytest.approx(17525.36)


@pytest.mark.skipif(not IFC4X3_AVAILABLE, reason="IFC4X3 not available")
def test_single_start_station_referent_roundtrip():
    # station_from_distance_along and distance_along_from_station are inverses.
    file = _make_file()
    alignment = _long_alignment(file, start_station=10000.0)

    for d in (0.0, 500.0, 3883.96, 7525.36):
        sta = sfda(file, alignment, d)
        assert dafs(file, alignment, sta) == pytest.approx(d)


# ---------------------------------------------------------------------------
# Test 3 — gap station equation
# ---------------------------------------------------------------------------


def test_gap_station_equation():
    # Reproduces the IFC Alignment Implementation Guide example (§ 9.2.6):
    #   P0: D 0,   S 1 000  (from start_station=1000)
    #   P3: D 400, S 1 700  (incoming 1 400 → gap of 300 stations)
    #   P4: D 600, S 1 850  (incoming 1 900 → overlap of 50 stations)
    #
    # station_from_distance_along is total — every dist_along has a station.
    # The gap/overlap affects the *station → dist* direction only.
    file = _make_file()
    alignment = _long_alignment(file, start_station=1000.0)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P3", alignment, distance_along=400.0, station=1700.0, incoming_station=1400.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P4", alignment, distance_along=600.0, station=1850.0, incoming_station=1900.0
    )

    # region governed by P0 (D 0–400, sigma +1)
    assert sfda(file, alignment, 0.0) == pytest.approx(1000.0)
    assert sfda(file, alignment, 300.0) == pytest.approx(1300.0)

    # at the gap equation referent itself
    assert sfda(file, alignment, 400.0) == pytest.approx(1700.0)

    # region governed by P3 (D 400–600, sigma +1): stations 1 700–1 900
    # (stations 1 400–1 700 are in the gap — skipped over in the D→S direction)
    assert sfda(file, alignment, 450.0) == pytest.approx(1750.0)

    # at the overlap equation referent: outgoing station 1 850
    assert sfda(file, alignment, 600.0) == pytest.approx(1850.0)

    # region governed by P4 (D >= 600, sigma +1)
    assert sfda(file, alignment, 675.0) == pytest.approx(1925.0)


def test_gap_station_equation_roundtrip():
    # For stations outside the gap, distance_along_from_station is the inverse.
    file = _make_file()
    alignment = _long_alignment(file, start_station=1000.0)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P3", alignment, distance_along=400.0, station=1700.0, incoming_station=1400.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P4", alignment, distance_along=600.0, station=1850.0, incoming_station=1900.0
    )

    for d in (300.0, 450.0, 675.0):
        sta = sfda(file, alignment, d)
        assert dafs(file, alignment, sta) == pytest.approx(d)


# ---------------------------------------------------------------------------
# Test 4 — overlap station equation
# ---------------------------------------------------------------------------


def test_overlap_station_equation():
    # Two dist_alongs that bracket the overlap equation at P4 both return
    # stations within the overlap band — no ambiguity going D→S.
    #   P4: D 600, incoming 1 900, outgoing 1 850 → overlap [1 850, 1 900]
    file = _make_file()
    alignment = _long_alignment(file, start_station=1000.0)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P3", alignment, distance_along=400.0, station=1700.0, incoming_station=1400.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P4", alignment, distance_along=600.0, station=1850.0, incoming_station=1900.0
    )

    # D 550 is in P3's region: station = 1700 + 1*(550-400) = 1850
    assert sfda(file, alignment, 550.0) == pytest.approx(1850.0)

    # D 600 is P4's outgoing point: station = 1850
    assert sfda(file, alignment, 600.0) == pytest.approx(1850.0)

    # D 625 is past P4: station = 1850 + 1*(625-600) = 1875
    assert sfda(file, alignment, 625.0) == pytest.approx(1875.0)


# ---------------------------------------------------------------------------
# Test 5 — decreasing stationing with a gap equation
# ---------------------------------------------------------------------------


def test_decreasing_stationing_with_gap():
    # Mirrors test_distance_along_from_station_reverse_stationing_with_gap_equation:
    #   R1: D 0,   S 2 000, HasIncreasingStation=False  → sigma -1
    #   R2: D 400, S 1 550, incoming 1 600              → sigma -1 (inherited)
    #   R3: D 800, S 1 150                              → sigma -1 (inherited)
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=400.0, station=1550.0, incoming_station=1600.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=800.0, station=1150.0)

    # R1's region (D 0–400, sigma -1): station = 2000 - dist_along
    assert sfda(file, alignment, 0.0) == pytest.approx(2000.0)
    assert sfda(file, alignment, 200.0) == pytest.approx(1800.0)

    # at R2 (D 400): station = 1550
    assert sfda(file, alignment, 400.0) == pytest.approx(1550.0)

    # R2's region (D 400–800, sigma -1): station = 1550 - (dist-400)
    assert sfda(file, alignment, 650.0) == pytest.approx(1300.0)

    # at R3 (D 800): station = 1150
    assert sfda(file, alignment, 800.0) == pytest.approx(1150.0)

    # past R3 (sigma -1 continues)
    assert sfda(file, alignment, 950.0) == pytest.approx(1000.0)


def test_decreasing_stationing_roundtrip():
    # distance_along_from_station is the inverse except within the gap zone.
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=400.0, station=1550.0, incoming_station=1600.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=800.0, station=1150.0)

    for d in (200.0, 650.0, 950.0):
        sta = sfda(file, alignment, d)
        assert dafs(file, alignment, sta) == pytest.approx(d)


# ---------------------------------------------------------------------------
# Test 6 — direction switch: increasing then decreasing (peak)
# ---------------------------------------------------------------------------


def test_direction_switch_increasing_then_decreasing():
    # Mirrors test_distance_along_from_station_direction_switch_increasing_then_decreasing:
    #   R1: D 0,    S 1 000                            sigma +1  [0, 500]
    #   R2: D 500,  S 1 500, HasIncreasingStation=False sigma -1  [500, 1000]
    #   R3: D 1000, S 1 000                            sigma -1
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(file, "R1", alignment, distance_along=0.0, station=1000.0)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=1000.0)

    # rising region [0, 500]: station = 1000 + dist_along
    assert sfda(file, alignment, 0.0) == pytest.approx(1000.0)
    assert sfda(file, alignment, 200.0) == pytest.approx(1200.0)

    # at the peak (D 500): station = 1500
    assert sfda(file, alignment, 500.0) == pytest.approx(1500.0)

    # falling region [500, 1000]: station = 1500 - (dist - 500)
    assert sfda(file, alignment, 800.0) == pytest.approx(1200.0)

    # at the end (D 1000): station = 1000
    assert sfda(file, alignment, 1000.0) == pytest.approx(1000.0)


def test_direction_switch_increasing_then_decreasing_symmetric_stations():
    # D 200 and D 800 both map to station 1200 — two dist_alongs, one station.
    # station_from_distance_along handles this without ambiguity (D→S is always 1:1).
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(file, "R1", alignment, distance_along=0.0, station=1000.0)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=1000.0)

    assert sfda(file, alignment, 200.0) == pytest.approx(1200.0)
    assert sfda(file, alignment, 800.0) == pytest.approx(1200.0)


# ---------------------------------------------------------------------------
# Test 7 — direction switch: decreasing then increasing (valley)
# ---------------------------------------------------------------------------


def test_direction_switch_decreasing_then_increasing():
    # Mirrors test_distance_along_from_station_direction_switch_decreasing_then_increasing:
    #   R1: D 0,    S 2 000, HasIncreasingStation=False  sigma -1  [0, 500]
    #   R2: D 500,  S 1 500, HasIncreasingStation=True   sigma +1  [500, 1000]
    #   R3: D 1000, S 2 000                              sigma +1
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=True
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=2000.0)

    # falling region [0, 500]: station = 2000 - dist_along
    assert sfda(file, alignment, 0.0) == pytest.approx(2000.0)
    assert sfda(file, alignment, 200.0) == pytest.approx(1800.0)

    # at the valley (D 500): station = 1500
    assert sfda(file, alignment, 500.0) == pytest.approx(1500.0)

    # rising region [500, 1000]: station = 1500 + (dist - 500)
    assert sfda(file, alignment, 800.0) == pytest.approx(1800.0)

    # at the end (D 1000): station = 2000
    assert sfda(file, alignment, 1000.0) == pytest.approx(2000.0)


# ---------------------------------------------------------------------------
# Test 8 — multiple direction switches
# ---------------------------------------------------------------------------


def test_multiple_direction_switches():
    # Mirrors test_distance_along_from_station_multiple_direction_switches.
    # Stationing direction flips at every referent (valid but not realistic IFC):
    #   R1 D 0    S 1000              sigma +1  [0, 300]   1000→1300
    #   R2 D 300  S 1300  HIS=False   sigma -1  [300, 600] 1300→1000
    #   R3 D 600  S 1000  HIS=True    sigma +1  [600, 900] 1000→1300
    #   R4 D 900  S 1300  HIS=False   sigma -1  [900, 1200] 1300→1000
    #   R5 D 1200 S 1000
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(file, "R1", alignment, distance_along=0.0, station=1000.0)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=300.0, station=1300.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R3", alignment, distance_along=600.0, station=1000.0, has_increasing_station=True
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R4", alignment, distance_along=900.0, station=1300.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R5", alignment, distance_along=1200.0, station=1000.0)

    # each region boundary
    assert sfda(file, alignment, 0.0) == pytest.approx(1000.0)
    assert sfda(file, alignment, 300.0) == pytest.approx(1300.0)
    assert sfda(file, alignment, 600.0) == pytest.approx(1000.0)
    assert sfda(file, alignment, 900.0) == pytest.approx(1300.0)
    assert sfda(file, alignment, 1200.0) == pytest.approx(1000.0)

    # mid-region values
    assert sfda(file, alignment, 150.0) == pytest.approx(1150.0)   # [0,300] rising
    assert sfda(file, alignment, 450.0) == pytest.approx(1150.0)   # [300,600] falling
    assert sfda(file, alignment, 750.0) == pytest.approx(1150.0)   # [600,900] rising
    assert sfda(file, alignment, 1050.0) == pytest.approx(1150.0)  # [900,1200] falling

    # same station (1100) appears in all four regions
    assert sfda(file, alignment, 100.0) == pytest.approx(1100.0)
    assert sfda(file, alignment, 500.0) == pytest.approx(1100.0)
    assert sfda(file, alignment, 700.0) == pytest.approx(1100.0)
    assert sfda(file, alignment, 1100.0) == pytest.approx(1100.0)


# ---------------------------------------------------------------------------
# Test 9 — extrapolation before the first referent
# ---------------------------------------------------------------------------


def test_extrapolation_before_first_referent():
    # When dist_along precedes the first referent's DistanceAlong, the station
    # is extrapolated backward using the first referent's sigma.
    file = _make_file()
    alignment = _long_alignment(file)

    # Single referent at D 100, S 1100, sigma +1.
    # dist_along 0 → station = 1100 + 1*(0-100) = 1000.
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=100.0, station=1100.0
    )

    assert sfda(file, alignment, 0.0) == pytest.approx(1000.0)
    assert sfda(file, alignment, 50.0) == pytest.approx(1050.0)
    assert sfda(file, alignment, 100.0) == pytest.approx(1100.0)
    assert sfda(file, alignment, 300.0) == pytest.approx(1300.0)


def test_extrapolation_before_first_referent_decreasing():
    # Decreasing stationing: first referent at D 100, S 1100, sigma -1.
    # dist_along 0 → station = 1100 + (-1)*(0-100) = 1200.
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=100.0, station=1100.0, has_increasing_station=False
    )

    assert sfda(file, alignment, 0.0) == pytest.approx(1200.0)
    assert sfda(file, alignment, 50.0) == pytest.approx(1150.0)
    assert sfda(file, alignment, 100.0) == pytest.approx(1100.0)
    assert sfda(file, alignment, 300.0) == pytest.approx(900.0)


# ---------------------------------------------------------------------------
# Test 10 — referent nest ordering drives the governing-referent walk
# ---------------------------------------------------------------------------


def test_referents_nest_in_distance_along_order():
    # add_stationing_referent is called out of DistanceAlong order; the nest must
    # still be sorted by DistanceAlong, and station_from_distance_along must pick
    # the last referent whose DistanceAlong does not exceed dist_along.
    file = _make_file()
    alignment = _long_alignment(file, start_station=1000.0)

    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=800.0, station=1800.0)
    ifcopenshell.api.alignment.add_stationing_referent(file, "R2", alignment, distance_along=400.0, station=1400.0)

    # nest is sorted by DistanceAlong: the D 0 start referent, then R2 (D 400), then R3 (D 800),
    # regardless of the order add_stationing_referent was called in.
    nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    assert [r.Name for r in nest.RelatedObjects][1:] == ["R2", "R3"]
    assert [_referent_distance_along(r) for r in nest.RelatedObjects] == [0.0, 400.0, 800.0]

    # governed by the D 0 start referent
    assert sfda(file, alignment, 200.0) == pytest.approx(1200.0)
    # governed by R2 (D 400): station = 1400 + (600 - 400)
    assert sfda(file, alignment, 600.0) == pytest.approx(1600.0)
    # governed by R3 (D 800): station = 1800 + (900 - 800)
    assert sfda(file, alignment, 900.0) == pytest.approx(1900.0)


# ---------------------------------------------------------------------------
# Test 11 — additional roundtrips through distance_along_from_station
# ---------------------------------------------------------------------------


def test_overlap_station_equation_roundtrip():
    # In the region *after* an overlap equation the mapping is one-to-one, so
    # distance_along_from_station recovers the original dist_along.
    file = _make_file()
    alignment = _long_alignment(file, start_station=1000.0)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P3", alignment, distance_along=400.0, station=1700.0, incoming_station=1400.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P4", alignment, distance_along=600.0, station=1850.0, incoming_station=1900.0
    )

    for d in (625.0, 675.0, 900.0):
        sta = sfda(file, alignment, d)
        assert dafs(file, alignment, sta) == pytest.approx(d)


def test_direction_switch_decreasing_then_increasing_roundtrip():
    # The valley: dist_alongs in the final (rising) region roundtrip cleanly;
    # distance_along_from_station returns the most downstream match.
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=True
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=2000.0)

    for d in (600.0, 800.0, 1000.0):
        sta = sfda(file, alignment, d)
        assert dafs(file, alignment, sta) == pytest.approx(d)


def test_multiple_direction_switches_roundtrip():
    # Every region boundary and the shared mid-region station roundtrip to the
    # most downstream distance along.
    file = _make_file()
    alignment = _long_alignment(file)

    ifcopenshell.api.alignment.add_stationing_referent(file, "R1", alignment, distance_along=0.0, station=1000.0)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=300.0, station=1300.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R3", alignment, distance_along=600.0, station=1000.0, has_increasing_station=True
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R4", alignment, distance_along=900.0, station=1300.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R5", alignment, distance_along=1200.0, station=1000.0)

    # station 1100 appears in every region; both functions agree on the last one
    assert sfda(file, alignment, 1100.0) == pytest.approx(1100.0)
    assert dafs(file, alignment, 1100.0) == pytest.approx(1100.0)


# ---------------------------------------------------------------------------
# Test 12 — negative and fractional distances along (no stationing nest)
# ---------------------------------------------------------------------------


def test_negative_and_fractional_dist_along_no_nest():
    # With no stationing nest the result is start_station (0.0) + dist_along for
    # any real dist_along, including negative and fractional values.
    file = _make_file()
    alignment = _long_alignment(file)  # no start_station -> no referent, no nest

    assert ifcopenshell.api.alignment.get_stationing_nest(file, alignment) is None
    assert sfda(file, alignment, -25.0) == pytest.approx(-25.0)
    assert sfda(file, alignment, 0.0) == pytest.approx(0.0)
    assert sfda(file, alignment, 123.456) == pytest.approx(123.456)


# ---------------------------------------------------------------------------
# Allow running the module directly for quick verification
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    test_no_stationing_nest_returns_dist_along()
    test_single_start_station_referent()
    test_single_start_station_referent_roundtrip()
    test_gap_station_equation()
    test_gap_station_equation_roundtrip()
    test_overlap_station_equation()
    test_decreasing_stationing_with_gap()
    test_decreasing_stationing_roundtrip()
    test_direction_switch_increasing_then_decreasing()
    test_direction_switch_increasing_then_decreasing_symmetric_stations()
    test_direction_switch_decreasing_then_increasing()
    test_multiple_direction_switches()
    test_extrapolation_before_first_referent()
    test_extrapolation_before_first_referent_decreasing()
    test_referents_nest_in_distance_along_order()
    test_overlap_station_equation_roundtrip()
    test_direction_switch_decreasing_then_increasing_roundtrip()
    test_multiple_direction_switches_roundtrip()
    test_negative_and_fractional_dist_along_no_nest()
    print("All tests passed.")
