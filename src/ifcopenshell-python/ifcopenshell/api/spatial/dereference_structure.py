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
import ifcopenshell.util.element


def dereference_structure(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    relating_structure: ifcopenshell.entity_instance,
) -> None:
    """Dereferences a list of products and space

    :param products: The list of physical IfcElements that exists in the space.
    :type products: list[ifcopenshell.entity_instance]
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
        ifcopenshell.api.run("aggregate.assign_object", model, products=[site], relating_object=project)

        # The site has a building, the building has a storey, and the storey has a space
        ifcopenshell.api.run("aggregate.assign_object", model, products=[building], relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", model, products=[storey], relating_object=building)
        ifcopenshell.api.run("aggregate.assign_object", model, products=[space], relating_object=storey)

        # Create a column, this column spans 3 storeys
        column = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

        # The column is contained in the lowermost storey
        ifcopenshell.api.run("spatial.assign_container", model, products=[column], relating_structure=storey1)

        # And referenced in the others
        ifcopenshell.api.run("spatial.reference_structure", model, products=[column], relating_structure=storey2)
        ifcopenshell.api.run("spatial.reference_structure", model, products=[column], relating_structure=storey3)

        # Actually, it only goes up to storey 2.
        ifcopenshell.api.run("spatial.dereference_structure", model, products=[column], relating_structure=storey3)
    """
    settings = {"products": products, "relating_structure": relating_structure}

    products = set(settings["products"])
    for rel in settings["relating_structure"].ReferencesElements:
        related_elements = set(rel.RelatedElements)
        if not related_elements.intersection(products):
            continue
        related_elements = related_elements - products
        if related_elements:
            rel.RelatedElements = list(related_elements)
            ifcopenshell.api.run("owner.update_owner_history", file, **{"element": rel})
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
