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
    def __init__(self, file, product=None):
        """Unassigns a container from a product.

        Caution: this API function may be replaced by spatial.unassign_container

        :param product: The IfcProduct to remove the containment from.
        :type product: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
            site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
            storey = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")

            # The project contains a site (note that project aggregation is a special case in IFC)
            ifcopenshell.api.run("aggregate.assign_object", model, product=site, relating_object=project)

            # The site has a building, the building has a storey, and the storey has a space
            ifcopenshell.api.run("aggregate.assign_object", model, product=building, relating_object=site)
            ifcopenshell.api.run("aggregate.assign_object", model, product=storey, relating_object=building)

            # Create a wall
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # The wall is in the storey
            ifcopenshell.api.run("spatial.assign_container", model, product=wall, relating_structure=storey)

            # Not anymore!
            ifcopenshell.api.run("spatial.remove_container", model, product=wall)
        """
        self.file = file
        self.settings = {"product": product}

    def execute(self):
        contained_in_structure = self.settings["product"].ContainedInStructure
        if not contained_in_structure:
            return

        related_elements = list(contained_in_structure[0].RelatedElements)
        related_elements.remove(self.settings["product"])
        if related_elements:
            contained_in_structure[0].RelatedElements = related_elements
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contained_in_structure[0]})
        else:
            self.file.remove(contained_in_structure[0])
