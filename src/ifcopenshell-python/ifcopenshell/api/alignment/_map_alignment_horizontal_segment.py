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

import math
from collections.abc import Sequence

import ifcopenshell
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import ifcopenshell.util.unit
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._get_cant_segment import _get_cant_segment
from ifcopenshell.api.alignment import _spiral_curvature


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

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

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

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

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

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

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

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    A0, A1, A2, A3, offset = _spiral_curvature.cubic_coefficients(length, start_radius, end_radius)

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

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    (A0_1, A1_1, A2_1), (A0_2, A1_2, A2_2) = _spiral_curvature.helmert_coefficients(length, start_radius, end_radius)

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
            Location=file.createIfcCartesianPoint(
                (
                    start_point.Coordinates[0] + x1 * math.cos(start_direction) - y1 * math.sin(start_direction),
                    start_point.Coordinates[1] + x1 * math.sin(start_direction) + y1 * math.cos(start_direction),
                )
            ),
            RefDirection=file.createIfcDirection(
                (math.cos(start_direction + angle1), math.sin(start_direction + angle1))
            ),
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
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    A0, A1, A2, A3 = _spiral_curvature.bloss_coefficients(length, start_radius, end_radius)

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
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    A0, A1 = _spiral_curvature.cosine_coefficients(length, start_radius, end_radius)

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
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    A0, A1, A2 = _spiral_curvature.sine_coefficients(length, start_radius, end_radius)

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


def _map_viennese_bend(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    design_parameters = segment.DesignParameters

    start_point = design_parameters.StartPoint
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature
    end_radius = design_parameters.EndRadiusOfCurvature
    length = design_parameters.SegmentLength
    gravity_centerline_height = (
        design_parameters.GravityCenterLineHeight if design_parameters.GravityCenterLineHeight != None else 0.0
    )

    angle_unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
    start_direction *= angle_unit_scale

    transition = "DISCONTINUOUS"

    cant_segment = _get_cant_segment(segment)
    if cant_segment:
        start_cant_left = cant_segment.DesignParameters.StartCantLeft
        end_cant_left = cant_segment.DesignParameters.EndCantLeft if cant_segment.DesignParameters.EndCantLeft else 0.0
        start_cant_right = cant_segment.DesignParameters.StartCantRight
        end_cant_right = (
            cant_segment.DesignParameters.EndCantRight if cant_segment.DesignParameters.EndCantRight else 0.0
        )
        cant_layout = cant_segment.Nests[0].RelatingObject
        rail_head_distance = cant_layout.RailHeadDistance
    else:
        start_cant_left = 0.0
        end_cant_left = 0.0
        start_cant_right = 0.0
        end_cant_right = 0.0
        rail_head_distance = 1.0

    cant_angle_start = (start_cant_right - start_cant_left) / rail_head_distance if rail_head_distance else 0.0
    cant_angle_end = (end_cant_right - end_cant_left) / rail_head_distance if rail_head_distance else 0.0

    cant_factor = -420.0 * (gravity_centerline_height / length) * (cant_angle_end - cant_angle_start)

    A0, A1, A2, A3, A4, A5, A6, A7 = _spiral_curvature.viennese_bend_coefficients(
        length, start_radius, end_radius, cant_factor
    )

    parent_curve = file.createIfcSeventhOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        SepticTerm=A7,
        SexticTerm=A6 if A6 != 0.0 else None,
        QuinticTerm=A5 if A5 != 0.0 else None,
        QuarticTerm=A4 if A4 != 0.0 else None,
        CubicTerm=A3 if A3 != 0.0 else None,
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


def _map_alignment_horizontal_segment(file: ifcopenshell.file, segment: entity_instance) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentHorizontalSegment business logic entity instance.
    A pair of entities is returned because a single business logic segment of type HELMERTCURVE maps to two representaiton entities.

    The IfcCurveSegment.Transition transition code is set to DISCONTINUOUS
    """
    expected_type = "IfcAlignmentSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment.is_a()}'.")

    predefined_type = segment.DesignParameters.PredefinedType
    if predefined_type == "LINE":
        result = _map_line(file, segment.DesignParameters)
    elif predefined_type == "CIRCULARARC":
        result = _map_circular_arc(file, segment.DesignParameters)
    elif predefined_type == "CLOTHOID":
        result = _map_clothoid(file, segment.DesignParameters)
    elif predefined_type == "CUBIC":
        result = _map_cubic(file, segment.DesignParameters)
    elif predefined_type == "HELMERTCURVE":
        result = _map_helmert_curve(file, segment.DesignParameters)
    elif predefined_type == "BLOSSCURVE":
        result = _map_bloss_curve(file, segment.DesignParameters)
    elif predefined_type == "COSINECURVE":
        result = _map_cosine_curve(file, segment.DesignParameters)
    elif predefined_type == "SINECURVE":
        result = _map_sine_curve(file, segment.DesignParameters)
    elif predefined_type == "VIENNESEBEND":
        result = _map_viennese_bend(file, segment)
    else:
        raise TypeError(f"Unexpected predefined type: '{predefined_type}'.")

    return result
