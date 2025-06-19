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

def angle_from_dms(d:int,m:int,s:float)->float:
    """
    Compute an angle, in radian, from an angle in d:m:s format.

    :param d: degree
    :param m: minute
    :param s: second
    :return: Angle in radian
    """
    if (m < 0 or 60 <= m) or (s < 0.0 or 60.0 <= s):
        raise ValueError("Invalid argument")

    angle = float(d) + float(m)/60. + s/3600.
    return math.radians(angle)
