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
import ifcopenshell.util.element


def remove_reference(
    file: ifcopenshell.file,
    reference: ifcopenshell.entity_instance,
    products: list[ifcopenshell.entity_instance],
) -> None:
    """Removes a classification reference from the list of products

    If the classification reference is no longer associated to any products,
    the classification reference itself is also removed.

    :param reference: The IfcClassificationReference entity of the
        relationship you want to remove.
    :type reference: ifcopenshell.entity_instance
    :param product: The list fo object entities of the relationship you want to
        remove.
    :type product: list[ifcopenshell.entity_instance]

    :raises TypeError: If file is IFC2X3 and `products` has non-IfcRoot elements.

    :return: None
    :rtype: None

    Example:

    .. code:: python

        wall_type = model.by_type("IfcWallType")[0]
        classification = ifcopenshell.api.run("classification.add_classification",
            model, classification="MyCustomClassification")
        reference = ifcopenshell.api.run("classification.add_reference", model,
            products=[wall_type], classification=classification,
            identification="W_01", name="Interior Walls")
        ifcopenshell.api.run("classification.remove_reference", model,
            reference=reference, products=[wall_type])
    """
    settings = {"reference": reference, "products": products}

    is_ifc2x3 = file.schema == "IFC2X3"
    products = set(settings["products"])
    referenced = ifcopenshell.util.element.get_referenced_elements(settings["reference"])
    products -= products.difference(referenced)

    # all products are already unassigned from a reference
    if not products:
        return

    rooted_products: set[ifcopenshell.entity_instance] = set()
    non_rooted_products: set[ifcopenshell.entity_instance] = set()
    for product in settings["products"]:
        if product.is_a("IfcRoot"):
            rooted_products.add(product)
        else:
            non_rooted_products.add(product)

    if non_rooted_products and is_ifc2x3:
        raise TypeError(f"Cannot add reference to non-IfcRoot element in IFC2X3: {non_rooted_products}.")

    if rooted_products:
        reference_rels: set[ifcopenshell.entity_instance] = set()
        for product in rooted_products:
            reference_rels.update(product.HasAssociations)

        reference_rels = {
            rel
            for rel in reference_rels
            if rel.is_a("IfcRelAssociatesClassification") and rel.RelatingClassification == settings["reference"]
        }

        for rel in reference_rels:
            related_objects = set(rel.RelatedObjects) - rooted_products
            if related_objects:
                rel.RelatedObjects = list(related_objects)
                ifcopenshell.api.run("owner.update_owner_history", file, **{"element": rel})
            else:
                history = rel.OwnerHistory
                file.remove(rel)
                if history:
                    ifcopenshell.util.element.remove_deep2(file, history)

    if non_rooted_products:
        reference_rels: set[ifcopenshell.entity_instance] = set()
        for product in non_rooted_products:
            rels = getattr(product, "HasExternalReferences", None)
            if rels is None:
                rels = getattr(product, "HasExternalReference", [])
            reference_rels.update(rels)

        reference_rels = {rel for rel in reference_rels if rel.RelatingReference == settings["reference"]}
        for rel in reference_rels:
            related_objects = set(rel.RelatedResourceObjects) - non_rooted_products
            if related_objects:
                rel.RelatedResourceObjects = list(related_objects)
            else:
                file.remove(rel)

    # TODO: we only handle lightweight classifications here
    referenced_elements = ifcopenshell.util.element.get_referenced_elements(settings["reference"])
    if not referenced_elements:
        file.remove(settings["reference"])
