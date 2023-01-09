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
import ifcopenshell.util.placement


class Usecase:
    def __init__(self, file, product=None, relating_structure=None):
        """Assigns a product to be contained hierarchically in a space

        All physical IFC model elements must be part of a hierarchical tree
        called the "spatial decomposition", where large things are made up of
        smaller things. This tree always begins at an "IfcProject" and is then
        broken down using "decomposition" relationships, of which aggregation is
        the first relationship you will use. See
        ifcopenshell.api.aggregate.assign_object for more details about
        aggregation.

        The IfcProject will be "decomposed" into spatial structure elements.
        These are virtual spaces like stes, buildings, storeys, and spaces (i.e.
        rooms). You can't physically touch these spaces, but you can touch the
        products contained within these spaces.

        To state that a product is contained in a space, you will use a
        "containment" relationship. Containment is a very common relationship
        used to create the hierarchical spatial decomposition tree. For example,
        you might say that "This wall is on the third building storey", or "this
        table is in the living room space".

        The distinguishing factor between aggregation and containment is that
        aggregation occurs between objects of the same type (e.g. a large space
        is made up of smaller spaces), whereas containment is between two
        different types: explicitly saying that a physical product exists within
        a virtual space.

        Containment is critical in construction management, to know which
        objects are in which spaces, as often you would divide your construction
        schedule into storey by storey, or zone by zone. Containment is also
        critical in facility management, as it indicates through which space
        equipment may be accessed for maintenance purposes.

        As a product may only have a single locaion in the "spatial
        decomposition" tree, assigning an aggregate relationship will remove any
        previous aggregation, containment, or nesting relationships it may have.

        :param product: The physical IfcElement that exists in the space.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param relating_structure: The IfcSpatialStructureElement element, such
            as IfcBuilding, IfcBuildingStorey, or IfcSpace that the element
            exists in.
        :return: The IfcRelContainedInSpatialStructure relationship instance
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
            site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
            building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
            storey = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")
            space = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSpace")

            # The project contains a site (note that project aggregation is a special case in IFC)
            ifcopenshell.api.run("aggregate.assign_object", model, product=site, relating_object=project)

            # The site has a building, the building has a storey, and the storey has a space
            ifcopenshell.api.run("aggregate.assign_object", model, product=building, relating_object=site)
            ifcopenshell.api.run("aggregate.assign_object", model, product=storey, relating_object=building)
            ifcopenshell.api.run("aggregate.assign_object", model, product=space, relating_object=storey)

            # Create a wall and furniture
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
            furniture = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")

            # The wall is in the storey, and the furniture is in the space
            ifcopenshell.api.run("spatial.assign_container", model, product=wall, relating_structure=storey)
            ifcopenshell.api.run("spatial.assign_container", model, product=furniture, relating_structure=space)
        """
        self.file = file
        self.settings = {
            "product": product,
            "relating_structure": relating_structure,
        }

    def execute(self):
        contained_in_structure = self.settings["product"].ContainedInStructure
        contains_elements = self.settings["relating_structure"].ContainsElements

        if contains_elements and contained_in_structure and contained_in_structure[0] == contains_elements[0]:
            return

        aggregate = ifcopenshell.util.element.get_aggregate(self.settings["product"])
        if aggregate:
            ifcopenshell.api.run(
                "aggregate.unassign_object", self.file, product=self.settings["product"]
            )

        if contained_in_structure:
            related_elements = list(contained_in_structure[0].RelatedElements)
            related_elements.remove(self.settings["product"])
            if related_elements:
                contained_in_structure[0].RelatedElements = related_elements
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contained_in_structure[0]})
            else:
                self.file.remove(contained_in_structure[0])

        if contains_elements:
            related_elements = list(contains_elements[0].RelatedElements)
            related_elements.append(self.settings["product"])
            contains_elements[0].RelatedElements = related_elements
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": contains_elements[0]})
        else:
            contains_elements = self.file.create_entity(
                "IfcRelContainedInSpatialStructure",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedElements": [self.settings["product"]],
                    "RelatingStructure": self.settings["relating_structure"],
                }
            )

        placement = getattr(self.settings["product"], "ObjectPlacement", None)
        if placement and placement.is_a("IfcLocalPlacement"):
            ifcopenshell.api.run(
                "geometry.edit_object_placement",
                self.file,
                product=self.settings["product"],
                matrix=ifcopenshell.util.placement.get_local_placement(self.settings["product"].ObjectPlacement),
                is_si=False,
            )

        return contains_elements
