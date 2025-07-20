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

import ifcopenshell
import ifcopenshell.api.unit
import ifcopenshell.util.alignment as sta


def _test_si_stations():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_si_unit(file, unit_type="LENGTHUNIT")  # meter
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    s = sta.station_as_string(file, 0.0)
    assert s == "0+000.000"

    s = sta.station_as_string(file, 100.00)
    assert s == "0+100.000"

    s = sta.station_as_string(file, -100.00)
    assert s == "-0+100.000"

    s = sta.station_as_string(file, 123456.789)
    assert s == "123+456.789"

    s = sta.station_as_string(file, -123456.789)
    assert s == "-123+456.789"


def _test_si_stations_millimeter():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    ifcopenshell.api.unit.assign_unit(file)

    s = sta.station_as_string(file, 100.00)
    assert s == "0+000.100"

    s = sta.station_as_string(file, 1000.00)
    assert s == "0+001.000"


def _test_us_stations():
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")
    length = ifcopenshell.api.unit.add_conversion_based_unit(file, name="foot")
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    s = sta.station_as_string(file, 0.0)
    assert s == "0+00.00"

    s = sta.station_as_string(file, 100.00)
    assert s == "1+00.00"

    s = sta.station_as_string(file, -100.00)
    assert s == "-1+00.00"

    s = sta.station_as_string(file, 123456.789)
    assert s == "1234+56.79"

    s = sta.station_as_string(file, -123456.789)
    assert s == "-1234+56.79"


def test_station_as_string():
    _test_si_stations()
    _test_si_stations_millimeter()
    _test_us_stations()


test_station_as_string()
