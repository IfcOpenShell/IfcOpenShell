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


import ifcopenshell.api.control
import ifcopenshell.api.cost
import test.bootstrap
import ifcopenshell.api.root

import ifcopenshell.util.cost as subject


class TestGetCostItemForProduct(test.bootstrap.IFC4):
    def test_run(self):
        model = self.file
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=cost_schedule)
        ifcopenshell.api.control.assign_control(model, related_objects=[element], relating_control=item1)
        assert list(subject.get_cost_items_for_product(element)) == [item1]

    def test_remove_cost_item(self):
        model = self.file
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=cost_schedule)
        ifcopenshell.api.control.assign_control(model, related_objects=[element], relating_control=item1)
        ifcopenshell.api.cost.remove_cost_item(model, cost_item=item1)
        assert list(subject.get_cost_items_for_product(element)) == []

    def test_no_assigned_cost_items(self):
        model = self.file
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item1 = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=cost_schedule)
        assert list(subject.get_cost_items_for_product(element)) == []
