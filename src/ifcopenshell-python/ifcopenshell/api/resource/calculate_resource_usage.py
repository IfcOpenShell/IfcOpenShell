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

import datetime

import ifcopenshell.api
import ifcopenshell.util.constraint
import ifcopenshell.util.resource
import ifcopenshell.util.sequence


def calculate_resource_usage(file: ifcopenshell.file, resource: ifcopenshell.entity_instance) -> None:
    """Calculates the number of resources required to perform scheduled work on a task.

    :param resource: The IfcConstructionResource to calculate the usage for.
    :return: None
    """

    if ifcopenshell.util.constraint.is_attribute_locked(resource, "Usage.ScheduleUsage"):
        return
    if not resource.Usage or not resource.Usage.ScheduleWork:
        return

    task = ifcopenshell.util.resource.get_task_assignments(resource)
    if not task or not task.TaskTime:
        return

    calendar = ifcopenshell.util.resource.get_calendar(resource)
    work_day = ifcopenshell.util.sequence.get_work_day_duration(task, calendar)
    duration_type = task.TaskTime.DurationType
    day = datetime.timedelta(days=1) if duration_type == "ELAPSEDTIME" else work_day

    task_duration = ifcopenshell.util.sequence.get_work_duration(task.TaskTime.ScheduleDuration, duration_type, day)
    seconds = task_duration.days * day.total_seconds() + task_duration.seconds + task_duration.microseconds / 1e6

    person_hours = ifcopenshell.util.sequence.get_work_duration(resource.Usage.ScheduleWork, "WORKTIME", work_day)
    person_seconds = (
        person_hours.days * work_day.total_seconds() + person_hours.seconds + person_hours.microseconds / 1e6
    )

    required_resources = person_seconds / seconds
    resource.Usage.ScheduleUsage = float(required_resources)
