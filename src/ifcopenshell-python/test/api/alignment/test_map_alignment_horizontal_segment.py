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
import math

def _BlossCurve_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == 120.98967350244398
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -112.62478804436063
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0

def _BlossCurve_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == -120.98967350244398
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 112.62478804436063
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0

def _BlossCurve_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == 110.66819197003217
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -100.0
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0

def _BlossCurve_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == -110.66819197003217
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 100.0
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0

def _BlossCurve_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == -120.98967350244398
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 112.62478804436063
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 1000.0

def _BlossCurve_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == 120.98967350244398
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -112.62478804436063
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -1000.0

def _BlossCurve_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == -110.66819197003217
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 100.0
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == None

def _BlossCurve_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="BLOSSCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcThirdOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CubicTerm == 110.66819197003217
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -100.0
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == None

def _CircularArc_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == -100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == -100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 1000.0

def _CircularArc_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == -100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _CircularArc_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CIRCULARARC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == -100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCircle")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Radius == 300.0

def _Clothoid_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -142.85714285714286
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == -207.01966780270627

def _Clothoid_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -142.85714285714286
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == 207.01966780270627

def _Clothoid_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -100.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == -173.20508075688775
	
def _Clothoid_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -100.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == 173.20508075688775

def _Clothoid_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 42.857142857142854
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == 207.01966780270627

def _Clothoid_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 42.857142857142854
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == -207.01966780270627

def _Clothoid_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == 173.20508075688775

def _Clothoid_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CLOTHOID")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcClothoid")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.ClothoidConstant == -173.20508075688775

def _CosineCurve_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == 857.1428571428573
	assert mapped_segments[0].ParentCurve.ConstantTerm == 461.5384615384615

def _CosineCurve_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == -857.1428571428573
	assert mapped_segments[0].ParentCurve.ConstantTerm == -461.5384615384615

def _CosineCurve_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == 600.0
	assert mapped_segments[0].ParentCurve.ConstantTerm == 600.0

def _CosineCurve_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == -600.0
	assert mapped_segments[0].ParentCurve.ConstantTerm == -600.0

def _CosineCurve_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == -857.1428571428573
	assert mapped_segments[0].ParentCurve.ConstantTerm == 461.5384615384615

def _CosineCurve_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == 857.1428571428573
	assert mapped_segments[0].ParentCurve.ConstantTerm == -461.5384615384615

def _CosineCurve_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == -600.0
	assert mapped_segments[0].ParentCurve.ConstantTerm == 600.0

def _CosineCurve_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="COSINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcCosineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CosineTerm == 600.0
	assert mapped_segments[0].ParentCurve.ConstantTerm == -600.0

def _Cubic_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -142.85714285714286
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, -3.888888888888889e-06)

def _Cubic_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -142.85714285714286
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, 3.8888888888888889e-06)

def _Cubic_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -100.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, -5.555555555555556e-06)

def _Cubic_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == -100.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, 5.555555555555556e-06)

def _Cubic_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 42.857142857142854
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, 3.888888888888889e-06)

def _Cubic_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 42.857142857142854
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, -3.888888888888889e-06)

def _Cubic_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, 5.555555555555556e-06)

def _Cubic_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="CUBIC")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcPolynomialCurve")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.CoefficientsX == (0.0, 1.0)
	assert mapped_segments[0].ParentCurve.CoefficientsY == (0.0, 0.0, 0.0, -5.555555555555556e-06)

def _HelmertCurve_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -128.9231989389298
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.79980344909147, 3.9160313941794076)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9892460407218963, 0.146260968532457)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (-0.009321141429516372, 0.46831933573745577)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9992574637140321, -0.03852948496670688)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == 128.9231989389298
	assert mapped_segments[1].ParentCurve.LinearTerm == -103.50983390135313
	assert mapped_segments[1].ParentCurve.ConstantTerm == 176.47058823529412

def _HelmertCurve_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 128.9231989389298
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.79980344909147, -3.9160313941794076)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9892460407218963, -0.146260968532457)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (-0.009321141429516372, -0.46831933573745577)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9992574637140321, 0.03852948496670688)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == -128.9231989389298
	assert mapped_segments[1].ParentCurve.LinearTerm == 103.50983390135313
	assert mapped_segments[1].ParentCurve.ConstantTerm == -176.47058823529412

def _HelmertCurve_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -114.47142425533319
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.812254369146046, 3.812634946725528)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9904138664989948, 0.1381317235341378)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (-0.010305467756443198, 0.6738837916692928)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9984794480380026, -0.05512523782919828)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == 114.47142425533319
	assert mapped_segments[1].ParentCurve.LinearTerm == -86.60254037844388
	assert mapped_segments[1].ParentCurve.ConstantTerm == 150.0

def _HelmertCurve_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 114.47142425533319
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.812254369146046, -3.812634946725528)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9904138664989948, -0.1381317235341378)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (-0.010305467756443198, -0.6738837916692928)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9984794480380026, 0.05512523782919828)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == -114.47142425533319
	assert mapped_segments[1].ParentCurve.LinearTerm == 86.60254037844388
	assert mapped_segments[1].ParentCurve.ConstantTerm == -150.0

def _HelmertCurve_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 128.9231989389298
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == 1000.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.968101127401276, 1.4925275284309163)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.997594495159641, 0.0693197174487962)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (0.010408767953926904, -0.4828832446956578)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9992463304688143, 0.03881714884698913)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == -128.9231989389298
	assert mapped_segments[1].ParentCurve.LinearTerm == 103.50983390135313
	assert mapped_segments[1].ParentCurve.ConstantTerm == -750.0000000000002

def _HelmertCurve_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -128.9231989389298
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == -1000.0
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.968101127401276, -1.4925275284309163)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.997594495159641, -0.0693197174487962)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (0.010408767953926904, 0.4828832446956578)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9992463304688143, -0.03881714884698913)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == 128.9231989389298
	assert mapped_segments[1].ParentCurve.LinearTerm == -103.50983390135313
	assert mapped_segments[1].ParentCurve.ConstantTerm == 750.0000000000002

def _HelmertCurve_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == 114.47142425533319
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == None
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.99724421633614, 0.3472044441797676)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9996143498860809, 0.027769614722351524)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (0.011625841243773832, -0.6968669147609581)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9984543318840984, 0.05557829739996359)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == -114.47142425533319
	assert mapped_segments[1].ParentCurve.LinearTerm == 86.60254037844388
	assert mapped_segments[1].ParentCurve.ConstantTerm == -300.0

def _HelmertCurve_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="HELMERTCURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
		DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.QuadraticTerm == -114.47142425533319
	assert mapped_segments[0].ParentCurve.LinearTerm == None
	assert mapped_segments[0].ParentCurve.ConstantTerm == None
	assert "DISCONTINUOUS" == mapped_segments[1].Transition
	assert mapped_segments[1].Placement.Location.Coordinates == (49.99724421633614, -0.3472044441797676)
	assert mapped_segments[1].Placement.RefDirection.DirectionRatios == (0.9996143498860809, -0.027769614722351524)
	assert mapped_segments[1].SegmentStart.wrappedValue == 50.0
	assert mapped_segments[1].SegmentLength.wrappedValue == 50.0
	assert mapped_segments[1].ParentCurve.is_a("IfcSecondOrderPolynomialSpiral")
	assert mapped_segments[1].ParentCurve.Position.Location.Coordinates == (0.011625841243773832, 0.6968669147609581)
	assert mapped_segments[1].ParentCurve.Position.RefDirection.DirectionRatios == (0.9984543318840984, -0.05557829739996359)
	assert mapped_segments[1].ParentCurve.QuadraticTerm == 114.47142425533319
	assert mapped_segments[1].ParentCurve.LinearTerm == -86.60254037844388
	assert mapped_segments[1].ParentCurve.ConstantTerm == 300.0

def _Line_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _Line_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="LINE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcLine")
	assert mapped_segments[0].ParentCurve.Pnt.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Orientation.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.Dir.Magnitude == 1.0

def _SineCurve_100_0_300_1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=1000.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == 2692.7937030769654
	assert mapped_segments[0].ParentCurve.LinearTerm == -207.01966780270627
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0

def _SineCurve_100_0__300__1000_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=-1000.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == -2692.7937030769654
	assert mapped_segments[0].ParentCurve.LinearTerm == 207.01966780270627
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0

def _SineCurve_100_0_300_inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == 1884.9555921538763
	assert mapped_segments[0].ParentCurve.LinearTerm == -173.20508075688775
	assert mapped_segments[0].ParentCurve.ConstantTerm == 300.0

def _SineCurve_100_0__300__inf_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-300.0,
		EndRadiusOfCurvature=0.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == -1884.9555921538763
	assert mapped_segments[0].ParentCurve.LinearTerm == 173.20508075688775
	assert mapped_segments[0].ParentCurve.ConstantTerm == -300.0

def _SineCurve_100_0_1000_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=1000.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == -2692.7937030769654
	assert mapped_segments[0].ParentCurve.LinearTerm == 207.01966780270627
	assert mapped_segments[0].ParentCurve.ConstantTerm == 1000.0

def _SineCurve_100_0__1000__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=-1000.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == 2692.7937030769654
	assert mapped_segments[0].ParentCurve.LinearTerm == -207.01966780270627
	assert mapped_segments[0].ParentCurve.ConstantTerm == -1000.0

def _SineCurve_100_0_inf_300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=300.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == -1884.9555921538763
	assert mapped_segments[0].ParentCurve.LinearTerm == 173.20508075688775
	assert mapped_segments[0].ParentCurve.ConstantTerm == None

def _SineCurve_100_0__inf__300_1_Meter(file):
	design_parameters = file.createIfcAlignmentHorizontalSegment(
		StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
		StartDirection=0.0,
		StartRadiusOfCurvature=0.0,
		EndRadiusOfCurvature=-300.0,
		SegmentLength=100.0,
		PredefinedType="SINECURVE")

	alignment_segment = file.createIfcAlignmentSegment(
		GlobalId=ifcopenshell.guid.new(),
	DesignParameters=design_parameters)

	mapped_segments = ifcopenshell.api.alignment.map_alignment_segment(file,alignment_segment)
	assert len(mapped_segments) == 2
	assert "DISCONTINUOUS" == mapped_segments[0].Transition
	assert mapped_segments[0].Placement.Location.Coordinates == (0.0, 0.0)
	assert mapped_segments[0].Placement.RefDirection.DirectionRatios == (1.0, 0.0)
	assert mapped_segments[0].SegmentStart.wrappedValue == 0.0
	assert mapped_segments[0].SegmentLength.wrappedValue == 100.0
	assert mapped_segments[0].ParentCurve.is_a("IfcSineSpiral")
	assert mapped_segments[0].ParentCurve.Position.Location.Coordinates == (0.0,0.0)
	assert mapped_segments[0].ParentCurve.Position.RefDirection.DirectionRatios == (1.0,0.0)
	assert mapped_segments[0].ParentCurve.SineTerm == 1884.9555921538763
	assert mapped_segments[0].ParentCurve.LinearTerm == -173.20508075688775
	assert mapped_segments[0].ParentCurve.ConstantTerm == None

def test_map_alignment_horizontal_segment():
	file = ifcopenshell.file(schema="IFC4X3_ADD2")
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
