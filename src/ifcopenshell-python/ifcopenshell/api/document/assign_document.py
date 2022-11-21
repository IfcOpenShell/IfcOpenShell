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
        self.settings = {
            "product": None,
            "document": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

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
