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
import ifcopenshell.api.document
import ifcopenshell.util.element


def remove_information(file: ifcopenshell.file, information: ifcopenshell.entity_instance) -> None:
    """Removes a document information

    All references and associations are also removed.

    :param information: The IfcDocumentInformation to remove
    :type information: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Add a document
        document = ifcopenshell.api.document.add_information(model)
        # ... and remove it!
        ifcopenshell.api.document.remove_information(model, information=document)
    """

    if file.schema == "IFC2X3":
        references = information.DocumentReferences or []
    else:
        references = information.HasDocumentReferences

    for reference in references:
        ifcopenshell.api.document.remove_reference(file, reference=reference)

    for rel in information.IsPointer or []:
        for info in rel.RelatedDocuments:
            ifcopenshell.api.document.remove_information(file, information=info)

    for rel in information.IsPointedTo or []:
        if rel.RelatedDocuments == (information,):
            # This relationship is non-rooted
            file.remove(rel)

    if file.schema == "IFC2X3":
        rels = [r for r in file.by_type("IfcRelAssociatesDocument") if r.RelatingDocument == information]
    else:
        rels = information.DocumentInfoForObjects

    for rel in rels:
        history = rel.OwnerHistory
        file.remove(rel)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
    file.remove(information)
