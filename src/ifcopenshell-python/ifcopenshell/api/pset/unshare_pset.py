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


def unshare_pset(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    pset: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance]:
    """Copy a shared pset as linked only to the provided elements.

    Note that method will create a copy of the pset for each element provided.

    :param products: Elements (or element types) to link the pset to.
    :param pset: Shared property set.
    :return: List of copied property sets.
    """
    is_ifc2x3 = file.schema == "IFC2X3"
    products_occurrences: set[ifcopenshell.entity_instance] = set()
    products_types: set[ifcopenshell.entity_instance] = set()
    for product in products:
        if product.is_a("IfcTypeProduct"):
            products_types.add(product)
        else:
            products_occurrences.add(product)

    # Check occurrences using pset.
    rels = pset.PropertyDefinitionOf if is_ifc2x3 else pset.DefinesOccurrence
    for rel in rels:
        objs = set(rel.RelatedObjects)
        if not any(p in objs for p in products_occurrences):
            continue
        objs.difference_update(products_occurrences)
        if objs:
            rel.RelatedObjects = list(objs)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # Check types using pset.
    for product in products_types:
        if not (psets := product.HasPropertySets):
            continue
        psets: list[ifcopenshell.entity_instance] = list(psets)
        psets.remove(pset)
        product.HasPropertySets = psets

    def assign_pset(product: ifcopenshell.entity_instance, pset: ifcopenshell.entity_instance) -> None:
        if product.is_a("IfcTypeProduct"):
            psets = list(product.HasPropertySets or [])
            if not psets:
                psets = []
            product.HasPropertySets = psets + [pset]
            return

        file.create_entity(
            "IfcRelDefinesByProperties",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": [product],
                "RelatingPropertyDefinition": pset_copy,
            },
        )

    pset_copies: list[ifcopenshell.entity_instance] = []
    for product in products:
        pset_copy = ifcopenshell.util.element.copy_deep(file, pset)
        pset_copies.append(pset_copy)
        assign_pset(product, pset_copy)

    return pset_copies
