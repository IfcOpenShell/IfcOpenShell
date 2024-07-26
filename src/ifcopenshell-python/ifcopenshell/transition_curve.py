# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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


from enum import Enum
from dataclasses import dataclass
import math

from OCC.Core.gp import gp_Pnt2d
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge2d
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeWire


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


@dataclass
class TransitionCurve:
    """
    A curve that transitions between a straight line and a circular arc
    (or the reverse).
    """

    StartPoint: tuple  # IfcSchema::IfcCartesianPoint
    StartDirection: float  # IfcSchema::IfcPlaneAngleMeasure
    SegmentLength: float  # IfcSchema::IfcPositiveLengthMeasure
    IsStartRadiusCCW: bool  # IfcSchema::IfcBoolean
    IsEndRadiusCCW: bool  # IfcSchema::IfcBoolean
    TransitionCurveType: IfcTransitionCurveType
    StartRadius: float = None  # IfcSchema::IfcPositiveLengthMeasure
    EndRadius: float = None  # IfcSchema::IfcPositiveLengthMeasure

    def _calc_biquadratic_parabola_point(self, lpt, L, R, ccw):
        x = lpt
        if x <= (L / 2):
            y = x**4 / (6 * R * L**2)
        else:

            yterm_1 = (-1 * x**4) / (6 * R * L**2)
            yterm_2 = (2 * x**3) / (3 * R * L)
            yterm_3 = x**2 / (2 * R)
            yterm_4 = (L * x) / (6 * R)
            yterm_5 = L**2 / (48 * R)

            y = yterm_1 + yterm_2 - yterm_3 + yterm_4 - yterm_5

        if not ccw:
            y = -y

        return gp_Pnt2d(x, y)

    def _calc_bloss_curve_point(self, lpt, L, R, ccw):
        pass

    def _calc_clothoid_curve_point(self, lpt, L, R, ccw):
        RL = R * L
        xterm_1 = 1
        xterm_2 = lpt**4 / (40 * RL**2)
        xterm_3 = lpt**8 / (3456 * RL**4)
        xterm_4 = lpt**12 / (599040 * RL**6)
        x = lpt * (xterm_1 - xterm_2 + xterm_3 - xterm_4)

        factor = lpt**3 / (6 * RL)
        yterm_1 = 1
        yterm_2 = lpt**4 / (56 * RL**2)
        yterm_3 = lpt**8 / (7040 * RL**4)
        yterm_4 = lpt**12 / (1612800 * RL**6)

        y = factor * (yterm_1 - yterm_2 + yterm_3 - yterm_4)

        if not ccw:
            y = -y

        return gp_Pnt2d(x, y)

    def _calc_cosine_curve_point(self, lpt, L, R, ccw):
        pi = math.pi
        psi_x = (pi * lpt) / L

        xterm_1 = (L**2) / (8.0 * pi**2 * R**2)
        xterm_2 = L / pi
        xterm_3 = psi_x**3 / (3.0)
        xterm_4 = psi_x / (2.0)
        xterm_5 = (math.sin(psi_x) * math.cos(psi_x)) / (2.0)
        xterm_6 = psi_x * math.cos(psi_x)

        x = lpt - xterm_1 * xterm_2 * (xterm_3 + xterm_4 - xterm_5 - (2.0 * xterm_6))

        # TODO: code for y - coordinate
        y = 0

        if not ccw:
            y = -y

        return gp_Pnt2d(x, y)

    def _calc_cubic_parabola_point(self, lpt, L, R, ccw):

        x = lpt
        y = math.pow(x, 3) / (6 * R * L)
        if not ccw:
            y = -y

        return gp_Pnt2d(x, y)

    def _calc_sine_curve_point(self, lpt, L, R, ccw):
        pass

    def _calc_transition_curve_point(self, lpt, L, R, ccw, trans_type):

        if trans_type == "BIQUADRATICPARABOLA":
            return self._calc_cubic_parabola_point(lpt, L, R, ccw)
        elif trans_type == "BLOSSCURVE":
            # return _calc_bloss_curve_point(lpt, L, R, ccw)
            raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
        elif trans_type == "CLOTHOIDCURVE":
            return self._calc_clothoid_curve_point(lpt, L, R, ccw)
        elif trans_type == "COSINECURVE":
            # return _calc_cosine_curve_point(lpt, L, R, ccw)
            raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
        elif trans_type == "CUBICPARABOLA":
            return self._calc_cubic_parabola_point(lpt, L, R, ccw)
        elif trans_type == "SINECURVE":
            # return _calc_sine_curve_point(lpt, L, R, ccw)
            raise ValueError(f"Transition Curve type '{trans_type}' not implemented yet.")
        else:
            raise ValueError(f"Invalid Transition Curve type '{trans_type}'.")

    def to_wire(self, stroking_interval=5.0):
        """convert IfcTransitionSegment2D to OCC wire

        :param stroking_interval: maximum curve length between points to be calculated
        :type stroking_interval: float
        :return: OCC wire containing interpolated points
        """
        points = list()

        L = self.SegmentLength
        R = self.EndRadius
        ccw = self.IsStartRadiusCCW
        trans_type = self.TransitionCurveType.name

        num_intervals = math.ceil(L / stroking_interval)
        interval_dist = L / num_intervals
        lpt = 0.0  # length along the curve at the point to be calculated

        for _ in range(num_intervals):
            points.append(self._calc_transition_curve_point(lpt, L, R, ccw, trans_type))
            lpt += interval_dist

        edges = list()
        for i in range(len(points) - 1):
            edges.append(BRepBuilderAPI_MakeEdge2d(points[i], points[i + 1]))

        wire = BRepBuilderAPI_MakeWire()
        for e in edges:
            wire.Add(e.Edge())
        # return wire
        return points
