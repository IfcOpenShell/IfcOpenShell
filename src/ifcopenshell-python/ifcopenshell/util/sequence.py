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
from math import floor
from functools import lru_cache
from typing import Union, Literal, Optional, Iterator


DURATION_TYPE = Literal["ELAPSEDTIME", "WORKTIME", "NOTDEFINED"]
RECURRENCE_TYPE = Literal[
    "BY_DAY_COUNT",
    "BY_WEEKDAY_COUNT",
    "DAILY",
    "MONTHLY_BY_DAY_OF_MONTH",
    "MONTHLY_BY_POSITION",
    "WEEKLY",
    "YEARLY_BY_DAY_OF_MONTH",
    "YEARLY_BY_POSITION",
]


def derive_date(
    task: ifcopenshell.entity_instance,
    attribute_name: str,
    date=None,
    is_earliest: bool = False,
    is_latest: bool = False,
):
    """

    :param task: IfcTask.

    """
    if task.TaskTime:
        current_date = (
            ifcopenshell.util.date.ifc2datetime(getattr(task.TaskTime, attribute_name))
            if getattr(task.TaskTime, attribute_name)
            else ""
        )
        if current_date:
            return current_date
    for subtask in get_all_nested_tasks(task):
        current_date = derive_date(
            subtask,
            attribute_name,
            date=date,
            is_earliest=is_earliest,
            is_latest=is_latest,
        )
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def derive_calendar(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    calendar = get_calendar(task)
    if calendar:
        return calendar
    for rel in task.Nests or []:
        return derive_calendar(rel.RelatingObject)


def get_calendar(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    calendar = [
        rel.RelatingControl
        for rel in task.HasAssignments or []
        if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkCalendar")
    ]
    if calendar:
        return calendar[0]


def count_working_days(start, finish, calendar: ifcopenshell.entity_instance) -> int:
    result = 0
    if start == finish:
        return 0
    current_date = datetime.date(start.year, start.month, start.day)
    finish_date = datetime.date(finish.year, finish.month, finish.day)
    while current_date <= finish_date:
        if calendar and calendar.WorkingTimes and is_working_day(current_date, calendar):
            result += 1
        elif not calendar or not is_calendar_applicable(current_date, calendar):
            result += 1
        current_date += datetime.timedelta(days=1)
    return result


def get_start_or_finish_date(
    start,
    duration,
    duration_type: DURATION_TYPE,
    calendar: ifcopenshell.entity_instance,
    date_type: Literal["START", "FINISH"] = "FINISH",
):
    if not duration.days:
        # Typically a milestone will have zero duration, so the start == finish
        return start
    # We minus 1 because the start day itself is counted as a day
    months = int(getattr(duration, "months", 0))
    years = int(getattr(duration, "years", 0))
    total_duration = duration.days + months * 30 + years * 12 * 30
    duration = datetime.timedelta(days=total_duration - 1)

    if date_type == "START":
        duration = -duration
    result = offset_date(start, duration, duration_type, calendar)
    if date_type == "START":
        return datetime.datetime.combine(result, datetime.time(9))
    return datetime.datetime.combine(result, datetime.time(17))


def offset_date(start, duration, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance):
    current_date = start
    months = getattr(duration, "months", 0)
    years = getattr(duration, "years", 0)

    abs_duration = abs((duration.days + months * 30 + years * 12 * 30))
    date_offset = datetime.timedelta(days=1 if duration.days > 0 else -1)
    while abs_duration > 0:
        if duration_type == "ELAPSEDTIME" or not is_calendar_applicable(current_date, calendar):
            abs_duration -= 1
        elif is_working_day(current_date, calendar):
            abs_duration -= 1
        current_date += date_offset
    if duration.days > 0:
        current_date = get_soonest_working_day(current_date, duration_type, calendar)
    else:
        current_date = get_recent_working_day(current_date, duration_type, calendar)
    return current_date


def get_soonest_working_day(start, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance):
    if duration_type == "ELAPSEDTIME" or not is_calendar_applicable(start, calendar):
        return start
    while not is_working_day(start, calendar):
        if not is_calendar_applicable(start, calendar):
            break
        start += datetime.timedelta(days=1)
    return start


def get_recent_working_day(start, duration_type: DURATION_TYPE, calendar: ifcopenshell.entity_instance):
    if duration_type == "ELAPSEDTIME" or not is_calendar_applicable(start, calendar):
        return start
    while not is_working_day(start, calendar):
        if not is_calendar_applicable(start, calendar):
            break
        start -= datetime.timedelta(days=1)
    return start


@lru_cache(maxsize=None)
def is_working_day(day, calendar: ifcopenshell.entity_instance) -> bool:
    is_working_day = False
    for work_time in calendar.WorkingTimes or []:
        if is_work_time_applicable_to_day(work_time, day):
            is_working_day = True
            break
    if not is_working_day:
        return is_working_day
    for work_time in calendar.ExceptionTimes or []:
        if is_work_time_applicable_to_day(work_time, day):
            is_working_day = False
            break
    return is_working_day


@lru_cache(maxsize=None)
def is_calendar_applicable(day, calendar: ifcopenshell.entity_instance) -> bool:
    if not calendar or not calendar.WorkingTimes:
        return False
    is_applicable = False
    for work_time in calendar.WorkingTimes or []:
        if is_day_in_work_time(day, work_time):
            is_applicable = True
            break
    return is_applicable


def is_day_in_work_time(day, work_time: ifcopenshell.entity_instance) -> bool:
    is_day_in_work_time = True
    if isinstance(day, datetime.datetime):
        day = datetime.date(day.year, day.month, day.day)
    # 4 IfcWorktime Start
    if start := work_time[4]:
        start = ifcopenshell.util.date.ifc2datetime(start)
        if day > start:
            is_day_in_work_time = True
        else:
            is_day_in_work_time = False
    # 5 IfcWorktime Finish
    if finish := work_time[5]:
        finish = ifcopenshell.util.date.ifc2datetime(finish)
        if day < finish:
            is_day_in_work_time = True
        else:
            is_day_in_work_time = False
    return is_day_in_work_time


def is_work_time_applicable_to_day(work_time: ifcopenshell.entity_instance, day) -> bool:
    if not is_day_in_work_time(day, work_time):
        return False
    if not work_time.RecurrencePattern:
        return True

    if isinstance(day, datetime.datetime):
        day = datetime.date(day.year, day.month, day.day)
    recurrence = work_time.RecurrencePattern
    recurrence_type: RECURRENCE_TYPE = recurrence.RecurrenceType
    if recurrence_type == "DAILY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return True
        # 4 IfcWorktime Start
        if not work_time[4]:
            return False
        return False  # TODO
    elif recurrence_type == "WEEKLY":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent
        # 4 IfcWorktime Start
        if not work_time[4]:
            return False
        return False  # TODO
    elif recurrence_type == "MONTHLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence_type == "MONTHLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (day.weekday() + 1) in recurrence.WeekdayComponent and floor(day.day / 7) + 1 == recurrence[
                "Position"
            ]
        return False  # TODO
    elif recurrence_type == "YEARLY_BY_DAY_OF_MONTH":
        if not recurrence.Interval and not recurrence.Occurrences:
            return day.month in recurrence.MonthComponent and day.day in recurrence.DayComponent
        return False  # TODO
    elif recurrence_type == "YEARLY_BY_POSITION":
        if not recurrence.Interval and not recurrence.Occurrences:
            return (
                day.month in recurrence.MonthComponent
                and (day.weekday() + 1) in recurrence.WeekdayComponent
                and floor(day.day / 7) + 1 == recurrence.Position
            )
        return False  # TODO


def get_task_work_schedule(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    parent_task = get_parent_task(task)
    if parent_task:
        return get_task_work_schedule(parent_task) or get_task_work_schedule(task)
    else:
        for rel in task.HasAssignments:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        return None


def get_nested_tasks(task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [object for rel in task.IsNestedBy or [] for object in rel.RelatedObjects if object.is_a("IfcTask")]


def get_parent_task(task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
    nests = task.Nests
    if nests and (obj := nests[0].RelatingObject).is_a("IfcTask"):
        return obj


def get_all_nested_tasks(task: ifcopenshell.entity_instance) -> Iterator[ifcopenshell.entity_instance]:
    for nested_task in get_nested_tasks(task):
        yield nested_task
        yield from get_all_nested_tasks(nested_task)


def get_work_schedule_tasks(work_schedule: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    tasks = []
    for root_task in get_root_tasks(work_schedule):
        nested_tasks = get_all_nested_tasks(root_task)
        tasks.extend(nested_tasks)
    return tasks


def get_root_tasks(work_schedule: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [obj for rel in work_schedule.Controls for obj in rel.RelatedObjects if obj.is_a("IfcTask")]


def get_root_tasks_ids(work_schedule: ifcopenshell.entity_instance) -> list[int]:
    return [obj.id() for rel in work_schedule.Controls for obj in rel.RelatedObjects if obj.is_a("IfcTask")]


def guess_date_range(work_schedule: ifcopenshell.entity_instance):
    earliest = None
    latest = None
    root_tasks = get_root_tasks(work_schedule)
    tasks_with_assignements = []
    for task in root_tasks:
        if has_task_outputs(task) or has_task_inputs(task):
            tasks_with_assignements.append(task)
        for sub_task in get_all_nested_tasks(task):
            if has_task_outputs(sub_task) or has_task_inputs(sub_task):
                tasks_with_assignements.append(sub_task)

    for task in tasks_with_assignements:
        derived_start = derive_date(task, "ScheduleStart", is_earliest=True)
        derived_finish = derive_date(task, "ScheduleFinish", is_latest=True)
        if derived_start and (not earliest or derived_start < earliest):
            earliest = derived_start
        if derived_finish and (not latest or derived_finish > latest):
            latest = derived_finish
    return earliest, latest


def get_direct_task_outputs(task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    return [rel.RelatingProduct for rel in task.HasAssignments if rel.is_a("IfcRelAssignsToProduct")]


def get_task_outputs(task: ifcopenshell.entity_instance, is_deep: bool = False) -> list[ifcopenshell.entity_instance]:
    if not is_deep:
        return get_direct_task_outputs(task)
    else:
        return [output for nested_task in get_all_nested_tasks(task) for output in get_direct_task_outputs(nested_task)]


def get_task_inputs(task: ifcopenshell.entity_instance, is_deep: bool = False) -> list[ifcopenshell.entity_instance]:
    if not is_deep:
        return [
            object
            for rel in task.OperatesOn
            if rel.is_a("IfcRelAssignsToProcess")
            for object in rel.RelatedObjects
            if object.is_a("IfcProduct")
        ]
    else:
        return [
            output
            for nested_task in get_all_nested_tasks(task)
            for output in [
                object
                for rel in nested_task.OperatesOn
                if rel.is_a("IfcRelAssignsToProcess")
                for object in rel.RelatedObjects
                if object.is_a("IfcProduct")
            ]
        ]


def get_task_resources(task: ifcopenshell.entity_instance, is_deep: bool = False) -> list[ifcopenshell.entity_instance]:
    if not is_deep:
        return [
            object
            for rel in task.OperatesOn
            if rel.is_a("IfcRelAssignsToProcess")
            for object in rel.RelatedObjects
            if object.is_a("IfcResource")
        ]
    else:
        return [
            resource
            for nested_task in get_all_nested_tasks(task)
            for resource in [
                object
                for rel in nested_task.OperatesOn
                if rel.is_a("IfcRelAssignsToProcess")
                for object in rel.RelatedObjects
                if object.is_a("IfcResource")
            ]
        ]


def has_task_outputs(task: ifcopenshell.entity_instance) -> bool:
    return len(get_task_outputs(task)) > 0


def has_task_inputs(task: ifcopenshell.entity_instance) -> bool:
    return len(get_task_inputs(task)) > 0


def get_tasks_for_product(
    product: ifcopenshell.entity_instance, schedule: Optional[ifcopenshell.entity_instance] = None
) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
    """
    Get all tasks assigned to or referenced by the given product.

    Args:
        product: An object that is assigned tasks or references tasks.
        schedule: An optional string representing the schedule name to filter tasks by.

    Returns:
        A tuple of two lists:
        - The first list contains all tasks assigned to the product.
        - The second list contains all tasks referenced by the product that are part of the given schedule.
    """
    inputs = [
        assignement.RelatingProcess
        for assignement in product.HasAssignments
        if assignement.is_a("IfcRelAssignsToProcess") and assignement.RelatingProcess.is_a("IfcTask")
    ]
    outputs = [
        obj
        for ref in product.ReferencedBy
        if ref.is_a("IfcRelAssignsToProduct")
        for obj in ref.RelatedObjects
        if obj.is_a("IfcTask")
    ]

    if schedule:
        inputs = [task for task in inputs if get_task_work_schedule(task).id() == schedule.id()]
        outputs = [task for task in outputs if get_task_work_schedule(task).id() == schedule.id()]

    return inputs, outputs


def get_sequence_assignment(task: ifcopenshell.entity_instance, sequence="successor"):
    if sequence == "successor":
        relationship_attr = "IsPredecessorTo"
    elif sequence == "predecessor":
        relationship_attr = "IsSuccessorFrom"
    else:
        return []

    relationship = getattr(task, relationship_attr, None)
    if relationship:
        return relationship

    for rel in task.Nests or []:
        result = get_sequence_assignment(rel.RelatingObject, sequence)
        if result:
            return result

    return []


def get_related_products(
    relating_product: Optional[ifcopenshell.entity_instance] = None,
    related_object: Optional[ifcopenshell.entity_instance] = None,
) -> set[ifcopenshell.entity_instance]:
    """Gets the related products being output by a task

    :param relating_product: One of the products already output by the task.
    :param related_object: The IfcTask that you want to get all the related
        products for.
    :return: A set of IfcProducts output by the IfcTask.

    Example:

    .. code:: python

        # Let's imagine we are creating a construction schedule. All tasks
        # need to be part of a work schedule.
        schedule = ifcopenshell.api.sequence.add_work_schedule(model, name="Construction Schedule A")

        # Let's create a construction task. Note that the predefined type is
        # important to distinguish types of tasks.
        task = ifcopenshell.api.sequence.add_task(model,
            work_schedule=schedule, name="Build wall", identification="A", predefined_type="CONSTRUCTION")

        # Let's say we have a wall somewhere.
        wall = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")

        # Let's construct that wall!
        ifcopenshell.api.sequence.assign_product(relating_product=wall, related_object=task)

        # This will give us a set with that wall in it.
        products = ifcopenshell.util.sequence.get_related_products(related_object=task)
    """

    assert relating_product or related_object, "Either relating_product or related_object must be provided."

    products = set()
    if not related_object and relating_product:
        for reference in relating_product.ReferencedBy:
            if reference.is_a("IfcRelAssignsToProduct"):
                related_object = reference.RelatedObjects[0]

    if related_object:
        assignments = related_object.HasAssignments
        for assignment in assignments:
            if assignment.is_a("IfcRelAssignsToProduct"):
                products.add(assignment.RelatingProduct.id())

    return products
