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
    def __init__(self, file, recurrence_pattern=None):
        """Unassigns a recurrence pattern

        Note that a recurring task time must have a recurrence pattern, so if
        you remove it, be sure to clean up after yourself.

        :param recurrence_pattern: The IfcRecurrencePattern to remove.
        :type recurrence_pattern: ifcopenshell.entity_instance.entity_instance
        :return: None
        :rtype: None

        Example:

        .. code:: python

            # Let's create a new calendar.
            calendar = ifcopenshell.api.run("sequence.add_work_calendar", model)

            # Let's start defining the times that we work during the week.
            work_time = ifcopenshell.api.run("sequence.add_work_time", model,
                work_calendar=calendar, time_type="WorkingTimes")

            # We create a weekly recurrence
            pattern = ifcopenshell.api.run("sequence.assign_recurrence_pattern", model,
                parent=work_time, recurrence_type="WEEKLY")

            # Change our mind, let's just maintain it whenever we feel like it.
            ifcopenshell.api.run("sequence.unassign_recurrence_pattern", recurrence_pattern=pattern)
        """
        self.file = file
        self.settings = {"recurrence_pattern": recurrence_pattern}

    def execute(self):
        self.file.remove(self.settings["recurrence_pattern"])
