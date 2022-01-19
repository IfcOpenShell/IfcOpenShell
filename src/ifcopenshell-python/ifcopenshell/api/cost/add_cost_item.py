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

import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"cost_schedule": None, "cost_item": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        cost_item = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcCostItem")

        if self.settings["cost_schedule"]:
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run("owner.create_owner_history", self.file),
                    "RelatedObjects": [cost_item],
                    "RelatingControl": self.settings["cost_schedule"],
                }
            )
        elif self.settings["cost_item"]:
            ifcopenshell.api.run(
                "nest.assign_object", self.file, related_object=cost_item, relating_object=self.settings["cost_item"]
            )
        return cost_item
