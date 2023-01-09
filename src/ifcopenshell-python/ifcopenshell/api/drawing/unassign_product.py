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
    def __init__(self, file, relating_product=None, related_object=None):
        """Unassigns a product and an object (typically an annotation)

        Smart annotation objects can be associated with products so that they
        can annotate attributes and properties. This function lets you remove
        the association, so that you may change the assocation with another
        object later or leave the annotation as a "dumb" annotation.

        :param relating_product: The IfcProduct the object is related to
        :type relating_product: ifcopenshell.entity_instance.entity_instance
        :param related_object: The object (typically IfcAnnotation) that the
            product is related to
        :type related_object: ifcopenshell.entity_instance.entity_instance
        :return: The created IfcRelAssignsToProduct relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            furniture = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")
            annotation = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcAnnotation")
            ifcopenshell.api.run("drawing.assign_product", model,
                relating_product=furniture, related_object=annotation)

            # Let's change our mind and remove the relationship
            ifcopenshell.api.run("drawing.unassign_product", model,
                relating_product=furniture, related_object=annotation)
        """
        self.file = file
        self.settings = {
            "relating_product": relating_product,
            "related_object": related_object,
        }

    def execute(self):
        for rel in self.settings["related_object"].HasAssignments or []:
            if not rel.is_a("IfcRelAssignsToProduct") or rel.RelatingProduct != self.settings["relating_product"]:
                continue
            if len(rel.RelatedObjects) == 1:
                return self.file.remove(rel)
            related_objects = list(rel.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            rel.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            return rel
