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
        self.settings = {"name": "Unnamed", "predefined_type": "NOTDEFINED"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        work_calendar = ifcopenshell.api.run(
            "root.create_entity",
            self.file,
            ifc_class="IfcWorkCalendar",
            predefined_type=self.settings["predefined_type"],
            name=self.settings["name"],
        )
        context = self.file.by_type("IfcContext")[0]
        ifcopenshell.api.run(
            "project.assign_declaration", self.file, definition=work_calendar, relating_context=context
        )
        return work_calendar
