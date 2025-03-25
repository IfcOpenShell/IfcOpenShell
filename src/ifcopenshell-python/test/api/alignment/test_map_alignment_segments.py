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


def test_map_alignment_horizontal_segment():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(Name="Test")
    geometric_representation_context = ifcopenshell.api.context.add_context(file, context_type="Model")
    axis_model_representation_subcontext = ifcopenshell.api.context.add_context(
        file,
        context_type="Model",
        context_identifier="Axis",
        target_view="MODEL_VIEW",
        parent=geometric_representation_context,
    )

    coordinates = [(500.0, 2500.0), (3340.0, 660.0), (4340.0, 5000.0), (7600.0, 4560.0), (8480.0, 2010.0)]
    radii = [(1000.0), (1250.0), (950.0)]
    vpoints = [(0.0, 100.0), (2000.0, 135.0), (5000.0, 105.0), (7400.0, 153.0), (9800.0, 105.0), (12800.0, 90.0)]
    lengths = [(1600.0), (1200.0), (2000.0), (800.0)]

    alignment = ifcopenshell.api.alignment.create_alignment_by_pi_method(
        file, "TestAlignment", coordinates, radii, vpoints, lengths
    )

    horizontal_alignment = alignment.IsNestedBy[0].RelatedObjects[0]
    assert horizontal_alignment.is_a("IfcAlignmentHorizontal")

    composite_curve = file.create_entity(
        type="IfcCompositeCurve",
        Segments=[],
        SelfIntersect=False,
    )

    ifcopenshell.api.alignment.map_alignment_segments(file, horizontal_alignment, composite_curve)
    assert len(composite_curve.Segments) == 8
    assert composite_curve.Segments[0].ParentCurve.is_a("IfcLine")
    assert composite_curve.Segments[0].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[1].ParentCurve.is_a("IfcCircle")
    assert composite_curve.Segments[1].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[2].ParentCurve.is_a("IfcLine")
    assert composite_curve.Segments[2].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[3].ParentCurve.is_a("IfcCircle")
    assert composite_curve.Segments[3].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[4].ParentCurve.is_a("IfcLine")
    assert composite_curve.Segments[4].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[5].ParentCurve.is_a("IfcCircle")
    assert composite_curve.Segments[5].Transition == "CONTSAMEGRADIENT"
    assert composite_curve.Segments[6].ParentCurve.is_a("IfcLine")
    assert composite_curve.Segments[6].Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert composite_curve.Segments[7].ParentCurve.is_a("IfcLine")
    assert composite_curve.Segments[7].Transition == "DISCONTINUOUS"

    vertical_alignment = alignment.IsNestedBy[0].RelatedObjects[1]
    assert vertical_alignment.is_a("IfcAlignmentVertical")

    gradient_curve = file.create_entity(
        type="IfcGradientCurve", Segments=[], SelfIntersect=False, BaseCurve=composite_curve, EndPoint=None
    )

    ifcopenshell.api.alignment.map_alignment_segments(file, vertical_alignment, gradient_curve)
    assert len(gradient_curve.Segments) == 10

    assert gradient_curve.Segments[0].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[0].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[1].ParentCurve.is_a("IfcPolynomialCurve")
    assert gradient_curve.Segments[1].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[2].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[2].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[3].ParentCurve.is_a("IfcPolynomialCurve")
    assert gradient_curve.Segments[3].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[4].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[4].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[5].ParentCurve.is_a("IfcPolynomialCurve")
    assert gradient_curve.Segments[5].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[6].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[6].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[7].ParentCurve.is_a("IfcPolynomialCurve")
    assert gradient_curve.Segments[7].Transition == "CONTSAMEGRADIENT"
    assert gradient_curve.Segments[8].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[8].Transition == "CONTSAMEGRADIENTSAMECURVATURE"
    assert gradient_curve.Segments[9].ParentCurve.is_a("IfcLine")
    assert gradient_curve.Segments[9].Transition == "DISCONTINUOUS"
