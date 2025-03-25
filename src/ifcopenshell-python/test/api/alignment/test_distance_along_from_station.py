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


def test_add_stationing_to_alignment():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(Name="Test")
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

    alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths
    )

    # test alignment without stationing referent
    assert ifcopenshell.api.alignment.distance_along_from_station(file, alignment, 500.0) == pytest.approx(500.0)

    # add stationing referent
    ifcopenshell.api.alignment.add_stationing_to_alignment(file, alignment, 10000.0)

    # Station 138+83.96
    assert ifcopenshell.api.alignment.distance_along_from_station(file, alignment, 13883.96) == pytest.approx(3883.96)

    # Station 175+25.36
    assert ifcopenshell.api.alignment.distance_along_from_station(file, alignment, 17525.36) == pytest.approx(7525.36)
