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

import math
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.resource


class Usecase:
    def __init__(self, file, resource=None):
        """Calculates the number of resources required to perform scheduled work on a task.
        """
        self.file = file
        self.settings = {"resource": resource}

    def execute(self):
        if ifcopenshell.util.constraint.is_attribute_locked(self.settings["resource"], "Usage.ScheduleUsage"):
            return
        if (
            not self.settings["resource"].Usage
            or not self.settings["resource"].Usage.ScheduleWork
        ):
            return

        task = ifcopenshell.util.resource.get_task_assignments(
            self.settings["resource"]
        )
        if not task or not task.TaskTime:
            return

        if not task.TaskTime.DurationType or task.TaskTime.DurationType == "WORKTIME":
            hours_per_day = 8
        else:
            hours_per_day = 24

        task_duration = ifcopenshell.util.date.ifc2datetime(
            task.TaskTime.ScheduleDuration
        )
        seconds = task_duration.days * hours_per_day * 60 * 60
        seconds += task_duration.seconds

        person_hours = ifcopenshell.util.date.ifc2datetime(
            self.settings["resource"].Usage.ScheduleWork
        )

        required_resources = person_hours.total_seconds() / seconds
        self.settings["resource"].Usage.ScheduleUsage = float(required_resources)
