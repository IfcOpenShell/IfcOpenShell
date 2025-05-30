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
    file = ifcopenshell.file(schema="IFC4X3")
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

    ifcopenshell.api.alignment.add_stationing_to_alignment(file, alignment, 2000.0)

    for rel in alignment.IsNestedBy:
        for referent in rel.RelatedObjects:
            if referent.is_a("IfcReferent"):
                assert referent.PredefinedType == "STATION"
                assert referent.Name == "2+000.000"
                assert ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing")
                assert (
                    ifcopenshell.util.element.get_pset(element=referent, name="Pset_Stationing", prop="Station")
                    == 2000.0
                )
                assert referent.ObjectPlacement != None
