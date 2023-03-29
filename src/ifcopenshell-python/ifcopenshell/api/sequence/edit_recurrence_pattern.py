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
import ifcopenshell.util.sequence


class Usecase:
    def __init__(self, file, recurrence_pattern=None, attributes=None):
        """Edits the attributes of an IfcRecurrencePattern

        For more information about the attributes and data types of an
        IfcRecurrencePattern, consult the IFC documentation.

        :param recurrence_pattern: The IfcRecurrencePattern entity you want to edit
        :type recurrence_pattern: ifcopenshell.entity_instance.entity_instance
        :param attributes: a dictionary of attribute names and values.
        :type attributes: dict, optional
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

            # State that we work from weekdays 1 to 5 (i.e. Monday to Friday)
            ifcopenshell.api.run("sequence.edit_recurrence_pattern", model,
                recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]})
        """
        self.file = file
        self.settings = {"recurrence_pattern": recurrence_pattern, "attributes": attributes or {}}

    def execute(self):
        for name, value in self.settings["attributes"].items():
            setattr(self.settings["recurrence_pattern"], name, value)

        ifcopenshell.util.sequence.is_working_day.cache_clear()
        ifcopenshell.util.sequence.is_calendar_applicable.cache_clear()
