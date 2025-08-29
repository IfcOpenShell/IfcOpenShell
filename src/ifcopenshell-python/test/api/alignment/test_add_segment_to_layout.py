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

from ifcopenshell.api.alignment._add_segment_to_layout import _add_segment_to_layout


def test_add_segment_to_layout():
    file = ifcopenshell.file(schema="IFC4X3")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    alignment = ifcopenshell.api.alignment.create(file, "")
    horizontal_alignment = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

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

    _add_segment_to_layout(file, horizontal_alignment, alignment_segment)

    assert len(horizontal_alignment.IsNestedBy) == 1
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal_alignment)
    assert len(segment_nest.RelatedObjects) == 2
    referent_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    assert len(referent_nest.RelatedObjects) == 3


test_add_segment_to_layout()
