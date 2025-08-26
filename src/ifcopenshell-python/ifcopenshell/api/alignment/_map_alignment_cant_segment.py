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
from ifcopenshell.api.alignment import get_axis_subcontext
from collections.abc import Sequence
import math


def _get_axis(file: ifcopenshell.file, Ds: float, rail_head_distance: float) -> entity_instance:
    Dy = rail_head_distance
    Dz = 2 * Ds
    D = math.sqrt(Dy * Dy + Dz * Dz)
    return file.createIfcDirection((0.0, Dz / D, Dy / D))


def _map_constant_cant(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Dsr = design_parameters.StartCantRight

    Ds = 0.5 * (Dsl + Dsr)

    transition = "DISCONTINUOUS"

    parent_curve = file.createIfcLine(
        Pnt=file.createIfcCartesianPoint((0.0, 0.0)),
        Dir=file.createIfcVector(Orientation=file.createIfcDirection((1.0, 0.0)), Magnitude=1.0),
    )

    start_point = file.createIfcCartesianPoint((dist_along, Ds, 0.0))
    start_direction = 0.0

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_linear_transition(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = 0.5 * (Dsl + Dsr)
    De = 0.5 * (Del + Der)
    f = De - Ds

    a0 = Ds  # constant term
    a1 = f  # linear term

    transition = "DISCONTINUOUS"

    A0 = math.pow(length, 2.0 / 1.0) * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = math.pow(length, 3.0 / 2.0) * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0

    parent_curve_location = file.createIfcCartesianPoint((0.0, 0.0))
    parent_curve = file.createIfcClothoid(
        Position=file.createIfcAxis2Placement2D(
            Location=parent_curve_location, RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        ClothoidConstant=A1,
    )

    start_point = file.createIfcCartesianPoint(
        (dist_along, math.pow(length, 2.0 / 1.0) / A0 if A0 != 0.0 else 0.0, 0.0)
    )
    start_direction = math.atan(A1 * math.pow(length, 2.0 / 1.0) / math.fabs(math.pow(A1, 3.0 / 1.0)))

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_helmert_curve(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = Dsl + Dsr
    De = Del + Der
    f = De - Ds

    transition = "DISCONTINUOUS"

    # First half
    a0_1 = 2.0 * Ds  # constant term
    a1_1 = 0.0  # linear term
    a2_1 = 4.0 * f  # quadratic term

    A0_1 = (
        math.pow(length, 2.0 / 1.0) * math.pow(math.fabs(a0_1), -1.0 / 1.0) * (a0_1 / math.fabs(a0_1))
        if a0_1 != 0.0
        else 0.0
    )
    A1_1 = (
        math.pow(length, 3.0 / 2.0) * math.pow(math.fabs(a1_1), -1.0 / 2.0) * (a1_1 / math.fabs(a1_1))
        if a1_1 != 0.0
        else 0.0
    )
    A2_1 = (
        math.pow(length, 4.0 / 3.0) * math.pow(math.fabs(a2_1), -1.0 / 3.0) * (a2_1 / math.fabs(a2_1))
        if a2_1 != 0.0
        else 0.0
    )

    parent_curve_1 = file.createIfcSecondOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        QuadraticTerm=A2_1,
        LinearTerm=A1_1 if A1_1 != 0.0 else None,
        ConstantTerm=A0_1 if A0_1 != 0.0 else None,
    )

    start_point_1 = file.createIfcCartesianPoint((dist_along, Ds / 2.0, 0.0))
    start_direction_1 = 0.0

    curve_segment_1 = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point_1,
            Axis=_get_axis(file, Ds / 2.0, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction_1), math.sin(start_direction_1), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length / 2.0),
        ParentCurve=parent_curve_1,
    )

    # Second half

    a0_2 = -2.0 * f + 2.0 * Ds  # constant term
    a1_2 = 8.0 * f  # linear term
    a2_2 = -4.0 * f  # quadratic term

    A0_2 = (
        math.pow(length, 2.0 / 1.0) * math.pow(math.fabs(a0_2), -1.0 / 1.0) * (a0_2 / math.fabs(a0_2))
        if a0_2 != 0.0
        else 0.0
    )
    A1_2 = (
        math.pow(length, 3.0 / 2.0) * math.pow(math.fabs(a1_2), -1.0 / 2.0) * (a1_2 / math.fabs(a1_2))
        if a1_2 != 0.0
        else 0.0
    )
    A2_2 = (
        math.pow(length, 4.0 / 3.0) * math.pow(math.fabs(a2_2), -1.0 / 3.0) * (a2_2 / math.fabs(a2_2))
        if a2_2 != 0.0
        else 0.0
    )

    parent_curve_2 = file.createIfcSecondOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        QuadraticTerm=A2_2,
        LinearTerm=A1_2 if A1_2 != 0.0 else None,
        ConstantTerm=A0_2 if A0_2 != 0.0 else None,
    )

    start_point_2 = file.createIfcCartesianPoint((dist_along + length / 2.0, Ds / 2.0 + f / 4.0, 0.0))
    slope = math.pow(length / 2.0, 2.0) * (2.0 * (length / 2.0) / pow(A2_1, 3.0))
    start_direction_2 = math.atan(slope)

    curve_segment_2 = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point_2,
            Axis=_get_axis(file, (Ds + De) / 4.0, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction_2), math.sin(start_direction_2), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(length / 2.0),
        SegmentLength=file.createIfcLengthMeasure(length / 2.0),
        ParentCurve=parent_curve_2,
    )

    return (curve_segment_1, curve_segment_2)


def _map_bloss_curve(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = 0.5 * (Dsl + Dsr)
    De = 0.5 * (Del + Der)
    f = De - Ds

    a0 = Ds  # constant term
    a1 = 0.0  # linear term
    a2 = 3.0 * f  # quadratic term
    a3 = -2.0 * f  # cubic term

    transition = "DISCONTINUOUS"

    A0 = math.pow(length, 2.0 / 1.0) * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = math.pow(length, 3.0 / 2.0) * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0
    A2 = math.pow(length, 4.0 / 3.0) * math.pow(math.fabs(a2), -1.0 / 3.0) * (a2 / math.fabs(a2)) if a2 != 0.0 else 0.0
    A3 = math.pow(length, 5.0 / 4.0) * math.pow(math.fabs(a3), -1.0 / 4.0) * (a3 / math.fabs(a3)) if a3 != 0.0 else 0.0

    parent_curve = file.createIfcThirdOrderPolynomialSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        CubicTerm=A3,
        QuadraticTerm=A2 if A2 != 0.0 else None,
        LinearTerm=A1 if A1 != 0.0 else None,
        ConstantTerm=A0 if A0 != 0.0 else None,
    )

    start_point = file.createIfcCartesianPoint((dist_along, Ds, 0.0))
    start_direction = 0.0

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_cosine_curve(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = 0.5 * (Dsl + Dsr)
    De = 0.5 * (Del + Der)
    f = De - Ds

    a0 = Ds + 0.5 * f  # constant term
    a1 = -0.5 * f  # cosine term

    A0 = math.pow(length, 2.0) * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = math.pow(length, 2.0) * math.pow(math.fabs(a1), -1.0 / 1.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0

    transition = "DISCONTINUOUS"

    parent_curve = file.createIfcCosineSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        CosineTerm=A1,
        ConstantTerm=A0 if A0 != 0.0 else None,
    )

    start_point = file.createIfcCartesianPoint((dist_along, Ds, 0.0))
    start_direction = 0.0

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_sine_curve(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = 0.5 * (Dsl + Dsr)
    De = 0.5 * (Del + Der)
    f = De - Ds

    a0 = Ds  # constant term
    a1 = f  # linear term
    a2 = -(1.0 / (2.0 * math.pi)) * f  # sine term

    A0 = math.pow(length, 2.0) * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = math.pow(length, 1.5) * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0
    A2 = math.pow(length, 2.0) * math.pow(math.fabs(a2), -1.0 / 1.0) * (a2 / math.fabs(a2)) if a2 != 0.0 else 0.0

    transition = "DISCONTINUOUS"

    parent_curve = file.createIfcSineSpiral(
        Position=file.createIfcAxis2Placement2D(
            Location=file.createIfcCartesianPoint((0.0, 0.0)), RefDirection=file.createIfcDirection((1.0, 0.0))
        ),
        SineTerm=A2,
        LinearTerm=A1 if A1 != 0 else None,
        ConstantTerm=A0 if A0 != 0.0 else None,
    )

    start_point = file.createIfcCartesianPoint((dist_along, Ds, 0.0))
    start_direction = 0.0

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_viennese_bend(
    file: ifcopenshell.file, design_parameters: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    dist_along = design_parameters.StartDistAlong
    length = design_parameters.HorizontalLength
    Dsl = design_parameters.StartCantLeft
    Del = design_parameters.EndCantLeft
    Dsr = design_parameters.StartCantRight
    Der = design_parameters.EndCantRight

    Ds = 0.5 * (Dsl + Dsr)
    De = 0.5 * (Del + Der)
    f = De - Ds

    a0 = Ds  # constant term
    a1 = 0.0  # linear term
    a2 = 0.0 * f  # quadratic term
    a3 = 0.0 * f  # cubic term
    a4 = 35.0 * f  # quartic term
    a5 = -84.0 * f  # quintic term
    a6 = 70.0 * f  # sextic term
    a7 = -20.0 * f  # septic term

    transition = "DISCONTINUOUS"

    A0 = math.pow(length, 2.0 / 1.0) * math.pow(math.fabs(a0), -1.0 / 1.0) * (a0 / math.fabs(a0)) if a0 != 0.0 else 0.0
    A1 = math.pow(length, 3.0 / 2.0) * math.pow(math.fabs(a1), -1.0 / 2.0) * (a1 / math.fabs(a1)) if a1 != 0.0 else 0.0
    A2 = math.pow(length, 4.0 / 3.0) * math.pow(math.fabs(a2), -1.0 / 3.0) * (a2 / math.fabs(a2)) if a2 != 0.0 else 0.0
    A3 = math.pow(length, 5.0 / 4.0) * math.pow(math.fabs(a3), -1.0 / 4.0) * (a3 / math.fabs(a3)) if a3 != 0.0 else 0.0
    A4 = math.pow(length, 6.0 / 5.0) * math.pow(math.fabs(a4), -1.0 / 5.0) * (a4 / math.fabs(a4)) if a4 != 0.0 else 0.0
    A5 = math.pow(length, 7.0 / 6.0) * math.pow(math.fabs(a5), -1.0 / 6.0) * (a5 / math.fabs(a5)) if a5 != 0.0 else 0.0
    A6 = math.pow(length, 8.0 / 7.0) * math.pow(math.fabs(a6), -1.0 / 7.0) * (a6 / math.fabs(a6)) if a6 != 0.0 else 0.0
    A7 = math.pow(length, 9.0 / 8.0) * math.pow(math.fabs(a7), -1.0 / 8.0) * (a7 / math.fabs(a7)) if a7 != 0.0 else 0.0

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

    start_point = file.createIfcCartesianPoint((dist_along, Ds, 0.0))
    start_direction = 0.0

    curve_segment = file.createIfcCurveSegment(
        Transition=transition,
        Placement=file.createIfcAxis2Placement3D(
            Location=start_point,
            Axis=_get_axis(file, Ds, rail_head_distance),
            RefDirection=file.createIfcDirection((math.cos(start_direction), math.sin(start_direction), 0.0)),
        ),
        SegmentStart=file.createIfcLengthMeasure(0.0),
        SegmentLength=file.createIfcLengthMeasure(length),
        ParentCurve=parent_curve,
    )
    return (curve_segment, None)


def _map_alignment_cant_segment(
    file: ifcopenshell.file, segment: entity_instance, rail_head_distance: float
) -> Sequence[entity_instance]:
    """
    Creates IfcCurveSegment entities for the represention of the supplied IfcAlignmentCantSegment business logic entity instance.
    A pair of entities is returned because a single business logic segment of type HELMERTCURVE maps to two representaiton entities.

    The IfcCurveSegment.Transition transition code is set to DISCONTINUOUS.
    """
    expected_type = "IfcAlignmentSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{segment.is_a()}'.")

    predefined_type = segment.DesignParameters.PredefinedType
    if predefined_type == "CONSTANTCANT":
        result = _map_constant_cant(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "LINEARTRANSITION":
        result = _map_linear_transition(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "HELMERTCURVE":
        result = _map_helmert_curve(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "BLOSSCURVE":
        result = _map_bloss_curve(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "COSINECURVE":
        result = _map_cosine_curve(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "SINECURVE":
        result = _map_sine_curve(file, segment.DesignParameters, rail_head_distance)
    elif predefined_type == "VIENNESEBEND":
        result = _map_viennese_bend(file, segment.DesignParameters, rail_head_distance)
    else:
        raise TypeError(f"Unexpected predefined type: '{predefined_type}'.")

    return result
