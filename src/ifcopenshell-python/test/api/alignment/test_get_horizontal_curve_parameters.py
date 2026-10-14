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

# This file was generated with the assistance of an AI coding tool.

import math

import pytest

import ifcopenshell.api.alignment
import ifcopenshell.api.context
import ifcopenshell.api.unit
import test.bootstrap


def _horizontal_segments(radii):
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")
    ifcopenshell.api.unit.assign_unit(file, units=[length])
    context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    # A 90 degree turn to the left at (1000, 0)
    alignment = ifcopenshell.api.alignment.create_by_pi_method(
        file, "TestAlignment", [(0.0, 0.0), (1000.0, 0.0), (1000.0, 1000.0)], radii
    )
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    return file, [
        segment
        for segment in ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects
        if segment.DesignParameters.SegmentLength > 0.0
    ]


@test.bootstrap.requires_ifc4x3
def test_circular_curve():
    file, (line, arc, _) = _horizontal_segments([500.0])
    curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(arc)

    assert curve.start_point == pytest.approx((500.0, 0.0))
    assert curve.end_point == pytest.approx((1000.0, 500.0))
    assert curve.pi == pytest.approx((1000.0, 0.0))
    assert curve.center == pytest.approx((500.0, 500.0))
    assert curve.delta == pytest.approx(math.pi / 2.0)
    assert curve.length == pytest.approx(250.0 * math.pi)
    assert curve.long_chord == pytest.approx(1000.0 * math.sin(math.pi / 4.0))
    assert curve.start_tangent == curve.end_tangent == pytest.approx(500.0)
    assert curve.radius == pytest.approx(500.0)
    assert curve.tangent == pytest.approx(500.0)
    assert curve.external == pytest.approx(500.0 * (math.sqrt(2.0) - 1.0))
    assert curve.mid_ordinate == pytest.approx(500.0 * (1.0 - math.sqrt(0.5)))

    # The design parameters can also be passed directly
    assert ifcopenshell.api.alignment.get_horizontal_curve_parameters(arc.DesignParameters) == curve


@test.bootstrap.requires_ifc4x3
def test_straight():
    file, (line, _, _) = _horizontal_segments([500.0])
    curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(line)

    assert curve.start_point == pytest.approx((0.0, 0.0))
    assert curve.end_point == pytest.approx((500.0, 0.0))
    assert curve.delta == 0.0
    assert curve.length == pytest.approx(500.0)
    assert curve.pi is None
    assert curve.center is None
    assert curve.radius is curve.tangent is curve.external is curve.mid_ordinate is None
    assert curve.long_chord is curve.start_tangent is curve.end_tangent is None


@test.bootstrap.requires_ifc4x3
def test_spiral_curve_spiral():
    file, segments = _horizontal_segments([(500.0, 100.0, 100.0)])
    spiral_in, arc, spiral_out = segments[1:4]

    # Each spiral turns L / 2R and the arc the rest of the 90 degrees
    spiral = ifcopenshell.api.alignment.get_horizontal_curve_parameters(spiral_in)
    assert spiral.delta == pytest.approx(0.1)
    assert spiral.length == pytest.approx(100.0)
    # Long tangent, short tangent and long chord of a clothoid from its end offsets X, Y and angle
    x, y, theta = ifcopenshell.api.alignment.compute_clothoid_end(100.0, 0.0, 1.0 / 500.0)
    assert spiral.start_tangent == pytest.approx(x - y / math.tan(theta))
    assert spiral.end_tangent == pytest.approx(y / math.sin(theta))
    assert spiral.long_chord == pytest.approx(math.hypot(x, y))
    assert spiral.radius is spiral.tangent is spiral.external is spiral.mid_ordinate is None
    assert spiral.pi is not None and spiral.center is not None
    assert spiral.end_point == pytest.approx(tuple(arc.DesignParameters.StartPoint.Coordinates), abs=1e-6)

    curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(arc)
    assert curve.delta == pytest.approx(math.pi / 2.0 - 0.2)
    assert curve.radius == pytest.approx(500.0)
    assert curve.tangent == pytest.approx(500.0 * math.tan(curve.delta / 2.0))
    assert curve.end_point == pytest.approx(tuple(spiral_out.DesignParameters.StartPoint.Coordinates), abs=1e-6)


@test.bootstrap.requires_ifc4x3
def test_right_turn_has_negative_delta():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    segment = file.createIfcAlignmentHorizontalSegment(
        StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
        StartDirection=0.0,
        StartRadiusOfCurvature=-100.0,
        EndRadiusOfCurvature=-100.0,
        SegmentLength=100.0 * math.pi / 3.0,
        PredefinedType="CIRCULARARC",
    )
    curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(segment)

    assert curve.delta == pytest.approx(-math.pi / 3.0)
    assert curve.center == pytest.approx((0.0, -100.0))
    assert curve.radius == pytest.approx(100.0)
    assert curve.tangent == pytest.approx(100.0 * math.tan(math.pi / 6.0))


def test_rejects_other_segments():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    with pytest.raises(TypeError):
        ifcopenshell.api.alignment.get_horizontal_curve_parameters(file.createIfcAlignmentVerticalSegment())


@test.bootstrap.requires_ifc4x3
def test_spiral_radii():
    file, (line, spiral_in, arc, spiral_out, _) = _horizontal_segments([(500.0, 100.0, 100.0)])

    # A spiral reports the radius at each end, infinite where it meets a straight
    entry = ifcopenshell.api.alignment.get_horizontal_curve_parameters(spiral_in)
    assert entry.start_radius == math.inf
    assert entry.end_radius == pytest.approx(500.0)
    exit = ifcopenshell.api.alignment.get_horizontal_curve_parameters(spiral_out)
    assert exit.start_radius == pytest.approx(500.0)
    assert exit.end_radius == math.inf

    # Lines and circular curves don't have them; a circular curve has its radius instead
    for segment in (line, arc):
        curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(segment)
        assert curve.start_radius is curve.end_radius is None


def _single_spiral(kind, start_radius, end_radius):
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    ifcopenshell.api.unit.assign_unit(file, units=[ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")])
    context = ifcopenshell.api.context.add_context(file, context_type="Model")
    ifcopenshell.api.context.add_context(
        file, context_type="Model", context_identifier="Axis", target_view="MODEL_VIEW", parent=context
    )
    alignment = ifcopenshell.api.alignment.create(file, "TestAlignment")
    ifcopenshell.api.alignment.create_layout_segment(
        file,
        ifcopenshell.api.alignment.get_horizontal_layout(alignment),
        file.createIfcAlignmentHorizontalSegment(
            StartPoint=file.createIfcCartesianPoint((0.0, 0.0)),
            StartDirection=0.0,
            StartRadiusOfCurvature=start_radius,
            EndRadiusOfCurvature=end_radius,
            SegmentLength=100.0,
            PredefinedType=kind,
        ),
    )
    horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    segment = ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects[0]
    return ifcopenshell.api.alignment.get_horizontal_curve_parameters(segment)


@test.bootstrap.requires_ifc4x3
@pytest.mark.parametrize(
    "kind,start_radius,end_radius",
    [
        ("CLOTHOID", -1000.0, -300.0),  # arc to arc, to the right: radii are positive like radius
        ("COSINECURVE", 300.0, 1000.0),
        ("CLOTHOID", -1000.0, -1000.0),  # a spiral whose radius doesn't change is still a spiral
    ],
)
def test_arc_to_arc_spiral_radii(kind, start_radius, end_radius):
    curve = _single_spiral(kind, start_radius, end_radius)
    assert curve.start_radius == pytest.approx(abs(start_radius))
    assert curve.end_radius == pytest.approx(abs(end_radius))
    assert curve.radius is None
