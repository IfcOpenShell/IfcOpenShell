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


def _BlossCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _BlossCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _BlossCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _BlossCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _BlossCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _BlossCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _BlossCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _BlossCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="BLOSSCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CubicTerm == pytest.approx(-500.00000000000017)
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(746.9007910928623)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _ConstantCant_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _ConstantCant_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="CONSTANTCANT",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcLine")
    assert mapped_segment.ParentCurve.Pnt.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Orientation.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.Dir.Magnitude == pytest.approx(1.0)


def _CosineCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _CosineCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="COSINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcCosineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.CosineTerm == pytest.approx(-250000.0)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(250000.0)


def _HelmertCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(31250.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, -0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(15625.0)


def _HelmertCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(31250.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, -0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(15625.0)


def _HelmertCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(31250.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, -0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(15625.0)


def _HelmertCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(31250.0)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, -0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(15625.0)


def _HelmertCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, 0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-31250.0)


def _HelmertCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, 0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-31250.0)


def _HelmertCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, 0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-31250.0)


def _HelmertCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="HELMERTCURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(None)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)
    mapped_segment = mapped_segments[1]
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((50.0, 0.04, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999998720000819, 0.00159999897600066, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(50.0)
    assert mapped_segment.ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.QuadraticTerm == pytest.approx(-538.6086725079696)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(883.8834764831845)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(-31250.0)


def _LinearTransition_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, -0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-3535.53390593274)


def _LinearTransition_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, -0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-3535.53390593274)


def _LinearTransition_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, -0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-3535.53390593274)


def _LinearTransition_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, -0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(-3535.53390593274)


def _LinearTransition_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, 0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(3535.53390593274)


def _LinearTransition_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, 0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(3535.53390593274)


def _LinearTransition_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, 0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(3535.53390593274)


def _LinearTransition_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="LINEARTRANSITION",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx(
        (0.999999680000154, 0.000799999744000123, 0.0)
    )
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcClothoid")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.ClothoidConstant == pytest.approx(3535.53390593274)


def _SineCurve_100_0_300_1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _SineCurve_100_0__300__1000_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _SineCurve_100_0_300_inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.16,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _SineCurve_100_0__300__inf_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.16,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.08, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(-3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(125000.0)


def _SineCurve_100_0_1000_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _SineCurve_100_0__1000__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _SineCurve_100_0_inf_300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.0,
        StartCantRight=0.0,
        EndCantRight=0.16,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def _SineCurve_100_0__inf__300_1_Meter(file):
    design_parameters = file.createIfcAlignmentCantSegment(
        StartDistAlong=0.0,
        HorizontalLength=100.0,
        StartCantLeft=0.0,
        EndCantLeft=0.16,
        StartCantRight=0.0,
        EndCantRight=0.0,
        PredefinedType="SINECURVE",
    )

    alignment_segment = file.createIfcAlignmentSegment(
        GlobalId=ifcopenshell.guid.new(), DesignParameters=design_parameters
    )

    mapped_segments = ifcopenshell.api.alignment.map_alignment_cant_segment(file, alignment_segment, 1.5)
    mapped_segment = mapped_segments[0]
    assert len(mapped_segments) == 2
    assert "DISCONTINUOUS" == mapped_segment.Transition
    assert mapped_segment.Placement.Location.Coordinates == pytest.approx((0.0, 0.0, 0.0))
    assert mapped_segment.Placement.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0, 0.0))
    assert mapped_segment.SegmentStart.wrappedValue == pytest.approx(0.0)
    assert mapped_segment.SegmentLength.wrappedValue == pytest.approx(100.0)
    assert mapped_segment.ParentCurve.is_a("IfcSineSpiral")
    assert mapped_segment.ParentCurve.Position.Location.Coordinates == pytest.approx((0.0, 0.0))
    assert mapped_segment.ParentCurve.Position.RefDirection.DirectionRatios == pytest.approx((1.0, 0.0))
    assert mapped_segment.ParentCurve.SineTerm == pytest.approx(-785398.163397448)
    assert mapped_segment.ParentCurve.LinearTerm == pytest.approx(3535.53390593274)
    assert mapped_segment.ParentCurve.ConstantTerm == pytest.approx(None)


def test_map_alignment_cant_segment():
    file = ifcopenshell.file(schema="IFC4X3")
    _BlossCurve_100_0_300_1000_1_Meter(file)
    _BlossCurve_100_0__300__1000_1_Meter(file)
    _BlossCurve_100_0_300_inf_1_Meter(file)
    _BlossCurve_100_0__300__inf_1_Meter(file)
    _BlossCurve_100_0_1000_300_1_Meter(file)
    _BlossCurve_100_0__1000__300_1_Meter(file)
    _BlossCurve_100_0_inf_300_1_Meter(file)
    _BlossCurve_100_0__inf__300_1_Meter(file)
    _ConstantCant_100_0_300_1000_1_Meter(file)
    _ConstantCant_100_0__300__1000_1_Meter(file)
    _ConstantCant_100_0_300_inf_1_Meter(file)
    _ConstantCant_100_0__300__inf_1_Meter(file)
    _ConstantCant_100_0_1000_300_1_Meter(file)
    _ConstantCant_100_0__1000__300_1_Meter(file)
    _ConstantCant_100_0_inf_300_1_Meter(file)
    _ConstantCant_100_0__inf__300_1_Meter(file)
    _CosineCurve_100_0_300_1000_1_Meter(file)
    _CosineCurve_100_0__300__1000_1_Meter(file)
    _CosineCurve_100_0_300_inf_1_Meter(file)
    _CosineCurve_100_0__300__inf_1_Meter(file)
    _CosineCurve_100_0_1000_300_1_Meter(file)
    _CosineCurve_100_0__1000__300_1_Meter(file)
    _CosineCurve_100_0_inf_300_1_Meter(file)
    _CosineCurve_100_0__inf__300_1_Meter(file)
    _HelmertCurve_100_0_300_1000_1_Meter(file)
    _HelmertCurve_100_0__300__1000_1_Meter(file)
    _HelmertCurve_100_0_300_inf_1_Meter(file)
    _HelmertCurve_100_0__300__inf_1_Meter(file)
    _HelmertCurve_100_0_1000_300_1_Meter(file)
    _HelmertCurve_100_0__1000__300_1_Meter(file)
    _HelmertCurve_100_0_inf_300_1_Meter(file)
    _HelmertCurve_100_0__inf__300_1_Meter(file)
    _LinearTransition_100_0_300_1000_1_Meter(file)
    _LinearTransition_100_0__300__1000_1_Meter(file)
    _LinearTransition_100_0_300_inf_1_Meter(file)
    _LinearTransition_100_0__300__inf_1_Meter(file)
    _LinearTransition_100_0_1000_300_1_Meter(file)
    _LinearTransition_100_0__1000__300_1_Meter(file)
    _LinearTransition_100_0_inf_300_1_Meter(file)
    _LinearTransition_100_0__inf__300_1_Meter(file)
    _SineCurve_100_0_300_1000_1_Meter(file)
    _SineCurve_100_0__300__1000_1_Meter(file)
    _SineCurve_100_0_300_inf_1_Meter(file)
    _SineCurve_100_0__300__inf_1_Meter(file)
    _SineCurve_100_0_1000_300_1_Meter(file)
    _SineCurve_100_0__1000__300_1_Meter(file)
    _SineCurve_100_0_inf_300_1_Meter(file)
    _SineCurve_100_0__inf__300_1_Meter(file)

    # VIENESSE BEND NOT IMPLEMENTED
