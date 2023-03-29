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
import ifcopenshell.util.sequence
from datetime import datetime
from datetime import timedelta


class Usecase:
    def __init__(self, file, recurrence_pattern=None, start_time=None, end_time=None):
        """Adds a time period to a recurrence pattern

        A recurring time may be an all-day event, or only during certain time
        periods of the day. For example, you might say that every 1st of January
        recurring is a public holiday, which is an all-day event. Alternatively,
        you might say that you work every (i.e. recurringly) Monday to Friday,
        from 9am to 5pm. The 9am to 5pm is the time period.

        There may also be multiple recurrence patterns, such as from 9am to
        12pm, and then another from 1pm to 5pm (to indicate an hour break for
        lunch).

        :param recurrence_pattern: The IfcRecurrencePattern to add the time
            period to. See ifcopenshell.api.sequence.assign_recurrence_pattern.
        :type recurrence_pattern: ifcopenshell.entity_instance.entity_instance
        :param start_time: The start time of the time period, in a format
            compatible with IfcTime, such as an ISO format time string or a
            datetime.time object.
        :type start_time: str,datetime.time
        :param end_time: The end time of the time period, in a format
            compatible with IfcTime, such as an ISO format time string or a
            datetime.time object.
        :type end_time: str,datetime.time
        :return: The newly created IfcTimePeriod
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

            # The morning work session, lunch, then the afternoon work session.
            ifcopenshell.api.run("sequence.add_time_period", model,
                recurrence_pattern=pattern, start_time="09:00", end_time="12:00")
            ifcopenshell.api.run("sequence.add_time_period", model,
                recurrence_pattern=pattern, start_time="13:00", end_time="17:00")
        """
        self.file = file
        self.settings = {
            "recurrence_pattern": recurrence_pattern,
            "start_time": start_time,
            "end_time": end_time,
        }

    def execute(self):
        time_period = self.file.create_entity("IfcTimePeriod")
        time_period.StartTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["start_time"], "IfcTime"
        )
        time_period.EndTime = ifcopenshell.util.date.datetime2ifc(
            self.settings["end_time"], "IfcTime"
        )
        time_periods = list(self.settings["recurrence_pattern"].TimePeriods or [])
        time_periods.append(time_period)
        self.settings["recurrence_pattern"].TimePeriods = time_periods

        ifcopenshell.util.sequence.is_working_day.cache_clear()
        ifcopenshell.util.sequence.is_calendar_applicable.cache_clear()

        return time_period
