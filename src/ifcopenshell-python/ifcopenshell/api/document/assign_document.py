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


def assign_document(
    file: ifcopenshell.file,
    products: list[ifcopenshell.entity_instance],
    document: ifcopenshell.entity_instance,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns a document to a list of products

    An object may be assigned to zero, one, or multiple documents. Almost
    any object or property may be assigned to a document, though typically
    we'd only use it for spaces, types, physical products and schedules.
    Adding a new assignment is typically done using a document reference and
    an object.  IFC technically allows association with a document
    information and an object, but this is not encouraged because it is not
    consistent with other external relationships (such as classification
    systems or libraries).

    :param product: The list of objects to associate the document to. This could be
        almost any sensible object in IFC.
    :param document: The IfcDocumentReference to associate to, or
        alternatively an IfcDocumentInformation, though this is not
        recommended.
    :return: The IfcRelAssociatesDocument relationship
        or `None` if `products` was an empty list or all products were
        already assigned to the `document`.

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
    """

    # TODO: do we need to support non-ifcroot elements like we do in classification.add_reference?
    # NOTE: reuses code from `library.assign_reference`

    referenced_elements = ifcopenshell.util.element.get_referenced_elements(document)
    products_set: set[ifcopenshell.entity_instance] = set(products)
    products_set = products_set - referenced_elements

    if not products_set:
        return

    if file.schema == "IFC2X3":
        rel = next(
            (r for r in file.by_type("IfcRelAssociatesDocument") if r.RelatingDocument == document),
            None,
        )
    else:
        ifc_class = document.is_a()
        if ifc_class == "IfcDocumentReference":
            rel = next(iter(document.DocumentRefForObjects), None)
        elif ifc_class == "IfcDocumentInformation":
            rel = next(iter(document.DocumentInfoForObjects), None)
        else:
            assert False, f"Unexpected document type: {ifc_class}"

    if not rel:
        return file.create_entity(
            "IfcRelAssociatesDocument",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
            RelatedObjects=list(products_set),
            RelatingDocument=document,
        )

    related_objects = set(rel.RelatedObjects) | products_set
    rel.RelatedObjects = list(related_objects)
    ifcopenshell.api.owner.update_owner_history(file, element=rel)
    return rel
