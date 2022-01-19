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
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "related_object": None,
            "relating_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        nests = None
        if self.settings["related_object"].Nests:
            nests = self.settings["related_object"].Nests[0]

        is_nested_by = None
        for rel in self.settings["relating_object"].IsNestedBy:
            if rel.is_a("IfcRelNests"):
                is_nested_by = rel
                break

        if nests and nests == is_nested_by:
            return

        if nests:
            related_objects = list(nests.RelatedObjects)
            related_objects.remove(self.settings["related_object"])
            if related_objects:
                nests.RelatedObjects = related_objects
                ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": nests})
            else:
                self.file.remove(nests)

        if is_nested_by:
            related_objects = list(is_nested_by.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            is_nested_by.RelatedObjects = related_objects
            ifcopenshell.api.run("owner.update_owner_history", self.file, **{"element": is_nested_by})
        else:
            is_nested_by = self.file.create_entity(
                "IfcRelNests",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingObject": self.settings["relating_object"],
                }
            )
        return is_nested_by
