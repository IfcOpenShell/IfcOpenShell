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
import ifcopenshell.api.sequence


def remove_work_time(file: ifcopenshell.file, work_time: ifcopenshell.entity_instance) -> None:
    """Removes a work time

    :param work_time: The IfcWorkTime to remove.
    :return: None

    Example:

    .. code:: python

        # Let's create a new calendar.
        calendar = ifcopenshell.api.sequence.add_work_calendar(model)

        # Let's start defining the times that we work during the week.
        work_time = ifcopenshell.api.sequence.add_work_time(model,
            work_calendar=calendar, time_type="WorkingTimes")

        # And remove it immediately
        ifcopenshell.api.sequence.remove_work_time(model, work_time=work_time)
    """

    # Currently in API recurrence patterns are created during assignment
    # and removed during unassignment, so they are never reused.
    if recurrence_pattern := work_time.RecurrencePattern:
        ifcopenshell.api.sequence.unassign_recurrence_pattern(file, recurrence_pattern)

    file.remove(work_time)
