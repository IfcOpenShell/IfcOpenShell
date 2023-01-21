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
    def __init__(self, file, cost_item=None):
        """Removes a cost item

        All associated relationships with the cost item are also removed,
        however the related resources, products, and tasks themselves are
        retained.

        :param cost_item: The IfcCostItem entity you want to remove
        :type cost_item: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            item = ifcopenshell.api.run("cost.add_cost_item", model, cost_schedule=schedule)
            ifcopenshell.api.run("cost.remove_cost_item", model, cost_item=item)
        """
        self.file = file
        self.settings = {"cost_item": cost_item}

    def execute(self):
        # TODO: do a deep purge
        for inverse in self.file.get_inverse(self.settings["cost_item"]):
            if inverse.is_a("IfcRelNests"):
                if inverse.RelatingObject == self.settings["cost_item"]:
                    for related_object in inverse.RelatedObjects:
                        ifcopenshell.api.run("cost.remove_cost_item", self.file, cost_item=related_object)
                elif inverse.RelatedObjects == tuple(self.settings["cost_item"]):
                    self.file.remove(inverse)
            elif inverse.is_a("IfcRelAssignsToControl"):
                self.file.remove(inverse)
        self.file.remove(self.settings["cost_item"])
