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
        """Unassigns a document and a product association

        :param product: The object that the document reference or information is
            related to.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param document: The IfcDocumentReference (typically) or in rare cases
            the IfcDocumentInformation that is associated with the product
        :type document: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

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

            # Now let's change our mind and remove the association
            ifcopenshell.api.run("document.unassign_document", model, product=storey, document=reference)
        """
        self.file = file
        self.settings = {
            "product": product,
            "document": document,
        }

    def execute(self):
        for rel in self.settings["product"].HasAssociations:
            if rel.is_a("IfcRelAssociatesDocument") and rel.RelatingDocument == self.settings["document"]:
                if len(rel.RelatedObjects) == 1:
                    self.file.remove(rel)
                else:
                    rel.RelatedObjects = [o for o in rel.RelatedObjects if o != self.settings["product"]]
