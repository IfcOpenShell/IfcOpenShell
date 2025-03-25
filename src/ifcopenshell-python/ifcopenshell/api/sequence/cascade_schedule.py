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
import ifcopenshell.util.date
import ifcopenshell.util.sequence
from ifcopenshell.util.sequence import DURATION_TYPE
from typing import Union, Optional


def cascade_schedule(file: ifcopenshell.file, task: ifcopenshell.entity_instance) -> None:
    """Cascades start and end dates of tasks based on durations

    Given a start task with a start date and duration, the end date, and the
    start and end of all successor tasks with durations may be automatically
    computed.

    Using this automatic computation is recommended is an alternative to
    manually specifying dates. It is useful for doing edits and cascading
    changes.

    Dates can only cascade from predecessor to successors, not backwards.
    Cyclical relationships are invalid and will result in a recursion error
    being raised.

    Note that there may be differences between how different planning
    software calculate start and end dates. Some may consider Monday 5pm to
    be equivalent to be Tuesday 8am, for instance.

    :param task: The start task to begin cascading from.
    :return: None

    Example:

    .. code:: python

        # Define a convenience function to add a task chained to a predecessor
        def add_task(model, name, predecessor, work_schedule):
            # Add a construction task
            task = ifcopenshell.api.sequence.add_task(model,
                work_schedule=work_schedule, name=name, predefined_type="CONSTRUCTION")

            # Give it a time
            task_time = ifcopenshell.api.sequence.add_task_time(model, task=task)

            # Arbitrarily set the task's scheduled time duration to be 1 week
            ifcopenshell.api.sequence.edit_task_time(model, task_time=task_time,
                attributes={"ScheduleStart": datetime.date(2000, 1, 1), "ScheduleDuration": "P1W"})

            # If a predecessor exists, create a finish to start relationship
            if predecessor:
                ifcopenshell.api.sequence.assign_sequence(model,
                    relating_process=predecessor, related_process=task)

            return task

        # Open an existing IFC4 model you have of a building
        model = ifcopenshell.open("/path/to/existing/model.ifc")

        # Create a new construction schedule
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction")

        # Let's imagine a starting task for site establishment.
        task = add_task(model, "Site establishment", None, schedule)
        start_task = task

        # Get all our storeys sorted by elevation ascending.
        storeys = sorted(model.by_type("IfcBuildingStorey"), key=lambda s: get_storey_elevation(s))

        # For each storey ...
        for storey in storeys:

            # Add a construction task to construct that storey, using our convenience function
            task = add_task(model, f"Construct {storey.Name}", task, schedule)

            # Assign all the products in that storey to the task as construction outputs.
            for product in get_decomposition(storey):
                ifcopenshell.api.sequence.assign_product(model, relating_product=product, related_object=task)

        # Ask the computer to calculate all the dates for us from the start task.
        # For example, if the first task started on the 1st of January and took a
        # week, the next task will start on the 8th of January. This saves us
        # manually doing date calculations.
        ifcopenshell.api.sequence.cascade_schedule(model, task=start_task)

        # Calculate the critical path and floats.
        ifcopenshell.api.sequence.recalculate_schedule(model, work_schedule=schedule)
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(task)


class Usecase:
    file: ifcopenshell.file

    def execute(self, task: ifcopenshell.entity_instance):
        self.calendar_cache = {}
        self.cascade_task(task, is_first_task=True)

    def cascade_task(
        self,
        task: ifcopenshell.entity_instance,
        is_first_task: bool = False,
        task_sequence: Optional[list[ifcopenshell.entity_instance]] = None,
    ) -> None:
        if task_sequence is None:
            task_sequence = []

        if task in task_sequence:
            print("Warning! Recursive sequence is as follows:")
            for i, debug_task in enumerate(task_sequence):
                if i == 0:
                    print("Starting at", debug_task)
                else:
                    print("... is a predecessor to ...", debug_task)
            print("... which is cyclically a predecessor to ...", task)
            raise RecursionError("Recursive tasks found. Could not cascade schedule.")

        if not task.TaskTime:
            return

        duration = (
            ifcopenshell.util.date.ifc2datetime(task.TaskTime.ScheduleDuration)
            if task.TaskTime.ScheduleDuration
            else datetime.timedelta()
        )

        finishes = []
        starts = []

        for rel in ifcopenshell.util.sequence.get_sequence_assignment(task, "predecessor"):
            predecessor = rel.RelatingProcess
            predecessor_duration = (
                ifcopenshell.util.date.ifc2datetime(predecessor.TaskTime.ScheduleDuration)
                if predecessor.TaskTime and predecessor.TaskTime.ScheduleDuration
                else datetime.timedelta()
            )
            if rel.SequenceType == "FINISH_START":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                days = 0 if predecessor_duration.days == 0 else 1
                duration_type = "WORKTIME"
                if rel.TimeLag:
                    # updated to handle IfcRatioMeasure as a TimeLag value
                    days += (
                        self.get_lag_time_days(rel.TimeLag)
                        if rel.TimeLag.LagValue.is_a("IfcDuration")
                        else predecessor_duration.days * rel.TimeLag.LagValue.wrappedValue
                    )
                    duration_type = rel.TimeLag.DurationType
                if days:
                    starts.append(
                        datetime.datetime.combine(
                            self.offset_date(finish, days, duration_type, self.get_calendar(task)),
                            datetime.time(9),
                        )
                    )
                    starts.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                finish,
                                days,
                                duration_type,
                                self.get_calendar(predecessor),
                            ),
                            datetime.time(9),
                        )
                    )
                else:
                    starts.append(finish)
            elif rel.SequenceType == "START_START":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                if rel.TimeLag:
                    days = (
                        self.get_lag_time_days(rel.TimeLag)
                        if rel.TimeLag.LagValue.is_a("IfcDuration")
                        else predecessor_duration.days * rel.TimeLag.LagValue.wrappedValue
                    )
                    duration_type = rel.TimeLag.DurationType
                    starts.append(self.offset_date(start, days, duration_type, self.get_calendar(task)))
                    starts.append(self.offset_date(start, days, duration_type, self.get_calendar(predecessor)))
                else:
                    starts.append(start)
            elif rel.SequenceType == "FINISH_FINISH":
                finish = self.get_task_time_attribute(predecessor, "ScheduleFinish")
                if not finish:
                    continue
                if rel.TimeLag:
                    days = (
                        self.get_lag_time_days(rel.TimeLag)
                        if rel.TimeLag.LagValue.is_a("IfcDuration")
                        else predecessor_duration.days * rel.TimeLag.LagValue.wrappedValue
                    )
                    duration_type = rel.TimeLag.DurationType
                    finishes.append(self.offset_date(finish, days, duration_type, self.get_calendar(task)))
                    finishes.append(self.offset_date(finish, days, duration_type, self.get_calendar(predecessor)))
                else:
                    finishes.append(finish)
            elif rel.SequenceType == "START_FINISH":
                start = self.get_task_time_attribute(predecessor, "ScheduleStart")
                if not start:
                    continue
                days = -1
                duration_type = "WORKTIME"
                if rel.TimeLag:
                    days += (
                        self.get_lag_time_days(rel.TimeLag)
                        if rel.TimeLag.LagValue.is_a("IfcDuration")
                        else predecessor_duration.days * rel.TimeLag.LagValue.wrappedValue
                    )
                    duration_type = rel.TimeLag.DurationType
                if days or rel.TimeLag:
                    finishes.append(
                        datetime.datetime.combine(
                            self.offset_date(start, days, duration_type, self.get_calendar(task)),
                            datetime.time(17),
                        )
                    )
                    finishes.append(
                        datetime.datetime.combine(
                            self.offset_date(
                                start,
                                days,
                                duration_type,
                                self.get_calendar(predecessor),
                            ),
                            datetime.time(17),
                        )
                    )
                else:
                    finishes.append(start)

        if starts and finishes:
            start = max(starts)
            finish = max(finishes)
            potential_finish = ifcopenshell.util.sequence.get_start_or_finish_date(
                start,
                duration,
                task.TaskTime.DurationType,
                self.get_calendar(task),
                date_type="FINISH",
            )
            if potential_finish > finish:
                start_ifc = ifcopenshell.util.date.datetime2ifc(start, "IfcDateTime")
                if task.TaskTime.ScheduleStart == start_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleStart = start_ifc
                task.TaskTime.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(potential_finish, "IfcDateTime")
            else:
                finish_ifc = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")
                if task.TaskTime.ScheduleFinish == finish_ifc and not is_first_task:
                    return
                task.TaskTime.ScheduleFinish = finish_ifc
                task.TaskTime.ScheduleStart = ifcopenshell.util.date.datetime2ifc(
                    ifcopenshell.util.sequence.get_start_or_finish_date(
                        finish,
                        duration,
                        task.TaskTime.DurationType,
                        self.get_calendar(task),
                        date_type="START",
                    ),
                    "IfcDateTime",
                )
        elif finishes:
            finish = max(finishes)
            finish_ifc = ifcopenshell.util.date.datetime2ifc(finish, "IfcDateTime")
            if task.TaskTime.ScheduleFinish == finish_ifc and not is_first_task:
                return
            task.TaskTime.ScheduleFinish = finish_ifc
            task.TaskTime.ScheduleStart = ifcopenshell.util.date.datetime2ifc(
                ifcopenshell.util.sequence.get_start_or_finish_date(
                    finish,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                    date_type="START",
                ),
                "IfcDateTime",
            )
        elif starts:
            start = max(starts)
            start_ifc = ifcopenshell.util.date.datetime2ifc(start, "IfcDateTime")
            if task.TaskTime.ScheduleStart == start_ifc and not is_first_task:
                return
            task.TaskTime.ScheduleStart = start_ifc
            task.TaskTime.ScheduleFinish = ifcopenshell.util.date.datetime2ifc(
                ifcopenshell.util.sequence.get_start_or_finish_date(
                    start,
                    duration,
                    task.TaskTime.DurationType,
                    self.get_calendar(task),
                    date_type="FINISH",
                ),
                "IfcDateTime",
            )

        for rel in task.IsPredecessorTo:
            self.cascade_task(rel.RelatedProcess, task_sequence=task_sequence + [task])

        for rel in task.IsNestedBy:
            [
                self.cascade_task(nested_task, task_sequence=task_sequence + [task])
                for nested_task in rel.RelatedObjects or []
            ]

    def get_lag_time_days(self, lag_time: ifcopenshell.entity_instance) -> int:
        return ifcopenshell.util.date.ifc2datetime(lag_time.LagValue.wrappedValue).days

    def get_calendar(self, task: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        if task.id() not in self.calendar_cache:
            self.calendar_cache[task.id()] = ifcopenshell.util.sequence.derive_calendar(task)
        return self.calendar_cache[task.id()]

    def offset_date(
        self, date: datetime.datetime, days: int, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance
    ) -> datetime.datetime:
        return ifcopenshell.util.sequence.offset_date(date, datetime.timedelta(days=days), duration_type, calendar)

    def get_task_time_attribute(
        self, task: ifcopenshell.entity_instance, attribute: str
    ) -> Union[datetime.datetime, None]:
        if task.TaskTime:
            value = getattr(task.TaskTime, attribute)
            if value:
                return ifcopenshell.util.date.ifc2datetime(value)
