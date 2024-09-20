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
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Union


def assign_pset(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    pset: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assign property set to provided elements.

    This method can be used to make psets shared by multiple elements.

    :param products: Elements (or element types) to assign the pset to.
    :param pset: Property set.
    :return: None if `products` is empty or has only type elements.
        IfcRelDefinesByProperties if `products` contains occurrences.

    Example:

    .. code:: python

        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.pset.assign_pset(model, [element], pset)
        # Pset is now assigned.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element}

        element1 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        ifcopenshell.api.pset.assign_pset(model, [element1, element2], pset)
        # Pset is now shared by multiple elements.
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {element, element1, element2}

        # Same for element types.
        element_type = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWallType")
        ifcopenshell.api.pset.assign_pset(model, [element_type], type_pset)
        # Pset is now assigned to the type.
        assert ifcopenshell.util.element.get_elements_by_pset(type_pset) == {element_type}
    """
    is_ifc2x3 = file.schema == "IFC2X3"

    products_occurrences: set[ifcopenshell.entity_instance] = set()
    products_types: set[ifcopenshell.entity_instance] = set()
    for product in products:
        if product.is_a("IfcTypeProduct"):
            products_types.add(product)
        else:
            products_occurrences.add(product)

    rel = None
    # Check occurrences using pset.
    if products_occurrences:
        rels = pset.PropertyDefinitionOf if is_ifc2x3 else pset.DefinesOccurrence
        rel = next(iter(rels), None)
        if rel is not None:
            objs = set(rel.RelatedObjects) | products_occurrences
            rel.RelatedObjects = list(objs)
        else:
            rel = file.create_entity(
                "IfcRelDefinesByProperties",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                    "RelatedObjects": list(products_occurrences),
                    "RelatingPropertyDefinition": pset,
                },
            )

    for product in products_types:
        psets = list(product.HasPropertySets or [])
        product.HasPropertySets = psets + [pset]

    return rel
