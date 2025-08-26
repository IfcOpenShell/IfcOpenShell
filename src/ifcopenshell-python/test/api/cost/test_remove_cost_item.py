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


class TestRemoveCostItem(test.bootstrap.IFC4):
    def test_remove_a_cost_item(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        item1 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        ifcopenshell.api.cost.remove_cost_item(self.file, cost_item=item1)
        assert not self.file.by_type("IfcCostItem")
        assert not self.file.by_type("IfcRelAssignsToControl")

    def test_remove_a_sub_cost_item(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        item1 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        item2 = ifcopenshell.api.cost.add_cost_item(self.file, cost_item=item1)
        ifcopenshell.api.cost.remove_cost_item(self.file, cost_item=item2)
        assert self.file.by_type("IfcCostItem") == [item1]
        assert self.file.by_type("IfcRelAssignsToControl")
        assert not self.file.by_type("IfcRelNests")

    def test_remove_a_parent_cost_item(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        item1 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        item2 = ifcopenshell.api.cost.add_cost_item(self.file, cost_item=item1)
        ifcopenshell.api.cost.remove_cost_item(self.file, cost_item=item1)
        assert not self.file.by_type("IfcCostItem")
        assert not self.file.by_type("IfcRelAssignsToControl")
        assert not self.file.by_type("IfcRelNests")

    def test_remove_cost_item_keep_rel_for_other_cost_items(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo", predefined_type="BUDGET")
        item1 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        item2 = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        ifcopenshell.api.cost.remove_cost_item(self.file, cost_item=item1)
        assert self.file.by_type("IfcCostItem") == [item2]
        rel = next(iter(self.file.by_type("IfcRelAssignsToControl")), None)
        assert rel
        assert rel.RelatedObjects == (item2,)


class TestRemoveCostItemIFC2X3(test.bootstrap.IFC2X3, TestRemoveCostItem):
    pass
