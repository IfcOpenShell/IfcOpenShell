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


def add_reference(file: ifcopenshell.file, information: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Creates a new reference to a document to assign to products

    A document may be associated with physical products, tasks, cost items,
    and so on. For example, spaces, storeys, and buildings may have a list
    of associated drawings so you can see which drawings (e.g. plans,
    sections, details) are documenting that location. Alternatively,
    equipment may have associated training manuals, operation and
    maintenance manuals or detailed assembly drawings. Resources may be
    training certification required, schedules may have gantt charts or bid
    documents, and so on.

    In order to associate a document with an object, a reference to that
    document needs to be created. It could be a reference to the entire
    document, or a reference to a particular page or chapter. See
    ifcopenshell.api.document.assign_document for more information.

    :param information: The IfcDocumentInformation that the reference will
        be created for
    :type information: ifcopenshell.entity_instance
    :return: The newly created IfcDocumentReference entity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        document = ifcopenshell.api.document.add_information(model)
        ifcopenshell.api.document.edit_information(model,
            information=document,
            attributes={"Identification": "A-GA-6100", "Name": "Overall Plan",
            "Location": "A-GA-6100 - Overall Plan.pdf"})

        # In this case, we don't specify any more information, and so the
        # reference is for the entire document, as opposed to a single page or
        # chapter or section.
        reference = ifcopenshell.api.document.add_reference(model, information=document)

        # Alternatively, we can specify a single section, such as by a
        # subheading code.
        reference2 = ifcopenshell.api.document.add_reference(model, information=document)
        ifcopenshell.api.document.edit_reference(model,
            reference=reference2, attributes={"Identification": "2.1.15"})
    """
    settings = {"information": information}

    if file.schema == "IFC2X3":
        reference = file.create_entity("IfcDocumentReference", ItemReference="X")
        if settings["information"]:
            references = list(settings["information"].DocumentReferences or [])
            references.append(reference)
            settings["information"].DocumentReferences = references
        return reference
    return file.create_entity("IfcDocumentReference", ReferencedDocument=settings["information"], Identification="X")
