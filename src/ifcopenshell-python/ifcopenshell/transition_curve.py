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

"""
Transition curves are required when the definition of an `IfcAlignment`
is expressed via parameter segments and does not contain an explicit
geometric representation.
"""
import math

import numpy as np


def rotate_points(coords: tuple, angle: float) -> np.ndarray:
    """
    rotate points by provided angle

    @param points: x, y tuple of cartestian coordinates
    """
    x, y = coords
    rot_mat = np.array(
        [
            [math.cos(angle), -math.sin(angle)],
            [math.sin(angle), math.cos(angle)],
        ]
    )
    return np.array([x, y]) @ rot_mat


def point_on_LINE(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a LINE segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    return np.array(
        [
            u * math.cos(segment.StartDirection),
            u * math.sin(segment.StartDirection),
            np.nan,
        ]
    )


def point_on_CIRCULARARC(segment, u: float) -> np.ndarray:
    """
    Point at distance u along a CIRCULARARC segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    # calc local point on circle with forward tangent of start point
    # on positive x-axis

    R = abs(segment.StartRadiusOfCurvature)
    x = R * math.cos(u / R)
    y = R * math.sin(u / R)

    # move calculated point so that rotation is about StartPoint
    x -= R

    if segment.is_CCW:
        rot_angle = (math.pi / 2) - segment.StartDirection
    else:
        y = -y
        rot_angle = (3 * math.pi / 2) - segment.StartDirection

    rotated = rotate_points(coords=(x, y), angle=rot_angle)

    return np.array([rotated[0], rotated[1], np.nan])


def point_on_HELMERTCURVE(segment, u: float) -> np.array:
    """
    2D point at distance u along a HELMERTCURVE segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    ccw = segment.is_CCW
    R = abs(segment.StartRadiusOfCurvature)
    R2 = abs(segment.EndRadiusOfCurvature)
    L = segment.SegmentLength
    x = u
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

    return np.array([x, y, np.NaN], dtype="float64")


def point_on_BLOSSCURVE(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a BLOSSCURVE segment
    Ref: https://pwayblog.com/2017/05/15/bloss-rectangular-coordinates/

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    from scipy import integrate

    if segment.StartRadiusOfCurvature == 0:
        R = abs(segment.EndRadiusOfCurvature)
    else:
        R = abs(segment.StartRadiusOfCurvature)
    L = abs(segment.SegmentLength)
    
    def theta(u, L, R):
        term1 = u**3 / (R * L**2)
        term2 = u**4 / (2 * R * L**3)
        return term1 - term2

    def fx(u):
        return math.cos(theta(u, L, R))

    def fy(u):
        return math.sin(theta(u, L, R))

    # x = integrate.quad(fx, 0, u)[0]
    # y = integrate.quad(fy, 0, u)[0]

    try:
        x_term1 = u
        x_term2 = u**7 / ((14 * R**2) * (L**4))
        x_term3 = u**8 / ((16 * R**2) * (L**5))
        x_term4 = u**9 / ((72 * R**2) * (L**6))
        x_term5 = u**13 / ((312 * R**4) * (L**8))
        x_term6 = u**14 / ((168 * R**4) * (L**9))
        x_term7 = u**15 / ((240 * R**4) * (L**10))
        x = x_term1 - x_term2 + x_term3 - x_term4 + x_term5 - x_term6 + x_term7
    except ZeroDivisionError as e:
        x = 0

    try:
        y_term1 = u**4 / ((4 * R) * (L**2))
        y_term2 = u**5 / ((10 * R) * (L**3))
        y_term3 = u**10 / ((60 * R**3) * (L**6))
        y_term4 = u**11 / ((44 * R**3) * (L**7))
        y_term5 = u**12 / ((96 * R**3) * (L**8))
        y_term6 = u**13 / ((624 * R**3) * (L**9))
        y_term7 = u**16 / ((1800 * R**5) * (L**10))
        y_term8 = u**17 / ((816 * R**5) * (L**11))

        y = y_term1 - y_term2 + y_term3 - y_term4 + y_term5 - y_term6 + y_term7 - y_term8
    except ZeroDivisionError as e:
        y = 0

    # quick check
    x_check = u
    try:
        y_check = (1 / R) * ((u**4 / (4 * L**2)) - (u**5 / (10 * L**3)))
    except ZeroDivisionError as e:
        y_check = 0

    if not segment.is_CCW:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def local_point_on_CLOTHOID(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a CLOTHOID segment with specific parameters:
    counter-clockwise deflection and StartRadius = 0 (starting from a line).

    Ref: https://pwayblog.com/2016/07/03/the-clothoid/

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    L = segment.SegmentLength
    if segment.StartRadiusOfCurvature == 0:
        R = abs(segment.EndRadiusOfCurvature)
    elif segment.EndRadiusOfCurvature == 0:
        R = abs(segment.StartRadiusOfCurvature)

    try:
        R
    except UnboundLocalError:
        if segment.EndRadiusOfCurvature < segment.StartRadiusOfCurvature:
            R = abs(segment.EndRadiusOfCurvature)
        else:
            R = abs(segment.StartRadiusOfCurvature)

    RL = R * L

    xterm_1 = u
    xterm_2 = u**5 / (40 * RL**2)
    xterm_3 = u**9 / (3456 * RL**4)
    xterm_4 = u**13 / (599040 * RL**6)
    x = xterm_1 - xterm_2 + xterm_3 - xterm_4

    yterm_1 = u**3 / (6 * RL)
    yterm_2 = u**7 / (336 * RL**3)
    yterm_3 = u**11 / (42240 * RL**5)
    yterm_4 = u**15 / (9676800 * RL**7)

    y = yterm_1 - yterm_2 + yterm_3 - yterm_4

    return (x, y)


def point_on_CLOTHOID(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a CLOTHOID segment, adjusted for specific case

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    ccw = segment.is_CCW
    L = segment.SegmentLength
    if segment.StartRadiusOfCurvature == 0:
        R = abs(segment.EndRadiusOfCurvature)
        curvature_is_increasing = True
    elif segment.EndRadiusOfCurvature == 0:
        R = abs(segment.StartRadiusOfCurvature)
        curvature_is_increasing = False
        u = L - u

    try:
        R
    except UnboundLocalError:
        if segment.EndRadiusOfCurvature < segment.StartRadiusOfCurvature:
            R = abs(segment.EndRadiusOfCurvature)
            curvature_is_increasing = True
        else:
            R = abs(segment.StartRadiusOfCurvature)
            curvature_is_increasing = False
            u = L - u

    end_point = local_point_on_CLOTHOID(segment=segment, u=segment.SegmentLength)
    x_end, y_end = end_point
    RL = R * L

    # clothoid constant
    A = math.sqrt(RL)
    total_deflection_angle = L / (2 * R)

    (x, y) = local_point_on_CLOTHOID(segment=segment, u=u)

    if ccw:
        if curvature_is_increasing:
            pass
        else:
            x = -x
            (x, y) = rotate_points(coords=(x, y), angle=-total_deflection_angle)
            x += x_end
            y += 2 * y_end
    else:
        if curvature_is_increasing:
            y = -y
        else:
            x = -x
            (x, y) = rotate_points(coords=(x, y), angle=-total_deflection_angle)
            x += x_end
            y += 2 * y_end
            y = -y

    rot_angle = 0 - segment.StartDirection

    rotated = rotate_points(coords=(x, y), angle=rot_angle)

    # return np.array([x, y, np.nan])
    return np.array([rotated[0], rotated[1], np.nan])


def point_on_COSINECURVE(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a COSINECURVE segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """

    ccw = segment.is_CCW
    if segment.StartRadiusOfCurvature == 0:
        R = abs(segment.EndRadiusOfCurvature)
    else:
        R = abs(segment.StartRadiusOfCurvature)
    L = segment.SegmentLength

    pi = math.pi
    psi = (pi * u) / L

    try:
        xterm_1 = (L**2) / (8.0 * pi**2 * R**2)
        xterm_2 = L / pi
        xterm_3 = psi**3 / (3.0)
        xterm_4 = psi / (2.0)
        xterm_5 = (math.sin(psi) * math.cos(psi)) / (2.0)
        xterm_6 = psi * math.cos(psi)

        x = u - xterm_1 * xterm_2 * (xterm_3 + xterm_4 - xterm_5 - (2.0 * xterm_6))
    except ZeroDivisionError:
        x = 0

    try:
        yfactor_1 = L / (2 * pi**2 * R)
        yterm_11 = psi**2 / 2
        yterm_12 = math.cos(psi)
        ycoeff_1 = yterm_11 + yterm_12 - 1
        yterm_1 = yfactor_1 * ycoeff_1

        yfactor_2 = L**3 / (48 * pi**4 * R**3)
        yterm_21 = psi**4 / 4
        yterm_22 = (((math.sin(psi)) ** 2) * (math.cos(psi))) / 3
        yterm_23 = 16 * math.cos(psi) / 3
        yterm_24 = (3 * psi**2) * (math.cos(psi))
        yterm_25 = 6 * psi * math.sin(psi)
        yterm_26 = 3 * psi**2 / 4
        yterm_27 = (3 * psi * math.sin(2 * psi)) / 4
        yterm_28 = (3 * math.cos(2 * psi)) / 8
        ycoeff_2 = (
            yterm_21
            + yterm_22
            - yterm_23
            + yterm_24
            - yterm_25
            + yterm_26
            - yterm_27
            - yterm_28
            + (137 / 24)
        )
        yterm_2 = yfactor_2 * ycoeff_2
        y = L * (yterm_1 - yterm_2)
    except ZeroDivisionError:
        y = 0

    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def point_on_CUBIC(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a CUBIC segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    ccw = segment.is_CCW
    R = abs(R)
    L = segment.SegmentLength

    x = u
    y = x**3 / (6 * R * L)
    if not ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")


def point_on_SINECURVE(segment, u: float) -> np.ndarray:
    """
    2D point at distance u along a SINECURVE segment

    @param segment: IfcAlignmentHorizontalSegment containing the point
    @type segment: ifcopenshell.alignment.AlignmentHorizontalSegment
    """
    from scipy import integrate

    ccw = segment.is_CCW
    R = abs(segment.StartRadiusOfCurvature)
    L = segment.SegmentLength

    # TODO
    pi = math.pi
    psi = (2 * pi * u) / L

    xfactor_1 = u
    xterm_11 = L**2 / (32 * pi**4 * R**2)
    xcoeff_1 = 1 - xterm_11
    xterm_1 = xfactor_1 * xcoeff_1

    xfactor_2 = L**3 / (3840 * pi**5 * R**2)
    xterm_21 = 3 * psi**5
    xterm_22 = 20 * psi**3
    xterm_23 = 30 * psi
    xterm_24 = (240 - 60 * psi**2) * math.sin(psi)
    xterm_25 = 30 * math.cos(psi) * math.sin(psi)
    xterm_26 = 120 * psi * math.cos(psi)
    xcoeff_2 = xterm_21 - xterm_22 + xterm_23 - xterm_24 + xterm_25 + xterm_26
    xterm_2 = xfactor_2 * xcoeff_2

    x = xterm_1 - xterm_2

    def theta(lpt, L, R):
        term1 = lpt**2 / (2 * R * L)
        factor2 = L / (4 * pi**2 * R)
        coeff2 = math.cos((2 * pi * lpt) / L)
        term2 = factor2 * (coeff2 - 1)
        return term1 + term2

    def fy(lpt):
        return math.sin(theta(lpt, L, R))

    y = integrate.quad(fy, 0, u)[0]

    if ccw:
        y = -y

    return np.array([x, y, np.NaN], dtype="float64")
