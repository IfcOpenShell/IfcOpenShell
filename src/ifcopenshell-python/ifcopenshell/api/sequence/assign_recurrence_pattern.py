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


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"parent": None, "recurrence_type": "WEEKLY"}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        recurrence = self.file.createIfcRecurrencePattern(
            self.settings["recurrence_type"]
        )

        if self.settings["parent"].is_a("IfcWorkTime"):
            if (
                self.settings["parent"].RecurrencePattern
                and len(
                    self.file.get_inverse(self.settings["parent"].RecurrencePattern)
                )
                == 1
            ):
                self.file.remove(self.settings["parent"].RecurrencePattern)
            self.settings["parent"].RecurrencePattern = recurrence
        elif self.settings["parent"].is_a("IfcTaskTimeRecurring"):
            if len(self.file.get_inverse(self.settings["parent"].Recurrence)) == 1:
                self.file.remove(self.settings["parent"].Recurrence)
            self.settings["parent"].Recurrence = recurrence
        return recurrence
