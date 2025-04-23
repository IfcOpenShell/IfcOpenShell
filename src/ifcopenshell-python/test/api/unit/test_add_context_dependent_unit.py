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


class TestAddContextDependentUnit(test.bootstrap.IFC4):
    def test_run(self):
        unit = ifcopenshell.api.unit.add_context_dependent_unit(
            self.file,
            unit_type="LENGTHUNIT",
            name="foobar",
            dimensions=(1, 2, 3, 4, 5, 6, 7),
        )
        assert unit.is_a("IfcContextDependentUnit")
        assert unit.Dimensions.LengthExponent == 1
        assert unit.Dimensions.MassExponent == 2
        assert unit.Dimensions.TimeExponent == 3
        assert unit.Dimensions.ElectricCurrentExponent == 4
        assert unit.Dimensions.ThermodynamicTemperatureExponent == 5
        assert unit.Dimensions.AmountOfSubstanceExponent == 6
        assert unit.Dimensions.LuminousIntensityExponent == 7
        assert unit.UnitType == "LENGTHUNIT"
        assert unit.Name == "foobar"


class TestAddContextDependentUnitIFC2X3(test.bootstrap.IFC2X3, TestAddContextDependentUnit):
    pass
