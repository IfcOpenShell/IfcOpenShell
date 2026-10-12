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
from typing import NamedTuple, Optional

from ifcopenshell import entity_instance
from ifcopenshell.api.alignment.solve_horizontal_alignment_by_pi_method import (
    HorizontalSegmentDefinition,
    compute_horizontal_segment_end,
)


class HorizontalCurveParameters(NamedTuple):
    """
    Key points and classic curve properties of one horizontal alignment segment.

    Coordinates are (X, Y) in the same coordinate system as the segment's StartPoint, lengths are
    in the file's length unit and angles are in radians. Fields that do not apply to the segment are
    None, for example the radius of a spiral or the PI of a straight.
    """

    start_point: tuple[float, float]
    """(X, Y) of the segment start, the P.C. of a circular curve"""

    end_point: tuple[float, float]
    """(X, Y) of the segment end, the P.T. of a circular curve"""

    pi: Optional[tuple[float, float]]
    """(X, Y) of the point of intersection of the start and end tangents, None for a straight or when the
    tangents are parallel or the curve turns through 180 degrees or more"""

    center: Optional[tuple[float, float]]
    """(X, Y) of the center of a circular curve. For a spiral, which has no single center, this is the
    intersection of the normals at the start and end. None for a straight."""

    delta: float
    """deflection angle (change in tangent direction) over the segment, positive turning left, negative
    turning right"""

    length: float
    """length of the segment measured along the curve, L for a circular curve"""

    long_chord: Optional[float]
    """straight-line distance from the start to the end of a curved segment, LC = 2R sin(delta/2) for a
    circular curve"""

    start_tangent: Optional[float]
    """T1, the distance from the start of a curved segment to its P.I. For a spiral this is its long
    tangent when it starts on a straight, and equals tangent for a circular curve."""

    end_tangent: Optional[float]
    """T2, the distance from the P.I. of a curved segment to its end, equal to tangent for a circular curve"""

    radius: Optional[float]
    """radius of a circular curve, always positive"""

    tangent: Optional[float]
    """tangent length T = R tan(delta/2), the distance from P.C. or P.T. to the P.I. of a circular curve"""

    external: Optional[float]
    """external distance E = R (sec(delta/2) - 1), from the P.I. to the midpoint of a circular curve"""

    mid_ordinate: Optional[float]
    """middle ordinate M = R (1 - cos(delta/2)), from the midpoint of the long chord to the midpoint of
    a circular curve"""


def get_horizontal_curve_parameters(segment: entity_instance) -> HorizontalCurveParameters:
    """
    Computes the key points (start, P.I., end, center) and the curve properties (radius, tangents,
    delta, length, long chord, external and middle ordinate) of a horizontal alignment segment from
    its design parameters.

    Radius, tangent, external and middle ordinate are only defined for CIRCULARARC segments. For
    spirals, the start, end, P.I., center (normals intersection), delta, length, long chord and the
    two tangents T1 and T2 are given.

    :param segment: An IfcAlignmentSegment whose DesignParameters is an IfcAlignmentHorizontalSegment,
        or the IfcAlignmentHorizontalSegment itself
    :return: The curve parameters

    Example:

    .. code:: python

        horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        for segment in ifcopenshell.api.alignment.get_alignment_segment_nest(horizontal).RelatedObjects:
            curve = ifcopenshell.api.alignment.get_horizontal_curve_parameters(segment)
            if curve.radius is not None:
                print(curve.radius, curve.tangent, math.degrees(abs(curve.delta)))
    """
    design_parameters = segment.DesignParameters if segment.is_a("IfcAlignmentSegment") else segment
    if design_parameters is None or not design_parameters.is_a("IfcAlignmentHorizontalSegment"):
        raise TypeError(f"Expected an IfcAlignmentHorizontalSegment, instead received {segment}")

    predefined_type = design_parameters.PredefinedType
    sx, sy = design_parameters.StartPoint.Coordinates[0:2]
    start_direction = design_parameters.StartDirection
    start_radius = design_parameters.StartRadiusOfCurvature or 0.0
    ex, ey, end_direction = compute_horizontal_segment_end(
        HorizontalSegmentDefinition(
            start_point=(sx, sy),
            start_direction=start_direction,
            start_radius_of_curvature=start_radius,
            end_radius_of_curvature=design_parameters.EndRadiusOfCurvature or 0.0,
            segment_length=design_parameters.SegmentLength,
            predefined_type=predefined_type,
        )
    )
    parameters = dict(
        start_point=(sx, sy),
        end_point=(ex, ey),
        pi=None,
        center=None,
        delta=end_direction - start_direction,
        length=design_parameters.SegmentLength,
        long_chord=None,
        start_tangent=None,
        end_tangent=None,
        radius=None,
        tangent=None,
        external=None,
        mid_ordinate=None,
    )
    delta = parameters["delta"]
    if predefined_type == "LINE" or delta == 0.0:
        return HorizontalCurveParameters(**parameters)

    parameters["long_chord"] = math.hypot(ex - sx, ey - sy)

    d1x, d1y = math.cos(start_direction), math.sin(start_direction)
    d2x, d2y = math.cos(end_direction), math.sin(end_direction)
    cross = d1x * d2y - d1y * d2x

    if abs(cross) > 1e-10 and abs(delta) < math.pi:
        t = ((ex - sx) * d2y - (ey - sy) * d2x) / cross
        pi = (sx + t * d1x, sy + t * d1y)
        parameters["pi"] = pi
        parameters["start_tangent"] = math.hypot(pi[0] - sx, pi[1] - sy)
        parameters["end_tangent"] = math.hypot(ex - pi[0], ey - pi[1])

    if predefined_type == "CIRCULARARC" and start_radius != 0.0:
        # Signed radius: positive centers to the left of the start tangent
        radius = abs(start_radius)
        half = 0.5 * abs(delta)
        parameters["center"] = (sx - start_radius * d1y, sy + start_radius * d1x)
        parameters["radius"] = radius
        parameters["mid_ordinate"] = radius * (1.0 - math.cos(half))
        if parameters["pi"] is not None:
            parameters["tangent"] = radius * math.tan(half)
            parameters["external"] = radius * (1.0 / math.cos(half) - 1.0)
        return HorizontalCurveParameters(**parameters)

    # A spiral has no single center; the start and end normals still meet at a useful reference point
    if abs(cross) > 1e-10:
        t = ((ex - sx) * d2x + (ey - sy) * d2y) / cross
        parameters["center"] = (sx - t * d1y, sy + t * d1x)
    return HorizontalCurveParameters(**parameters)
