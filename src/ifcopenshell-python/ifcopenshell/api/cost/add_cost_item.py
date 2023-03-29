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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, cost_schedule=None, cost_item=None):
        """Add a new cost item

        A cost item represents a single line item in a cost schedule. Cost items
        may then be broken down into cost subitems.

        :param cost_schedule: If the cost item is to be added as a root or top
            level cost item to a cost schedule, the IfcCostSchedule may be
            specified. This is mutually exlclusive to the cost_item parameter.
        :type cost_schedule: ifcopenshell.entity_instance.entity_instance
        :param cost_item: If the cost item is to be added as a subitem to an
            existing cost item, the parent IfcCostItem may be specified. This is
            mutually exclusive to the cost_schedule parameter.
        :type cost_item: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcCostItem
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # The very first cost item must be in a cost schedule
            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)

            # You may add cost items as top level item in the schedule
            item1 = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)

            # Alternatively you may add them as subitems
            item2 = ifcopenshell.api.run("cost.add_cost_item", model, cost_item=item1)
        """
        self.file = file
        self.settings = {"cost_schedule": cost_schedule, "cost_item": cost_item}

    def execute(self):
        cost_item = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcCostItem")

        if self.settings["cost_schedule"]:
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [cost_item],
                    "RelatingControl": self.settings["cost_schedule"],
                }
            )
        elif self.settings["cost_item"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=cost_item, relating_object=self.settings["cost_item"]
            )
        return cost_item
