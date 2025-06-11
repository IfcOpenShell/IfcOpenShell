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

# These are test cases generated from https://github.com/bSI-RailwayRoom/IFC-Rail-Unit-Test-Reference-Code/tree/master/alignment_testset/IFC-WithGeneratedGeometry
# for horizontal alignment.

import pytest
import ifcopenshell.api.alignment


def _BlossCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(120.989673502444)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-112.624788044361)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)


def _BlossCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-120.989673502444)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(112.624788044361)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)


def _BlossCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(110.668191970032)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)


def _BlossCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-110.668191970032)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)


def _BlossCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-120.989673502444)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(112.624788044361)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(1000.0)


def _BlossCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(120.989673502444)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-112.624788044361)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-1000.0)


def _BlossCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-110.668191970032)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _BlossCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(110.668191970032)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _CircularArc_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(1000.0)


def _CircularArc_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _CircularArc_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(300.0)


def _Clothoid_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-142.857142857143)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-207.019667802706)


def _Clothoid_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-142.857142857143)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(207.019667802706)


def _Clothoid_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-173.205080756888)


def _Clothoid_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(173.205080756888)


def _Clothoid_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(42.8571428571429)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(207.019667802706)


def _Clothoid_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(42.8571428571429)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-207.019667802706)


def _Clothoid_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(173.205080756888)


def _Clothoid_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CLOTHOID",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-173.205080756888)


def _CosineCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(857.142857142857)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(461.538461538462)


def _CosineCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-857.142857142857)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-461.538461538462)


def _CosineCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(600.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(600.0)


def _CosineCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-600.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-600.0)


def _CosineCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-857.142857142857)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(461.538461538462)


def _CosineCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(857.142857142857)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-461.538461538462)


def _CosineCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-600.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(600.0)


def _CosineCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(600.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-600.0)


def _Cubic_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-142.857142857143)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, -3.88888888888889e-06))


def _Cubic_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-142.857142857143)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, 3.88888888888889e-06))


def _Cubic_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, -5.55555555555556e-06))


def _Cubic_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(-100.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, 5.55555555555556e-06))


def _Cubic_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(42.8571428571429)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, 3.88888888888889e-06))


def _Cubic_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(42.8571428571429)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, -3.88888888888889e-06))


def _Cubic_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, 5.55555555555556e-06))


def _Cubic_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="CUBIC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((0.0, 0.0, 0.0, -5.55555555555556e-06))


def _HelmertCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.7998035122387, 3.91603145329256))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.9892460407218963, 0.146260968532457)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-0.009321141429516372, 0.46831933573745577)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9992574637140321, -0.03852948496670688)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-103.509833901353)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(176.470588235294)


def _HelmertCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.7998035122387, -3.91603145329256))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.9892460407218963, -0.146260968532457)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-0.009321141429516372, -0.46831933573745577)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9992574637140321, 0.03852948496670688)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(103.509833901353)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-176.470588235294)


def _HelmertCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.8122545525202, 3.81263503030693))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.9904138664989948, 0.1381317235341378)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-0.010305467756443198, 0.6738837916692928)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9984794480380026, -0.05512523782919828)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-86.6025403784439)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(150.0)


def _HelmertCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.8122545525202, -3.81263503030693))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.9904138664989948, -0.1381317235341378)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-0.010305467756443198, -0.6738837916692928)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9984794480380026, 0.05512523782919828)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(86.6025403784439)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-150.0)


def _HelmertCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(1000.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.9681012468824, 1.49252747074135))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.997594495159641, 0.0693197174487962)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (0.010408767953926904, -0.4828832446956578)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9992463304688143, 0.03881714884698913)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(103.509833901353)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-750.0)


def _HelmertCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-1000.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.9681012468824, -1.49252747074135))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.997594495159641, -0.0693197174487962)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (0.010408767953926904, 0.4828832446956578)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9992463304688143, -0.03881714884698913)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(128.92319893893)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-103.509833901353)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(750.0)


def _HelmertCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.9972443634885, 0.347204361427475))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999614222337484, 0.027769614722351524)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (0.011625841243773832, -0.6968669147609581)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9984543318840984, 0.05557829739996359)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(86.6025403784439)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)


def _HelmertCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((49.9972443634885, -0.347204361427475))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999614222337484, -0.027769614722351524)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (0.011625841243773832, 0.6968669147609581)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx(
        (0.9984543318840984, -0.05557829739996359)
    )
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(114.471424255333)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-86.6025403784439)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)


def _Line_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _Line_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="LINE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _SineCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=1000.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(2692.79370307697)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-207.019667802706)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)


def _SineCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=-1000.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-2692.79370307697)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(207.019667802706)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)


def _SineCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(1884.95559215388)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-173.205080756888)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(300.0)


def _SineCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-300.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-1884.95559215388)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(173.205080756888)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-300.0)


def _SineCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=1000.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-2692.79370307697)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(207.019667802706)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(1000.0)


def _SineCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-1000.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(2692.79370307697)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-207.019667802706)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-1000.0)


def _SineCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=300.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-1884.95559215388)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(173.205080756888)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _SineCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=-300.0,
        SegmentLength=100.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_horizontal_segment(file, alignment_segment)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(1884.95559215388)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-173.205080756888)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def test_map_alignment_horizontal_segment():
    file = ifcopenshell.file(schema="IFC4X3")
    _BlossCurve_100_0_300_1000_1_Meter(file)
    _BlossCurve_100_0__300__1000_1_Meter(file)
    _BlossCurve_100_0_300_inf_1_Meter(file)
    _BlossCurve_100_0__300__inf_1_Meter(file)
    _BlossCurve_100_0_1000_300_1_Meter(file)
    _BlossCurve_100_0__1000__300_1_Meter(file)
    _BlossCurve_100_0_inf_300_1_Meter(file)
    _BlossCurve_100_0__inf__300_1_Meter(file)
    _CircularArc_100_0_300_1000_1_Meter(file)
    _CircularArc_100_0__300__1000_1_Meter(file)
    _CircularArc_100_0_300_inf_1_Meter(file)
    _CircularArc_100_0__300__inf_1_Meter(file)
    _CircularArc_100_0_1000_300_1_Meter(file)
    _CircularArc_100_0__1000__300_1_Meter(file)
    _CircularArc_100_0_inf_300_1_Meter(file)
    _CircularArc_100_0__inf__300_1_Meter(file)
    _Clothoid_100_0_300_1000_1_Meter(file)
    _Clothoid_100_0__300__1000_1_Meter(file)
    _Clothoid_100_0_300_inf_1_Meter(file)
    _Clothoid_100_0__300__inf_1_Meter(file)
    _Clothoid_100_0_1000_300_1_Meter(file)
    _Clothoid_100_0__1000__300_1_Meter(file)
    _Clothoid_100_0_inf_300_1_Meter(file)
    _Clothoid_100_0__inf__300_1_Meter(file)
    _CosineCurve_100_0_300_1000_1_Meter(file)
    _CosineCurve_100_0__300__1000_1_Meter(file)
    _CosineCurve_100_0_300_inf_1_Meter(file)
    _CosineCurve_100_0__300__inf_1_Meter(file)
    _CosineCurve_100_0_1000_300_1_Meter(file)
    _CosineCurve_100_0__1000__300_1_Meter(file)
    _CosineCurve_100_0_inf_300_1_Meter(file)
    _CosineCurve_100_0__inf__300_1_Meter(file)
    _Cubic_100_0_300_1000_1_Meter(file)
    _Cubic_100_0__300__1000_1_Meter(file)
    _Cubic_100_0_300_inf_1_Meter(file)
    _Cubic_100_0__300__inf_1_Meter(file)
    _Cubic_100_0_1000_300_1_Meter(file)
    _Cubic_100_0__1000__300_1_Meter(file)
    _Cubic_100_0_inf_300_1_Meter(file)
    _Cubic_100_0__inf__300_1_Meter(file)
    _HelmertCurve_100_0_300_1000_1_Meter(file)
    _HelmertCurve_100_0__300__1000_1_Meter(file)
    _HelmertCurve_100_0_300_inf_1_Meter(file)
    _HelmertCurve_100_0__300__inf_1_Meter(file)
    _HelmertCurve_100_0_1000_300_1_Meter(file)
    _HelmertCurve_100_0__1000__300_1_Meter(file)
    _HelmertCurve_100_0_inf_300_1_Meter(file)
    _HelmertCurve_100_0__inf__300_1_Meter(file)
    _Line_100_0_300_1000_1_Meter(file)
    _Line_100_0__300__1000_1_Meter(file)
    _Line_100_0_300_inf_1_Meter(file)
    _Line_100_0__300__inf_1_Meter(file)
    _Line_100_0_1000_300_1_Meter(file)
    _Line_100_0__1000__300_1_Meter(file)
    _Line_100_0_inf_300_1_Meter(file)
    _Line_100_0__inf__300_1_Meter(file)
    _SineCurve_100_0_300_1000_1_Meter(file)
    _SineCurve_100_0__300__1000_1_Meter(file)
    _SineCurve_100_0_300_inf_1_Meter(file)
    _SineCurve_100_0__300__inf_1_Meter(file)
    _SineCurve_100_0_1000_300_1_Meter(file)
    _SineCurve_100_0__1000__300_1_Meter(file)
    _SineCurve_100_0_inf_300_1_Meter(file)
    _SineCurve_100_0__inf__300_1_Meter(file)

    # VIENESSE BEND NOT IMPLEMENTED
