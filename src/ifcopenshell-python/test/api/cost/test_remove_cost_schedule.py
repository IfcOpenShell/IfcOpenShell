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
import ifcopenshell.api
import ifcopenshell.api.cost


class TestRemoveCostSchedule(test.bootstrap.IFC4):
    def test_remove_a_cost_schedule(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        ifcopenshell.api.cost.remove_cost_schedule(self.file, cost_schedule=schedule)
        assert not self.file.by_type("IfcCostSchedule")

    def test_remove_a_schedule_with_items(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        item1 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        item2 = ifcopenshell.api.cost.add_cost_item(self.file, cost_item=item1)
        ifcopenshell.api.cost.remove_cost_schedule(self.file, cost_schedule=schedule)
        assert not self.file.by_type("IfcCostSchedule")
        assert not self.file.by_type("IfcCostItem")
        assert not self.file.by_type("IfcRelNests")
        assert not self.file.by_type("IfcRelAssignsToControl")


class TestRemoveCostScheduleIFC2X3(test.bootstrap.IFC2X3, TestRemoveCostSchedule):
    pass
