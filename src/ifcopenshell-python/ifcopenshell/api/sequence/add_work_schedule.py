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
import ifcopenshell.util.date
from datetime import datetime


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "name": "Unnamed",
            "predefined_type": "NOTDEFINED",
            "start_time": datetime.now(),
            "work_plan": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_schedule = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkSchedule",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        work_schedule.CreationDate = ifcopenshell.util.date.datetime2ifc(
            datetime.now(), "IfcDateTime"
        )
        user = ifcopenshell.api.owner.settings.get_user(self.file)
        if user:
            work_schedule.Creators = [user.ThePerson]
        work_schedule.StartTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["start_time"], "IfcDateTime"
        )

        if self.settings["work_plan"]:
            ifcopenshell.api.run(
                "aggregate.assign_object",
                self.file,
                **{
                    "product": work_schedule,
                    "relating_object": self.settings["work_plan"],
                }
            )
        else:
            # TODO: this is an ambiguity by buildingSMART
            # See https://forums.buildingsmart.org/t/is-the-ifcworkschedule-project-declaration-mutually-exclusive-to-aggregation-within-a-relating-ifcworkplan/3510
            context = self.file.by_type("IfcContext")[0]
            ifcopenshell.api.run(
                "project.assign_declaration",
                self.file,
                definition=work_schedule,
                relating_context=context,
            )
        return work_schedule
