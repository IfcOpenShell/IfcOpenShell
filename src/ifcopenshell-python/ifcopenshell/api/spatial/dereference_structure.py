# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
    def __init__(self, file, product=None, relating_structure=None):
        """Dereferences the a product and space

        :param product: The physical IfcElement that exists in the space.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param relating_structure: The IfcSpatialStructureElement element, such
            as IfcBuilding, IfcBuildingStorey, or IfcSpace that the element
            exists in.
        :return: None
        :rtype: None

        Example:

        .. code:: python

            project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
            site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
            storey1 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")
            storey2 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")
            storey3 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")

            # The project contains a site (note that project aggregation is a special case in IFC)
            ifcopenshell.api.run("aggregate.assign_object", model, product=site, relating_object=project)

            # The site has a building, the building has a storey, and the storey has a space
            ifcopenshell.api.run("aggregate.assign_object", model, product=building, relating_object=site)
            ifcopenshell.api.run("aggregate.assign_object", model, product=storey, relating_object=building)
            ifcopenshell.api.run("aggregate.assign_object", model, product=space, relating_object=storey)

            # Create a column, this column spans 3 storeys
            column = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

            # The column is contained in the lowermost storey
            ifcopenshell.api.run("spatial.assign_container", model, product=column, relating_structure=storey1)

            # And referenced in the others
            ifcopenshell.api.run("spatial.reference_structure", model, product=column, relating_structure=storey2)
            ifcopenshell.api.run("spatial.reference_structure", model, product=column, relating_structure=storey3)

            # Actually, it only goes up to storey 2.
            ifcopenshell.api.run("spatial.dereference_structure", model, product=column, relating_structure=storey3)
        """
        self.file = file
        self.settings = {"product": product, "relating_structure": relating_structure}

    def execute(self):
        for rel in self.settings["product"].ReferencedInStructures:
            if rel.RelatingStructure != self.settings["relating_structure"]:
                continue
            related_elements = list(rel.RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                rel.RelatedElements = related_elements
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
            else:
                self.file.remove(rel)
