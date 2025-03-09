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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(1053.72220965611)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(103.674757133105)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((-0.0, 223.606797749979))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(223.606797749979)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(351.240736552036)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-103.674757133105)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-1.36919674566051e-14, -223.606797749979)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(223.606797749979)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(454.915493685141)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-103.674757133105)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((100.0, -200.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(223.606797749979)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(950.047452523004)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(103.674757133105)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((100.0, 200.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(223.606797749979)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(1991.60150186753)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(123.801073716741)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-172.075922005613, 344.151844011225)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(384.773458895502)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(426.001441657352)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-123.801073716741)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (-172.075922005613, -344.151844011225)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(384.773458895502)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, 0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(906.601103821832)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(-123.801073716741)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (272.075922005613, -272.075922005613)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(384.773458895502)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, -0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(1511.00183970305)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(123.801073716741)
    assert mapped_segment.ParentCurve.is_a("IfcCircle")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx(
        (272.075922005613, 272.075922005613)
    )
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Radius == pytest.approx(384.773458895502)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(111.803398874989)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(111.803398874989)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(111.803398874989)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(111.803398874989)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, 0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(141.42135623731)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, -0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(141.42135623731)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(104.02288238772185)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, 0.0, 0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(104.02288238772185)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, 0.0, -0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(104.02288238772185)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, 0.5, -0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(104.02288238772185)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, -0.5, 0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, 0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(125.53583325398947)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, 0.5, 0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.894427190999916, -0.447213595499958)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(125.53583325398947)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, -0.5, -0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, 0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(125.53583325398947)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, 1.0, -0.0025))


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
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert mapped_segments[1] == None
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 10.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.707106781186547, -0.707106781186547)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(125.53583325398947)
    assert mapped_segment.ParentCurve.is_a("IfcPolynomialCurve")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.CoefficientsX == pytest.approx((0.0, 1.0))
    assert mapped_segment.ParentCurve.CoefficientsY == pytest.approx((10.0, -1.0, 0.0025))


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
