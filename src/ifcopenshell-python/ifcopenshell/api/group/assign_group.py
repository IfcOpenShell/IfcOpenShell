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
    def __init__(self, file, products=None, group=None):
        """Assigns products to a group

        If a product is already assigned to the group, it will not be assigned
        twice.

        :param products: A list of IfcProduct elements to assign to the group
        :type products: list[ifcopenshell.entity_instance.entity_instance]
        :param group: The IfcGroup to assign the products to
        :type group: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAssignsToGroup relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            group = ifcopenshell.api.run("group.add_group", model, Name="Furniture")
            ifcopenshell.api.run("group.assign_group", model,
                products=model.by_type("IfcFurniture"), group=group)
        """
        self.file = file
        self.settings = {
            "products": products,
            "group": group,
        }

    def execute(self):
        if not self.settings["group"].IsGroupedBy:
            return self.file.create_entity(
                "IfcRelAssignsToGroup",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": self.settings["products"],
                    "RelatingGroup": self.settings["group"],
                }
            )
        rel = self.settings["group"].IsGroupedBy[0]
        related_objects = set(rel.RelatedObjects) or set()
        for obj in self.settings["products"]:
            related_objects.add(obj)
        rel.RelatedObjects = list(related_objects)
        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
