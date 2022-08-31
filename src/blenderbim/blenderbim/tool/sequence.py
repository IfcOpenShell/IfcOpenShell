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
from dateutil import parser
import bpy
import re
import isodate
from datetime import datetime
import ifcopenshell
import json
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper


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
        def get_root_tasks_ids(work_schedule):
            related_objects_ids = []
            if work_schedule.Controls:
                for rel in work_schedule.Controls:
                    for obj in rel.RelatedObjects:
                        if obj.is_a("IfcTask"):
                            related_objects_ids.append(obj.id())
            return related_objects_ids

        bpy.context.scene.BIMTaskTreeProperties.tasks.clear()
        props = bpy.context.scene.BIMWorkScheduleProperties
        cls.contracted_tasks = json.loads(props.contracted_tasks)

        related_objects_ids = get_root_tasks_ids(work_schedule)
        if not related_objects_ids:
            return
        cls.sort_keys = {i: cls.get_sort_key(tool.Ifc.get().by_id(i)) for i in related_objects_ids}
        related_objects_ids = sorted(cls.sort_keys, key=cls.natural_sort_key)
        if props.is_sort_reversed:
            related_objects_ids.reverse()
        for related_object_id in related_objects_ids:
            cls.create_new_task_li(related_object_id, 0)

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
                cls.sort_keys = {subtask.id(): cls.get_sort_key(subtask) for subtask in helper.get_nested_tasks(task)}
                related_object_ids = sorted(cls.sort_keys, key=cls.natural_sort_key)
                if bpy.context.scene.BIMWorkScheduleProperties.is_sort_reversed:
                    related_object_ids.reverse()
                for related_object_id in related_object_ids:
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
                derived_start = helper.derive_date(task, "ScheduleStart", is_earliest=True)
                derived_finish = helper.derive_date(task, "ScheduleFinish", is_latest=True)
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
        ]

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
                if name == "ScheduleDuration" and data[name] and isinstance(data[name], str):
                    time_object = ifcopenshell.util.date.ifc2datetime(data[name])
                    minutes = int(round(time_object.seconds / 60 % 60))
                    hours = (time_object.seconds - minutes * 60) / 60 / 60
                    bpy.context.scene.BIMDuration.duration_days = int(time_object.days)
                    bpy.context.scene.BIMDuration.duration_hours = round(hours)
                    bpy.context.scene.BIMDuration.duration_minutes = (
                        minutes  # should consider years, months and seconds.
                    )
                if isinstance(data[name], datetime):
                    prop.string_value = "" if prop.is_null else data[name].isoformat()
                    if name == "ScheduleDuration":
                        bpy.context.scene.BIMDuration.duration_days = data[name].days
                        bpy.context.scene.BIMDuration.duration_hours = round(data[name].seconds / 60 / 60)
                        bpy.context.scene.BIMDuration.duration_minutes = data[name].seconds / 60 % 60
                    return True
                elif isinstance(data[name], isodate.Duration):
                    prop.string_value = (
                        "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name], "IfcDuration")
                    )
                    return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_time_attributes.clear()
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
            elif prop.name == "ScheduleDuration":
                if prop.is_null:
                    return True
                # TODO make this parse PT32 as P4D
                attributes[prop.name] = helper.parse_duration(prop.string_value)
                dprops = bpy.context.scene.BIMDuration
                duration_days = dprops.duration_days if dprops.duration_days else 0
                duration_hours = dprops.duration_hours if dprops.duration_hours else 0
                duration_minutes = dprops.duration_minutes if dprops.duration_minutes else 0
                dprops.duration_days = 0
                dprops.duration_hours = 0
                dprops.duration_minutes = 0
                attributes[prop.name] = helper.parse_duration(f"P{duration_days}DT{duration_hours}H{duration_minutes}M")
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
    def get_task_outputs(cls, task):
        return [rel.RelatingProduct for rel in task.HasAssignments if rel.is_a("IfcRelAssignsToProduct")]

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
    def select_task_products(cls, products):
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
    def get_work_schedule(cls, task):
        for rel in task.HasAssignments or []:
            if rel.is_a("IfcRelAssignsToControl") and rel.RelatingControl.is_a("IfcWorkSchedule"):
                return rel.RelatingControl
        for rel in task.Nests or []:
            return cls.get_work_schedule(rel.RelatingObject)

    @classmethod
    def expand_ancestors(cls, task):
        for rel in task.Nests or []:
            parent_task = rel.RelatingObject if rel.RelatingObject.is_a("IfcTask") else None
            print(parent_task)
            contracted_tasks = json.loads(bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks)
            if parent_task and parent_task.id() in contracted_tasks:
                contracted_tasks.remove(parent_task.id())
                bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks = json.dumps(contracted_tasks)
                cls.expand_ancestors(parent_task)

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
