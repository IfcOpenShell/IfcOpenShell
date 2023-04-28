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
    def __init__(self, file, task=None, is_recurring=False):
        """Adds a task time to a task

        Some tasks, such as activities within a work breakdown structure or
        overall maintenance tasks will have time related information. This
        includes start dates, durations, end dates, and possible recurring times
        (especially for maintenance tasks).

        :param task: The task to add time data to.
        :type task: ifcopenshell.entity_instance.entity_instance
        :param is_recurring: Whether or not the time should recur.
        :type is_recurring: bool
        :return: The newly created IfcTaskTime.
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's imagine we are creating a construction schedule.
            schedule = ifcopenshell.api.run("sequence.add_work_schedule", model, name="Construction Schedule A")

            # Create a portion of a work breakdown structure.
            construction = ifcopenshell.api.run("sequence.add_task", model,
                work_schedule=schedule, name="Construction", identification="C")
            superstructure = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=construction, name="Superstructure", identification="C3")
            task = ifcopenshell.api.run("sequence.add_task", model,
                parent_task=superstructure, name="Ground Floor FRP", identification="C3.1")

            # Add time data. Note that time data is blank by default.
            time = ifcopenshell.api.run("sequence.add_task_time", model, task=task)

            # Let's say our task starts on the first of January when everybody
            # is still drunk from the new years celebration, and lasts for 2
            # days. Note we don't need to specify the end date, as that is
            # derived from the start plus the duration. In this simple example,
            # no calendar has been specified, so we are working 24/7. Yikes!
            ifcopenshell.api.run("sequence.edit_task_time", model,
                task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})
        """
        self.file = file
        self.settings = {"task": task, "is_recurring": is_recurring}

    def execute(self):
        if self.settings["is_recurring"]:
            task_time = self.file.create_entity("IfcTaskTimeRecurring")
        else:
            task_time = self.file.create_entity("IfcTaskTime")
        self.settings["task"].TaskTime = task_time
        return task_time
