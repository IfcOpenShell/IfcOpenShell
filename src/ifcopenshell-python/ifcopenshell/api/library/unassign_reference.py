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
import ifcopenshell.util.element
import ifcopenshell.api.owner


def unassign_reference(
    file: ifcopenshell.file,
    reference: ifcopenshell.entity_instance,
    products: list[ifcopenshell.entity_instance],
) -> None:
    """Unassigns a product of products from a reference

    If the product isn't assigned to the reference, nothing will happen.

    :param reference: The IfcLibraryReference to unassign from
    :param products: A list of IfcProduct elements to unassign from the reference
    :return: None

    Example:

    .. code:: python

        library = ifcopenshell.api.library.add_library(model, name="Brickschema")

        # Let's create a reference to a single AHU in our Brickschema dataset
        reference = ifcopenshell.api.library.add_reference(model, library=library)
        ifcopenshell.api.library.edit_reference(model,
            reference=reference, attributes={"Identification": "http://example.org/digitaltwin#AHU01"})

        # Let's assume we have an AHU in our model.
        ahu = ifcopenshell.api.root.create_entity(model,
            ifc_class="IfcUnitaryEquipment", predefined_type="AIRHANDLER")

        # And now assign the IFC model's AHU with its Brickschema counterpart
        ifcopenshell.api.library.assign_reference(model, reference=reference, products=[ahu])

        # Let's change our mind and unassign it.
        ifcopenshell.api.library.unassign_reference(model, reference=reference, products=[ahu])
    """
    # TODO: do we need to support non-ifcroot elements like we do in classification.add_reference?

    reference_rels: set[ifcopenshell.entity_instance] = set()
    products_set = set(products)
    for product in products_set:
        reference_rels.update(product.HasAssociations)

    reference_rels = {
        rel for rel in reference_rels if rel.is_a("IfcRelAssociatesLibrary") and rel.RelatingLibrary == reference
    }

    for rel in reference_rels:
        related_objects = set(rel.RelatedObjects) - products_set
        if related_objects:
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(file, **{"element": rel})
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
