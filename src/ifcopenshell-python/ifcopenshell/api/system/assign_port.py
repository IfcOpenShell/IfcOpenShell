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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "element": None,
            "port": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.file.schema == "IFC2X3":
            return self.execute_ifc2x3()

        rels = self.settings["element"].IsNestedBy or []

        for rel in rels:
            if self.settings["port"] in rel.RelatedObjects:
                return

        if not rels:
            return self.file.create_entity(
                "IfcRelNests",
                GlobalId=ifcopenshell.guid.new(),
                OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
                RelatedObjects=[self.settings["port"]],
                RelatingObject=self.settings["element"],
            )

        rel = rels[0]
        related_objects = set(rel.RelatedObjects) or set()
        related_objects.add(self.settings["port"])
        rel.RelatedObjects = list(related_objects)
        ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": rel})
        return rel

    def execute_ifc2x3(self):
        for rel in self.settings["element"].HasPorts or []:
            if rel.RelatingPort == self.settings["port"]:
                return
        return self.file.create_entity(
            "IfcRelConnectsPortToElement",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=ifcopenshell.api.run("owner.create_owner_history", self.file),
            RelatingPort=self.settings["port"],
            RelatedElement=self.settings["element"],
        )
