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
import ifcopenshell.api.sequence
import ifcopenshell.api.resource
import ifcopenshell.util.constraint
import ifcopenshell.util.date
import ifcopenshell.util.sequence
from typing import Any


def edit_task_time(
    file: ifcopenshell.file,
    task_time: ifcopenshell.entity_instance,
    attributes: dict[str, Any],
) -> None:
    """Edits the attributes of an IfcTaskTime

    For more information about the attributes and data types of an
    IfcTaskTime, consult the IFC documentation.

    :param task_time: The IfcTaskTime entity you want to edit
    :type task_time: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Create a task to do formwork
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Formwork", identification="A")

        # Let's say it takes 2 days and starts on the 1st of January, 2000
        time = ifcopenshell.api.sequence.add_task_time(model, task=formwork)
        ifcopenshell.api.sequence.edit_task_time(model,
            task_time=time, attributes={"ScheduleStart": "2000-01-01", "ScheduleDuration": "P2D"})
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {"task_time": task_time, "attributes": attributes}
    return usecase.execute()


class Usecase:
    def execute(self):
        self.task = self.get_task()
        self.calendar = ifcopenshell.util.sequence.derive_calendar(self.task)

        # If the user specifies both an end date and a duration, the duration takes priority
        if (
            self.settings["attributes"].get("ScheduleDuration", None)
            and "ScheduleFinish" in self.settings["attributes"].keys()
        ):
            del self.settings["attributes"]["ScheduleFinish"]

        duration_type = self.settings["attributes"].get("DurationType", self.settings["task_time"].DurationType)
        finish = self.settings["attributes"].get("ScheduleFinish", None)
        if finish:
            if isinstance(finish, str):
                finish = datetime.datetime.fromisoformat(finish)
            self.settings["attributes"]["ScheduleFinish"] = datetime.datetime.combine(
                ifcopenshell.util.sequence.get_soonest_working_day(finish, duration_type, self.calendar),
                datetime.time(17),
            )
        start = self.settings["attributes"].get("ScheduleStart", None)
        if start:
            if isinstance(start, str):
                start = datetime.datetime.fromisoformat(start)
            self.settings["attributes"]["ScheduleStart"] = datetime.datetime.combine(
                ifcopenshell.util.sequence.get_soonest_working_day(start, duration_type, self.calendar),
                datetime.time(9),
            )

        for name, value in self.settings["attributes"].items():
            if value is not None:
                if "Start" in name or "Finish" in name or name == "StatusTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDateTime")
                elif name == "ScheduleDuration" or name == "ActualDuration" or name == "RemainingTime":
                    value = ifcopenshell.util.date.datetime2ifc(value, "IfcDuration")
            setattr(self.settings["task_time"], name, value)

        if (
            "ScheduleDuration" in self.settings["attributes"].keys()
            and self.settings["task_time"].ScheduleDuration
            and self.settings["task_time"].ScheduleStart
        ):
            self.calculate_finish()
        elif self.settings["attributes"].get("ScheduleStart", None) and self.settings["task_time"].ScheduleDuration:
            self.calculate_finish()
        elif self.settings["attributes"].get("ScheduleFinish", None) and self.settings["task_time"].ScheduleStart:
            self.calculate_duration()

        if self.settings["task_time"].ScheduleDuration and (
            "ScheduleStart" in self.settings["attributes"].keys()
            or "ScheduleFinish" in self.settings["attributes"].keys()
            or "ScheduleDuration" in self.settings["attributes"].keys()
        ):
            ifcopenshell.api.sequence.cascade_schedule(self.file, task=self.task)
        if self.settings["task_time"].ScheduleDuration:
            self.handle_resource_calculation()

    def calculate_finish(self):
        finish = ifcopenshell.util.sequence.get_start_or_finish_date(
            ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleStart),
            ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleDuration),
            self.settings["task_time"].DurationType,
            self.calendar,
            date_type="FINISH",
        )
        self.settings["task_time"].ScheduleFinish = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")

    def calculate_duration(self):
        start = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleStart)
        finish = ifcopenshell.util.date.ifc2datetime(self.settings["task_time"].ScheduleFinish)
        current_date = datetime.date(start.year, start.month, start.day)
        finish_date = datetime.date(finish.year, finish.month, finish.day)
        duration = datetime.timedelta(days=1)
        while current_date < finish_date:
            if self.settings["task_time"].DurationType == "ELAPSEDTIME" or not self.calendar:
                duration += datetime.timedelta(days=1)
            elif ifcopenshell.util.sequence.is_working_day(current_date, self.calendar):
                duration += datetime.timedelta(days=1)
            current_date += datetime.timedelta(days=1)
        self.settings["task_time"].ScheduleDuration = ifcopenshell.util.date.datetime2ifc(duration, "IfcDuration")

    def get_task(self) -> ifcopenshell.entity_instance:
        return next(e for e in self.file.get_inverse(self.settings["task_time"]) if e.is_a("IfcTask"))

    def handle_resource_calculation(self):
        resources = ifcopenshell.util.sequence.get_task_resources(self.task, is_deep=False)
        for resource in resources:
            if ifcopenshell.util.constraint.is_attribute_locked(resource, "Usage.ScheduleWork"):
                ifcopenshell.api.resource.calculate_resource_usage(self.file, resource=resource)
            # TODO: If the duration changes, this implies the productivity rate must change to accomModate the new Schedule Work to be calculated.
            # elif ifcopenshell.util.constraint.is_attribute_locked(resource, "Usage.ScheduleUsage"):
            #     ifcopenshell.api.resource.calculate_resource_work(self.file, resource=resource)
