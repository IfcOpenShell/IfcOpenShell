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


def remove_cost_item_quantity(
    file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance, physical_quantity: ifcopenshell.entity_instance
) -> None:
    """Removes a quantity assigned to a cost item

    If the quantity is part of a product (e.g. wall), then the quantity will
    still exist and merely the relationship to the cost item will be
    removed.

    :param cost_item: The IfcCostItem that the quantity is assigned to
    :param physical_quantity: The IfcPhysicalQuantity to remove
    :return: None

    Example:

    .. code:: python

        schedule = ifcopenshell.api.cost.add_cost_schedule(model)
        item = ifcopenshell.api.cost.add_cost_item(model, cost_schedule=schedule)
        quantity = ifcopenshell.api.cost.add_cost_item_quantity(model,
            cost_item=item, ifc_class="IfcQuantityVolume")
        # Let's change our mind and delete it
        ifcopenshell.api.cost.remove_cost_item(model,
            cost_item=item, physical_quantity=quantity)
    """
    if file.get_total_inverses(physical_quantity) == 1:
        file.remove(physical_quantity)
        return
    quantities = list(cost_item.CostQuantities or [])
    quantities.remove(physical_quantity)
    cost_item.CostQuantities = quantities
