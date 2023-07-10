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

import ifcopenshell.util.element
import ifcopenshell.api


class Usecase:
    def __init__(self, file, source=None, destination=None):
        """Copies all cost values from one cost item to another

        Any previously existing values will be removed. The entire value is
        copied, including all components and formulas. However they are not
        parametrically linked, so if one value changes, the other will not.

        :param source: The IfcCostItem to copy cost values from
        :type source: ifcopenshell.entity_instance.entity_instance
        :param destination: The IfcCostItem to copy cost values from
        :type destination: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Assume we have a schedule with multiple items in it
            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item1 = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)
            item2 = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)

            # One of the items has a value
            value = ifcopenshell.api.run("cost.add_cost_value", model, parent=item)
            ifcopenshell.api.run("cost.edit_cost_value", model, cost_value=value,
                attributes={"AppliedValue": 5000.0})

            # Let's copy the value from one item to another
            ifcopenshell.api.run("cost.copy_cost_item_values", model, source=item1, destination=item2)
        """
        self.file = file
        self.settings = {"source": source, "destination": destination}

    def execute(self):
        for cost_value in self.settings["destination"].CostValues or []:
            ifcopenshell.api.run("cost.remove_cost_item_value", self.file, cost_value=cost_value)
        copied_cost_values = []
        for cost_value in self.settings["source"].CostValues or []:
            copied_cost_values.append(ifcopenshell.util.element.copy_deep(self.file, cost_value))
        self.settings["destination"].CostValues = copied_cost_values
