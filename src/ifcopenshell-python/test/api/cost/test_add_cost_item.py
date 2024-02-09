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


class TestAddCostItem(test.bootstrap.IFC4):
    def test_add_a_cost_item(self):
        schedule = ifcopenshell.api.run("cost.add_cost_schedule", self.file, name="Foo")
        item1 = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_schedule=schedule)
        assert item1.is_a("IfcCostItem")
        assert item1.HasAssignments[0].is_a("IfcRelAssignsToControl")
        assert item1.HasAssignments[0].RelatingControl == schedule

    def test_add_a_sub_cost_item(self):
        schedule = ifcopenshell.api.run("cost.add_cost_schedule", self.file, name="Foo")
        item1 = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_schedule=schedule)
        item2 = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_item=item1)
        assert item2.is_a("IfcCostItem")
        assert item2.Nests[0].RelatingObject == item1
