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


def test_add_segment_to_curve():
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

    line = file.createIfcCurveSegment(
        Placement=file.createIfcAxis2Placement2d(
            file.createIfcCartesianPoint((5469.395067, 4847.56631)),
            file.createIfcDirection((0.991014275066766, -0.133756146078947)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(1564.635765),
        ParentCurve=file.createIfcLine(
            Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
            Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
        ),
    )

    composite_curve = file.createIfcCompositeCurve(SelfIntersect=False)

    ifcopenshell.api.alignment.add_segment_to_curve(file, circular_arc, composite_curve)
    assert circular_arc.UsingCurves[0] == composite_curve
    assert composite_curve.Segments[-1] == circular_arc

    ifcopenshell.api.alignment.add_segment_to_curve(file, line, composite_curve)
    assert line.UsingCurves[0] == composite_curve
    assert composite_curve.Segments[-1] == line
