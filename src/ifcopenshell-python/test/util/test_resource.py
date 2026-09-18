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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.control
import ifcopenshell.api.cost
import ifcopenshell.api.resource
import ifcopenshell.api.root
import test.bootstrap

import ifcopenshell.util.cost
import ifcopenshell.util.resource as subject


# NOTE: resource module features relies on entities introduced in IFC4
# therefore no IFC2X3 tests
class TestResourceBuildUpPrecision(test.bootstrap.IFC4):
    """Regression tests for #6964: DimitriosThe's invariant is that a
    resource build-up total must carry no rounding whatsoever. These assert
    that a many-significant-digit value put into a resource cost or
    quantity comes back bit-identical, not truncated, through the same
    functions Bonsai's cost/resource panels call."""

    def test_get_cost_preserves_a_many_significant_digit_applied_value(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=resource)
        applied_value = 150.79197255123456
        ifcopenshell.api.cost.edit_cost_value(self.file, cost_value=value, attributes={"AppliedValue": applied_value})
        cost, unit = subject.get_cost(resource)
        assert cost == applied_value

    def test_get_cost_sums_nested_resources_without_rounding(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        crew = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        labour = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource", parent_resource=crew)
        equipment = ifcopenshell.api.resource.add_resource(
            self.file, ifc_class="IfcConstructionEquipmentResource", parent_resource=crew
        )
        labour_value = 38.707200048
        equipment_value = 0.03000000119
        for resource, value in ((labour, labour_value), (equipment, equipment_value)):
            cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=resource)
            ifcopenshell.api.cost.edit_cost_value(self.file, cost_value=cost_value, attributes={"AppliedValue": value})

        crew_cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=crew)
        crew_cost_value.Category = "*"
        total, unit = subject.get_cost(crew)
        assert total == labour_value + equipment_value

    def test_get_quantity_preserves_a_duration_with_a_fractional_second(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcLaborResource")
        resource_time = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource)
        ifcopenshell.api.resource.edit_resource_time(
            self.file, resource_time=resource_time, attributes={"ScheduleWork": "PT2H29M59.999867S"}
        )
        assert subject.get_quantity(resource) == 8999.999867 / 3600


class TestCalculateCostItemResourceValuePrecision(test.bootstrap.IFC4):
    """The cost item's calculated value is a formula of resource cost times
    resource quantity, not a stored rounded number. It must reproduce the
    exact product on every read."""

    def test_run(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)

        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcConstructionMaterialResource")
        ifcopenshell.api.control.assign_control(self.file, relating_control=item, related_objects=[resource])

        unit_cost = 42.123456789012
        cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=resource)
        ifcopenshell.api.cost.edit_cost_value(self.file, cost_value=cost_value, attributes={"AppliedValue": unit_cost})

        quantity = ifcopenshell.api.resource.add_resource_quantity(
            self.file, resource=resource, ifc_class="IfcQuantityVolume"
        )
        volume = 200.987654321
        ifcopenshell.api.resource.edit_resource_quantity(
            self.file, physical_quantity=quantity, attributes={"VolumeValue": volume}
        )

        ifcopenshell.api.cost.calculate_cost_item_resource_value(self.file, cost_item=item)

        total = ifcopenshell.util.cost.calculate_applied_value(item, item.CostValues[0])
        assert total == unit_cost * volume
