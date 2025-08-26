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
import ifcopenshell.api.owner
import ifcopenshell.util.element


def unassign_object(file: ifcopenshell.file, products: list[ifcopenshell.entity_instance]) -> None:
    """Unassigns products from their aggregate

    A product (i.e. a smaller part of a whole) may be aggregated into zero
    or one larger space or element. This function will remove that
    aggregation relationship.

    As all physical IFC model elements must be part of a hierarchical tree
    called the "spatial decomposition", using this function will remove the
    product from that tree. This is a dangerous operation and may result in
    the product no longer being visible in IFC applications.

    If the product is not part of an aggregation relationship, nothing will
    happen.

    :param products: The list of parts of the aggregate, typically of IfcElements or
        IfcSpatialStructureElement subclass
    :return: None

    Example:

    .. code:: python

        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcSite")
        subelement1 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")
        subelement2 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcBuilding")
        ifcopenshell.api.aggregate.assign_object(model, products=[subelement1], relating_object=element)
        ifcopenshell.api.aggregate.assign_object(model, products=[subelement2], relating_object=element)
        # nothing is returned
        ifcopenshell.api.aggregate.unassign_object(model, products=[subelement1])
        # nothing is returned, relationship is removed
        ifcopenshell.api.aggregate.unassign_object(model, products=[subelement2])
    """
    settings = {"products": products}

    products = set(settings["products"])
    rels = set(
        rel
        for product in products
        if (rel := next((rel for rel in product.Decomposes if rel.is_a("IfcRelAggregates")), None))
    )

    for rel in rels:
        related_objects = set(rel.RelatedObjects) - products
        if related_objects:
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
