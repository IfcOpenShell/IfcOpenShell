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

import ifcopenshell
from ifcopenshell import ifcopenshell_wrapper
from ifcopenshell import entity_instance
from typing import Sequence
import math


def _polynomial_length(A: float, B: float, C: float, L: float) -> float:
    # closed form solultion for length of parabolic curve.
    # see https://www.integral-table.com, equation #37
    # Parabolic curve equation: y = A + Bx + Cx^2
    # y' = B + 2Cx
    # Length of a curve = Integral[0,L]( (y')^2 + 1) dx)
    # y'^2 = 4C^2x^2 + 4BCx + B^2
    # Substituting,  Length of a curve = Integral[0,L]( (4C^2)x^2 + (4BC)x + (B^2 + 1)) dx)
    # for eq. #37 cited above, a = 4C^2, b = 4BC, c = B^2 + 1
    a = 4.0 * C * C
    b = 4.0 * B * C
    c = B * B + 1

    v1 = lambda a, b, c, x: (b + 2.0 * a * x) / (4.0 * a)
    v2 = lambda a, b, c, x: math.sqrt(a * x * x + b * x + c)
    v3 = lambda a, b, c, x: (4.0 * a * c - b * b) / (8.0 * math.pow(a, 1.5))
    v4 = lambda a, b, c, x: math.log(math.fabs(2.0 * a * x + b + 2.0 * math.sqrt(a * (a * x * x + b * x + c))))

    fn = lambda a, b, c, x: v1(a, b, c, x) * v2(a, b, c, x) + v3(a, b, c, x) * v4(a, b, c, x)

    curve_length = fn(a, b, c, L) - fn(
        a, b, c, 0
    )  # remember when evaluating an integral, it must be evaluated at end points (L and 0)
    return curve_length


def _map_constant_gradient(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_distance_along = design_parameters.StartDistAlong
    horizontal_length = design_parameters.HorizontalLength
    start_height = design_parameters.StartHeight
    start_gradient = design_parameters.StartGradient
    end_gradient = design_parameters.EndGradient
    radius_of_curvature = design_parameters.RadiusOfCurvature
    transition = "DISCONTINUOUS"

    parent_curve = file.create_entity(
        type="IfcLine",
        Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
        Dir=file.create_entity(
            type="IfcVector",
            Orientation=file.create_entity(
                type="IfcDirection",
                DirectionRatios=(1.0, 0.0),
            ),
            Magnitude=1.0,
        ),
    )

    dx = math.cos(math.atan(start_gradient))
    dy = math.sin(math.atan(start_gradient))
    curve_segment_length = horizontal_length / dx

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((start_distance_along, start_height)),
            RefDirection=file.createIfcDirection((dx, dy)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(curve_segment_length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_parabolic_arc(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_distance_along = design_parameters.StartDistAlong
    horizontal_length = design_parameters.HorizontalLength
    start_height = design_parameters.StartHeight
    start_gradient = design_parameters.StartGradient
    end_gradient = design_parameters.EndGradient
    radius_of_curvature = design_parameters.RadiusOfCurvature
    transition = "DISCONTINUOUS"

    A = start_height
    B = start_gradient
    C = (end_gradient - start_gradient) / (2.0 * horizontal_length)

    parent_curve = file.create_entity(
        type="IfcPolynomialCurve",
        Position=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection(
                (1.0, 0.0),
            ),
        ),
        CoefficientsX=(0.0, 1.0),
        CoefficientsY=(A, B, C),
    )

    dx = math.cos(math.atan(start_gradient))
    dy = math.sin(math.atan(start_gradient))
    curve_segment_length = _polynomial_length(A, B, C, horizontal_length)

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=file.createIfcCartesianPoint((start_distance_along, start_height)),
            RefDirection=file.createIfcDirection((dx, dy)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(curve_segment_length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_circular_arc(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_distance_along = design_parameters.StartDistAlong
    horizontal_length = design_parameters.HorizontalLength
    start_height = design_parameters.StartHeight
    start_gradient = design_parameters.StartGradient
    end_gradient = design_parameters.EndGradient
    radius_of_curvature = design_parameters.RadiusOfCurvature
    transition = "DISCONTINUOUS"

    start_angle = math.atan(start_gradient)
    end_angle = math.atan(end_gradient)
    dx = math.cos(start_angle)
    dy = math.sin(start_angle)
    if start_angle < end_angle:
        radius = horizontal_length / (math.sin(end_angle) - math.sin(start_angle))
        x = -radius * math.sin(start_angle)
        y = radius * math.cos(start_angle)
        start_angle += 3.0 * math.pi / 2.0
        end_angle += 3.0 * math.pi / 2.0
    else:
        radius = horizontal_length / (math.sin(start_angle) - math.sin(end_angle))
        x = radius * math.sin(start_angle)
        y = -radius * math.cos(start_angle)
        start_angle += math.pi / 2.0
        end_angle += math.pi / 2.0

    parent_curve = file.createIfcCircle(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((x, y)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        Radius=radius,
    )

    segment_curve_length = radius * math.fabs(end_angle - start_angle)

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((start_distance_along, start_height)),
            RefDirection=file.createIfcDirection(
                (dx, dy),
            ),
        ),
        SegmentStart=file.createIfcLengthMeasure(radius * start_angle),
        SegmentLength=file.createIfcLengthMeasure(radius * (end_angle - start_angle)),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_clothoid(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("mapping for IfcVerticalSegment.CLOTHOID not implemented")


def map_alignment_vertical_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentVerticalSegment business logic entity instance.
    A pair of entities is returned for consistency with map_alignment_horizontal_segment and map_alignment_cant_segment.

    """
    expected_type = "IfcAlignmentSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment.is_a()}'.")

    match segment.DesignParameters.PredefinedType:
        case "CONSTANTGRADIENT":
            result = _map_constant_gradient(file, segment.DesignParameters)

        case "PARABOLICARC":
            result = _map_parabolic_arc(file, segment.DesignParameters)

        case "CIRCULARARC":
            result = _map_circular_arc(file, segment.DesignParameters)

        case "CLOTHOID":
            result = _map_clothoid(file, segment.DesignParameters)

        case _:
            raise TypeError(f"Unexpected predefined type - got {segment.DesignParameters.PredefinedType}")

    return result
