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


class TestUnassignUnit(test.bootstrap.IFC4):
    def test_run(self):
        project = self.file.createIfcProject()
        unit1 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        unit2 = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="JPY")
        assignment = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1, unit2])
        ifcopenshell.api.unit.unassign_unit(self.file, units=[unit1])
        assert unit1 not in assignment.Units
        assert unit2 in assignment.Units

    def test_unassigning_the_last_unit(self):
        project = self.file.createIfcProject()
        unit = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        ifcopenshell.api.unit.unassign_unit(self.file, units=[unit])
        assert project.UnitsInContext is None

    def test_doing_nothing_if_the_unit_is_not_assigned(self):
        unit = ifcopenshell.api.unit.add_monetary_unit(self.file, currency="USD")
        assert ifcopenshell.api.unit.unassign_unit(self.file, units=[unit]) is None


class TestUnassignUnitIFC2X3(test.bootstrap.IFC2X3, TestUnassignUnit):
    pass
