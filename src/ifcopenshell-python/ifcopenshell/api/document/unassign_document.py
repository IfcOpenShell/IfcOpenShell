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


def unassign_document(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    document: ifcopenshell.entity_instance,
) -> None:
    """Unassigns a document and an association to the list of products

    :param product: The list of objects that the document reference or information is
        related to.
    :param document: The IfcDocumentReference (typically) or in rare cases
        the IfcDocumentInformation that is associated with the product
    :return: None

    Example:

    .. code:: python

        document = ifcopenshell.api.document.add_information(model)
        ifcopenshell.api.document.edit_information(model,
            information=document,
            attributes={"Identification": "A-GA-6100", "Name": "Overall Plan",
            "Location": "A-GA-6100 - Overall Plan.pdf"})
        reference = ifcopenshell.api.document.add_reference(model, information=document)

        # Let's imagine storey represents an IfcBuildingStorey for the ground floor
        ifcopenshell.api.document.assign_document(model, products=[storey], document=reference)

        # Now let's change our mind and remove the association
        ifcopenshell.api.document.unassign_document(model, products=[storey], document=reference)
    """

    # TODO: do we need to support non-ifcroot elements like we do in classification.add_reference?
    # NOTE: reuses code from `library.un assign_reference`

    reference_rels: set[ifcopenshell.entity_instance] = set()
    products_set = set(products)
    for product in products_set:
        reference_rels.update(product.HasAssociations)

    reference_rels = {
        rel for rel in reference_rels if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument == document
    }

    for rel in reference_rels:
        related_objects = set(rel.RelatedObjects) - products_set
        if related_objects:
            rel.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
