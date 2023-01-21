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


class Usecase:
    def __init__(self, file, cost_item=None, physical_quantity=None):
        """Removes a quantity assigned to a cost item

        If the quantity is part of a product (e.g. wall), then the quantity will
        still exist and merely the relationship to the cost item will be
        removed.

        :param cost_item: The IfcCostItem that the quantity is assigned to
        :type cost_item: ifcopenshell.entity_instance.entity_instance
        :param physical_quantity: The IfcPhysicalQuantity to remove
        :type physical_quantity: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)
            quantity = ifcopenshell.api.run("cost.add_cost_item_quantity", model,
                cost_item=item, ifc_class="IfcQuantityVolume")
            # Let's change our mind and delete it
            ifcopenshell.api.run("cost.remove_cost_item", model,
                cost_item=item, physical_quantity=quantity)
        """
        self.file = file
        self.settings = {"cost_item": cost_item, "physical_quantity": physical_quantity}

    def execute(self):
        if len(self.file.get_inverse(self.settings["physical_quantity"])) == 1:
            self.file.remove(self.settings["physical_quantity"])
            return
        quantities = list(self.settings["cost_item"].CostQuantities or [])
        quantities.remove(self.settings["physical_quantity"])
        self.settings["cost_item"].CostQuantities = quantities
