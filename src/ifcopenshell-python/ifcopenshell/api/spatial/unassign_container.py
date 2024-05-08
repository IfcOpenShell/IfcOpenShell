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


def unassign_container(file: ifcopenshell.file, products: list[ifcopenshell.entity_instance]) -> None:
    """Unassigns a container from products.

    :param product: A list of IfcProducts to remove the containment from.
    :type product: list[ifcopenshell.entity_instance]
    :return: None
    :rtype: None

    Example:

    .. code:: python

        project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject")
        site = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcSite")
        building = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuilding")
        storey = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcBuildingStorey")

        # The project contains a site (note that project aggregation is a special case in IFC)
        ifcopenshell.api.run("aggregate.assign_object", model, products=[site], relating_object=project)

        # The site has a building, the building has a storey, and the storey has a space
        ifcopenshell.api.run("aggregate.assign_object", model, products=[building], relating_object=site)
        ifcopenshell.api.run("aggregate.assign_object", model, products=[storey], relating_object=building)

        # Create a wall
        wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")

        # The wall is in the storey
        ifcopenshell.api.run("spatial.assign_container", model, products=[wall], relating_structure=storey)

        # Not anymore!
        ifcopenshell.api.run("spatial.unassign_container", model, products=[wall])
    """
    settings = {
        "products": products,
    }

    products = set(settings["products"])
    rels = set(rel for product in products if (rel := next(iter(product.ContainedInStructure), None)))

    for rel in rels:
        related_elements = set(rel.RelatedElements) - products
        if related_elements:
            rel.RelatedElements = list(related_elements)
            ifcopenshell.api.run("owner.update_owner_history", file, element=rel)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
