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
    for subtask in get_nested_tasks(task):
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
    tasks = []
    for rel in task.IsNestedBy:
        for object in rel.RelatedObjects:
            if object.is_a("IfcTask"):
                tasks.append(object)
    return tasks


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
