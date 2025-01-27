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


class TestAssignUnit(test.bootstrap.IFC4):
    def test_run(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        unit2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        assignment = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1, unit2])
        assert project.UnitsInContext == assignment
        assert assignment.is_a("IfcUnitAssignment")
        assert unit1 in assignment.Units
        assert unit2 in assignment.Units

    def test_assign_units_to_an_existing_assignment(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        unit2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        assignment1 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1])
        assignment2 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit2])
        assert project.UnitsInContext == assignment1
        assert assignment1 == assignment2
        assert unit1 in assignment1.Units
        assert unit2 in assignment1.Units

    def test_overwriting_an_existing_unit_type(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="MILLI")
        unit2 = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT", prefix="CENTI")
        assignment1 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1])
        assignment2 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit2])
        assert project.UnitsInContext == assignment1
        assert assignment1 == assignment2
        assert unit1 not in assignment1.Units
        assert unit2 in assignment1.Units

    def test_overwriting_an_existing_monetary_unit(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        unit2 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="AUD")
        assignment1 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1])
        assignment2 = ifcopenshell.api.unit.assign_unit(self.file, units=[unit2])
        assert project.UnitsInContext == assignment1
        assert assignment1 == assignment2
        assert unit1 not in assignment1.Units
        assert unit2 in assignment1.Units


class TestAssignUnitIFC2X3(test.bootstrap.IFC2X3, TestAssignUnit):
    pass
