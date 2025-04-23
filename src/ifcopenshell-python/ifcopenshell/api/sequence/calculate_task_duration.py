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
import ifcopenshell.api.sequence
import ifcopenshell.util.date
import ifcopenshell.util.element
from typing import Union


def calculate_task_duration(file: ifcopenshell.file, task: ifcopenshell.entity_instance) -> None:
    """Calculates the task duration based on resource usage

    If a task has labour or equipment resources assigned to it, its duration
    may be parametrically derived from the scheduled work of the resource.
    For example, a labour resource with scheduled work of 10 working days
    and a resource utilisation of 200% (i.e. two labour teams) will imply
    that the task duration is 5 working days.

    If this data is not available, such as if the task has no resources,
    then nothing happens.

    :param task: The IfcTask to calculate the duration for.
    :return: None

    Example:

    .. code:: python

        # Add our own crew
        crew = ifcopenshell.api.resource.add_resource(model, ifc_class="IfcCrewResource")

        # Add some labour to our crew.
        labour = ifcopenshell.api.resource.add_resource(model,
            parent_resource=crew, ifc_class="IfcLaborResource")

        # Labour resource is quantified in terms of time.
        quantity = ifcopenshell.api.resource.add_resource_quantity(model,
            resource=labour, ifc_class="IfcQuantityTime")

        # Store the unit time used in hours
        ifcopenshell.api.resource.edit_resource_quantity(model,
            physical_quantity=quantity, attributes={"TimeValue": 8.0})

        # Let's imagine we've used the resource for 10 days with a
        # utilisation of 200%.
        time = ifcopenshell.api.resource.add_resource_time(model, resource=labour)
        ifcopenshell.api.resource.edit_resource_time(model,
            resource_time=time, attributes={"ScheduleWork": "PT80H", "ScheduleUsage": 2})

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's create a construction task. Note that the predefined type is
        # important to distinguish types of tasks.
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Foundations", identification="A")

        # Assign our resource to the task.
        ifcopenshell.api.sequence.assign_process(model, relating_process=task, related_object=labour)

        # Now we can calculate the task duration based on the resource. This
        # will set task.TaskTime.ScheduleDuration to be P5D.
        ifcopenshell.api.sequence.calculate_task_duration(model, task=task)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(task)


class Usecase:
    file: ifcopenshell.file

    def execute(self, task: ifcopenshell.entity_instance) -> None:
        self.task = task
        self.seconds_per_workday = self.calculate_seconds_per_workday()
        duration = self.calculate_max_resource_usage_duration()
        if duration:
            self.set_task_duration(duration)

    def calculate_seconds_per_workday(self) -> float:
        def get_work_schedule(task):
            for rel in task.HasAssignments or []:
                if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                    return rel.RelatingControl
            for rel in task.Nests or []:
                return get_work_schedule(rel.RelatingObject)

        default_seconds_per_workday = 8 * 60 * 60
        work_schedule = get_work_schedule(self.task)
        if not work_schedule:
            return default_seconds_per_workday
        psets = ifcopenshell.util.element.get_psets(work_schedule)
        if (
            not psets
            or "Pset_WorkControlCommon" not in psets
            or "WorkDayDuration" not in psets["Pset_WorkControlCommon"]
        ):
            return default_seconds_per_workday
        work_day_duration = ifcopenshell.util.date.ifc2datetime(psets["Pset_WorkControlCommon"]["WorkDayDuration"])
        return work_day_duration.seconds

    def calculate_max_resource_usage_duration(self) -> float:
        max_duration = 0
        for rel in self.task.OperatesOn or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcConstructionResource"):
                    duration = self.calculate_duration_in_days(related_object)
                    if duration and duration > max_duration:
                        max_duration = duration
        return max_duration

    def calculate_duration_in_days(self, resource: ifcopenshell.entity_instance) -> Union[float, None]:
        def is_hourly_work(schedule_work):
            return "T" in schedule_work

        if not resource.Usage or not resource.Usage.ScheduleWork:
            return
        schedule_usage = resource.Usage.ScheduleUsage or 1
        schedule_duration = ifcopenshell.util.date.ifc2datetime(resource.Usage.ScheduleWork)
        if is_hourly_work(resource.Usage.ScheduleWork):
            schedule_seconds = (schedule_duration.days * 24 * 60 * 60) + schedule_duration.seconds
        else:
            partial_days = schedule_duration.seconds / (24 * 60 * 60)
            schedule_seconds = (schedule_duration.days + partial_days) * self.seconds_per_workday
        return math.ceil((schedule_seconds / self.seconds_per_workday) / schedule_usage)

    def set_task_duration(self, duration: float) -> None:
        if not (task_time := self.task.TaskTime):
            task_time = ifcopenshell.api.sequence.add_task_time(self.file, task=self.task)
        task_time.ScheduleDuration = f"P{duration}D"
