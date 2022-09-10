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
import ifcopenshell


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "work_schedule": None,
            "parent_task": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        task = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcTask",
            name=None,
            predefined_type="NOTDEFINED",
        )
        task.IsMilestone = False
        if self.settings["work_schedule"]:
            self.file.create_entity(
                "IfcRelAssignsToControl",
                **{
                    "GlobalId": ifcopenshell.guid.new(),
                    "OwnerHistory": ifcopenshell.api.run(
                        "owner.create_owner_history", self.file
                    ),
                    "RelatedObjects": [task],
                    "RelatingControl": self.settings["work_schedule"],
                }
            )
        elif self.settings["parent_task"]:
            rel = ifcopenshell.api.run(
                "nest.assign_object",
                self.file,
                related_object=task,
                relating_object=self.settings["parent_task"],
            )
            if self.settings["parent_task"].Identification:
                task.Identification = (
                    self.settings["parent_task"].Identification
                    + "."
                    + str(len(rel.RelatedObjects))
                )
        return task
