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
import math


def _test_horizontal() -> ifcopenshell.file:
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

    # creates an IfcAlignment with an IfcAlignmentHorizontal layout containing only the zero length segment
    ali = ifcopenshell.api.alignment.create(file, "A1")

    # append a segment to the horizontal layout
    horizontal_alignment = ifcopenshell.api.alignment.get_horizontal_layout(ali)

    curve = ifcopenshell.api.alignment.get_curve(horizontal_alignment)
    assert curve == None  # for single horizontal, geometric representation is on IfcAlignment
    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcCompositeCurve")
    assert len(curve.Segments) == 1

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
    end = ifcopenshell.api.alignment.create_layout_segment(file, horizontal_alignment, design_parameters)

    assert len(horizontal_alignment.IsNestedBy[0].RelatedObjects) == 2

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 100.0
    assert y == 0.0
    assert z == 0.0

    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcCompositeCurve")
    assert len(curve.Segments) == 2

    design_parameters = file.create_entity(
        type="IfcAlignmentHorizontalSegment",
        StartTag=None,
        EndTag=None,
        StartPoint=file.createIfcCartesianPoint(Coordinates=((x.item(), y.item()))),
        StartDirection=math.pi / 6,
        StartRadiusOfCurvature=0.0,
        EndRadiusOfCurvature=0.0,
        SegmentLength=50.0,
        GravityCenterLineHeight=None,
        PredefinedType="LINE",
    )

    end = ifcopenshell.api.alignment.create_layout_segment(file, horizontal_alignment, design_parameters)
    assert len(horizontal_alignment.IsNestedBy[0].RelatedObjects) == 3

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 100.0 + 50.0 * math.cos(math.pi / 6)
    assert y == 50.0 * math.sin(math.pi / 6)
    assert z == 0.0

    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcCompositeCurve")
    assert len(curve.Segments) == 3

    return file


def _test_horizontal_vertical():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
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

    # creates an IfcAlignment with an IfcAlignmentHorizontal layout containing only the zero length segment
    ali = ifcopenshell.api.alignment.create(file, "A1", True)

    # append a segment to the horizontal layout
    horizontal_alignment = ifcopenshell.api.alignment.get_horizontal_layout(ali)
    vertical_alignment = ifcopenshell.api.alignment.get_vertical_layout(ali)

    curve = ifcopenshell.api.alignment.get_curve(horizontal_alignment)
    assert curve == None

    curve = ifcopenshell.api.alignment.get_curve(vertical_alignment)
    assert curve == None

    basis_curve = ifcopenshell.api.alignment.get_basis_curve(ali)
    assert basis_curve.is_a("IfcCompositeCurve")
    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcGradientCurve")
    assert len(basis_curve.Segments) == 1
    assert len(curve.Segments) == 1

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
    end = ifcopenshell.api.alignment.create_layout_segment(file, horizontal_alignment, design_parameters)
    basis_curve = ifcopenshell.api.alignment.get_basis_curve(ali)
    assert basis_curve.is_a("IfcCompositeCurve")
    assert len(basis_curve.Segments) == 2

    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=50.0,
        StartHeight=20.0,
        StartGradient=1.0 / 100.0,
        EndGradient=1.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vertical_alignment, design_parameters)

    assert len(vertical_alignment.IsNestedBy[0].RelatedObjects) == 2

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 50.0
    assert y == 20.5
    assert z == 0.0

    dx = end[0, 0]
    dy = end[1, 0]
    gradient = dy / dx

    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=50.0,
        HorizontalLength=50.0,
        StartHeight=y.item(),
        StartGradient=-gradient,
        EndGradient=-gradient,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vertical_alignment, design_parameters)

    assert len(vertical_alignment.IsNestedBy[0].RelatedObjects) == 3

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 100.0
    assert y == 20.0
    assert z == 0.0

    basis_curve = ifcopenshell.api.alignment.get_basis_curve(ali)
    assert basis_curve.is_a("IfcCompositeCurve")
    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcGradientCurve")
    assert len(basis_curve.Segments) == 2
    assert len(curve.Segments) == 3


def _test_horizontal_vertical2(file: ifcopenshell.file):
    ali = file.by_type("IfcAlignment")[0]

    vertical_alignment = ifcopenshell.api.alignment.get_vertical_layout(ali)
    assert vertical_alignment == None

    vertical_alignment = ifcopenshell.api.alignment.add_vertical_layout(file, ali)

    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=0.0,
        HorizontalLength=50.0,
        StartHeight=20.0,
        StartGradient=1.0 / 100.0,
        EndGradient=1.0 / 100.0,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vertical_alignment, design_parameters)

    assert len(vertical_alignment.IsNestedBy[0].RelatedObjects) == 2

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 50.0
    assert y == 20.5
    assert z == 0.0

    dx = end[0, 0]
    dy = end[1, 0]
    gradient = dy / dx

    design_parameters = file.createIfcAlignmentVerticalSegment(
        StartDistAlong=50.0,
        HorizontalLength=50.0,
        StartHeight=y.item(),
        StartGradient=-gradient,
        EndGradient=-gradient,
        PredefinedType="CONSTANTGRADIENT",
    )
    end = ifcopenshell.api.alignment.create_layout_segment(file, vertical_alignment, design_parameters)

    assert len(vertical_alignment.IsNestedBy[0].RelatedObjects) == 3

    x = end[0, 3]
    y = end[1, 3]
    z = end[2, 3]

    assert x == 100.0
    assert y == 20.0
    assert z == 0.0

    curve = ifcopenshell.api.alignment.get_curve(ali)
    assert curve.is_a("IfcGradientCurve")
    assert len(curve.Segments) == 3


def test_append_segment():
    file = _test_horizontal()
    _test_horizontal_vertical()
    _test_horizontal_vertical2(file)


test_append_segment()
