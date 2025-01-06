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
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union


def reference_structure(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    relating_structure: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Denote that a list products is related to a list of spatial structures

    This is similar to ifcopenshell.api.spatial.assign_container, except
    that containment can only occur between a product and a single spatial
    structure element. This is fine if a wall is on level 1, but not
    appropriate if you have a multistorey column on multiple levels, or a
    door with a to and from space, or a stair going from one floor to
    another floor. This is where spatial referencing is used.

    Typically, the product will be contained in the lowermost, constructed
    first, or primarily accessible space. For a multistorey column or stair,
    the column or stair will therefore be contained in the lowermost storey.
    Then, any other storeys will be referenced.

    Referencing is non-hierarchical, so a door may be referenced in multiple
    spaces simultaneously.

    :param products: The list of physical IfcElements that exists in the space.
    :type products: list[ifcopenshell.entity_instance]
    :param relating_structure: The IfcSpatialStructureElement element, such
        as IfcBuilding, IfcBuildingStorey, or IfcSpace that the element
        exists in.
    :type relating_structure: ifcopenshell.entity_instance
    :return: The IfcRelReferencedInSpatialStructure relationship instance
        or `None` if `products` was an empty list.
    :rtype: Union[ifcopenshell.entity_instance, None]

    Example:

    .. code:: python

        project = ifcopenshell.api.root.create_entity(model, ifc_class="IfcProject")
        site = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite")
        building = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")
        storey1 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
        storey2 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")
        storey3 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuildingStorey")

        # The project contains a site (note that project aggregation is a special case in IFC)
        ifcopenshell.api.aggregate.assign_object(model, products=[site], relating_object=project)

        # The site has a building, the building has a storey, and the storey has a space
        ifcopenshell.api.aggregate.assign_object(model, products=[building], relating_object=site)
        ifcopenshell.api.aggregate.assign_object(model, products=[storey], relating_object=building)
        ifcopenshell.api.aggregate.assign_object(model, products=[space], relating_object=storey)

        # Create a column, this column spans 3 storeys
        column = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # The column is contained in the lowermost storey
        ifcopenshell.api.spatial.assign_container(model, products=[column], relating_structure=storey1)

        # And referenced in the others
        ifcopenshell.api.spatial.reference_structure(
            model, products=[column], relating_structure=[storey2, storey3]
        )
    """
    settings = {
        "products": products,
        "relating_structure": relating_structure,
    }

    structure = settings["relating_structure"]
    products = set(settings["products"])

    if not products:
        return

    referenced = ifcopenshell.util.element.get_structure_referenced_elements(structure)
    products_to_assign = products - referenced
    rel = next(iter(structure.ReferencesElements), None)

    if not products_to_assign:
        return rel

    if rel is None:
        rel = file.create_entity(
            "IfcRelReferencedInSpatialStructure",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
            RelatedElements=list(products_to_assign),
            RelatingStructure=structure,
        )
    else:
        related_elements = set(rel.RelatedElements) | products_to_assign
        rel.RelatedElements = list(related_elements)
        ifcopenshell.api.owner.update_owner_history(file, element=rel)

    return rel
