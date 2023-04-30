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


from dataclasses import dataclass
import math

import numpy as np

from ifcopenshell.alignment import AlignmentHorizontalSegmentTypeEnum



@dataclass
class TransitionCurve:
    """
    A curve that transitions between a straight line and a circular arc
    (or the reverse).
    """

    StartPoint: np.array  # IfcSchema::IfcCartesianPoint
    StartDirection: float  # IfcSchema::IfcPlaneAngleMeasure
    StartRadiusOfCurvature: float  # IfcSchema::IfcLengthMeasure
    EndRadiusOfCurvature: float  # IfcSchema::IfcPositiveLengthMeasure
    SegmentLength: float  # IfcSchema::IfcNonNegativeLengthMeasure
    PredefinedType: AlignmentHorizontalSegmentTypeEnum
    GravityCenterLineHeight: float = None  # IfcSchema::IfcPositiveLengthMeasure


def isCCW(radius: float) -> bool:
    if radius >= 0:
        return True
    else:
        return False


def calc_transition_curve_point_HELMERTCURVE(lpt : float, L: float, R: float) -> np.array:
    """
    Calculate the x, y coordinates of a point on a
    BIQUADRATICPARABOLA horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    ccw = isCCW(R)
    R = abs(R)
    x = lpt
    if x <= (L / 2):
        y = x ** 4 / (6 * R * L ** 2)
    else:
        yterm_1 = (-1 * x ** 4) / (6 * R * L ** 2)
        yterm_2 = (2 * x ** 3) / (3 * R * L)
        yterm_3 = x ** 2 / (2 * R)
        yterm_4 = (L * x) / (6 * R)
        yterm_5 = L ** 2 / (48 * R)

        y = yterm_1 + yterm_2 - yterm_3 + yterm_4 - yterm_5

    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def calc_transition_curve_point_BLOSSCURVE(lpt, L, R):
    """
    Calculate the x, y coordinates of a point on a
    BLOSSCURVE horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    from scipy import integrate
    ccw = isCCW(R)
    R = abs(R)

    def theta(lpt, L, R):
        term1 = lpt ** 3 / (R * L ** 2)
        term2 = lpt ** 4 / (2 * R * L ** 3)
        return term1 - term2

    def fx(lpt):
        return math.cos(theta(lpt, L, R))

    def fy(lpt):
        return math.sin(theta(lpt, L, R))

    x = integrate.quad(fx, 0, lpt)[0]
    y = integrate.quad(fy, 0, lpt)[0]

    if ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def calc_transition_curve_point_CLOTHOID(lpt, L, R):
    """
    Calculate the x, y coordinates of a point on a
    CLOTHOID horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    ccw = isCCW(R)
    R = abs(R)

    RL = R * L
    xterm_1 = 1
    xterm_2 = lpt ** 4 / (40 * RL ** 2)
    xterm_3 = lpt ** 8 / (3456 * RL ** 4)
    xterm_4 = lpt ** 12 / (599040 * RL ** 6)
    x = lpt * (xterm_1 - xterm_2 + xterm_3 - xterm_4)

    factor = lpt ** 3 / (6 * RL)
    yterm_1 = 1
    yterm_2 = lpt ** 4 / (56 * RL ** 2)
    yterm_3 = lpt ** 8 / (7040 * RL ** 4)
    yterm_4 = lpt ** 12 / (1612800 * RL ** 6)

    y = factor * (yterm_1 - yterm_2 + yterm_3 - yterm_4)

    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def calc_transition_curve_point_COSINECURVE(lpt, L, R):
    """
    Calculate the x, y coordinates of a point on a
    COSINECURVE horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    ccw = isCCW(R)
    R = abs(R)

    pi = math.pi
    psi = (pi * lpt) / L

    xterm_1 = (L ** 2) / (8.0 * pi ** 2 * R ** 2)
    xterm_2 = L / pi
    xterm_3 = psi ** 3 / (3.0)
    xterm_4 = psi / (2.0)
    xterm_5 = (math.sin(psi) * math.cos(psi)) / (2.0)
    xterm_6 = psi * math.cos(psi)

    x = lpt - xterm_1 * xterm_2 * (xterm_3 + xterm_4 - xterm_5 - (2.0 * xterm_6))

    yfactor_1 = L / (2 * pi ** 2 * R)
    yterm_11 = psi ** 2 / 2
    yterm_12 = math.cos(psi)
    ycoeff_1 = yterm_11 + yterm_12 - 1
    yterm_1 = yfactor_1 * ycoeff_1

    yfactor_2 = L ** 3 / (48 * pi ** 4 * R ** 3)
    yterm_21 = psi ** 4 / 4
    yterm_22 = (((math.sin(psi)) ** 2) * (math.cos(psi))) / 3
    yterm_23 = 16 * math.cos(psi) / 3
    yterm_24 = (3 * psi ** 2) * (math.cos(psi))
    yterm_25 = 6 * psi * math.sin(psi)
    yterm_26 = 3 * psi ** 2 / 4
    yterm_27 = (3 * psi * math.sin(2 * psi)) / 4
    yterm_28 = (3 * math.cos(2 * psi)) / 8
    ycoeff_2 = yterm_21 + yterm_22 - yterm_23 + yterm_24 - yterm_25 + yterm_26 - yterm_27 - yterm_28 + (137 / 24)
    yterm_2 = yfactor_2 * ycoeff_2
    y = L * (yterm_1 - yterm_2)

    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def calc_transition_curve_point_CUBIC(lpt, L, R):
    """
    Calculate the x, y coordinates of a point on a
    CUBIC horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    ccw = isCCW(R)
    R = abs(R)

    x = lpt
    y = x ** 3 / (6 * R * L)
    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def calc_transition_curve_point_SINECURVE(lpt, L, R):
    """
    Calculate the x, y coordinates of a point on a
    SINECURVE horizontal alignment segment.

    @param lpt: distance along the transition curve segment to the point
    to be calculated (in the range of 0 to L)
    @param L: transition curve segment total length
    @param R: radius of curvature
    """
    from scipy import integrate
    ccw = isCCW(R)
    R = abs(R)

    # TODO
    pi = math.pi
    psi = (2 * pi * lpt) / L

    xfactor_1 = lpt
    xterm_11 = L ** 2 / (32 * pi ** 4 * R ** 2)
    xcoeff_1 = 1 - xterm_11
    xterm_1 = xfactor_1 * xcoeff_1

    xfactor_2 = L ** 3 / (3840 * pi ** 5 * R ** 2)
    xterm_21 = 3 * psi ** 5
    xterm_22 = 20 * psi ** 3
    xterm_23 = 30 * psi
    xterm_24 = (240 - 60 * psi ** 2) * math.sin(psi)
    xterm_25 = 30 * math.cos(psi) * math.sin(psi)
    xterm_26 = 120 * psi * math.cos(psi)
    xcoeff_2 = xterm_21 - xterm_22 + xterm_23 - xterm_24 + xterm_25 + xterm_26
    xterm_2 = xfactor_2 * xcoeff_2

    x = xterm_1 - xterm_2

    def theta(lpt, L, R):
        term1 = lpt ** 2 / (2 * R * L)
        factor2 = L / (4 * pi ** 2 * R)
        coeff2 = math.cos((2 * pi * lpt) / L)
        term2 = factor2 * (coeff2 - 1)
        return term1 + term2

    def fy(lpt):
        return math.sin(theta(lpt, L, R))

    y = integrate.quad(fy, 0, lpt)[0]

    if ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def curve_to_array(L: float, R: float, trans_type, stroking_interval=5.0) -> np.array:
    """return array of [x, y, NaN] coordinates for a semantic horizontal segment definition

    :param stroking_interval: maximum curve length between points to be calculated
    :type stroking_interval: float
    :return: numpy ndarray containing interpolated points
    """
    points = list()

    num_intervals = math.ceil(L / stroking_interval)
    interval_dist = L / num_intervals
    lpt = 0.0  # length along the curve at the point to be calculated

    for _ in range(num_intervals):
        points.append(globals()[f"calc_transition_curve_point_{trans_type}"](lpt, L, R))
        lpt += interval_dist

    return np.array(points)
