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
            "relating_resource": None,
            "related_object": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        if self.settings["related_object"].HasAssignments:
            for assignment in self.settings["related_object"].HasAssignments:
                if (
                    assignment.is_a("IfclRelAssignsToResource")
                    and assignment.RelatingResource
                    == self.settings["relating_resource"]
                ):
                    return

        resource_of = None
        if self.settings["relating_resource"].ResourceOf:
            resource_of = self.settings["relating_resource"].ResourceOf[0]

        if resource_of:
            related_objects = list(resource_of.RelatedObjects)
            related_objects.append(self.settings["related_object"])
            resource_of.RelatedObjects = related_objects
            ifcopenshell.api.run(
                "owner.update_owner_history", self.file, **{"element": resource_of}
            )
        else:
            resource_of = self.file.create_entity(
                "IfcRelAssignsToResource",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", self.file
                    ),
                    "RelatedObjects": [self.settings["related_object"]],
                    "RelatingResource": self.settings["relating_resource"],
                }
            )
        return resource_of
