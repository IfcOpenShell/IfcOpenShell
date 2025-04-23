# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.cost


class TestAddCostSchedule(test.bootstrap.IFC4):
    def test_add_a_cost_schedule(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        assert schedule.is_a("IfcCostSchedule")
        assert schedule.Name == "Foo"
        assert schedule.PredefinedType == "BUDGET"

    def test_adding_a_userdefined_type(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="FOO")
        assert schedule.is_a("IfcCostSchedule")
        assert schedule.Name == "Foo"
        assert schedule.PredefinedType == "USERDEFINED"
        assert schedule.ObjectType == "FOO"


class TestAddCostScheduleIFC2X3(test.bootstrap.IFC2X3, TestAddCostSchedule):
    pass
