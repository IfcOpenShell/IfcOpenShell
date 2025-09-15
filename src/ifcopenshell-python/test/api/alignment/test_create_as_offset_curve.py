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

import ifcopenshell.util
import ifcopenshell.util.unit
import pytest
import math
import ifcopenshell.api.alignment
import ifcopenshell.api.unit


def test_create_as_offset_curve():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="OCBD Test Alignment")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    # create main alignment
    alignment = ifcopenshell.api.alignment.create(file, "A1", include_vertical=True)
    layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

    segment1 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint(Coordinates=((0.0, 0.0))),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=500,
        PredefinedType="LINE",
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment1)

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    segment2 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100,
        PredefinedType="CLOTHOID",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment2)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    segment3 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=1500.0,
        PredefinedType="CIRCULARARC",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment3)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    segment4 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100,
        PredefinedType="CLOTHOID",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment4)

    x = float(end[0, 3]) / unit_scale
    y = float(end[1, 3]) / unit_scale
    dx = float(end[0, 0])
    dy = float(end[1, 0])
    dir = math.atan2(dy, dx)
    segment5 = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((x, y)),
        StartDirection=dir,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=800.0,
        PredefinedType="LINE",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, layout, segment5)

    # create vertical for main alignment
    vlayout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

    segment1 = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=3000.0,
        StartHeight=100.0,
        StartGradient=1.75 / 100.0,
        EndGradient=1.75 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file, vlayout, segment1)

    # create the offset alignment
    basis_curve = ifcopenshell.api.alignment.get_curve(alignment)  # want the IfcGradientCurve

    offsets = [
        file.createIfcPointByDistanceExpression(
            DistanceAlong=file.createIfcLengthMeasure(0.0), OffsetLateral=100.0, BasisCurve=basis_curve
        ),
    ]

    offset_alignment = ifcopenshell.api.alignment.create_as_offset_curve(file, "A2", offsets)
    assert offset_alignment.is_a("IfcAlignment")
    curve = ifcopenshell.api.alignment.get_curve(offset_alignment)
    assert curve.is_a("IfcOffsetCurveByDistances")
    assert curve.BasisCurve == basis_curve


test_create_as_offset_curve()
