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

import test.bootstrap
import ifcopenshell.api.unit


class TestAddConversionBasedUnitIFC2X3(test.bootstrap.IFC2X3):
    def test_run(self):
        unit = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="foot")
        assert unit.is_a("IfcConversionBasedUnit")
        assert unit.Dimensions.LengthExponent == 1
        assert unit.Dimensions.MassExponent == 0
        assert unit.Dimensions.TimeExponent == 0
        assert unit.Dimensions.ElectricCurrentExponent == 0
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 0
        assert unit.Dimensions.AmountOfSubstanceExponent == 0
        assert unit.Dimensions.LuminousIntensityExponent == 0
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "foot"
        assert unit.ConversionFactor.ValueComponent.wrappedValue == 0.3048
        si_unit = unit.ConversionFactor.UnitComponent
        assert si_unit.is_a("IfcSIUnit")
        assert si_unit.UnitType == "LENGTHUNIT"
        assert si_unit.Prefix is None
        assert si_unit.Name == "METRE"


class TestAddConversionBasedUnitIFC4(test.bootstrap.IFC4, TestAddConversionBasedUnitIFC2X3):
    def test_adding_a_unit_with_offset(self):
        unit = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="fahrenheit")
        assert unit.is_a("IfcConversionBasedUnitWithOffset")
        assert unit.Dimensions.LengthExponent == 0
        assert unit.Dimensions.MassExponent == 0
        assert unit.Dimensions.TimeExponent == 0
        assert unit.Dimensions.ElectricCurrentExponent == 0
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 1
        assert unit.Dimensions.AmountOfSubstanceExponent == 0
        assert unit.Dimensions.LuminousIntensityExponent == 0
        assert unit.UnitType == "THERMODYNAMICTEMPERATUREUNIT"
        assert unit.Name == "fahrenheit"
        assert unit.ConversionFactor.ValueComponent.wrappedValue == 1.8
        si_unit = unit.ConversionFactor.UnitComponent
        assert si_unit.is_a("IfcSIUnit")
        assert si_unit.UnitType == "THERMODYNAMICTEMPERATUREUNIT"
        assert si_unit.Prefix is None
        assert si_unit.Name == "KELVIN"
        assert unit.ConversionOffset == -459.67
