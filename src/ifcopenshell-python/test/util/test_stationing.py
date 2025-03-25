# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.stationing as sta


def test_station_as_string():
    # test with a bunch of "random" station values
    s = sta.station_as_string(0.0)
    assert s == "0+000.000"

    s = sta.station_as_string(0.0, 2, 2)
    assert s == "0+00.00"

    s = sta.station_as_string(0.0, 2)
    assert s == "0+00.000"

    s = sta.station_as_string(100.00)
    assert s == "0+100.000"

    s = sta.station_as_string(-100.00)
    assert s == "-0+100.000"

    s = sta.station_as_string(123456.789, 2, 2)
    assert s == "1234+56.79"

    s = sta.station_as_string(-123456.789, 2, 2)
    assert s == "-1234+56.79"

    s = sta.station_as_string(123456.789, 3, 4)
    assert s == "123+456.7890"
