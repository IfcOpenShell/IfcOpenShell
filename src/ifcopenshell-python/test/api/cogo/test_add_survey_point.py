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
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.cogo


def test_add_survey_point():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(Name="Test")
    site = file.createIfcSite(GlobalId=ifcopenshell.guid.new(), Name="MySite")
    ifcopenshell.api.aggregate.assign_object(file, relating_object=project, products=[site])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Annotation",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    annotation = ifcopenshell.api.cogo.add_survey_point(file, file.createIfcCartesianPoint((50.0, 10.0)))
    assert annotation
    assert annotation.PredefinedType == "SURVEY"
    assert annotation.Representation.Representations[0].RepresentationIdentifier == "Annotation"
    assert annotation.Representation.Representations[0].RepresentationType == "Point"
    assert annotation.Representation.Representations[0].Items[0].Coordinates == pytest.approx((50.0, 10.0))
