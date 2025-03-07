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

# import test.bootstrap
import ifcopenshell.api.alignment
import ifcopenshell.api.context


# class TestGetBasisCurve(test.bootstrap.IFC4X3):
def test_horizontal():
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

    alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(file, "TestAlignment", coordinates, radii)
    ifcopenshell.api.alignment.create_geometric_representation(file, alignment)
    basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    assert basis_curve.is_a("IfcCompositeCurve")


def test_horizontal_and_vertical():
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
    ifcopenshell.api.alignment.create_geometric_representation(file, alignment)
    basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    assert basis_curve.is_a("IfcCompositeCurve")
