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
import ifcopenshell.guid
import ifcopenshell.api.owner
from typing import Optional


def add_information(
    file: ifcopenshell.file, parent: Optional[ifcopenshell.entity_instance] = None
) -> ifcopenshell.entity_instance:
    """Adds a new document information to the project

    An IFC document information is a document associated with the project.
    It may be a drawing, specification, schedule, certificate, warranty
    guarantee, manual, contract, and so on. They are often used for drawings
    and facility management purposes.

    A document may also be a subdocument of a larger document, this is
    useful for superseding documents or tracking older versions. The parent
    is considered the latest version and the children are older revisions.

    :param parent: The parent document, if necessary.
    :type parent: ifcopenshell.entity_instance, optional
    :return: The newly created IfcDocumentInformation entity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        document = ifcopenshell.api.document.add_information(model)
        # A document typically has a unique drawing or document name (which
        # follows a coding system depending on the project), as well as a
        # title.  This should match what is shown on the titleblock or title
        # page of the document. At a minimum you'd also want to specify a
        # URI location. The location may be on local, or on a CDE, or any
        # other platform.
        ifcopenshell.api.document.edit_information(model,
            information=document,
            attributes={"Identification": "A-GA-6100", "Name": "Overall Plan",
            "Location": "A-GA-6100 - Overall Plan.pdf"})
    """
    id_attribute = "DocumentId" if file.schema == "IFC2X3" else "Identification"
    information = file.create_entity("IfcDocumentInformation", **{id_attribute: "X", "Name": "Unnamed"})
    if not parent and file.by_type("IfcProject"):
        parent = file.by_type("IfcProject")[0]
    if parent.is_a("IfcProject") or parent.is_a("IfcContext"):
        file.create_entity(
            "IfcRelAssociatesDocument",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
            RelatingDocument=information,
            RelatedObjects=[parent],
        )
    elif parent.is_a("IfcDocumentInformation"):
        if parent.IsPointer:
            rel = parent.IsPointer[0]
            documents = set(rel.RelatedDocuments)
            documents.add(information)
            rel.RelatedDocuments = list(documents)
        else:
            file.create_entity(
                "IfcDocumentInformationRelationship", RelatingDocument=parent, RelatedDocuments=[information]
            )
    return information
