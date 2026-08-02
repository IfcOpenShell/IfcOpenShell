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


def test_distance_along_from_station():
    file = ifcopenshell.file(schema="IFC4X3")
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
    file = ifcopenshell.file(schema="IFC4X3")
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


test_distance_along_from_station()
test_distance_along_from_station_with_station_equations()
