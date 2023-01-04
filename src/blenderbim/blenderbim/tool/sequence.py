# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
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

import bpy
import re
import isodate
import ifcopenshell
import ifcopenshell.util.sequence
import ifcopenshell.util.date
import json
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper
from dateutil import parser
from datetime import datetime
import mathutils


class Sequence(blenderbim.core.tool.Sequence):
    @classmethod
    def get_work_plan_attributes(cls):
        def callback(attributes, prop):
            if "Date" in prop.name or "Time" in prop.name:
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True
            elif prop.name == "Duration" or prop.name == "TotalFloat":
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_duration(prop.string_value)
                return True

        props = bpy.context.scene.BIMWorkPlanProperties
        return blenderbim.bim.helper.export_attributes(props.work_plan_attributes, callback)

    @classmethod
    def load_work_plan_attributes(cls, work_plan):
        def callback(name, prop, data):
            if name in ["CreationDate", "StartTime", "FinishTime"]:
                prop.string_value = "" if prop.is_null else data[name]
                return True

        props = bpy.context.scene.BIMWorkPlanProperties
        props.work_plan_attributes.clear()
        blenderbim.bim.helper.import_attributes2(work_plan, props.work_plan_attributes, callback)

    @classmethod
    def enable_editing_work_plan(cls, work_plan):
        if work_plan:
            bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = work_plan.id()
            bpy.context.scene.BIMWorkPlanProperties.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_plan(cls):
        bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = 0

    @classmethod
    def enable_editing_work_plan_schedules(cls, work_plan):
        if work_plan:
            bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = work_plan.id()
            bpy.context.scene.BIMWorkPlanProperties.editing_type = "SCHEDULES"

    @classmethod
    def get_work_schedule_attributes(cls):
        def callback(attributes, prop):
            if "Date" in prop.name or "Time" in prop.name:
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True
            elif prop.name == "Duration" or prop.name == "TotalFloat":
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_duration(prop.string_value)
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        return blenderbim.bim.helper.export_attributes(props.work_schedule_attributes, callback)

    @classmethod
    def load_work_schedule_attributes(cls, work_schedule):
        def callback(name, prop, data):
            if name in ["CreationDate", "StartTime", "FinishTime"]:
                prop.string_value = "" if prop.is_null else data[name]
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.work_schedule_attributes.clear()
        blenderbim.bim.helper.import_attributes2(work_schedule, props.work_schedule_attributes, callback)

    @classmethod
    def enable_editing_work_schedule(cls, work_schedule):
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = work_schedule.id()
        bpy.context.scene.BIMWorkScheduleProperties.editing_type = "WORK_SCHEDULE"

    @classmethod
    def disable_editing_work_schedule(cls):
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0

    @classmethod
    def enable_editing_work_schedule_tasks(cls, work_schedule):
        if work_schedule:
            props = bpy.context.scene.BIMWorkScheduleProperties
            props.active_work_schedule_id = work_schedule.id()
            props.editing_type = "TASKS"

    @classmethod
    def create_task_tree(cls, work_schedule):
        bpy.context.scene.BIMTaskTreeProperties.tasks.clear()
        props = bpy.context.scene.BIMWorkScheduleProperties
        cls.contracted_tasks = json.loads(props.contracted_tasks)

        related_objects_ids = cls.get_sorted_tasks_ids(ifcopenshell.util.sequence.get_root_tasks(work_schedule))
        for related_object_id in related_objects_ids:
            cls.create_new_task_li(related_object_id, 0)

    @classmethod
    def get_sorted_tasks_ids(cls, tasks):
        cls.sort_keys = {task.id(): cls.get_sort_key(task) for task in tasks}
        related_object_ids = sorted(cls.sort_keys, key=cls.natural_sort_key)
        if bpy.context.scene.BIMWorkScheduleProperties.is_sort_reversed:
            return related_object_ids.reverse()
        return related_object_ids

    @classmethod
    def create_new_task_li(cls, related_object_id, level_index):
        task = tool.Ifc.get().by_id(related_object_id)
        new = bpy.context.scene.BIMTaskTreeProperties.tasks.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in cls.contracted_tasks
        new.level_index = level_index
        if task.IsNestedBy:
            new.has_children = True
            if new.is_expanded:
                for related_object_id in cls.get_sorted_tasks_ids(ifcopenshell.util.sequence.get_nested_tasks(task)):
                    cls.create_new_task_li(related_object_id, level_index + 1)

    @classmethod
    def natural_sort_key(cls, i, _nsre=re.compile("([0-9]+)")):
        s = cls.sort_keys[i]
        return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

    @classmethod
    def get_sort_key(cls, task):
        # Sorting only applies to actual tasks, not the WBS
        for rel in task.IsNestedBy:
            for object in rel.RelatedObjects:
                if object.is_a("IfcTask"):
                    return "0000000000" + (task.Identification or "")
        if not bpy.context.scene.BIMWorkScheduleProperties.sort_column:
            return task.Identification or ""
        column_type, name = bpy.context.scene.BIMWorkScheduleProperties.sort_column.split(".")
        if column_type == "IfcTask":
            return task.Name or ""
        elif column_type == "IfcTaskTime" and task.TaskTime:
            return task.TaskTime.Name or ""
        return task.Identification or ""

    @classmethod
    def load_task_properties(cls, task=None):
        def canonicalise_time(time):
            if not time:
                return "-"
            return time.strftime("%d/%m/%y")

        props = bpy.context.scene.BIMWorkScheduleProperties
        task_props = bpy.context.scene.BIMTaskTreeProperties
        props.is_task_update_enabled = False

        for item in task_props.tasks:
            # if task and item.ifc_definition_id != task.id():
            #     continue
            task = tool.Ifc.get().by_id(item.ifc_definition_id)
            item.name = task.Name or "Unnamed"
            item.identification = task.Identification or "XXX"
            if props.active_task_id:
                item.is_predecessor = props.active_task_id in [rel.RelatedProcess.id() for rel in task.IsPredecessorTo]
                item.is_successor = props.active_task_id in [rel.RelatingProcess.id() for rel in task.IsSuccessorFrom]
            calendar = ifcopenshell.util.sequence.derive_calendar(task)
            if task.HasAssignments:
                for rel in task.HasAssignments:
                    if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkCalendar"):
                        item.calendar = calendar.Name if calendar else ""
            else:
                item.calendar = ""
                item.derived_calendar = calendar.Name if calendar else ""

            if task.TaskTime:
                task_time = task.TaskTime
                item.start = (
                    canonicalise_time(ifcopenshell.util.date.ifc2datetime(task_time.ScheduleStart))
                    if task_time.ScheduleStart
                    else "-"
                )
                item.finish = (
                    canonicalise_time(ifcopenshell.util.date.ifc2datetime(task_time.ScheduleFinish))
                    if task_time.ScheduleFinish
                    else "-"
                )
                item.duration = (
                    isodate.duration_isoformat(ifcopenshell.util.date.ifc2datetime(task_time.ScheduleDuration))
                    if task_time.ScheduleDuration
                    else "-"
                )
            else:
                derived_start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                derived_finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
                item.derived_start = canonicalise_time(derived_start) if derived_start else ""
                item.derived_finish = canonicalise_time(derived_finish) if derived_finish else ""
                if derived_start and derived_finish and calendar:
                    derived_duration = ifcopenshell.util.sequence.count_working_days(
                        derived_start, derived_finish, calendar
                    )
                    item.derived_duration = f"P{derived_duration}D"
                item.start = "-"
                item.finish = "-"
                item.duration = "-"

        bpy.context.scene.BIMWorkScheduleProperties.is_task_update_enabled = True

    @classmethod
    def get_active_work_schedule(cls):
        if not bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
            return None
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id)

    @classmethod
    def get_selected_resource(cls):
        if bpy.context.scene.BIMResourceTreeProperties.resources:
            selected_resource_id = bpy.context.scene.BIMResourceTreeProperties.resources[
                bpy.context.scene.BIMResourceProperties.active_resource_index
            ].ifc_definition_id
            return tool.Ifc.get().by_id(selected_resource_id)

    @classmethod
    def expand_task(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.remove(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def expand_all_tasks(cls):
        bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks = json.dumps([])

    @classmethod
    def contract_all_tasks(cls):
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        for task_item in bpy.context.scene.BIMTaskTreeProperties.tasks:
            if task_item.is_expanded:
                contracted_tasks.append(task_item.ifc_definition_id)
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def contract_task(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.append(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def disable_work_schedule(cls):
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0

    @classmethod
    def disable_selecting_deleted_task(cls):
        props = bpy.context.scene.BIMWorkScheduleProperties
        if props.active_task_id not in [
            task.ifc_definition_id for task in bpy.context.scene.BIMTaskTreeProperties.tasks
        ]:  # Task was deleted
            bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
            bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0

    @classmethod
    def get_checked_tasks(cls):
        return [
            tool.Ifc.get().by_id(task.ifc_definition_id)
            for task in bpy.context.scene.BIMTaskTreeProperties.tasks
            if task.is_selected
        ] or []

    @classmethod
    def get_task_attribute_value(cls, attribute_name):
        return bpy.context.scene.BIMWorkScheduleProperties.task_attributes.get(attribute_name).get_value()

    @classmethod
    def get_active_task(cls):
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_task_id)

    @classmethod
    def get_active_work_time(cls):
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkCalendarProperties.active_work_time_id)

    @classmethod
    def get_task_time(cls, task):
        return task.TaskTime if task.TaskTime else None

    @classmethod
    def load_task_attributes(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_attributes.clear()
        blenderbim.bim.helper.import_attributes2(task, props.task_attributes)

    @classmethod
    def get_selected_products(cls):
        return [
            tool.Ifc.get_entity(obj)
            for obj in bpy.context.selected_objects
            if obj.BIMObjectProperties.ifc_definition_id
        ] or []

    @classmethod
    def enable_editing_task(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.editing_task_type = "ATTRIBUTES"

    @classmethod
    def get_task_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.task_attributes)

    @classmethod
    def load_task_time_attributes(cls, task_time):
        def callback(name, prop, data):
            if prop.data_type == "string":
                duration_props = bpy.context.scene.BIMWorkScheduleProperties.durations_attributes.add()
                duration_props.name = name
                if prop.is_null:
                    for key in duration_props.keys():
                        if key != "name":
                            setattr(duration_props, key, 0)
                    return True
                if name in ["ScheduleDuration", "ActualDuration", "FreeFloat", "TotalFloat"] and data[name]:
                    time_object = ifcopenshell.util.date.ifc2datetime(data[name])
                    for key, value in helper.parse_duration_as_blender_props(time_object).items():
                        duration_props[key] = value
                    return True
            if isinstance(data[name], datetime):
                prop.string_value = "" if prop.is_null else data[name].isoformat()
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_time_attributes.clear()
        props.durations_attributes.clear()
        blenderbim.bim.helper.import_attributes2(task_time, props.task_time_attributes, callback)

    @classmethod
    def enable_editing_task_time(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.active_task_time_id = task.TaskTime.id()
        props.editing_task_type = "TASKTIME"

    @classmethod
    def disable_editing_task(cls):
        bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
        bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0

    @classmethod
    def get_task_time_attributes(cls):
        def callback(attributes, prop):

            if "Start" in prop.name or "Finish" in prop.name or prop.name == "StatusTime":
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True
            elif prop.name in ["ScheduleDuration", "ActualDuration", "FreeFloat", "TotalFloat"]:
                props = bpy.context.scene.BIMWorkScheduleProperties
                if prop.is_null:
                    attributes[prop.name] = None
                    for value in props.durations_attributes.values():
                        value = 0
                    return True
                else:
                    duration_type = getattr(attributes, "DurationType", None)
                    time_split_iso_duration = helper.simplify_duration(
                        props.durations_attributes, duration_type, prop.name
                    )
                    attributes[prop.name] = time_split_iso_duration
                    for value in props.durations_attributes.values():
                        value = 0
                    return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        return blenderbim.bim.helper.export_attributes(props.task_time_attributes, callback)

    @classmethod
    def load_task_resources(cls, resources):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_resources.clear()
        if resources:
            for resource in resources:
                new = props.task_resources.add()
                new.ifc_definition_id = resource.id()
                new.name = resource.Name or "Unnamed"
                new.schedule_usage = resource.Usage.ScheduleUsage or 1 if resource.Usage else 0

    @classmethod
    def load_resources(cls):
        bpy.ops.bim.load_resources()  # remove and refactor

    @classmethod
    def get_task_inputs(cls, task):
        inputs = []
        for rel in task.OperatesOn:
            for object in rel.RelatedObjects:
                if object.is_a("IfcProduct"):
                    inputs.append(object)
        return inputs

    @classmethod
    def load_task_inputs(cls, inputs):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_inputs.clear()
        for input in inputs:
            new = props.task_inputs.add()
            new.ifc_definition_id = input.id()
            new.name = input.Name or "Unnamed"

    @classmethod
    def load_task_outputs(cls, outputs):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_outputs.clear()
        if outputs:
            for output in outputs:
                new = props.task_outputs.add()
                new.ifc_definition_id = output.id()
                new.name = output.Name or "Unnamed"

    @classmethod
    def get_highlighted_task(cls):
        props = bpy.context.scene.BIMWorkScheduleProperties
        task_props = bpy.context.scene.BIMTaskTreeProperties
        return tool.Ifc.get().by_id(task_props.tasks[props.active_task_index].ifc_definition_id)

    @classmethod
    def get_direct_nested_tasks(cls, task):
        return ifcopenshell.util.sequence.get_nested_tasks(task)

    @classmethod
    def get_direct_task_outputs(cls, task):
        return ifcopenshell.util.sequence.get_direct_task_outputs(task)

    @classmethod
    def get_task_outputs(cls, task):
        is_deep = bpy.context.scene.BIMWorkScheduleProperties.is_nested_task_outputs
        return ifcopenshell.util.sequence.get_task_outputs(task, is_deep)

    @classmethod
    def get_task_resources(cls, task):
        resources = []
        for rel in task.OperatesOn:
            for object in rel.RelatedObjects:
                if object.is_a("IfcResource"):
                    resources.append(object)
        return resources

    @classmethod
    def enable_editing_work_calendar_times(cls, work_calendar):
        props = bpy.context.scene.BIMWorkCalendarProperties
        props.active_work_calendar_id = work_calendar.id()
        props.editing_type = "WORKTIMES"

    @classmethod
    def load_work_calendar_attributes(cls, work_calendar):
        props = bpy.context.scene.BIMWorkCalendarProperties
        props.work_calendar_attributes.clear()
        return blenderbim.bim.helper.import_attributes2(work_calendar, props.work_calendar_attributes)

    @classmethod
    def enable_editing_work_calendar(cls, work_calendar):
        bpy.context.scene.BIMWorkCalendarProperties.active_work_calendar_id = work_calendar.id()
        bpy.context.scene.BIMWorkCalendarProperties.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_calendar(cls):
        bpy.context.scene.BIMWorkCalendarProperties.active_work_calendar_id = 0

    @classmethod
    def get_work_calendar_attributes(cls):
        return blenderbim.bim.helper.export_attributes(
            bpy.context.scene.BIMWorkCalendarProperties.work_calendar_attributes
        )

    @classmethod
    def load_work_time_attributes(cls, work_time):
        def callback(name, prop, data):
            if name in ["Start", "Finish"]:
                prop.string_value = "" if prop.is_null else data[name]
                return True

        props = bpy.context.scene.BIMWorkCalendarProperties
        props.work_time_attributes.clear()

        blenderbim.bim.helper.import_attributes2(work_time, props.work_time_attributes, callback)

    @classmethod
    def enable_editing_work_time(cls, work_time):
        def initialise_recurrence_components(props):
            if len(props.day_components) == 0:
                for i in range(0, 31):
                    new = props.day_components.add()
                    new.name = str(i + 1)
            if len(props.weekday_components) == 0:
                for d in ["M", "T", "W", "T", "F", "S", "S"]:
                    new = props.weekday_components.add()
                    new.name = d
            if len(props.month_components) == 0:
                for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                    new = props.month_components.add()
                    new.name = m

        def load_recurrence_pattern_data(work_time, props):
            props.position = 0
            props.interval = 0
            props.occurrences = 0
            props.start_time = ""
            props.end_time = ""
            for component in props.day_components:
                component.is_specified = False
            for component in props.weekday_components:
                component.is_specified = False
            for component in props.month_components:
                component.is_specified = False
            if not work_time.RecurrencePattern:
                return
            recurrence_pattern = work_time.RecurrencePattern
            for attribute in ["Position", "Interval", "Occurrences"]:
                if getattr(recurrence_pattern, attribute):
                    setattr(props, attribute.lower(), getattr(recurrence_pattern, attribute))
            for component in recurrence_pattern.DayComponent or []:
                props.day_components[component - 1].is_specified = True
            for component in recurrence_pattern.WeekdayComponent or []:
                props.weekday_components[component - 1].is_specified = True
            for component in recurrence_pattern.MonthComponent or []:
                props.month_components[component - 1].is_specified = True

        props = bpy.context.scene.BIMWorkCalendarProperties
        initialise_recurrence_components(props)
        load_recurrence_pattern_data(work_time, props)
        props.active_work_time_id = work_time.id()
        props.editing_type = "WORKTIMES"

    @classmethod
    def get_work_time_attributes(cls):
        def callback(attributes, prop):
            if "Start" in prop.name or "Finish" in prop.name:
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True

        props = bpy.context.scene.BIMWorkCalendarProperties
        return blenderbim.bim.helper.export_attributes(props.work_time_attributes, callback)

    @classmethod
    def get_recurrence_pattern_attributes(cls, recurrence_pattern):
        props = bpy.context.scene.BIMWorkCalendarProperties
        attributes = {
            "Interval": props.interval if props.interval > 0 else None,
            "Occurrences": props.occurrences if props.occurrences > 0 else None,
        }
        applicable_data = {
            "DAILY": ["Interval", "Occurrences"],
            "WEEKLY": ["WeekdayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_DAY_OF_MONTH": ["DayComponent", "Interval", "Occurrences"],
            "MONTHLY_BY_POSITION": ["WeekdayComponent", "Position", "Interval", "Occurrences"],
            "BY_DAY_COUNT": ["Interval", "Occurrences"],
            "BY_WEEKDAY_COUNT": ["WeekdayComponent", "Interval", "Occurrences"],
            "YEARLY_BY_DAY_OF_MONTH": ["DayComponent", "MonthComponent", "Interval", "Occurrences"],
            "YEARLY_BY_POSITION": ["WeekdayComponent", "MonthComponent", "Position", "Interval", "Occurrences"],
        }
        if "Position" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["Position"] = props.position if props.position != 0 else None
        if "DayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["DayComponent"] = [i + 1 for i, c in enumerate(props.day_components) if c.is_specified]
        if "WeekdayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["WeekdayComponent"] = [i + 1 for i, c in enumerate(props.weekday_components) if c.is_specified]
        if "MonthComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["MonthComponent"] = [i + 1 for i, c in enumerate(props.month_components) if c.is_specified]
        return attributes

    @classmethod
    def disable_editing_work_time(cls):
        bpy.context.scene.BIMWorkCalendarProperties.active_work_time_id = 0

    @classmethod
    def get_recurrence_pattern_times(cls):
        props = bpy.context.scene.BIMWorkCalendarProperties
        try:
            start_time = parser.parse(props.start_time)
            end_time = parser.parse(props.end_time)
            return start_time, end_time
        except:
            return  # improve UI / refactor to add user hints

    @classmethod
    def reset_time_period(cls):
        bpy.context.scene.BIMWorkCalendarProperties.start_time = ""
        bpy.context.scene.BIMWorkCalendarProperties.end_time = ""

    @classmethod
    def enable_editing_task_calendar(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.editing_task_type = "CALENDAR"

    @classmethod
    def enable_editing_task_sequence(cls, task):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.editing_task_type = "SEQUENCE"

    @classmethod
    def disable_editing_task_time(cls):
        bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
        bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0

    @classmethod
    def load_rel_sequence_attributes(cls, rel_sequence):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.sequence_attributes.clear()
        blenderbim.bim.helper.import_attributes2(rel_sequence, props.sequence_attributes)

    @classmethod
    def enable_editing_rel_sequence_attributes(cls, rel_sequence):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "ATTRIBUTES"

    @classmethod
    def load_lag_time_attributes(cls, lag_time):
        def callback(name, prop, data):
            if name == "LagValue":
                prop = bpy.context.scene.BIMWorkScheduleProperties.lag_time_attributes.add()
                prop.name = name
                prop.is_null = data[name] is None
                prop.is_optional = False
                prop.data_type = "string"
                prop.string_value = (
                    "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name].wrappedValue, "IfcDuration")
                )
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.lag_time_attributes.clear()
        blenderbim.bim.helper.import_attributes2(lag_time, props.lag_time_attributes, callback)

    @classmethod
    def enable_editing_sequence_lag_time(cls, rel_sequence):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "LAG_TIME"

    @classmethod
    def get_rel_sequence_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.sequence_attributes)

    @classmethod
    def disable_editing_rel_sequence(cls):
        bpy.context.scene.BIMWorkScheduleProperties.active_sequence_id = 0

    @classmethod
    def get_lag_time_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.lag_time_attributes)

    @classmethod
    def select_products(cls, products):
        for obj in bpy.context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in [product.id() for product in products]:
                obj.select_set(True)

    @classmethod
    def add_task_column(cls, column_type, name, data_type):
        props = bpy.context.scene.BIMWorkScheduleProperties
        new = props.columns.add()
        new.name = f"{column_type}.{name}"
        new.data_type = data_type

    @classmethod
    def setup_default_task_columns(cls):
        items = [
            {
                "column_type": "IfcTaskTime",
                "name": "ScheduleStart",
            },
            {
                "column_type": "IfcTaskTime",
                "name": "ScheduleFinish",
            },
            {
                "column_type": "IfcTaskTime",
                "name": "ScheduleDuration",
            },
        ]

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.columns.clear()
        for item in items:
            new = props.columns.add()
            new.name = f"{item['column_type']}.{item['name']}"
            new.data_type = "string"

    @classmethod
    def remove_task_column(cls, name):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.columns.remove(props.columns.find(name))

    @classmethod
    def set_task_sort_column(cls, column):
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.sort_column = column

    @classmethod
    def find_related_input_tasks(cls, object):
        related_tasks = []
        for assignment in object.HasAssignments:
            if assignment.is_a("IfcRelAssignsToProcess") and assignment.RelatingProcess.is_a("IfcTask"):
                related_tasks.append(assignment.RelatingProcess)
        return related_tasks

    @classmethod
    def find_related_output_tasks(cls, object):
        related_tasks = []
        for reference in object.ReferencedBy:
            if reference.is_a("IfcRelAssignsToProduct") and reference.RelatedObjects[0].is_a("IfcTask"):
                related_tasks.append(reference.RelatedObjects[0])
        return related_tasks

    @classmethod
    def get_work_schedule(cls, task):
        for rel in task.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        for rel in task.Nests or []:
            return cls.get_work_schedule(rel.RelatingObject)

    @classmethod
    def is_work_schedule_active(cls, work_schedule):
        return (
            True if work_schedule.id() == bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id else False
        )

    @classmethod
    def highlight_task(cls, task):
        def expand_ancestors(task):
            for rel in task.Nests or []:
                parent_task = rel.RelatingObject if rel.RelatingObject.is_a("IfcTask") else None
                contracted_tasks = json.loads(bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks)
                if parent_task and parent_task.id() in contracted_tasks:
                    contracted_tasks.remove(parent_task.id())
                    bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks = json.dumps(contracted_tasks)
                    expand_ancestors(parent_task)
            work_schedule = cls.get_active_work_schedule()
            cls.create_task_tree(work_schedule)
            cls.load_task_properties()

        task_props = bpy.context.scene.BIMTaskTreeProperties
        displayed_tasks = [item.ifc_definition_id for item in task_props.tasks]
        if not task.id() in displayed_tasks:
            expand_ancestors(task)
        task_index = [item.ifc_definition_id for item in task_props.tasks].index(task.id()) or 0
        bpy.context.scene.BIMWorkScheduleProperties.active_task_index = task_index

    @classmethod
    def guess_date_range(cls, work_schedule):
        return ifcopenshell.util.sequence.guess_date_range(work_schedule)

    @classmethod
    def update_visualisation_date(cls, start_date, finish_date):
        def canonicalise_time(time):
            if not time:
                return "-"
            return time.strftime("%d/%m/%y")

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.visualisation_start = canonicalise_time(start_date)
        props.visualisation_finish = canonicalise_time(finish_date)

    @classmethod
    def get_animation_bar_tasks(cls):
        return [
            tool.Ifc.get().by_id(item.ifc_definition_id)
            for item in bpy.context.scene.BIMTaskTreeProperties.tasks
            if item.has_bar_visual
        ] or []

    @classmethod
    def create_bars(cls, tasks):
        def set_material(name, r, g, b):
            material = bpy.data.materials.new(name)
            material.use_nodes = True
            material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (r, g, b, 1.0)
            return material

        def get_animation_materials():
            if "color_progress" in bpy.data.materials:
                material_progress = bpy.data.materials["color_progress"]
            else:
                material_progress = set_material("color_progress", 0.0, 1.0, 0.0)
            if "color_full" in bpy.data.materials:
                material_full = bpy.data.materials["color_full"]
            else:
                material_full = set_material("color_full", 1.0, 0.0, 0.0)
            return material_progress, material_full

        vertical_spacing = 0.5
        size_ratio = 1 / 20
        collection = bpy.data.collections.new("Bar Visual")
        bpy.context.scene.collection.children.link(collection)

        lead_bar_thickness = 0.2
        size = 1.0

        def create_task_bar_data(tasks, vertical_spacing):
            props = bpy.context.scene.BIMWorkScheduleProperties
            viz_start = (
                parser.parse(props.visualisation_start, dayfirst=True, fuzzy=True)
                if props.visualisation_start
                else None
            )
            viz_finish = parser.parse(props.visualisation_finish, dayfirst=True, fuzzy=True)

            start_frame = bpy.context.scene.frame_start
            end_frame = bpy.context.scene.frame_end
            total_frames = end_frame - start_frame
            task_data = []

            material_progress, material_full = get_animation_materials()
            for task in tasks:
                task_start_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                finish_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
                if task_start_date and finish_date:
                    duration = viz_finish - viz_start
                    task_start_frame = round(start_frame + (((task_start_date - viz_start) / duration) * total_frames))
                    task_finish_frame = round(start_frame + (((finish_date - viz_start) / duration) * total_frames))
                    data = {
                        "Name": task.Name if task.Name else "Unnamed",
                        "StartDate": task_start_date,
                        "FinishDate": finish_date,
                        "Start_frame": task_start_frame,
                        "Finish_frame": task_finish_frame,
                        "bar": None,
                    }
                    bar = add_bar(
                        size=1, material=material_progress, vertical_spacing=vertical_spacing, task=data, animate=True
                    )
                    color_progress = bpy.context.scene.BIMAnimationProperties.color_progress
                    bar.color = (color_progress.r, color_progress.g, color_progress.b, 1.0)

                    bar2 = add_bar(
                        size=1, material=material_full, vertical_spacing=vertical_spacing, task=data, animate=False
                    )
                    color_full = bpy.context.scene.BIMAnimationProperties.color_full
                    bar2.color = (color_full.r, color_full.g, color_full.b, 1.0)

                    bar_size = (data["Finish_frame"] - data["Start_frame"]) * size_ratio
                    bar2.scale = (lead_bar_thickness, bar_size, 1)

                    shift_object(bar2, x=-((size + lead_bar_thickness) / 2))

                    start_text = add_text(
                        data["StartDate"].strftime("%d/%m/%y"), 0, "RIGHT", vertical_spacing, collection
                    )

                    add_text(data["Name"], 0, "LEFT", vertical_spacing, collection)

                    finish_text = add_text(
                        data["FinishDate"].strftime("%d/%m/%y"), bar_size, "LEFT", vertical_spacing, collection
                    )

                    shift_object(start_text, y=-(size + lead_bar_thickness))

                    shift_object(finish_text, y=-(size + lead_bar_thickness))

                    vertical_spacing += 5
                    collection.objects.link(bar)
                    collection.objects.link(bar2)

            return

        def animate_bar(bar, task):
            scale = (1, size_ratio, 1)
            bar.scale = scale
            bar.keyframe_insert(data_path="scale", frame=task["Start_frame"])
            scale2 = (1, (task["Finish_frame"] - task["Start_frame"]) * size_ratio, 1)
            bar.scale = scale2
            bar.keyframe_insert(data_path="scale", frame=task["Finish_frame"])

        def place_bar(bar, vertical_spacing):
            for vertex in bar.data.vertices:
                vertex.co[1] += 0.5
            bpy.ops.transform.rotate(value=1.5708, orient_axis="Z")
            bpy.ops.transform.translate(value=(0, -vertical_spacing, 0), orient_type="GLOBAL")

        def shift_object(obj, x=0.0, y=0.0, z=0.0):
            vec = mathutils.Vector((x, y, z))
            inv = obj.matrix_world.copy()
            inv.invert()
            vec_rot = vec @ inv
            obj.location = obj.location + vec_rot

        def add_text(text, x_position, align, vertical_spacing, collection=None):
            bpy.ops.object.text_add()
            bpy.context.object.data.align_x = align
            bpy.context.object.data.align_y = "CENTER"
            bpy.ops.transform.translate(value=(x_position, -(vertical_spacing - 1), 0), orient_type="GLOBAL")
            bpy.context.object.data.body = text
            if collection:
                collection.objects.link(bpy.context.object)
            return bpy.context.object

        def add_bar(size, material, vertical_spacing, task=None, animate=False):
            bpy.ops.mesh.primitive_plane_add(size=size)
            bpy.context.object.data.materials.append(material)
            place_bar(bpy.context.object, vertical_spacing)
            if task and animate:
                animate_bar(bpy.context.object, task)
            return bpy.context.object

        if tasks:
            data = create_task_bar_data(tasks, vertical_spacing)

    @classmethod
    def enable_editing_task_animation_colors(cls):
        bpy.context.scene.BIMAnimationProperties.is_editing = True

    @classmethod
    def load_task_animation_colors(cls):
        props = bpy.context.scene.BIMAnimationProperties
        if not props.task_colors_components_inputs:
            if tool.Ifc.schema():
                # for attribute in tool.Ifc.schema().declaration_by_name("IfcTask").all_attributes():
                #     if attribute.name() != "PredefinedType":
                #         continue
                #     task_types = ifcopenshell.util.attribute.get_enum_items(attribute)
                # return [(e, e, "") for e in enum_items]
                groups = {
                    "CREATION": {
                        "PredefinedType": ["CONSTRUCTION", "INSTALLATION"],
                        "Color": (0.0, 1.0, 0.0),
                    },
                    "DESTRUCTION": {
                        "PredefinedType": ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"],
                        "Color": (1.0, 0.0, 0.0),
                    },
                    "MOVEMENT_FROM": {
                        "PredefinedType": ["LOGISTIC", "MOVE"],
                        "Color": (1.0, 0.5, 0.0),
                    },
                    "MOVEMENT_TO": {
                        "PredefinedType": ["LOGISTIC", "MOVE"],
                        "Color": (1.0, 1.0, 0.0),
                    },
                    "OPERATION": {
                        "PredefinedType": ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"],
                        "Color": (0.0, 0.0, 1.0),
                    },
                    "USERDEFINED": {
                        "PredefinedType": ["USERDEFINED", "NOTDEFINED"],
                        "Color": (0.2, 0.2, 0.2),
                    },
                }
                for group, data in groups.items():
                    for predefined_type in data["PredefinedType"]:
                        if group in ["CREATION", "OPERATION", "MOVEMENT_TO"]:
                            predefined_type_item = props.task_colors_components_outputs.add()
                        elif group in ["MOVEMENT_FROM", "DESTRUCTION"]:
                            predefined_type_item = props.task_colors_components_inputs.add()
                        else:
                            predefined_type_item = props.task_colors_components_outputs.add()
                        predefined_type_item.name = predefined_type
                        predefined_type_item.color = data["Color"]

    @classmethod
    def disable_editing_task_animation_colors(cls):
        bpy.context.scene.BIMAnimationProperties.is_editing = False

    @classmethod
    def get_animation_settings(cls):
        def calculate_total_frames(fps):
            if props.speed_types == "FRAME_SPEED":
                return calculate_using_frames(
                    start,
                    finish,
                    props.speed_animation_frames,
                    isodate.parse_duration(props.speed_real_duration),
                )
            elif props.speed_types == "DURATION_SPEED":
                return calculate_using_duration(
                    start,
                    finish,
                    fps,
                    isodate.parse_duration(props.speed_animation_duration),
                    isodate.parse_duration(props.speed_real_duration),
                )
            elif props.speed_types == "MULTIPLIER_SPEED":
                return calculate_using_multiplier(
                    start,
                    finish,
                    fps,
                    props.speed_multiplier,
                )

        def calculate_using_multiplier(start, finish, fps, multiplier):
            animation_time = (finish - start) / multiplier
            return animation_time.seconds_left() * fps

        def calculate_using_duration(start, finish, fps, animation_duration, real_duration):
            return calculate_using_multiplier(start, finish, fps, real_duration / animation_duration)

        def calculate_using_frames(start, finish, animation_frames, real_duration):
            return ((finish - start) / real_duration) * animation_frames

        props = bpy.context.scene.BIMWorkScheduleProperties
        start = parser.parse(props.visualisation_start, dayfirst=True, fuzzy=True)
        finish = parser.parse(props.visualisation_finish, dayfirst=True, fuzzy=True)
        duration = finish - start
        start_frame = 1
        total_frames = calculate_total_frames(bpy.context.scene.render.fps)
        return {
            "start": start,
            "finish": finish,
            "duration": duration,
            "start_frame": start_frame,
            "total_frames": total_frames,
        }

    @classmethod
    def get_animation_product_frames(cls, work_schedule, settings):
        def preprocess_task(task):
            for subtask in ifcopenshell.util.sequence.get_nested_tasks(task):
                preprocess_task(subtask)
            start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
            finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
            if not start or not finish:
                return
            for output in ifcopenshell.util.sequence.get_task_outputs(task):
                add_product_frame(output.id(), task.PredefinedType, start, finish, "output")
            for input in cls.get_task_inputs(task):
                add_product_frame(input.id(), task.PredefinedType, start, finish, "input")

        def add_product_frame(product_id, type, product_start, product_finish, relationship):
            product_frames.setdefault(product_id, []).append(
                {
                    "type": type,
                    "relationship": relationship,
                    "STARTED": round(
                        settings["start_frame"]
                        + (((product_start - settings["start"]) / settings["duration"]) * settings["total_frames"])
                    ),
                    "COMPLETED": round(
                        settings["start_frame"]
                        + (((product_finish - settings["start"]) / settings["duration"]) * settings["total_frames"])
                    ),
                }
            )

        product_frames = {}
        for root_task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            preprocess_task(root_task)
        return product_frames

    @classmethod
    def animate_objects(cls, settings, frames):
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if obj.animation_data:
                obj.animation_data_clear()
            cls.earliest_frame = None
            product_frames = frames.get(obj.BIMObjectProperties.ifc_definition_id, [])
            for product_frame in product_frames:
                if product_frame["relationship"] == "input":
                    cls.animate_input(obj, settings["start_frame"], product_frame)
                elif product_frame["relationship"] == "output":
                    cls.animate_output(obj, settings["start_frame"], product_frame)
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        bpy.context.scene.frame_start = settings["start_frame"]
        bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"])

    @classmethod
    def animate_input(cls, obj, start_frame, product_frame):
        props = bpy.context.scene.BIMAnimationProperties
        color = props.task_colors_components_inputs[product_frame["type"]].color
        if product_frame["type"] in ["LOGISTIC", "MOVE"]:
            cls.animate_movement_from(obj, start_frame, product_frame, color)
        elif product_frame["type"] in ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"]:
            cls.animate_destruction(obj, start_frame, product_frame, color)
        else:
            cls.animate_consumption(obj, start_frame, product_frame, color)

    @classmethod
    def animate_output(cls, obj, start_frame, product_frame):
        props = bpy.context.scene.BIMAnimationProperties
        color = props.task_colors_components_outputs[product_frame["type"]].color
        if product_frame["type"] in ["CONSTRUCTION", "INSTALLATION", "NOTDEFINED"]:
            cls.animate_creation(obj, start_frame, product_frame, color)
        elif product_frame["type"] in ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"]:
            cls.animate_operation(obj, start_frame, product_frame, color)
        elif product_frame["type"] in ["LOGISTIC", "MOVE"]:
            cls.animate_movement_to(obj, product_frame, color)
        else:
            cls.animate_operation(obj, start_frame, product_frame, color)

    @classmethod
    def animate_destruction(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="color", frame=start_frame)
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_movement_from(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"] - 1)
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_consumption(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"] - 1)
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_creation(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_operation(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_movement_to(cls, obj, start_frame, product_frame, color):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    @classmethod
    def add_text_animation_handler(cls, settings):
        def remove_handler(function):
            bpy.app.handlers.frame_change_post.remove(function)

        def append_handler(function):
            bpy.app.handlers.frame_change_post.append(function)

        def animate_text_handler(scene):
            data = bpy.data.curves.get("Timeline")
            if not data or not bpy.data.objects.get("Timeline"):
                remove_handler(animate_text_handler)
            data.body = get_frame_date(scene, data.BIMDateTextProperties)

        def get_frame_date(scene, props):
            start = parser.parse(props.start, dayfirst=True, fuzzy=True)
            finish = parser.parse(props.finish, dayfirst=True, fuzzy=True)
            duration = finish - start
            frame_date = (((scene.frame_current - props.start_frame) / props.total_frames) * duration) + start
            return frame_date.date().isoformat()

        data = bpy.data.curves.get("Timeline")
        if not data:
            data = bpy.data.curves.new(type="FONT", name="Timeline")
        obj = bpy.data.objects.get("Timeline")
        if not obj:
            obj = bpy.data.objects.new(name="Timeline", object_data=data)
            bpy.context.scene.collection.objects.link(obj)

        obj.data.BIMDateTextProperties.start_frame = settings["start_frame"]
        obj.data.BIMDateTextProperties.total_frames = int(settings["total_frames"])
        obj.data.BIMDateTextProperties.start = bpy.context.scene.BIMWorkScheduleProperties.visualisation_start
        obj.data.BIMDateTextProperties.finish = bpy.context.scene.BIMWorkScheduleProperties.visualisation_finish
        append_handler(animate_text_handler)
