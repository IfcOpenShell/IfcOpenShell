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
from ifcopenshell import entity_instance
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
from typing import Sequence
import math


def _get_curve_factor(design_parameters: entity_instance) -> float:
    start_radius = design_parameters.StartRadiusOfCurvature
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    f = (0.0 if end_radius == 0.0 else length / end_radius) - (0.0 if start_radius == 0.0 else length / start_radius)
    return f


def _map_line(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    parent_curve = file.create_entity(
        type="IfcLine",
        Pnt=file.create_entity(
            type="IfcCartesianPoint",
            Coordinates=(0.0, 0.0),
        ),
        Dir=file.create_entity(
            type="IfcVector",
            Orientation=file.create_entity(
                type="IfcDirection",
                DirectionRatios=(1.0, 0.0),
            ),
            Magnitude=1.0,
        ),
    )
    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection(
                (math.cos(start_direction), math.sin(start_direction)),
            ),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_circular_arc(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    parent_curve = file.createIfcCircle(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        Radius=math.fabs(start_radius),
    )

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.createIfcAxis2Placement2D(
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length * (start_radius / math.fabs(start_radius))),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_clothoid(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    f = _get_curve_factor(design_parameters)
    A = (length / math.sqrt(math.fabs(f))) * (f / math.fabs(f))
    parent_curve = file.createIfcClothoid(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        ClothoidConstant=A,
    )

    if (math.fabs(start_radius) < math.fabs(end_radius) and start_radius != 0.0) or end_radius == 0.0:
        offset = -length - (length * start_radius / (end_radius - start_radius) if end_radius != 0.0 else 0.0)
    else:
        offset = length * end_radius / (start_radius - end_radius) if start_radius != 0.0 else 0.0

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(offset),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_cubic(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    offset = 0.0
    A0 = 0.0  # constant term
    A1 = 0.0  # linear term
    A2 = 0.0  # quadratic term
    A3 = 0.0  # cubic term

    if end_radius != 0.0 and start_radius != 0.0 and end_radius != start_radius:
        f = (start_radius - end_radius) / end_radius  # note, this "f" is different that _get_curve_factor computes
        A3 = f / (6.0 * start_radius * length)
        offset = length / f
    elif end_radius != 0.0:
        A3 = 1.0 / (6.0 * end_radius * length)
        offset = 0.0
    elif start_radius != 0.0:
        A3 = -1.0 / (6.0 * start_radius * length)
        offset = -length

    parent_curve = file.createIfcPolynomialCurve(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        CoefficientsX=(0.0, 1.0),
        CoefficientsY=(A0, A1, A2, A3),
    )

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(offset),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_helmert_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"
    f = _get_curve_factor(design_parameters)

    a0_1 = 0.0 * f + length / start_radius if start_radius != 0 else 0.0  # constant term, first half
    a1_1 = 0.0 * f  # linear term, first half
    a2_1 = 2.0 * f  # quadratic term, first half

    A0_1 = length * math.pow(math.fabs(a0_1), -1.0 / 1.0) * a0_1 / math.fabs(a0_1) if a0_1 != 0.0 else 0.0
    A1_1 = length * math.pow(math.fabs(a1_1), -1.0 / 2.0) * a1_1 / math.fabs(a1_1) if a1_1 != 0.0 else 0.0
    A2_1 = length * math.pow(math.fabs(a2_1), -1.0 / 3.0) * a2_1 / math.fabs(a2_1) if a2_1 != 0.0 else 0.0

    x1, y1, angle1 = ifcopenshell_wrapper.helmert_curve_point(A0_1, A1_1, A2_1, length / 2)

    parent_curve1 = file.createIfcSecondOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        QuadraticTerm=A2_1,
        LinearTerm=A1_1 if A1_1 != 0.0 else None,
        ConstantTerm=A0_1 if A0_1 != 0.0 else None,
    )

    curve_segment1 = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length / 2),
        ParentCurve=parent_curve1,
    )

    a0_2 = -1.0 * f + (length / start_radius if start_radius != 0.0 else 0.0)  # constant term, second half
    a1_2 = 4.0 * f  # linear term, second half
    a2_2 = -2.0 * f  # quadratic term, second half

    A0_2 = length * math.pow(math.fabs(a0_2), -1.0 / 1.0) * (a0_2 / math.fabs(a0_2)) if a0_2 != 0.0 else 0.0
    A1_2 = length * math.pow(math.fabs(a1_2), -1.0 / 2.0) * (a1_2 / math.fabs(a1_2)) if a1_2 != 0.0 else 0.0
    A2_2 = length * math.pow(math.fabs(a2_2), -1.0 / 3.0) * (a2_2 / math.fabs(a2_2)) if a2_2 != 0.0 else 0.0

    x2, y2, angle2 = ifcopenshell_wrapper.helmert_curve_point(A0_2, A1_2, A2_2, length / 2)
    anglep = angle1 - angle2
    xp = x1 - x2 * math.cos(anglep) + y2 * math.sin(anglep)
    yp = y1 - x2 * math.sin(anglep) - y2 * math.cos(anglep)

    parent_curve2 = file.createIfcSecondOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((xp, yp)),
            RefDirection=file.createIfcDirection((math.cos(anglep), math.sin(anglep))),
        ),
        QuadraticTerm=A2_2,
        LinearTerm=A1_2 if A1_2 != 0.0 else None,
        ConstantTerm=A0_2 if A0_2 != 0.0 else None,
    )

    curve_segment2 = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=file.createIfcCartesianPoint((x1, y1)),
            RefDirection=file.createIfcDirection((math.cos(angle1), math.sin(angle1))),
        ),
        SegmentStart=file.createIfcLengthMeasure(length / 2),
        SegmentLength=file.createIfcLengthMeasure(length / 2),
        ParentCurve=parent_curve2,
    )

    return curve_segment1, curve_segment2


def _map_bloss_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"
    f = _get_curve_factor(design_parameters)

    a0 = length / start_radius if start_radius != 0.0 else 0.0  # constant term
    a1 = 0.0  # linear term
    a2 = 3.0 * f  # quadratic term
    a3 = -2.0 * f  # cubic term

    A0 = length * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = length * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0
    A2 = length * math.pow(math.fabs(a2), -1.0 / 3.0) * (a2 / math.fabs(a2)) if a2 != 0.0 else 0.0
    A3 = length * math.pow(math.fabs(a3), -1.0 / 4.0) * (a3 / math.fabs(a3)) if a3 != 0.0 else 0.0

    parent_curve = file.createIfcThirdOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        CubicTerm=A3,
        QuadraticTerm=A2 if A2 != 0.0 else None,
        LinearTerm=A1 if A1 != 0.0 else None,
        ConstantTerm=A0 if A0 != 0.0 else None,
    )

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_cosine_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    f = _get_curve_factor(design_parameters)

    a0 = 0.5 * f + (length / start_radius if start_radius != 0.0 else 0.0)
    a1 = -0.5 * f

    A0 = length * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = length * math.pow(math.fabs(a1), -1.0 / 1.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0

    parent_curve = file.createIfcCosineSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        CosineTerm=A1,
        ConstantTerm=(A0 if A0 != 0.0 else None),
    )

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_sine_curve(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    length = design_parameters.SegmentLength

    transition = "DISCONTINUOUS"

    f = _get_curve_factor(design_parameters)
    a0 = length / start_radius if start_radius != 0.0 else 0.0
    a1 = f
    a2 = -f / (2.0 * math.pi)

    A0 = length * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = length * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0
    A2 = length * math.pow(math.fabs(a2), -1.0 / 1.0) * (a2 / math.fabs(a2)) if a2 != 0.0 else 0.0

    parent_curve = file.createIfcSineSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)),
            RefDirection=file.createIfcDirection((1.0, 0.0)),
        ),
        SineTerm=A2,
        LinearTerm=(A1 if A1 != 0.0 else None),
        ConstantTerm=(A0 if A0 != 0.0 else None),
    )

    curve_segment = file.create_entity(
        type="IfcCurveSegment",
        Transition=transition,
        Placement=file.create_entity(
            type="IfcAxis2Placement2D",
            Location=start_point,
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction))),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_viennese_bend(file: ifcopenshell.file, design_parameters: entity_instance) -> Sequence[entity_instance]:
    raise NotImplementedError("VIENNESEBEND not implemented")


def map_alignment_horizontal_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentHorizontalSegment business logic entity instance.
    A pair of entities is returned because a single business logic segment of type HELMERTCURVE maps to two representaiton entities.

    The IfcCurveSegment.Transition transition code is set to DISCONTINUOUS
    """
    expected_type = "IfcAlignmentSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment.is_a()}'.")

    match segment.DesignParameters.PredefinedType:
        case "LINE":
            result = _map_line(file, segment.DesignParameters)
        case "CIRCULARARC":
            result = _map_circular_arc(file, segment.DesignParameters)
        case "CLOTHOID":
            result = _map_clothoid(file, segment.DesignParameters)
        case "CUBIC":
            result = _map_cubic(file, segment.DesignParameters)
        case "HELMERTCURVE":
            result = _map_helmert_curve(file, segment.DesignParameters)
        case "BLOSSCURVE":
            result = _map_bloss_curve(file, segment.DesignParameters)
        case "COSINECURVE":
            result = _map_cosine_curve(file, segment.DesignParameters)
        case "SINECURVE":
            result = _map_sine_curve(file, segment.DesignParameters)
        case "VIENNESEBEND":
            result = _map_viennese_bend(file, segment.DesignParameters)
        case _:
            raise TypeError("Unexpected predefined type")

    return result
