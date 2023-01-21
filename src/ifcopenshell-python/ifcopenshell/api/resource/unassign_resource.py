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
    def __init__(self, file, relating_resource=None, related_object=None):
        """Removes the relationship between a resource and object

        :param relating_resource: The IfcResource to assign the object to.
        :type relating_resource: ifcopenshell.entity_instance.entity_instance
        :param related_object: The IfcProduct or IfcActor to assign to the
            object.
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcRelAssignsToResource
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Add our own crew
            crew = ifcopenshell.api.run("resource.add_resource", model, ifc_class="IfcCrewResource")

            # Add some a tower crane to our crew.
            crane = ifcopenshell.api.run("resource.add_resource", model,
                parent_resource=crew, ifc_class="IfcConstructionEquipmentResource", name="Tower Crane 01")

            # Our tower crane will be placed via this physical product.
            product = ifcopenshell.api.run("root.create_entity", model,
                ifc_class="IfcBuildingElementProxy", predefined_type="CRANE")

            # Let's assign our crane to the resource. The crane now represents
            # the resource.
            ifcopenshell.api.run("resource.assign_resource", model,
                relating_resource=crane, related_object=product)

            # Undo it.
            ifcopenshell.api.run("resource.unassign_resource", model,
                relating_resource=crane, related_object=product)
        """
        self.file = file
        self.settings = {
            "relating_resource": relating_resource,
            "related_object": related_object,
        }

    def execute(self):
        for rel in self.settings["related_object"].HasAssignments or []:
            if (
                not rel.is_a("IfcRelAssignsToResource")
                or rel.RelatingResource != self.settings["relating_resource"]
            ):
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run(
                "owner.update_owner_history", self.file, **{"element": rel}
            )
            return rel
