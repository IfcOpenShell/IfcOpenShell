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
    def __init__(self, file, relating_actor=None, related_object=None):
        """Unassigns an actor to an object

        This means that the actor is no longer responsible for the object.

        :param relating_actor: The IfcActor who is responsible for the object.
        :type relating_actor: ifcopenshell.entity_instance.entity_instance
        :param related_object: The object the actor is responsible for.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: The updated IfcRelAssignsToActor relationship or none if there
            is no more valid relationship.
        :rtype: None, ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # We need to procure and install 2 of this particular pump type in our facility.
            pump_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcPumpType")

            # Define who the manufacturer is
            manufacturer = ifcopenshell.api.run("owner.add_organisation", model,
                identification="PWP", name="Pumps With Power")
            ifcopenshell.api.run("owner.add_role", model, assigned_object=manufacturer, role="MANUFACTURER")

            # Make the manufacturer responsible for that pump type.
            ifcopenshell.api.run("owner.assign_actor", model,
                relating_actor=manufacturer, related_object=pump_type)

            # Undo the assignment
            ifcopenshell.api.run("owner.unassign_actor", model,
                relating_actor=manufacturer, related_object=pump_type)
        """
        self.file = file
        self.settings = {
            "relating_actor": relating_actor,
            "related_object": related_object,
        }

    def execute(self):
        for rel in self.settings["related_object"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToActor") or rel.RelatingActor != self.settings["relating_actor"]:
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel
