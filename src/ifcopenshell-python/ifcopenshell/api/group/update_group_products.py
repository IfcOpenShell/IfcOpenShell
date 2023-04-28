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
    def __init__(self, file, group=None, products=None):
        """Sets a group products to be an explicit list of products

        Any previous products assigned to that group will have their assignment
        removed.

        :param products: A list of IfcProduct elements to assign to the group
        :type products: list[ifcopenshell.entity_instance.entity_instance]
        :param group: The IfcGroup to assign the products to
        :type group: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAssignsToGroup relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            group = ifcopenshell.api.run("group.add_group", model, Name="Furniture")
            ifcopenshell.api.run("group.update_group_products", model,
                products=model.by_type("IfcFurniture"), group=group)
        """
        self.file = file
        self.settings = {
            "group": group,
            "products": products,
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
        else:
            # assumes 1:1 cardinality, will need to be updated to reflect IFC4 changes
            # where the cardinality is 0:? - vulevukusej
            rel = self.settings["group"].IsGroupedBy[0]
            existing_sub_groups = [g for g in rel.RelatedObjects if g.is_a("IfcGroup")]

            rel.RelatedObjects = self.settings["products"]
            for g in existing_sub_groups:
                rel.RelatedObjects.add(g)
