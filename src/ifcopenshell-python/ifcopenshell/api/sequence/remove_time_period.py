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


def remove_time_period(file: ifcopenshell.file, time_period: ifcopenshell.entity_instance) -> None:
    """Removes a time period

    :param time_period: The IfcTimePeriod to remove.
    :type time_period: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's create a new calendar.
        calendar = ifcopenshell.api.sequence.add_work_calendar(model)

        # Let's start defining the times that we work during the week.
        work_time = ifcopenshell.api.sequence.add_work_time(model,
            work_calendar=calendar, time_type="WorkingTimes")

        # We create a weekly recurrence
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(model,
            parent=work_time, recurrence_type="WEEKLY")

        # State that we work from weekdays 1 to 5 (i.e. Monday to Friday)
        ifcopenshell.api.sequence.edit_recurrence_pattern(model,
            recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]})

        # The morning work session, lunch, then the afternoon work session.
        morning = ifcopenshell.api.sequence.add_time_period(model,
            recurrence_pattern=pattern, start_time="09:00", end_time="12:00")
        afternoon = ifcopenshell.api.sequence.add_time_period(model,
            recurrence_pattern=pattern, start_time="13:00", end_time="17:00")

        # Let's take the afternoon off!
        ifcopenshell.api.sequence.remove_time_period(model, time_period=afternoon)
    """
    settings = {"time_period": time_period}

    file.remove(settings["time_period"])
