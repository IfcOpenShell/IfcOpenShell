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
# for vertical alignment.

import pytest
import ifcopenshell.api.alignment
import ifcopenshell.api.context


def _CircularArc_100_0_10_0_0_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=0.5,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 1053.7222096561088
    assert mapped_segments[0].SegmentLength.wrappedValue == 103.67475713310459
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (-0.0, 223.60679774997897)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 223.60679774997897


def _CircularArc_100_0_10_0_0_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=-0.5,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 351.2407365520363
    assert mapped_segments[0].SegmentLength.wrappedValue == -103.67475713310459
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, -223.60679774997897)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 223.60679774997897


def _CircularArc_100_0_10_0_0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=0.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 454.9154936851409
    assert mapped_segments[0].SegmentLength.wrappedValue == -103.67475713310459
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (100.0, -200.0)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 223.60679774997897


def _CircularArc_100_0_10_0__0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=0.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 950.0474525230043
    assert mapped_segments[0].SegmentLength.wrappedValue == 103.67475713310459
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (100.0, 200.0)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 223.60679774997897


def _CircularArc_100_0_10_0_0_5_1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=1.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 1991.601501867533
    assert mapped_segments[0].SegmentLength.wrappedValue == 123.80107371674127
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (-172.0759220056126, 344.1518440112252)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 384.77345889550173


def _CircularArc_100_0_10_0__0_5__1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=-1.0,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 426.0014416573519
    assert mapped_segments[0].SegmentLength.wrappedValue == -123.80107371674127
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (-172.0759220056126, -344.1518440112252)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 384.77345889550173


def _CircularArc_100_0_10_0_1_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=1.0,
        EndGradient=0.5,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, 0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 906.6011038218319
    assert mapped_segments[0].SegmentLength.wrappedValue == -123.80107371674127
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (272.0759220056126, -272.0759220056126)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 384.77345889550173


def _CircularArc_100_0_10_0__1_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-1.0,
        EndGradient=-0.5,
        PredefinedType="CIRCULARARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, -0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 1511.001839703053
    assert mapped_segments[0].SegmentLength.wrappedValue == 123.80107371674127
    assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (272.0759220056126, 272.0759220056126)
    assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Radius == 384.77345889550173


def _ConstantGradient_100_0_10_0_0_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=0.5,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0_0_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=-0.5,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0_0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=0.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 111.80339887498948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0__0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=0.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 111.80339887498948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0_0_5_1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=1.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 111.80339887498948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0__0_5__1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=-1.0,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 111.80339887498948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0_1_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=1.0,
        EndGradient=0.5,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, 0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 141.42135623730948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ConstantGradient_100_0_10_0__1_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-1.0,
        EndGradient=-0.5,
        PredefinedType="CONSTANTGRADIENT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, -0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 141.42135623730948
    assert mapped_segments[0].ParentCurve.is_a("IfcLine")
    assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0


def _ParabolicArc_100_0_10_0_0_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=0.5,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 104.02288194345505
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, 0.0, 0.0025)


def _ParabolicArc_100_0_10_0_0_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.0,
        EndGradient=-0.5,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 104.02288194345505
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, 0.0, -0.0025)


def _ParabolicArc_100_0_10_0_0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=0.0,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 104.0228819434551
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, 0.5, -0.0025)


def _ParabolicArc_100_0_10_0__0_5_0_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=0.0,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 104.0228819434551
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, -0.5, 0.0025)


def _ParabolicArc_100_0_10_0_0_5_1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=0.5,
        EndGradient=1.0,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, 0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 125.53583299580873
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, 0.5, 0.0025)


def _ParabolicArc_100_0_10_0__0_5__1_0_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-0.5,
        EndGradient=-1.0,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.8944271909999159, -0.4472135954999579)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 125.53583299580873
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, -0.5, -0.0025)


def _ParabolicArc_100_0_10_0_1_0_0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=1.0,
        EndGradient=0.5,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, 0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 125.53583299580873
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, 1.0, -0.0025)


def _ParabolicArc_100_0_10_0__1_0__0_5_1_Meter(file):
    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartHeight=10.0,
        StartGradient=-1.0,
        EndGradient=-0.5,
        PredefinedType="PARABOLICARC",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file, alignment_segment)
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segments[0].Transition
    assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 10.0)
    assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (0.7071067811865476, -0.7071067811865476)
    assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
    assert mapped_segments[0].SegmentLength.wrappedValue == 125.53583299580873
    assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
    assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
    assert mapped_segments[0].ParentCurve.CoefficientsY == (10.0, -1.0, 0.0025)


def test_map_alignment_vertical_segment():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    _CircularArc_100_0_10_0_0_0_0_5_1_Meter(file)
    _CircularArc_100_0_10_0_0_0__0_5_1_Meter(file)
    _CircularArc_100_0_10_0_0_5_0_0_1_Meter(file)
    _CircularArc_100_0_10_0__0_5_0_0_1_Meter(file)
    _CircularArc_100_0_10_0_0_5_1_0_1_Meter(file)
    _CircularArc_100_0_10_0__0_5__1_0_1_Meter(file)
    _CircularArc_100_0_10_0_1_0_0_5_1_Meter(file)
    _CircularArc_100_0_10_0__1_0__0_5_1_Meter(file)
    _ConstantGradient_100_0_10_0_0_0_0_5_1_Meter(file)
    _ConstantGradient_100_0_10_0_0_0__0_5_1_Meter(file)
    _ConstantGradient_100_0_10_0_0_5_0_0_1_Meter(file)
    _ConstantGradient_100_0_10_0__0_5_0_0_1_Meter(file)
    _ConstantGradient_100_0_10_0_0_5_1_0_1_Meter(file)
    _ConstantGradient_100_0_10_0__0_5__1_0_1_Meter(file)
    _ConstantGradient_100_0_10_0_1_0_0_5_1_Meter(file)
    _ConstantGradient_100_0_10_0__1_0__0_5_1_Meter(file)
    _ParabolicArc_100_0_10_0_0_0_0_5_1_Meter(file)
    _ParabolicArc_100_0_10_0_0_0__0_5_1_Meter(file)
    _ParabolicArc_100_0_10_0_0_5_0_0_1_Meter(file)
    _ParabolicArc_100_0_10_0__0_5_0_0_1_Meter(file)
    _ParabolicArc_100_0_10_0_0_5_1_0_1_Meter(file)
    _ParabolicArc_100_0_10_0__0_5__1_0_1_Meter(file)
    _ParabolicArc_100_0_10_0_1_0_0_5_1_Meter(file)
    _ParabolicArc_100_0_10_0__1_0__0_5_1_Meter(file)

    # VERTICAL CLOTHOID NOT IMPLEMENTED
