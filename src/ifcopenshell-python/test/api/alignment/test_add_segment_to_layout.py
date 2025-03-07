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


def test_add_segment_to_layout():
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

    horizontal_alignment = file.create_entity(
        type="IfcAlignmentHorizontal",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
    )

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )
    alignment_segment = file.create_entity(
        type="IfcAlignmentSegment",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=None,
        Description=None,
        ObjectType=None,
        ObjectPlacement=None,
        Representation=None,
        DesignParameters=design_parameters,
    )

    ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal_alignment, alignment_segment)

    assert len(horizontal_alignment.IsNestedBy) == 1
    assert len(horizontal_alignment.IsNestedBy[0].RelatedObjects) == 1
    assert horizontal_alignment.IsNestedBy[0].RelatedObjects[0] == alignment_segment
