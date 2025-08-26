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

import ifcopenshell.util.geolocation


def bearing2dd(bearing: str) -> float:
    """
    Converts a quadrant bearing string to decimal degrees

    The format of the string is "N|S dd (mm (ss.s)) E|W"
    where:
    N|S is N or S for North or South
    dd is degree (required)
    mm is minute (optional, but required if second is provided)
    ss.s is second (required)
    E|W is E or W for East or West

    :param str: the bearing string
    :return: Angle in radian
    """
    error_msg = "Invalid bearing string"

    bearing = bearing.strip()  # trim external white space
    bearing = " ".join(bearing.split())  # make sure all parts separated by a single space
    parts = bearing.split()
    nParts = len(parts)
    if nParts < 3 or 5 < nParts:
        raise ValueError(error_msg)

    cY = parts[0]
    cY = cY.upper()
    if cY != "N" and cY != "S":
        raise ValueError(error_msg)

    cX = parts[-1]
    cX = cX.upper()
    if cX != "E" and cX != "W":
        raise ValueError(error_msg)

    d = 0
    m = 0
    s = 0.0
    ms = 0

    if nParts == 3:
        d = int(parts[1])
    elif nParts == 4:
        d = int(parts[1])
        m = int(parts[2])
    elif nParts == 5:
        d = int(parts[1])
        m = int(parts[2])
        s = float(parts[3])

    # s in a decimal number
    # need to break it into whole seconds and milliseconds
    ms = 100.0 * (s - int(s))
    s = int(s)

    if d < 0 or (m < 0 or 60 <= m) or (s < 0 or 60 <= s) or ms < 0:
        raise ValueError(error_msg)

    if cY == "N" and cX == "E":
        angle = 90.0
        sign = -1.0
    elif cY == "N" and cX == "W":
        angle = 90.0
        sign = 1.0
    elif cY == "S" and cX == "E":
        angle = 270.0
        sign = 1.0
    elif cY == "S" and cX == "W":
        angle = 270.0
        sign = -1.0

    try:
        dms = ifcopenshell.util.geolocation.dms2dd(d, m, s, ms)
    except ValueError:
        raise ValueError(error_msg)

    if dms < 0.0 or 90.0 < dms:
        raise ValueError(error_msg)

    angle += sign * dms

    # S 90 E will evaluate to 360
    if angle == 360.0:
        angle = 0.0

    return angle
