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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"parent": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        id_attribute = "DocumentId" if self.file.schema == "IFC2X3" else "Identification"
        information = self.file.create_entity(
            "IfcDocumentInformation", **{id_attribute: "X", "Name": "Unnamed"}
        )
        parent = self.settings["parent"]
        if not parent and self.file.by_type("IfcProject"):
            parent = self.file.by_type("IfcProject")[0]
        if parent.is_a("IfcProject") or parent.is_a("IfcContext"):
            self.file.create_entity(
                "IfcRelAssociatesDocument",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
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
                self.file.create_entity(
                    "IfcDocumentInformationRelationship",
                    RelatingDocument=parent,
                    RelatedDocuments=[information]
                )
        return information
