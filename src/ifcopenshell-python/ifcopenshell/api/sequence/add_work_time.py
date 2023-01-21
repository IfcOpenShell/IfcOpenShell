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
    def __init__(self, file, work_calendar=None, time_type="WorkingTimes"):
        """Add either working times or holiday times to a calendar

        A calendar defines when work occurs by defining working times and
        holiday times. First, the working times are defined, then the holidays
        may override the working times. For this reason, holidays are also known
        as exception times. For example, you might define the working times as
        every Monday to Friday, then define a few holidays in the year, such as
        the 1st of January. If the 1st of January is on a weekday, it will
        override the work time.

        :param work_calendar: The IfcWorkCalendar to add the work or holiday
            time definition to.
        :type work_calendar: ifcopenshell.entity_instance.entity_instance
        :param time_type: Either WorkingTimes or ExceptionTimes, depending on
            what you want to define.
        :type time_type: str
        :return: The newly created IfcWorkTime
        :rtype: ifcopenshell.entity_instance.entity_instance

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

            # Let's set some holidays
            holidays = ifcopenshell.api.run("sequence.add_work_time", model,
                work_calendar=calendar, time_type="ExceptionTimes")

            # We create a yearly recurrence
            pattern = ifcopenshell.api.run("sequence.assign_recurrence_pattern", model,
                parent=work_time, recurrence_type="YEARLY_BY_DAY_OF_MONTH")

            # The holiday is every 1st of January
            ifcopenshell.api.run("sequence.edit_recurrence_pattern", model,
                recurrence_pattern=pattern, attributes={"DayComponent": [1], "MonthComponent": [1]})
        """
        self.file = file
        self.settings = {"work_calendar": work_calendar, "time_type": time_type}

    def execute(self):
        work_time = self.file.create_entity("IfcWorkTime")
        if self.settings["time_type"] == "WorkingTimes":
            working_times = list(self.settings["work_calendar"].WorkingTimes or [])
            working_times.append(work_time)
            self.settings["work_calendar"].WorkingTimes = working_times
        elif self.settings["time_type"] == "ExceptionTimes":
            exception_times = list(self.settings["work_calendar"].ExceptionTimes or [])
            exception_times.append(work_time)
            self.settings["work_calendar"].ExceptionTimes = exception_times
        return work_time
