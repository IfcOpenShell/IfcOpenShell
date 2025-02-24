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

import math


def station_as_string(station: float, plus_seperator=3, accuracy=3):
    """
    Returns a stringized version of a station. Example 100.0 is 1+00.00 as a stationing string
    @param station: the station to be stringized
    @param plus_seperator: location of the '+' symbol relative to the decimal place (typically 2 for US units and 3 for SI units)
    @param accuracy: number of digits following the decimal place
    """
    value = math.fabs(station)

    shifter = math.pow(10.0, plus_seperator)
    v1 = math.floor(value / shifter)
    v2 = value - v1 * shifter

    # Check to make sure that v2 is not basically the same as shifter
    # If station = 69500.00000, we sometimes get 694+100.00 instead of 695+00.00
    if math.isclose(v2 - shifter, 5.0 * math.pow(10.0, -(accuracy + 1))):
        v2 = 0.0
        v1 += 1

    v1 = -1 * v1 if station < 0 else v1

    station_string = "{:d}+{:0{}.{}f}".format(v1, v2, plus_seperator + accuracy + 1, accuracy)

    # special case when v1 is 0 and station is negative, the string above doesn't get the leading
    # negative sign. this snippet fixes that
    if v1 == 0 and station < 0:
        station_string = "-" + station_string

    return station_string
