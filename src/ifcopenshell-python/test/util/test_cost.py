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


class TestCalculateAppliedValuePrecision(test.bootstrap.IFC4):
    """Regression tests for #6964: DimitriosThe's invariant is that "there
    should be absolutely no rounding whatsoever, happening ever anywhere"
    in a cost calculation. These assert a cost item total made of several
    many-significant-digit components comes back bit-identical to the
    Python sum, not truncated."""

    def test_a_single_component_is_not_rounded(self):
        model = self.file
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=cost_schedule)
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        applied_value = 150.79197255123456
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value, attributes={"AppliedValue": applied_value})
        assert subject.calculate_applied_value(item, value) == applied_value

    def test_a_sum_of_many_significant_digit_components_is_not_rounded(self):
        model = self.file
        cost_schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=cost_schedule)
        sum_value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        components = [10.481575000123, 9.9278884001, 0.887000024, 1.612800002]
        for component_value in components:
            component = ifcopenshell.api.cost.add_cost_value(model, parent=sum_value)
            ifcopenshell.api.cost.edit_cost_value(
                model, cost_value=component, attributes={"AppliedValue": component_value}
            )
        sum_value.ArithmeticOperator = "ADD"
        assert subject.calculate_applied_value(item, sum_value) == sum(components)
