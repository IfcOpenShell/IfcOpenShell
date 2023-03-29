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
    def __init__(self, file, parent=None, cost_value=None):
        """Removes a cost value

        The cost value may be assigned either to a cost item, a construction
        resource, or another cost value (i.e. it is a subcomponent of a cost)

        :param parent: The IfcCostItem, IfcConstructionResource, or IfcCostValue
            that the IfcCostValue is assigned to.
        :type parent: ifcopenshell.entity_instance.entity_instance
        :param cost_value: The IfcCostValue that you want to remove
        :type parent: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)

            # This cost item will have a unit cost of 5 and a volume of 3
            value = ifcopenshell.api.run("cost.add_cost_value", model, parent=item)
            ifcopenshell.api.run("cost.edit_cost_value", model, cost_value=value,
                attributes={"AppliedValue": 5.0})

            ifcopenshell.api.run("cost.remove_cost_value", model, parent=item, cost_value=value)
        """
        self.file = file
        self.settings = {"parent": parent, "cost_value": cost_value}

    def execute(self):
        if len(self.file.get_inverse(self.settings["cost_value"])) == 1:
            self.file.remove(self.settings["cost_value"])
            # TODO deep purge
        elif self.settings["parent"].is_a("IfcCostItem"):
            values = list(self.settings["parent"].CostValues)
            values.remove(self.settings["cost_value"])
            self.settings["parent"].CostValues = values if values else None
        elif self.settings["parent"].is_a("IfcConstructionResource"):
            values = list(self.settings["parent"].BaseCosts)
            values.remove(self.settings["cost_value"])
            self.settings["parent"].BaseCosts = values if values else None
        elif self.settings["parent"].is_a("IfcCostValue"):
            components = list(self.settings["parent"].Components)
            components.remove(self.settings["cost_value"])
            self.settings["parent"].Components = components if components else None
