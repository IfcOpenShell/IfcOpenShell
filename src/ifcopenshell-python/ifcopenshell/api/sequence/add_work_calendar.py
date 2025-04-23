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

import ifcopenshell.api.root
import ifcopenshell.api.project


def add_work_calendar(
    file: ifcopenshell.file, name: str = "Unnamed", predefined_type: str = "NOTDEFINED"
) -> ifcopenshell.entity_instance:
    """Add a work calendar

    A work calendar defines when work is allowed to occur and when the
    holidays are. This is a fundamental concept in construction planning.
    Every task in a work schedule will have an associated calendar. Some
    task and resources work 24/7, whereas others work Monday to Friday, or
    5.5 day weeks, etc. This is important, as tasks durations may only occur
    during working times in a work calendar.

    Work calendars can also be used to associate with events, such as
    indicating that during certain days and times of the year, motion
    sensors should turn on the lights, and other smart building controls.

    :param name: The name of the calendar. Typically something like
        "5 Day Working Week" or "24/7".
    :param predefined_type: The type of calendar, typically used to more
        specifically define shifts, such as FIRSTSHIFT, SECONDSHIFT, or
        THIRDSHIFT. Leave as NOTDEFINED for basic calendar usage.
    :return: The newly created IfcWorkCalendar

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Add a root task to represent the construction tasks.
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Construction", identification="C")

        # Let's create a new calendar.
        calendar = ifcopenshell.api.sequence.add_work_calendar(model, name="5 Day Week")

        # Let's start defining the times that we work during the week.
        work_time = ifcopenshell.api.sequence.add_work_time(model,
            work_calendar=calendar, time_type="WorkingTimes")

        # We create a weekly recurrence
        pattern = ifcopenshell.api.sequence.assign_recurrence_pattern(model,
            parent=work_time, recurrence_type="WEEKLY")

        # State that we work from weekdays 1 to 5 (i.e. Monday to Friday), 9am to 5pm
        ifcopenshell.api.sequence.edit_recurrence_pattern(model,
            recurrence_pattern=pattern, attributes={"WeekdayComponent": [1, 2, 3, 4, 5]})
        ifcopenshell.api.sequence.add_time_period(model,
            recurrence_pattern=pattern, start_time="09:00", end_time="17:00")

        # We associate the calendar with the construction root task. All
        # subtasks underneath the construction work task will also inherit
        # this calendar by default (though you can override them).
        ifcopenshell.api.control.assign_control(model, relating_control=calendar, related_object=task)
    """
    work_calendar = ifcopenshell.api.root.create_entity(
        file,
        ifc_class="IfcWorkCalendar",
        predefined_type=predefined_type,
        name=name,
    )
    context = file.by_type("IfcContext")[0]
    ifcopenshell.api.project.assign_declaration(
        file,
        definitions=[work_calendar],
        relating_context=context,
    )
    return work_calendar
