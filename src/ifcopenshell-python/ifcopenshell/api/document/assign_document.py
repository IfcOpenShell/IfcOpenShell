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


class Usecase:
    def __init__(self, file, product=None, document=None):
        """Assigns a document to a product

        An object may be assigned to zero, one, or multiple documents. Almost
        any object or property may be assigned to a document, though typically
        we'd only use it for spaces, types, physical products and schedules.
        Adding a new assignment is typically done using a document reference and
        an object.  IFC technically allows association with a document
        information and an object, but this is not encouraged because it is not
        consistent with other external relationships (such as classification
        systems or libraries).

        :param product: The object to associate the document to. This could be
            almost any sensible object in IFC.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param document: The IfcDocumentReference to associate to, or
            alternatively an IfcDocumentInformation, though this is not
            recommended.
        :type document: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAssociatesDocument relationship
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            document = ifcopenshell.api.run("document.add_information", model)
            ifcopenshell.api.run("document.edit_information", model,
                information=document,
                attributes={"Identification": "A-GA-6100", "Name": "Overall Plan",
                "Location": "A-GA-6100 - Overall Plan.pdf"})
            reference = ifcopenshell.api.run("document.add_reference", model, information=document)

            # Let's imagine storey represents an IfcBuildingStorey for the ground floor
            ifcopenshell.api.run("document.assign_document", model, product=storey, document=reference)
        """
        self.file = file
        self.settings = {
            "product": product,
            "document": document,
        }

    def execute(self):
        rel = self.get_document_rel()
        related_objects = set(rel.RelatedObjects) if rel.RelatedObjects else set()
        related_objects.add(self.settings["product"])
        rel.RelatedObjects = list(related_objects)

    def get_document_rel(self):
        if self.file.schema == "IFC2X3":
            for rel in self.file.by_type("IfcRelAssociatesDocument"):
                if rel.RelatingDocument == self.settings["document"]:
                    return rel
        else:
            if (
                hasattr(self.settings["document"], "DocumentRefForObjects")
                and self.settings["document"].DocumentRefForObjects
            ):
                return self.settings["document"].DocumentRefForObjects[0]
            elif (
                hasattr(self.settings["document"], "DocumentInfoForObjects")
                and self.settings["document"].DocumentInfoForObjects
            ):
                return self.settings["document"].DocumentInfoForObjects[0]

        return self.file.create_entity(
            "IfcRelAssociatesDocument",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                "RelatingDocument": self.settings["document"],
            }
        )
