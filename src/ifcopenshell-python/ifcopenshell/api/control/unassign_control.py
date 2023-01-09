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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, relating_control=None, related_object=None):
        """Unassigns a planning control or constraint to an object

        :param relating_control: The IfcControl entity that is creating the
            control or constraint
        :type relating_control: ifcopenshell.entity_instance.entity_instance
        :param related_object: The IfcObjectDefinition that is being controlled
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: If the control still is related to other objects, the
            IfcRelAssignsToControl is returned, otherwise None.
        :rtype: ifcopenshell.entity_instance.entity_instance, None

        Example:

        .. code:: python

            # Let's relate a cost item and a product
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
            schedule = ifcopenshell.api.run("cost.add_cost_schedule", model)
            cost_item = ifcopenshell.api.run("cost.add_cost_item", model,
                cost_schedule=schedule)
            ifcopenshell.api.run("control.assign_control", model,
                relating_control=cost_item, related_object=wall)

            # And now let's change our mind
            ifcopenshell.api.run("control.unassign_control", model,
                relating_control=cost_item, related_object=wall)
        """

        self.file = file
        self.settings = {
            "relating_control": relating_control,
            "related_object": related_object,
        }

    def execute(self):
        for rel in self.settings["related_object"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToControl") or rel.RelatingControl != self.settings["relating_control"]:
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel
