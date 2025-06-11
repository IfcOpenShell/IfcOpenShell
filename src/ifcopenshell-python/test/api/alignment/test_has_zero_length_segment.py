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
import ifcopenshell.api.alignment.has_zero_length_segment
import ifcopenshell.api.alignment.remove_zero_length_segment
import ifcopenshell.api.context
import ifcopenshell.guid
import ifcopenshell.api.nest


def _test_business_definition():
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

    horizontal = file.createIfcAlignmentHorizontal("Horizontal Alignment")
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )
    segment = file.createIfcAlignmentSegment(GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters)
    ifcopenshell.api.nest.assign_object(
        file,
        related_objects=[
            segment,
        ],
        relating_object=horizontal,
    )

    assert False == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)

    ifcopenshell.api.alignment.add_zero_length_segment(file, horizontal)
    assert len(horizontal.IsNestedBy[0].RelatedObjects) == 2

    assert True == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)

    zero_length_segment = ifcopenshell.api.alignment.remove_zero_length_segment(file, horizontal)
    assert len(horizontal.IsNestedBy[0].RelatedObjects) == 1
    assert False == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)

    ifcopenshell.api.alignment.add_segment_to_layout(file, horizontal, zero_length_segment)
    assert len(horizontal.IsNestedBy[0].RelatedObjects) == 2
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(horizontal)


def _test_geometric_definition():
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
    circular_arc = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((4084.115884, 3889.462938)),
            file.createIfcDirection((0.224530986099614, 0.974466949814685)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(-1848.115835),
        ParentCurve=file.createIfcCircle(
            Position=file.createIfcAxis2Placement2d(
                file.createIfcCartesianPoint((0.0, 0.0)), file.createIfcDirection((1.0, 0.0))
            ),
            Radius=1250.0,
        ),
    )

    composite_curve = file.createIfcCompositeCurve(Segments=(circular_arc,), SelfIntersect=False)

    assert False == ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)

    ifcopenshell.api.alignment.add_zero_length_segment(file, composite_curve)

    assert True == ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)

    assert len(composite_curve.Segments) == 2

    zero_length_segment = ifcopenshell.api.alignment.remove_zero_length_segment(file, composite_curve)
    assert len(composite_curve.Segments) == 1
    assert False == ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)

    ifcopenshell.api.alignment.add_segment_to_curve(file, zero_length_segment, composite_curve)
    assert len(composite_curve.Segments) == 2
    assert True == ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)

    segment = composite_curve.Segments[-1]
    assert segment.Placement.Location.Coordinates == (5469.394535876198, 4847.567078630914)
    assert segment.Placement.RefDirection.DirectionRatios == (0.9910142986043448, -0.13375597168627318)


def test_has_zero_length_segment():
    _test_business_definition()
    _test_geometric_definition()
