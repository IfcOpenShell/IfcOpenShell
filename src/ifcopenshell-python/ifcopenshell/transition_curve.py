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
    pass


def _calc_bloss_curve_point(lpt, L, R, ccw):
    pass


def _calc_clothoid_curve_point(lpt, L, R, ccw):
    pass


def _calc_cosine_curve_point(lpt, L, R, ccw):
    pass


def _calc_cubic_parabola_point(lpt, L, R, ccw):

    x = lpt
    y = (x ** 3) / (6 * R * L)
    if not ccw:
        y = -1 * y

    return gp_Pnt2d(x, y)


def _calc_sine_curve_point(lpt, L, R, ccw):
    pass


def _calc_transition_curve_point(lpt, L, R, ccw, trans_type):

    if trans_type == "CUBICPARABOLA":
        x, y = _calc_cubic_parabola_point(lpt, L, R, ccw)
        return gp_Pnt2d(x, y)
    else:
        raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")


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
    ccw = segment.IsstartRadiusCCW
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
