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

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit

try:
    ifcopenshell.file(schema="IFC4X3_ADD2")
    IFC4X3_AVAILABLE = True
except RuntimeError:
    IFC4X3_AVAILABLE = False


@pytest.mark.skipif(not IFC4X3_AVAILABLE, reason="IFC4X3 not available")
def test_distance_along_from_station():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths, start_station=10000.0
    )

    # Station 138+83.96
    assert ifcopenshell.api.alignment.distance_along_from_station(file, alignment, 13883.96) == pytest.approx(3883.96)

    # Station 175+25.36
    assert ifcopenshell.api.alignment.distance_along_from_station(file, alignment, 17525.36) == pytest.approx(7525.36)


def test_distance_along_from_station_with_station_equations():
    # Reproduces the worked example from the IFC Alignment Geometry Implementation Guide, chapter 9.2.6:
    # a gap equation (P3: incoming 14+00.00, outgoing 17+00.00) and an overlap equation
    # (P4: incoming 19+00.00, outgoing 18+50.00).
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths, start_station=1000.0
    )

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P3", alignment, distance_along=400.0, station=1700.0, incoming_station=1400.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "P4", alignment, distance_along=600.0, station=1850.0, incoming_station=1900.0
    )

    distance_along_from_station = ifcopenshell.api.alignment.distance_along_from_station

    # between P2 and P3: Sta. 13+00.00
    assert distance_along_from_station(file, alignment, 1300.0) == pytest.approx(300.0)

    # between P3 and P4: Sta. 18+00.00
    assert distance_along_from_station(file, alignment, 1800.0) == pytest.approx(500.0)

    # between P4 and P5: Sta. 19+25.00
    assert distance_along_from_station(file, alignment, 1925.0) == pytest.approx(675.0)

    # Sta. 15+00.00 falls inside the gap opened by the equation at P3 and has no corresponding distance along
    assert distance_along_from_station(file, alignment, 1500.0) is None

    # Sta. 18+75.00 falls inside the overlap zone at P4; the post-equation (outgoing) match is returned
    assert distance_along_from_station(file, alignment, 1875.0) == pytest.approx(625.0)


def test_distance_along_from_station_reverse_stationing_with_gap_equation():
    # A reverse-stationed alignment: HasIncreasingStation=False on the starting referent, station
    # labels decreasing as distance along increases, with one gap equation.
    #   R1: D 0.0,   Station 20+00.00,  HasIncreasingStation=False
    #   R2: D 400.0, Station 15+50.00,  IncomingStation 16+00.00  (gap of 50)
    #   R3: D 800.0, Station 11+50.00
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    alignment = ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, radii)

    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=400.0, station=1550.0, incoming_station=1600.0
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=800.0, station=1150.0)

    distance_along_from_station = ifcopenshell.api.alignment.distance_along_from_station

    # Sta. 18+00.00 -> governed by R1
    assert distance_along_from_station(file, alignment, 1800.0) == pytest.approx(200.0)

    # Sta. 13+00.00 -> governed by R2; naive subtraction from the start would overstate by the 50 ft gap
    assert distance_along_from_station(file, alignment, 1300.0) == pytest.approx(650.0)

    # Sta. 15+75.00 falls inside the range the gap equation at R2 skipped -> no distance along
    assert distance_along_from_station(file, alignment, 1575.0) is None


def _long_alignment(file):
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )
    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    return ifcopenshell.api.alignment.create_by_pi_method(file, "TestAlignment", coordinates, radii)


def test_distance_along_from_station_direction_switch_increasing_then_decreasing():
    # A peak: station labels rise to R2 then fall. HasIncreasingStation=False on R2 governs the
    # region after it. Data is self-consistent (no equations): each region is 500 units long with
    # a 500 station-label swing.
    #   R1 D 0.0   S 1000.0
    #   R2 D 500.0 S 1500.0  HasIncreasingStation=False
    #   R3 D 1000.0 S 1000.0
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    alignment = _long_alignment(file)
    ifcopenshell.api.alignment.add_stationing_referent(file, "R1", alignment, distance_along=0.0, station=1000.0)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=1000.0)

    dafs = ifcopenshell.api.alignment.distance_along_from_station

    # Sta 12+00 appears twice (rising at D 200, falling at D 800); the downstream match is returned
    assert dafs(file, alignment, 1200.0) == pytest.approx(800.0)
    # the peak label sits at the single point D 500
    assert dafs(file, alignment, 1500.0) == pytest.approx(500.0)
    # the end label
    assert dafs(file, alignment, 1000.0) == pytest.approx(1000.0)
    # Sta 16+00 is above the peak - it exists nowhere on the alignment
    assert dafs(file, alignment, 1600.0) is None


def test_distance_along_from_station_direction_switch_decreasing_then_increasing():
    # A valley: labels fall to R2 then rise. R1 starts the alignment decreasing
    # (HasIncreasingStation=False); R2 switches it back to increasing.
    #   R1 D 0.0    S 2000.0  HasIncreasingStation=False
    #   R2 D 500.0  S 1500.0  HasIncreasingStation=True
    #   R3 D 1000.0 S 2000.0
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    alignment = _long_alignment(file)
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R1", alignment, distance_along=0.0, station=2000.0, has_increasing_station=False
    )
    ifcopenshell.api.alignment.add_stationing_referent(
        file, "R2", alignment, distance_along=500.0, station=1500.0, has_increasing_station=True
    )
    ifcopenshell.api.alignment.add_stationing_referent(file, "R3", alignment, distance_along=1000.0, station=2000.0)

    dafs = ifcopenshell.api.alignment.distance_along_from_station

    # Sta 18+00 appears twice (falling at D 200, rising at D 800); the downstream match is returned
    assert dafs(file, alignment, 1800.0) == pytest.approx(800.0)
    # the valley label sits at the single point D 500
    assert dafs(file, alignment, 1500.0) == pytest.approx(500.0)
    # Sta 14+00 is below the valley - it exists nowhere on the alignment
    assert dafs(file, alignment, 1400.0) is None


def test_distance_along_from_station_multiple_direction_switches():
    # Not realistic, but valid IFC: stationing direction flips at every referent.
    #   R1 D 0.0    S 1000.0                            increasing  [0, 300]   1000 -> 1300
    #   R2 D 300.0  S 1300.0  HasIncreasingStation=False decreasing  [300, 600] 1300 -> 1000
    #   R3 D 600.0  S 1000.0  HasIncreasingStation=True  increasing  [600, 900] 1000 -> 1300
    #   R4 D 900.0  S 1300.0  HasIncreasingStation=False decreasing  [900, 1200] 1300 -> 1000
    #   R5 D 1200.0 S 1000.0
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

    dafs = ifcopenshell.api.alignment.distance_along_from_station

    # referents nest in DistanceAlong order regardless of the direction flips
    nest = ifcopenshell.api.alignment.get_stationing_nest(file, alignment)
    assert [r.Name for r in nest.RelatedObjects] == ["R1", "R2", "R3", "R4", "R5"]

    # Sta 11+00 appears in every one of the four regions; the last (most downstream) match wins
    assert dafs(file, alignment, 1100.0) == pytest.approx(1100.0)
    # the shared min label resolves to the very end of the alignment
    assert dafs(file, alignment, 1000.0) == pytest.approx(1200.0)
    # Sta 13+50 is above every peak - nowhere on the alignment
    assert dafs(file, alignment, 1350.0) is None
    # a label exactly at a peak
    assert dafs(file, alignment, 1300.0) == pytest.approx(900.0)


test_distance_along_from_station()
test_distance_along_from_station_with_station_equations()
test_distance_along_from_station_reverse_stationing_with_gap_equation()
test_distance_along_from_station_direction_switch_increasing_then_decreasing()
test_distance_along_from_station_direction_switch_decreasing_then_increasing()
test_distance_along_from_station_multiple_direction_switches()
