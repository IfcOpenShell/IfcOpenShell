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


import ifcopenshell.api


class Usecase:
    def __init__(self, file, information=None):
        """Removes a document information

        All references and associations are also removed.

        :param information: The IfcDocumentInformation to remove
        :type information: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Add a document
            document = ifcopenshell.api.run("document.add_information", model)
            # ... and remove it!
            ifcopenshell.api.run("document.remove_information", model, information=document)
        """
        self.file = file
        self.settings = {"information": information}

    def execute(self):
        for reference in self.settings["information"].HasDocumentReferences or []:
            ifcopenshell.api.run("document.remove_reference", self.file, reference=reference)
        for rel in self.settings["information"].IsPointer or []:
            for information in rel.RelatedDocuments:
                ifcopenshell.api.run("document.remove_information", self.file, information=information)
            self.file.remove(rel)
        for rel in self.settings["information"].DocumentInfoForObjects or []:
            self.file.remove(rel)
        self.file.remove(self.settings["information"])
