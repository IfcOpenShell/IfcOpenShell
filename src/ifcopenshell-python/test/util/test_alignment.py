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


def _test_custom_named_conversion_based_unit_stations():
    """Regression test: station_as_string() must work for an
    IfcConversionBasedUnit whose Name isn't one of the fixed set
    ifcopenshell.util.unit.si_conversions recognises (e.g. a project that,
    reasonably, names its foot-based unit something other than the bare
    "foot" IfcOpenShell's own add_conversion_based_unit() produces -- for
    instance to distinguish the US survey foot, 1200/3937 m exactly, from
    the international foot, 0.3048 m exactly, which differ by ~2 ppm and
    are NOT interchangeable once a project is tied to a US state plane CRS,
    virtually all of which are defined in US survey feet).

    Previously, station_as_string() converted via
    ifcopenshell.util.unit.convert(), which looks up the conversion factor
    BY NAME in si_conversions -- silently substituting a factor of 1.0
    (i.e. treating the value as if it were already in the display unit) for
    any unrecognised name, rather than raising an error. For a project unit
    like "US survey foot" this inflated every station string by the
    project-unit<->metre ratio (~3.28x), even though the underlying
    Pset_Stationing.Station numeric value written by
    ifcopenshell.api.alignment.create()/update_key_point_referents was
    correct throughout -- only the display text was wrong.
    """
    file = ifcopenshell.file(schema="IFC4X3_ADD2")
    project = file.createIfcProject(GlobalId=ifcopenshell.guid.new(), Name="Test")

    # Hand-built rather than via add_conversion_based_unit(), since that
    # API also resolves its conversion factor by name (si_conversions) and
    # can't produce a custom name paired with a specific factor.
    si_unit = file.createIfcSIUnit(UnitType="LENGTHUNIT", Name="METRE")
    value_component = file.create_entity("IfcReal", wrappedValue=1200.0 / 3937.0)  # US survey foot, exact
    conversion_factor = file.createIfcMeasureWithUnit(value_component, si_unit)
    exponents = file.createIfcDimensionalExponents(1, 0, 0, 0, 0, 0, 0)
    length = file.createIfcConversionBasedUnit(exponents, "LENGTHUNIT", "US survey foot", conversion_factor)
    ifcopenshell.api.unit.assign_unit(file, units=[length])

    # US survey foot and international foot differ by ~2 ppm. At small
    # station values that's invisible at 2-decimal-place precision, so
    # these match _test_us_stations()'s "foot" case exactly.
    s = sta.station_as_string(file, 0.0)
    assert s == "0+00.00"

    s = sta.station_as_string(file, 100.00)
    assert s == "1+00.00"

    s = sta.station_as_string(file, -100.00)
    assert s == "-1+00.00"

    # At a large enough station, ~2 ppm DOES become visible at 2 decimal
    # places (123456.789 * 2e-6 =~ 0.25) -- this is the real, correct US
    # survey foot vs. international foot difference, not a bug. Before the
    # fix, the name-based lookup's silent 1.0 fallback inflated this same
    # input by ~3.28x to "1234+57.036" -> "4050+82.90"-ish territory, wildly
    # different from either correct answer -- so this still exercises the
    # regression, it's just not identical to the "foot" case's value.
    s = sta.station_as_string(file, 123456.789)
    assert s == "1234+57.04"

    s = sta.station_as_string(file, -123456.789)
    assert s == "-1234+57.04"


def test_station_as_string():
    _test_si_stations()
    _test_si_stations_millimeter()
    _test_us_stations()
    _test_custom_named_conversion_based_unit_stations()


test_station_as_string()
