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


def unassign_recurrence_pattern(file: ifcopenshell.file, recurrence_pattern: ifcopenshell.entity_instance) -> None:
    """Unassigns a recurrence pattern

    Note that a recurring task time must have a recurrence pattern, so if
    you remove it, be sure to clean up after this API call
    (e.g. remove IfcTaskTimeRecurring entity
    or assign a different recurrence patern to it
    or replace IfcTaskTimeRecurring with IfcTaskTime).

    :param recurrence_pattern: The IfcRecurrencePattern to remove.
    :return: None

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

        # Change our mind, let's just maintain it whenever we feel like it.
        ifcopenshell.api.sequence.unassign_recurrence_pattern(recurrence_pattern=pattern)
    """
    for time_period in recurrence_pattern.TimePeriods or []:
        file.remove(time_period)
    file.remove(recurrence_pattern)
