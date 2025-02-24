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
import ifcopenshell


def remove_cost_value(
    file: ifcopenshell.file, parent: ifcopenshell.entity_instance, cost_value: ifcopenshell.entity_instance
) -> None:
    """Removes a cost value

    The cost value may be assigned either to a cost item, a construction
    resource, or another cost value (i.e. it is a subcomponent of a cost)

    :param parent: The IfcCostItem, IfcConstructionResource, or IfcCostValue
        that the IfcCostValue is assigned to.
    :param cost_value: The IfcCostValue that you want to remove
    :return: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)

        # This cost item will have a unit cost of 5 and a volume of 3
        value = ifcopenshell.api.cost.add_cost_value(model, parent=item)
        ifcopenshell.api.cost.edit_cost_value(model, cost_value=value,
            attributes={"AppliedValue": 5.0})

        ifcopenshell.api.cost.remove_cost_value(model, parent=item, cost_value=value)
    """
    if file.get_total_inverses(cost_value) == 1:
        file.remove(cost_value)
        # TODO deep purge
    elif parent.is_a("IfcCostItem"):
        values = list(parent.CostValues)
        values.remove(cost_value)
        parent.CostValues = values if values else None
    elif parent.is_a("IfcConstructionResource"):
        values = list(parent.BaseCosts)
        values.remove(cost_value)
        parent.BaseCosts = values if values else None
    elif parent.is_a("IfcCostValue"):
        components = list(parent.Components)
        components.remove(cost_value)
        parent.Components = components if components else None
