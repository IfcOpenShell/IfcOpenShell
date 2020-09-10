###############################################################################
#                                                                             #
# This file is part of IfcOpenShell.                                          #
#                                                                             #
# IfcOpenShell is free software: you can redistribute it and/or modify        #
# it under the terms of the Lesser GNU General Public License as published by #
# the Free Software Foundation, either version 3.0 of the License, or         #
# (at your option) any later version.                                         #
#                                                                             #
# IfcOpenShell is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# Lesser GNU General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the Lesser GNU General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################

from enum import Enum
from dataclasses import DataClass
import math

from OCC.gp import gp_Pnt2d
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.BRepBuilderAPI import BRepBuilderAPI_MakeWire


class IfcTransitionCurveType(Enum):
    """IFC 4.1 Section 8.9.2.9
    [https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/schema/ifcgeometryresource/lexical/ifctransitioncurvetype.htm]

    The IfcTransitionCurveType indicates the curvature of a transition curve.
    """
    BIQUADRATICPARABOLA = 1  # NOTE also referred to as Schramm curve.
    BLOSSCURVE = 2
    CLOTHOIDCURVE = 3
    COSINECURVE = 4
    CUBICPARABOLA = 5
    SINECURVE = 6  # NOTE also referred to as Klein curve


@DataClass
class IfcTransitionSegment2D:
    """IFC 4.1 Section 8.9.3.65
    [https://standards.buildingsmart.org/IFC/RELEASE/IFC4_1/FINAL/HTML/schema/ifcgeometryresource/lexical/ifctransitioncurvesegment2d.htm]

    A curve that transitions between a straight line and a circular arc (or the reverse).
    """
    StartPoint: tuple  # IfcSchema::IfcCartesianPoint
    StartDirection: float  # IfcSchema::IfcPlaneAngleMeasure
    SegmentLength: float  # IfcSchema::IfcPositiveLengthMeasure
    StartRadius: float = None  # IfcSchema::IfcPositiveLengthMeasure
    EndRadius: float = None  # IfcSchema::IfcPositiveLengthMeasure
    IsStartRadiusCCW: bool  # IfcSchema::IfcBoolean
    IsEndRadiusCCW: bool  # IfcSchema::IfcBoolean
    TransitionCurveType: IfcTransitionCurveType


def _calc_biquadratic_parabola_point(lpt, L, R, ccw):
    x = lpt
    if x <= L / 2:
        y = math.pow(x, 4) / (6 * R * math.pow(L, 2))
    else:
        y = ((-1 * math.pow(x, 4)) / (6 * R * math.pow(L, 2))) \
            + ((2 * math.pow(x, 3)) / (3 * R * L)) \
            - ((math.pow(x, 2)) / (2 * R)) \
            + ((L * x) / (6 * R)) \
            - ((math.pow(L, 2) / (48 * R))

    if not ccw:
        y = -y

    return gp_Pnt2d(x, y)


def _calc_bloss_curve_point(lpt, L, R, ccw):
    pass


def _calc_clothoid_curve_point(lpt, L, R, ccw):
    x = lpt * (1 - (math.pow(lpt, 4) / (40 * math.pow(R, 2) * math.pow(L, 2))) \
        + (math.pow(lpt, 8) / 3456 * math.pow(R, 4) * math.pow(L, 4)))

    y = ((math.pow(lpt, 3) / (6 * R * L)) \
        * (1 - (math.pow(lpt, 4) / (56 * math.pow(R, 2) \
        * math.pow(L, 2))) \
        + (math.pow(lpt, 8) / 7040 * math.pow(R, 4) * math.pow(L, 4))))

    if not ccw:
        y = -y

    return gp_Pnt2d(x, y)


def _calc_cosine_curve_point(lpt, L, R, ccw):
    pi = math.pi
    psi_x = (pi * lpt) / L
    terms = list()
    terms.append(math.pow(L, 2) / (8.0 * math.pow(pi, 2) * math.pow(R, 2)))
    terms.append(L / pi)
    terms.append(math.pow(psi_x, 3) / 3.0)
    terms.append(psi_x / 2.0)
    terms.append((math.sin(psi_x) * math.cos(psi_x) / 2.0)
    terms.append((psi_x * math.cos(psi_x))

    x = (lpt - terms[0] * terms[1] * ( terms[2] + terms[3] - terms[4] - (2.0 * terms[5])))

    # TODO: code for y - coordinate
    y = 0

    if not ccw:
        y = -y

    return gp_Pnt2d(x, y)


def _calc_cubic_parabola_point(lpt, L, R, ccw):

    x = lpt
    y = math.pow(x, 3) / (6 * R * L)
    if not ccw:
        y = -y

    return gp_Pnt2d(x, y)


def _calc_sine_curve_point(lpt, L, R, ccw):
    pass


def _calc_transition_curve_point(lpt, L, R, ccw, trans_type):

    if trans_type == "BIQUADRATICPARABOLA":
        return _calc_cubic_parabola_point
    elif trans_type == "BLOSSCURVE":
        # return _calc_bloss_curve_point(lpt, L, R, ccw)
        raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
    elif trans_type == "CLOTHOIDCURVE":
        return _calc_clothoid_curve_point(lpt, L, R, ccw)
    elif trans_type == "COSINECURVE":
        # return _calc_cosine_curve_point(lpt, L, R, ccw)
        raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
    elif trans_type == "CUBICPARABOLA":
        return _calc_cubic_parabola_point(lpt, L, R, ccw)
    elif trans_type == "SINECURVE":
        # return _calc_sine_curve_point(lpt, L, R, ccw)
        raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
    else:
        raise ValueError(f"Invalid Transition Curve type '{trans_type}'.")


def convert_IfcTransitionSegment2D(segment, stroking_interval=5.0):
    """convert IfcTransitionSegment2D to OCC wire

    :param segment: ifc entity to be parsed into geometry
    :type segment: IfcTransitionSegment2D
    :param stroking_interval: maximum curve length between points to be calculated
    :type stroking_interval: float
    :return: OCC wire containing interpolated points
    """
    points = list()

    L = segment.SegmentLength
    R = segment.EndRadius
    ccw = segment.IsStartRadiusCCW
    trans_type = segment.TransitionCurveType.name

    num_intervals = math.ceil(L / stroking_interval)
    interval_dist = L / num_intervals
    lpt = 0.0  # length along the curve at the point to be calculated

    for _ in num_intervals:
        points.append(_calc_transition_curve_point(
            lpt, L, R, ccw, trans_type
            ))
        lpt += interval_dist

    e = BRepBuilderAPI_MakeEdge(points)

    return BRepBuilderAPI_MakeWire(e)
