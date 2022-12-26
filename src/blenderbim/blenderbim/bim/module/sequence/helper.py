# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import isodate
from dateutil import parser
import ifcopenshell.util.date as ifcdateutils


def derive_date(task, attribute_name, date=None, is_earliest=False, is_latest=False):
    if task.TaskTime:
        current_date = (
            ifcdateutils.ifc2datetime(getattr(task.TaskTime, attribute_name))
            if getattr(task.TaskTime, attribute_name)
            else ""
        )
        if current_date:
            return current_date
    for subtask in get_all_nested_tasks(task):
        current_date = derive_date(subtask, attribute_name, date=date, is_earliest=is_earliest, is_latest=is_latest)
        if is_earliest:
            if current_date and (date is None or current_date < date):
                date = current_date
        if is_latest:
            if current_date and (date is None or current_date > date):
                date = current_date
    return date


def parse_datetime(value):
    try:
        return parser.isoparse(value)
    except:
        try:
            return parser.parse(value, dayfirst=True, fuzzy=True)
        except:
            return None


def parse_duration(value):
    try:
        return isodate.parse_duration(value)
    except:
        return None


def canonicalise_time(time):
    if not time:
        return "-"
    return time.strftime("%d/%m/%y")


def get_nested_tasks(task):
    return [related_object for rel in task.IsNestedBy for related_object in rel.RelatedObjects if related_object.is_a("IfcTask")]


def get_parent_task(task):
    return task.Nests[0].RelatingObject if task.Nests and task.Nests[0].RelatingObject.is_a("IfcTask") else None

def get_task_work_schedule(task):
    parent_task = get_parent_task(task)
    if parent_task:
        get_task_work_schedule(parent_task)
    else:
        schedules = [
            rel.RelatingControl
            for rel in task.HasAssignments
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule")
        ]
        print(f"Returning {schedules}")
        return schedules

def get_all_nested_tasks(task):
    for nested_task in get_nested_tasks(task):
        yield nested_task
        yield from get_all_nested_tasks(nested_task)
        
def get_work_schedule_tasks(work_schedule):
    tasks = []
    for root_task in get_root_tasks(work_schedule):
        nested_tasks = get_all_nested_tasks(root_task)
        tasks.extend(nested_tasks)
    return tasks

def get_root_tasks(work_schedule):
    return [obj for rel in work_schedule.Controls for obj in rel.RelatedObjects if obj.is_a("IfcTask")]

def get_root_tasks_ids(work_schedule):
    return [obj.id() for rel in work_schedule.Controls for obj in rel.RelatedObjects if obj.is_a("IfcTask")]

def guess_date_range(work_schedule):
    earliest = None
    latest = None
    root_tasks = get_root_tasks(work_schedule)
    tasks_with_assignements = []
    for task in root_tasks:
        if has_task_outputs(task):
            tasks_with_assignements.append(task)
        for sub_task in get_all_nested_tasks(task):
            if has_task_outputs(sub_task):
                tasks_with_assignements.append(sub_task)

    for task in tasks_with_assignements:
        derived_start = derive_date(task, "ScheduleStart", is_earliest=True)
        derived_finish = derive_date(task, "ScheduleFinish", is_latest=True)
        if derived_start and (not earliest or derived_start < earliest):
            earliest = derived_start
        if derived_finish and (not latest or derived_finish > latest):
            latest = derived_finish
    return earliest, latest

def get_direct_task_outputs(task):       
    return [rel.RelatingProduct for rel in task.HasAssignments if rel.is_a("IfcRelAssignsToProduct")]

def get_task_outputs(task, is_deep=False):
    if not is_deep:
        return get_direct_task_outputs(task)
    else:
        nested_tasks = get_all_nested_tasks(task)
        return [output for nested_task in nested_tasks for output in get_direct_task_outputs(nested_task)]

def has_task_outputs(task):
    return len(get_task_outputs(task)) > 0