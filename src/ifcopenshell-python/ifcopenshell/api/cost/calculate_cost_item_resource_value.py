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

import ifcopenshell.api.cost
import ifcopenshell.util.date
import ifcopenshell.util.resource


def calculate_cost_item_resource_value(file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance) -> None:
    """Calculates the total cost of all resources associated with a cost item

    A cost item may have construction resources (e.g. equipment, material,
    etc) assigned to it. Construction resources may be assigned directly to
    the cost item, or assigned first to a task, and the task is then
    assigned to the cost item.

    The cost of a resource is calculated by the total sum of all of its base
    costs. If no quantity is provided, that sum is considered to be the
    total cost. Otherwise, it is considered to be a unit cost, and is then
    multiplied by the resource quantity. The quantity is either stored as a
    base quantity (such as a volume) for a things like material resources,
    or as a duration as a daily rate for labour resources.

    The final calculated cost is set as the cost item's value. Any
    previously existing values are removed.

    :param cost_item: The IfcCostItem to calculate
    :type cost_item: ifccopenshell.entity_instance.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # First, we need a cost schedule and item
        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # Let's imagine we have our own formworking crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # ... and they need concrete
        concrete = ifcopenshell.api.resource.add_resource(model,
            ifc_class="IfcConstructionMaterialResource", parent_resource=crew)
        ifcopenshell.api.control.assign_control(model,
            relating_control=item, related_object=concrete)
        # ... which has a unit price of 42.0 per m3
        value = ifcopenshell.api.cost.add_cost_value(model, parent=concrete)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 42.0})
        # ... and a volume of 200m3
        quantity = ifcopenshell.api.resource.add_resource_quantity(model,
            resource=concrete, ifc_class="IfcQuantityVolume")
        ifcopenshell.api.resource.edit_resource_quantity(model,
            physical_quantity=quantity, "attributes": {"VolumeValue": 200.0})

        # Let's say they also need some equipment
        equipment = ifcopenshell.api.resource.add_resource(model,
            ifc_class="IfcConstructionEquipmentResource", parent_resource=crew)
        ifcopenshell.api.control.assign_control(model,
            relating_control=item, related_object=equipment)
        # ... with a fixed price of 50,000
        value = ifcopenshell.api.cost.add_cost_value(model, parent=concrete)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 42.0})

        # (42 * 200) + 50000 = 58400 is our calculated cost
        ifcopenshell.api.cost.calculate_cost_item_resource_value(model, cost_item=item)
    """
    settings = {"cost_item": cost_item}

    for cost_value in settings["cost_item"].CostValues or []:
        ifcopenshell.api.cost.remove_cost_value(file, parent=settings["cost_item"], cost_value=cost_value)

    resources = []
    for rel in settings["cost_item"].Controls or []:
        for related_object in rel.RelatedObjects:
            if related_object.is_a("IfcConstructionResource"):
                resources.append(related_object)
            elif related_object.is_a("IfcTask"):
                for rel2 in related_object.OperatesOn or []:
                    for related_object2 in rel2.RelatedObjects:
                        if related_object2.is_a("IfcConstructionResource"):
                            resources.append(related_object2)

    for resource in resources:
        cost, unit = ifcopenshell.util.resource.get_cost(resource)
        if not cost:
            cost, unit = ifcopenshell.util.resource.get_parent_cost(
                resource
            )  # Concept to standardise - Not defined in schema, but this makes manual scheduling of resources 10x faster and less duplicate data.
        quantity = ifcopenshell.util.resource.get_quantity(resource)
        if not cost or not quantity:
            continue
        if unit and "day" in unit:
            quantity = quantity / 8  # Assume 8 hour working day - TODO implement resource calendar
        quantity = round(quantity, 2)
        formula = "{}*{}".format(cost, quantity)
        cost_value = ifcopenshell.api.cost.add_cost_value(file, parent=settings["cost_item"])
        cost_value.Name = resource.Name
        ifcopenshell.api.cost.edit_cost_value_formula(file, cost_value=cost_value, formula=formula)
