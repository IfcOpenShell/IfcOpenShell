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


class TestRemoveUnit(test.bootstrap.IFC4):
    def test_remove_a_single_unit(self):
        self.file.createIfcProject()
        unit = self.file.createIfcContextDependentUnit()
        ifcopenshell.api.unit.remove_unit(self.file, unit=unit)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0

    def test_remove_the_only_assigned_unit(self):
        self.file.createIfcProject()
        unit = self.file.createIfcContextDependentUnit()
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        ifcopenshell.api.unit.remove_unit(self.file, unit=unit)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0
        assert len(self.file.by_type("IfcUnitAssignment")) == 0

    def test_remove_an_assigned_unit(self):
        self.file.createIfcProject()
        unit1 = self.file.createIfcContextDependentUnit()
        unit2 = self.file.createIfcSIUnit()
        assignment = ifcopenshell.api.unit.assign_unit(self.file, units=[unit1, unit2])
        ifcopenshell.api.unit.remove_unit(self.file, unit=unit1)
        assert len(self.file.by_type("IfcContextDependentUnit")) == 0
        assert assignment.Units == (unit2,)

    def test_removing_a_unit_deeply(self):
        self.file.createIfcProject()
        unit = ifcopenshell.api.unit.add_conversion_based_unit(self.file, name="foot")
        ifcopenshell.api.unit.remove_unit(self.file, unit=unit)
        assert len([e for e in self.file]) == 1


class TestRemoveUnitIFC2X3(test.bootstrap.IFC2X3, TestRemoveUnit):
    pass
