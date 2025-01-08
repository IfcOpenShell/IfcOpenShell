# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import bpy
import json
import base64
import pystache
import mathutils
import webbrowser
import ifcopenshell
import ifcopenshell.util.sequence
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.unit
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.helper
from dateutil import parser
from datetime import datetime
from typing import Optional, Any, Union, Literal


class Sequence(bonsai.core.tool.Sequence):

    RELATED_OBJECT_TYPE = Literal["RESOURCE", "PRODUCT", "CONTROL"]

    @classmethod
    def get_work_plan_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.helper as helper

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
        return bonsai.bim.helper.export_attributes(props.work_plan_attributes, callback)

    @classmethod
    def load_work_plan_attributes(cls, work_plan: ifcopenshell.entity_instance) -> None:
        def callback(name, prop, data):
            if name in ["CreationDate", "StartTime", "FinishTime"]:
                prop.string_value = "" if prop.is_null else data[name]
                return True

        props = bpy.context.scene.BIMWorkPlanProperties
        props.work_plan_attributes.clear()
        bonsai.bim.helper.import_attributes2(work_plan, props.work_plan_attributes, callback)

    @classmethod
    def enable_editing_work_plan(cls, work_plan: Union[ifcopenshell.entity_instance, None]) -> None:
        if work_plan:
            bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = work_plan.id()
            bpy.context.scene.BIMWorkPlanProperties.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_plan(cls) -> None:
        bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = 0

    @classmethod
    def enable_editing_work_plan_schedules(cls, work_plan: Union[ifcopenshell.entity_instance, None]) -> None:
        if work_plan:
            bpy.context.scene.BIMWorkPlanProperties.active_work_plan_id = work_plan.id()
            bpy.context.scene.BIMWorkPlanProperties.editing_type = "SCHEDULES"

    @classmethod
    def get_work_schedule_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.helper as helper

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
        return bonsai.bim.helper.export_attributes(props.work_schedule_attributes, callback)

    @classmethod
    def load_work_schedule_attributes(cls, work_schedule: ifcopenshell.entity_instance) -> None:
        def callback(name, prop, data):
            if name in ["CreationDate", "StartTime", "FinishTime"]:
                prop.string_value = "" if prop.is_null else data[name]
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.work_schedule_attributes.clear()
        bonsai.bim.helper.import_attributes2(work_schedule, props.work_schedule_attributes, callback)

    @classmethod
    def enable_editing_work_schedule(cls, work_schedule: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = work_schedule.id()
        bpy.context.scene.BIMWorkScheduleProperties.editing_type = "WORK_SCHEDULE"

    @classmethod
    def disable_editing_work_schedule(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0

    @classmethod
    def enable_editing_work_schedule_tasks(cls, work_schedule: Union[ifcopenshell.entity_instance, None]) -> None:
        if work_schedule:
            props = bpy.context.scene.BIMWorkScheduleProperties
            props.active_work_schedule_id = work_schedule.id()
            props.editing_type = "TASKS"

    @classmethod
    def load_task_tree(cls, work_schedule: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMTaskTreeProperties.tasks.clear()
        props = bpy.context.scene.BIMWorkScheduleProperties
        cls.contracted_tasks = json.loads(props.contracted_tasks)

        related_objects_ids = cls.get_sorted_tasks_ids(ifcopenshell.util.sequence.get_root_tasks(work_schedule))
        for related_object_id in related_objects_ids:
            cls.create_new_task_li(related_object_id, 0)

    @classmethod
    def get_sorted_tasks_ids(cls, tasks: list[ifcopenshell.entity_instance]) -> list[int]:
        def get_sort_key(task):
            # Sorting only applies to actual tasks, not the WBS
            # for rel in task.IsNestedBy:
            #     for object in rel.RelatedObjects:
            #         if object.is_a("IfcTask"):
            #             return "0000000000" + (task.Identification or "")
            column_type, name = bpy.context.scene.BIMWorkScheduleProperties.sort_column.split(".")
            if column_type == "IfcTask":
                return task.get_info(task)[name] or ""
            elif column_type == "IfcTaskTime" and task.TaskTime:
                return task.TaskTime.get_info(task)[name] if task.TaskTime.get_info(task)[name] else ""
            return task.Identification or ""

        def natural_sort_key(i, _nsre=re.compile("([0-9]+)")):
            s = sort_keys[i]
            return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]

        if bpy.context.scene.BIMWorkScheduleProperties.sort_column:
            sort_keys = {task.id(): get_sort_key(task) for task in tasks}
            related_object_ids = sorted(sort_keys, key=natural_sort_key)
        else:
            related_object_ids = [task.id() for task in tasks]
        if bpy.context.scene.BIMWorkScheduleProperties.is_sort_reversed:
            related_object_ids.reverse()
        return related_object_ids

    @classmethod
    def create_new_task_li(cls, related_object_id: int, level_index: int) -> None:
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

    # TODO: task argument is never used?
    @classmethod
    def load_task_properties(cls, task: Optional[ifcopenshell.entity_instance] = None) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        task_props = bpy.context.scene.BIMTaskTreeProperties
        tasks_with_visual_bar = cls.get_task_bar_list()
        props.is_task_update_enabled = False

        for item in task_props.tasks:
            task = tool.Ifc.get().by_id(item.ifc_definition_id)
            item.name = task.Name or "Unnamed"
            item.identification = task.Identification or "XXX"
            item.has_bar_visual = item.ifc_definition_id in tasks_with_visual_bar
            if props.highlighted_task_id:
                item.is_predecessor = props.highlighted_task_id in [
                    rel.RelatedProcess.id() for rel in task.IsPredecessorTo
                ]
                item.is_successor = props.highlighted_task_id in [
                    rel.RelatingProcess.id() for rel in task.IsSuccessorFrom
                ]
            calendar = ifcopenshell.util.sequence.derive_calendar(task)
            if ifcopenshell.util.sequence.get_calendar(task):
                item.calendar = calendar.Name or "Unnamed" if calendar else ""
            else:
                item.calendar = ""
                item.derived_calendar = calendar.Name or "Unnamed" if calendar else ""

            if task.TaskTime and (
                task.TaskTime.ScheduleStart or task.TaskTime.ScheduleFinish or task.TaskTime.ScheduleDuration
            ):
                task_time = task.TaskTime
                item.start = (
                    ifcopenshell.util.date.canonicalise_time(
                        ifcopenshell.util.date.ifc2datetime(task_time.ScheduleStart)
                    )
                    if task_time.ScheduleStart
                    else "-"
                )
                item.finish = (
                    ifcopenshell.util.date.canonicalise_time(
                        ifcopenshell.util.date.ifc2datetime(task_time.ScheduleFinish)
                    )
                    if task_time.ScheduleFinish
                    else "-"
                )
                item.duration = (
                    str(ifcopenshell.util.date.readable_ifc_duration(task_time.ScheduleDuration))
                    if task_time.ScheduleDuration
                    else "-"
                )
            else:
                derived_start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
                derived_finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
                item.derived_start = ifcopenshell.util.date.canonicalise_time(derived_start) if derived_start else ""
                item.derived_finish = ifcopenshell.util.date.canonicalise_time(derived_finish) if derived_finish else ""
                if derived_start and derived_finish:
                    derived_duration = ifcopenshell.util.sequence.count_working_days(
                        derived_start, derived_finish, calendar
                    )
                    item.derived_duration = str(ifcopenshell.util.date.readable_ifc_duration(f"P{derived_duration}D"))
                item.start = "-"
                item.finish = "-"
                item.duration = "-"

        props.is_task_update_enabled = True

    @classmethod
    def get_active_work_schedule(cls) -> Union[ifcopenshell.entity_instance, None]:
        if not bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id:
            return None
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id)

    @classmethod
    def expand_task(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.remove(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def expand_all_tasks(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks = json.dumps([])

    @classmethod
    def contract_all_tasks(cls) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        for task_item in bpy.context.scene.BIMTaskTreeProperties.tasks:
            if task_item.is_expanded:
                contracted_tasks.append(task_item.ifc_definition_id)
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def contract_task(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.append(task.id())
        props.contracted_tasks = json.dumps(contracted_tasks)

    @classmethod
    def disable_work_schedule(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0

    @classmethod
    def disable_selecting_deleted_task(cls) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        if props.active_task_id not in [
            task.ifc_definition_id for task in bpy.context.scene.BIMTaskTreeProperties.tasks
        ]:  # Task was deleted
            bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
            bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0

    @classmethod
    def get_checked_tasks(cls) -> list[ifcopenshell.entity_instance]:
        return [
            tool.Ifc.get().by_id(task.ifc_definition_id)
            for task in bpy.context.scene.BIMTaskTreeProperties.tasks
            if task.is_selected
        ] or []

    @classmethod
    def get_task_attribute_value(cls, attribute_name: str) -> Any:
        return bpy.context.scene.BIMWorkScheduleProperties.task_attributes.get(attribute_name).get_value()

    @classmethod
    def get_active_task(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkScheduleProperties.active_task_id)

    @classmethod
    def get_active_work_time(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_id(bpy.context.scene.BIMWorkCalendarProperties.active_work_time_id)

    @classmethod
    def get_task_time(cls, task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return task.TaskTime or None

    @classmethod
    def load_task_attributes(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_attributes.clear()
        bonsai.bim.helper.import_attributes2(task, props.task_attributes)

    @classmethod
    def enable_editing_task_attributes(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.editing_task_type = "ATTRIBUTES"

    @classmethod
    def get_task_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.task_attributes)

    @classmethod
    def load_task_time_attributes(cls, task_time: ifcopenshell.entity_instance) -> None:
        import bonsai.bim.module.sequence.helper as helper

        def callback(name, prop, data):
            if prop and prop.data_type == "string":
                duration_props = bpy.context.scene.BIMWorkScheduleProperties.durations_attributes.add()
                duration_props.name = name
                if prop.is_null:
                    for key in duration_props.keys():
                        if key != "name":
                            setattr(duration_props, key, 0)
                    return True
                if name in ["ScheduleDuration", "ActualDuration", "FreeFloat", "TotalFloat"] and data[name]:
                    for key, value in helper.parse_duration_as_blender_props(data[name]).items():
                        duration_props[key] = value
                    return True
            if isinstance(data[name], datetime):
                prop.string_value = "" if prop.is_null else data[name].isoformat()
                return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_time_attributes.clear()
        props.durations_attributes.clear()
        bonsai.bim.helper.import_attributes2(task_time, props.task_time_attributes, callback)

    @classmethod
    def enable_editing_task_time(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.active_task_time_id = task.TaskTime.id()
        props.editing_task_type = "TASKTIME"

    @classmethod
    def disable_editing_task(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
        bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        bpy.context.scene.BIMWorkScheduleProperties.editing_task_type = ""

    @classmethod
    def get_task_time_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.helper as helper

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
                    duration_type = attributes["DurationType"] if "DurationType" in attributes else None
                    time_split_iso_duration = helper.blender_props_to_iso_duration(
                        props.durations_attributes, duration_type, prop.name
                    )
                    attributes[prop.name] = time_split_iso_duration
                    for value in props.durations_attributes.values():
                        value = 0
                    return True

        props = bpy.context.scene.BIMWorkScheduleProperties
        return bonsai.bim.helper.export_attributes(props.task_time_attributes, callback)

    @classmethod
    def load_task_resources(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        rprops = bpy.context.scene.BIMResourceProperties
        props.task_resources.clear()
        rprops.is_resource_update_enabled = False
        for resource in cls.get_task_resources(task) or []:
            new = props.task_resources.add()
            new.ifc_definition_id = resource.id()
            new.name = resource.Name or "Unnamed"
            new.schedule_usage = resource.Usage.ScheduleUsage or 0 if resource.Usage else 0
        rprops.is_resource_update_enabled = True

    @classmethod
    def get_task_inputs(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        is_deep = bpy.context.scene.BIMWorkScheduleProperties.show_nested_inputs
        return ifcopenshell.util.sequence.get_task_inputs(task, is_deep)

    @classmethod
    def get_task_outputs(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        is_deep = bpy.context.scene.BIMWorkScheduleProperties.show_nested_outputs
        return ifcopenshell.util.sequence.get_task_outputs(task, is_deep)

    @classmethod
    def are_entities_same_class(cls, entities: list[ifcopenshell.entity_instance]) -> bool:
        if not entities:
            return False
        if len(entities) == 1:
            return True
        first_class = entities[0].is_a()
        for entity in entities:
            if entity.is_a() != first_class:
                return False
        return True

    @classmethod
    def get_task_resources(
        cls, task: Union[ifcopenshell.entity_instance, None]
    ) -> Union[list[ifcopenshell.entity_instance], None]:
        if not task:
            return
        is_deep = bpy.context.scene.BIMWorkScheduleProperties.show_nested_resources
        return ifcopenshell.util.sequence.get_task_resources(task, is_deep)

    @classmethod
    def load_task_inputs(cls, inputs: list[ifcopenshell.entity_instance]) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_inputs.clear()
        for input in inputs:
            new = props.task_inputs.add()
            new.ifc_definition_id = input.id()
            new.name = input.Name or "Unnamed"

    @classmethod
    def load_task_outputs(cls, outputs: list[ifcopenshell.entity_instance]) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.task_outputs.clear()
        if outputs:
            for output in outputs:
                new = props.task_outputs.add()
                new.ifc_definition_id = output.id()
                new.name = output.Name or "Unnamed"

    @classmethod
    def get_highlighted_task(cls) -> Union[ifcopenshell.entity_instance, None]:
        tasks = bpy.context.scene.BIMTaskTreeProperties.tasks
        if len(tasks) and len(tasks) > bpy.context.scene.BIMWorkScheduleProperties.active_task_index:
            return tool.Ifc.get().by_id(
                tasks[bpy.context.scene.BIMWorkScheduleProperties.active_task_index].ifc_definition_id
            )

    @classmethod
    def get_direct_nested_tasks(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.sequence.get_nested_tasks(task)

    @classmethod
    def get_direct_task_outputs(cls, task: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.sequence.get_direct_task_outputs(task)

    @classmethod
    def enable_editing_work_calendar_times(cls, work_calendar: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkCalendarProperties
        props.active_work_calendar_id = work_calendar.id()
        props.editing_type = "WORKTIMES"

    @classmethod
    def load_work_calendar_attributes(cls, work_calendar: ifcopenshell.entity_instance) -> dict[str, Any]:
        props = bpy.context.scene.BIMWorkCalendarProperties
        props.work_calendar_attributes.clear()
        return bonsai.bim.helper.import_attributes2(work_calendar, props.work_calendar_attributes)

    @classmethod
    def enable_editing_work_calendar(cls, work_calendar: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMWorkCalendarProperties.active_work_calendar_id = work_calendar.id()
        bpy.context.scene.BIMWorkCalendarProperties.editing_type = "ATTRIBUTES"

    @classmethod
    def disable_editing_work_calendar(cls) -> None:
        bpy.context.scene.BIMWorkCalendarProperties.active_work_calendar_id = 0

    @classmethod
    def get_work_calendar_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMWorkCalendarProperties.work_calendar_attributes)

    @classmethod
    def load_work_time_attributes(cls, work_time: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkCalendarProperties
        props.work_time_attributes.clear()

        bonsai.bim.helper.import_attributes2(work_time, props.work_time_attributes)

    @classmethod
    def enable_editing_work_time(cls, work_time: ifcopenshell.entity_instance) -> None:
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
    def get_work_time_attributes(cls) -> dict[str, Any]:
        import bonsai.bim.module.sequence.helper as helper

        def callback(attributes, prop):
            if "Start" in prop.name or "Finish" in prop.name:
                if prop.is_null:
                    attributes[prop.name] = None
                    return True
                attributes[prop.name] = helper.parse_datetime(prop.string_value)
                return True

        props = bpy.context.scene.BIMWorkCalendarProperties
        return bonsai.bim.helper.export_attributes(props.work_time_attributes, callback)

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
    def disable_editing_work_time(cls) -> None:
        bpy.context.scene.BIMWorkCalendarProperties.active_work_time_id = 0

    @classmethod
    def get_recurrence_pattern_times(cls) -> Union[tuple[datetime, datetime], None]:
        props = bpy.context.scene.BIMWorkCalendarProperties
        try:
            start_time = parser.parse(props.start_time)
            end_time = parser.parse(props.end_time)
            return start_time, end_time
        except:
            return  # improve UI / refactor to add user hints

    @classmethod
    def reset_time_period(cls) -> None:
        bpy.context.scene.BIMWorkCalendarProperties.start_time = ""
        bpy.context.scene.BIMWorkCalendarProperties.end_time = ""

    @classmethod
    def enable_editing_task_calendar(cls, task: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_task_id = task.id()
        props.editing_task_type = "CALENDAR"

    @classmethod
    def enable_editing_task_sequence(cls) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.editing_task_type = "SEQUENCE"

    @classmethod
    def disable_editing_task_time(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_task_id = 0
        bpy.context.scene.BIMWorkScheduleProperties.active_task_time_id = 0

    @classmethod
    def load_rel_sequence_attributes(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.sequence_attributes.clear()
        bonsai.bim.helper.import_attributes2(rel_sequence, props.sequence_attributes)

    @classmethod
    def enable_editing_rel_sequence_attributes(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "ATTRIBUTES"

    @classmethod
    def load_lag_time_attributes(cls, lag_time: ifcopenshell.entity_instance) -> None:
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
        bonsai.bim.helper.import_attributes2(lag_time, props.lag_time_attributes, callback)

    @classmethod
    def enable_editing_sequence_lag_time(cls, rel_sequence: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.active_sequence_id = rel_sequence.id()
        props.editing_sequence_type = "LAG_TIME"

    @classmethod
    def get_rel_sequence_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.sequence_attributes)

    @classmethod
    def disable_editing_rel_sequence(cls) -> None:
        bpy.context.scene.BIMWorkScheduleProperties.active_sequence_id = 0

    @classmethod
    def get_lag_time_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMWorkScheduleProperties.lag_time_attributes)

    @classmethod
    def select_products(cls, products):
        [obj.select_set(False) for obj in bpy.context.selected_objects]
        for product in products:
            obj = tool.Ifc.get_object(product)
            obj.select_set(True) if obj else None

    @classmethod
    def add_task_column(cls, column_type: str, name: str, data_type: str):
        props = bpy.context.scene.BIMWorkScheduleProperties
        new = props.columns.add()
        new.name = f"{column_type}.{name}"
        new.data_type = data_type

    @classmethod
    def setup_default_task_columns(cls) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.columns.clear()
        default_columns = ["ScheduleStart", "ScheduleFinish", "ScheduleDuration"]
        for item in default_columns:
            new = props.columns.add()
            new.name = f"IfcTaskTime.{item}"
            new.data_type = "string"

    @classmethod
    def remove_task_column(cls, name: str) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.columns.remove(props.columns.find(name))
        if props.sort_column == name:
            props.sort_column = ""

    @classmethod
    def set_task_sort_column(cls, column: str) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.sort_column = column

    @classmethod
    def find_related_input_tasks(cls, product):
        related_tasks = []
        for assignment in product.HasAssignments:
            if assignment.is_a("IfcRelAssignsToProcess") and assignment.RelatingProcess.is_a("IfcTask"):
                related_tasks.append(assignment.RelatingProcess)
        return related_tasks

    @classmethod
    def find_related_output_tasks(cls, product):
        related_tasks = []
        for reference in product.ReferencedBy:
            if reference.is_a("IfcRelAssignsToProduct") and reference.RelatedObjects[0].is_a("IfcTask"):
                related_tasks.append(reference.RelatedObjects[0])
        return related_tasks

    @classmethod
    def get_work_schedule(cls, task: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
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
    def go_to_task(cls, task):
        def get_ancestor_ids(task):
            ids = []
            for rel in task.Nests or []:
                ids.append(rel.RelatingObject.id())
                ids.extend(get_ancestor_ids(rel.RelatingObject))
            return ids

        contracted_tasks = json.loads(bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks)
        for ancestor_id in get_ancestor_ids(task):
            if ancestor_id in contracted_tasks:
                contracted_tasks.remove(ancestor_id)
        bpy.context.scene.BIMWorkScheduleProperties.contracted_tasks = json.dumps(contracted_tasks)

        work_schedule = cls.get_active_work_schedule()
        cls.load_task_tree(work_schedule)
        cls.load_task_properties()

        task_props = bpy.context.scene.BIMTaskTreeProperties
        expanded_tasks = [item.ifc_definition_id for item in task_props.tasks]
        bpy.context.scene.BIMWorkScheduleProperties.active_task_index = expanded_tasks.index(task.id()) or 0

    # TODO: proper typing
    @classmethod
    def guess_date_range(cls, work_schedule: ifcopenshell.entity_instance) -> tuple[Any, Any]:
        return ifcopenshell.util.sequence.guess_date_range(work_schedule)

    @classmethod
    def update_visualisation_date(cls, start_date, finish_date):
        if not (start_date and finish_date):
            return
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.visualisation_start = ifcopenshell.util.date.canonicalise_time(start_date)
        props.visualisation_finish = ifcopenshell.util.date.canonicalise_time(finish_date)

    @classmethod
    def get_animation_bar_tasks(cls) -> list[ifcopenshell.entity_instance]:
        return [tool.Ifc.get().by_id(task_id) for task_id in cls.get_task_bar_list()]

    @classmethod
    def create_bars(cls, tasks):
        full_bar_thickness = 0.2
        size = 1.0
        vertical_spacing = 3.5
        vertical_increment = 0
        size_to_duration_ratio = 1 / 30
        margin = 0.2

        def process_task_data(task, settings):
            task_start_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
            finish_date = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)

            if not (task_start_date and finish_date):
                return
            else:
                total_frames = settings["end_frame"] - settings["start_frame"]
                duration = settings["viz_finish"] - settings["viz_start"]
                task_start_frame = round(
                    settings["start_frame"] + (((task_start_date - settings["viz_start"]) / duration) * total_frames)
                )
                task_finish_frame = round(
                    settings["start_frame"] + (((finish_date - settings["viz_start"]) / duration) * total_frames)
                )
                return {
                    "name": task.Name if task.Name else "Unnamed",
                    "start_date": task_start_date,
                    "finish_date": finish_date,
                    "start_frame": task_start_frame,
                    "finish_frame": task_finish_frame,
                }

        def create_task_bar_data(tasks, vertical_increment, collection):
            props = bpy.context.scene.BIMWorkScheduleProperties
            settings = {
                "viz_start": (
                    parser.parse(props.visualisation_start, dayfirst=True, fuzzy=True)
                    if props.visualisation_start
                    else None
                ),
                "viz_finish": (
                    parser.parse(props.visualisation_finish, dayfirst=True, fuzzy=True)
                    if props.visualisation_finish
                    else None
                ),
                "start_frame": bpy.context.scene.frame_start,
                "end_frame": bpy.context.scene.frame_end,
            }

            material_progress, material_full = get_animation_materials()
            empty = bpy.data.objects.new("collection_origin", None)
            link_collection(empty, collection)
            for task in tasks:
                task_data = process_task_data(task, settings)
                if task_data:
                    position_shift = task_data["start_frame"] * size_to_duration_ratio
                    bar_size = (task_data["finish_frame"] - task_data["start_frame"]) * size_to_duration_ratio

                    color_progress = bpy.context.scene.BIMAnimationProperties.color_progress
                    bar = add_bar(
                        material=material_progress,
                        vertical_increment=vertical_increment,
                        collection=collection,
                        parent=empty,
                        task=task_data,
                        scale=True,
                        color=(color_progress.r, color_progress.g, color_progress.b, 1.0),
                        shift_x=position_shift,
                        name=task_data["name"] + "/Progress Bar",
                    )

                    color_full = bpy.context.scene.BIMAnimationProperties.color_full
                    bar2 = add_bar(
                        material=material_full,
                        vertical_increment=vertical_increment,
                        parent=empty,
                        collection=collection,
                        task=task_data,
                        color=(color_full.r, color_full.g, color_full.b, 1.0),
                        shift_x=position_shift,
                        name=task_data["name"] + "/Full Bar",
                    )
                    bar2.color = (color_full.r, color_full.g, color_full.b, 1.0)

                    bar2.scale = (full_bar_thickness, bar_size, 1)
                    shift_object(bar2, y=((size + full_bar_thickness) / 2))

                    start_text = add_text(
                        task_data["start_date"].strftime("%d/%m/%y"),
                        0,
                        "RIGHT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    start_text.name = task_data["name"] + "/Start Date"
                    shift_object(start_text, x=position_shift - margin, y=-(size + full_bar_thickness))

                    task_text = add_text(
                        task_data["name"],
                        0,
                        "RIGHT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    task_text.name = task_data["name"] + "/Task Name"
                    shift_object(task_text, x=position_shift, y=0.2)
                    finish_text = add_text(
                        task_data["finish_date"].strftime("%d/%m/%y"),
                        bar_size,
                        "LEFT",
                        vertical_increment,
                        parent=empty,
                        collection=collection,
                    )
                    finish_text.name = task_data["name"] + "/Finish Date"
                    shift_object(finish_text, x=position_shift + margin, y=-(size + full_bar_thickness))
                vertical_increment += vertical_spacing
            return empty.select_set(True) if empty else None

        def set_material(name, r, g, b):
            material = bpy.data.materials.new(name)
            material.use_nodes = True
            tool.Blender.get_material_node(material, "BSDF_PRINCIPLED").inputs[0].default_value = (r, g, b, 1.0)
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

        def animate_scale(bar, task):
            scale = (1, size_to_duration_ratio, 1)
            bar.scale = scale
            bar.keyframe_insert(data_path="scale", frame=task["start_frame"])
            scale2 = (1, (task["finish_frame"] - task["start_frame"]) * size_to_duration_ratio, 1)
            bar.scale = scale2
            bar.keyframe_insert(data_path="scale", frame=task["finish_frame"])

        def animate_color(bar, task, color):
            bar.keyframe_insert(data_path="color", frame=task["start_frame"])
            bar.color = color
            bar.keyframe_insert(data_path="color", frame=task["start_frame"] + 1)
            bar.color = color

        def place_bar(bar, vertical_increment):
            for vertex in bar.data.vertices:
                vertex.co[1] += 0.5
            bar.rotation_euler[2] = -1.5708
            shift_object(bar, y=-vertical_increment)

        def shift_object(obj, x=0.0, y=0.0, z=0.0):
            vec = mathutils.Vector((x, y, z))
            inv = obj.matrix_world.copy()
            inv.invert()
            vec_rot = vec @ inv
            obj.location = obj.location + vec_rot

        def link_collection(obj, collection):
            if collection:
                collection.objects.link(obj)
                if obj.name in bpy.context.scene.collection.objects.keys():
                    bpy.context.scene.collection.objects.unlink(obj)
            return obj

        def create_plane(material, collection, vertical_increment):
            x = 0.5
            y = 0.5
            vert = [(-x, -y, 0.0), (x, -y, 0.0), (-x, y, 0.0), (x, y, 0.0)]
            fac = [(0, 1, 3, 2)]
            mesh = bpy.data.meshes.new("PL")
            mesh.from_pydata(vert, [], fac)
            obj = bpy.data.objects.new("PL", mesh)
            obj.data.materials.append(material)
            place_bar(obj, vertical_increment)
            link_collection(obj, collection)
            return obj

        def add_text(text, x_position, align, vertical_increment, parent=None, collection=None):
            data = bpy.data.curves.new(type="FONT", name="Timeline")
            data.align_x = align
            data.align_y = "CENTER"

            data.body = text
            obj = bpy.data.objects.new(name="Unnamed", object_data=data)
            link_collection(obj, collection)
            shift_object(obj, x=x_position, y=-(vertical_increment - 1))
            if parent:
                obj.parent = parent
            return obj

        def add_bar(
            material,
            vertical_increment,
            parent=None,
            collection=None,
            task=None,
            color=False,
            scale=False,
            shift_x=None,
            name=None,
        ):
            plane = create_plane(material, collection, vertical_increment)
            if parent:
                plane.parent = parent
            if color:
                animate_color(plane, task, color)
            if scale:
                animate_scale(plane, task)
            if shift_x:
                shift_object(plane, x=shift_x)
            if name:
                plane.name = name
            return plane

        if "Bar Visual" in bpy.data.collections:
            collection = bpy.data.collections["Bar Visual"]
            for obj in collection.objects:
                bpy.data.objects.remove(obj)

        else:
            collection = bpy.data.collections.new("Bar Visual")
            bpy.context.scene.collection.children.link(collection)

        if tasks:
            create_task_bar_data(tasks, vertical_increment, collection)

    @classmethod
    def has_animation_colors(cls):
        return bpy.context.scene.BIMAnimationProperties.task_output_colors

    @classmethod
    def load_default_animation_color_scheme(cls):
        groups = {
            "CREATION": {
                "PredefinedType": ["CONSTRUCTION", "INSTALLATION"],
                "Color": (0.0, 1.0, 0.0),
            },
            "OPERATION": {
                "PredefinedType": ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"],
                "Color": (0.0, 0.0, 1.0),
            },
            "MOVEMENT_TO": {
                "PredefinedType": ["LOGISTIC", "MOVE"],
                "Color": (1.0, 1.0, 0.0),
            },
            "DESTRUCTION": {
                "PredefinedType": ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"],
                "Color": (1.0, 0.0, 0.0),
            },
            "MOVEMENT_FROM": {
                "PredefinedType": ["LOGISTIC", "MOVE"],
                "Color": (1.0, 0.5, 0.0),
            },
            "USERDEFINED": {
                "PredefinedType": ["USERDEFINED", "NOTDEFINED"],
                "Color": (0.2, 0.2, 0.2),
            },
        }
        props = bpy.context.scene.BIMAnimationProperties
        props.task_output_colors.clear()
        props.task_input_colors.clear()
        for group, data in groups.items():
            for predefined_type in data["PredefinedType"]:
                if group in ["CREATION", "OPERATION", "MOVEMENT_TO"]:
                    predefined_type_item = props.task_output_colors.add()
                elif group in ["MOVEMENT_FROM"]:
                    predefined_type_item = props.task_input_colors.add()
                elif group in ["USERDEFINED", "DESTRUCTION"]:
                    predefined_type_item = props.task_input_colors.add()
                    predefined_type_item2 = props.task_output_colors.add()
                    predefined_type_item2.name = predefined_type
                    predefined_type_item2.color = data["Color"]
                # TO DO: consider cases where users confuses inputs and outputs
                predefined_type_item.name = predefined_type
                predefined_type_item.color = data["Color"]

    @classmethod
    def get_start_date(cls) -> Union[datetime, None]:
        start = parser.parse(bpy.context.scene.BIMWorkScheduleProperties.visualisation_start, dayfirst=True, fuzzy=True)
        return start or None

    @classmethod
    def get_finish_date(cls) -> Union[datetime, None]:
        finish = parser.parse(
            bpy.context.scene.BIMWorkScheduleProperties.visualisation_finish, dayfirst=True, fuzzy=True
        )
        return finish or None

    @classmethod
    def process_construction_state(cls, work_schedule: ifcopenshell.entity_instance, date: datetime) -> dict[str, Any]:
        cls.to_build = set()
        cls.in_construction = set()
        cls.completed = set()
        cls.to_demolish = set()
        cls.in_demolition = set()
        cls.demolished = set()
        for rel in work_schedule.Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTask"):
                    cls.process_task_status(related_object, date)
        return {
            "TO_BUILD": cls.to_build,
            "IN_CONSTRUCTION": cls.in_construction,
            "COMPLETED": cls.completed,
            "TO_DEMOLISH": cls.to_demolish,
            "IN_DEMOLITION": cls.in_demolition,
            "DEMOLISHED": cls.demolished,
        }

    @classmethod
    def process_task_status(cls, task: ifcopenshell.entity_instance, date: datetime) -> None:
        for rel in task.IsNestedBy or []:
            [cls.process_task_status(related_object, date) for related_object in rel.RelatedObjects]
        start = ifcopenshell.util.sequence.derive_date(task, "ScheduleStart", is_earliest=True)
        finish = ifcopenshell.util.sequence.derive_date(task, "ScheduleFinish", is_latest=True)
        if not start or not finish:
            return
        outputs = ifcopenshell.util.sequence.get_task_outputs(task) or []
        inputs = cls.get_task_inputs(task) or []
        if date < start:
            [cls.to_build.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.to_demolish.add(tool.Ifc.get_object(input)) for input in inputs]
        elif date < finish:
            [cls.in_construction.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.in_demolition.add(tool.Ifc.get_object(input)) for input in inputs]
        else:
            [cls.completed.add(tool.Ifc.get_object(output)) for output in outputs]
            [cls.demolished.add(tool.Ifc.get_object(input)) for input in inputs]

    @classmethod
    def show_snapshot(cls, product_states):
        bpy.context.scene.frame_start = 1
        bpy.context.scene.frame_end = 2
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.hide_viewport = False
            obj.hide_render = False

        for obj in cls.to_build:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=1)
            obj.keyframe_insert(data_path="hide_render", frame=1)

        for obj in cls.in_construction:
            obj.color = (1.0, 0.7, 0.0, 1)
            obj.keyframe_insert(data_path="color", frame=1)

        for obj in cls.completed:
            obj.color = (0.0, 1.0, 0.0, 1)
            obj.keyframe_insert(data_path="color", frame=1)

        for obj in cls.to_demolish:
            if obj in cls.to_build:
                continue
            elif obj.animation_data:
                obj.animation_data_clear()
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="hide_viewport", frame=1)
            obj.keyframe_insert(data_path="hide_render", frame=1)
        for obj in cls.in_demolition:
            obj.color = (1.0, 0.0, 0.0, 1)
            obj.keyframe_insert(data_path="color", frame=1)
        for obj in cls.demolished:
            if obj.animation_data:
                obj.animation_data_clear()
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=1)
            obj.keyframe_insert(data_path="hide_render", frame=1)

    @classmethod
    def set_object_shading(cls):
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"

    @classmethod
    def get_animation_settings(cls):
        def calculate_total_frames(fps):
            if props.speed_types == "FRAME_SPEED":
                return calculate_using_frames(
                    start,
                    finish,
                    props.speed_animation_frames,
                    ifcopenshell.util.date.parse_duration(props.speed_real_duration),
                )
            elif props.speed_types == "DURATION_SPEED":
                animation_duration = ifcopenshell.util.date.parse_duration(props.speed_animation_duration)
                real_duration = ifcopenshell.util.date.parse_duration(props.speed_real_duration)
                return calculate_using_duration(
                    start,
                    finish,
                    fps,
                    animation_duration,
                    real_duration,
                )
            elif props.speed_types == "MULTIPLIER_SPEED":
                return calculate_using_multiplier(
                    start,
                    finish,
                    1,
                    props.speed_multiplier,
                )

        def calculate_using_multiplier(start, finish, fps, multiplier):
            animation_time = (finish - start) / multiplier
            return animation_time.total_seconds() * fps

        def calculate_using_duration(start, finish, fps, animation_duration, real_duration):
            return calculate_using_multiplier(start, finish, fps, real_duration / animation_duration)

        def calculate_using_frames(start, finish, animation_frames, real_duration):
            return ((finish - start) / real_duration) * animation_frames

        props = bpy.context.scene.BIMWorkScheduleProperties
        if not (props.visualisation_start and props.visualisation_finish):
            return

        start = cls.get_start_date()
        finish = cls.get_finish_date()
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
    def get_animation_product_frames(cls, work_schedule: ifcopenshell.entity_instance, settings: dict[str, Any]):
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
    def clear_object_animation(cls, obj):
        if obj.animation_data:
            obj.animation_data_clear()

    @classmethod
    def clear_object_color(cls, obj):
        obj.color = (1.0, 1.0, 1.0, 1.0)

    @classmethod
    def display_object(cls, obj):
        if not obj.visible_get():
            obj.hide_viewport = False
            obj.hide_render = False

    @classmethod
    def hide_object(cls, obj):
        if obj.visible_get():
            obj.hide_viewport = True
            obj.hide_render = True

    @classmethod
    def clear_objects_animation(cls, include_blender_objects=True):
        for obj in bpy.data.objects:
            if not include_blender_objects and not obj.BIMObjectProperties.ifc_definition_id:
                continue
            cls.clear_object_animation(obj)
            cls.clear_object_color(obj)
            cls.display_object(obj)

    @classmethod
    def animate_objects(cls, settings, frames, animation_type=""):
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            if tool.Ifc.get().by_id(obj.BIMObjectProperties.ifc_definition_id).is_a("IfcSpace"):
                cls.hide_object(obj)
                continue
            cls.earliest_frame = None
            product_frames = frames.get(obj.BIMObjectProperties.ifc_definition_id, [])
            for product_frame in product_frames:
                if product_frame["relationship"] == "input":
                    cls.animate_input(obj, settings["start_frame"], product_frame, animation_type)
                elif product_frame["relationship"] == "output":
                    cls.animate_output(obj, settings["start_frame"], product_frame, animation_type)
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        bpy.context.scene.frame_start = settings["start_frame"]
        bpy.context.scene.frame_end = int(settings["start_frame"] + settings["total_frames"] + 1)

    @classmethod
    def animate_input(cls, obj, start_frame, product_frame, animation_type):
        props = bpy.context.scene.BIMAnimationProperties
        color = props.task_input_colors[product_frame["type"]].color
        if product_frame["type"] in ["LOGISTIC", "MOVE", "DISPOSAL"]:
            cls.animate_destruction(obj, start_frame, product_frame, color, animation_type)
        else:
            cls.animate_consumption(obj, start_frame, product_frame, color, animation_type)

    @classmethod
    def animate_output(cls, obj, start_frame, product_frame, animation_type):
        props = bpy.context.scene.BIMAnimationProperties
        color = props.task_output_colors[product_frame["type"]].color
        if product_frame["type"] in ["CONSTRUCTION", "INSTALLATION", "NOTDEFINED"]:
            cls.animate_creation(obj, start_frame, product_frame, color)
        elif product_frame["type"] in ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"]:
            cls.animate_destruction(obj, start_frame, product_frame, color, animation_type)
        elif product_frame["type"] in ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"]:
            cls.animate_operation(obj, start_frame, product_frame, color)
        elif product_frame["type"] in ["LOGISTIC", "MOVE"]:
            cls.animate_movement_to(obj, start_frame, product_frame, color)
        else:
            cls.animate_operation(obj, start_frame, product_frame, color)

    @classmethod
    def animate_destruction(cls, obj, start_frame, product_frame, color, animation_type):
        if cls.earliest_frame is None or product_frame["STARTED"] < cls.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="color", frame=start_frame)
            obj.keyframe_insert(data_path="hide_viewport", frame=start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=start_frame)
            cls.earliest_frame = product_frame["STARTED"]
        if animation_type == "snapshot":
            start = product_frame["STARTED"]
        else:
            start = product_frame["STARTED"] - 1
        obj.keyframe_insert(data_path="color", frame=start)
        obj.keyframe_insert(data_path="hide_viewport", frame=start)
        obj.keyframe_insert(data_path="hide_render", frame=start)
        obj.color = (color.r, color.g, color.b, 1)
        obj.keyframe_insert(data_path="color", frame=start + 1)
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    @classmethod
    def animate_movement_from(cls, obj, start_frame, product_frame, color, animation_type):
        cls.animate_destruction(obj, start_frame, product_frame, color, animation_type)

    @classmethod
    def animate_consumption(cls, obj, start_frame, product_frame, color, animation_type):
        cls.animate_destruction(obj, start_frame, product_frame, color, animation_type)

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
        cls.animate_creation(obj, start_frame, product_frame, color)

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

    @classmethod
    def create_tasks_json(cls, work_schedule: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        sequence_type_map = {
            None: "FS",
            "START_START": "SS",
            "START_FINISH": "SF",
            "FINISH_START": "FS",
            "FINISH_FINISH": "FF",
            "USERDEFINED": "FS",
            "NOTDEFINED": "FS",
        }
        is_baseline = False
        if work_schedule.PredefinedType == "BASELINE":
            is_baseline = True
            relating_work_schedule = work_schedule.IsDeclaredBy[0].RelatingObject
            work_schedule = relating_work_schedule
        tasks_json = []
        for task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            if is_baseline:
                cls.create_new_task_json(task, tasks_json, sequence_type_map, baseline_schedule=work_schedule)
            else:
                cls.create_new_task_json(task, tasks_json, sequence_type_map)
        return tasks_json

    @classmethod
    def create_new_task_json(cls, task, json, type_map=None, baseline_schedule=None):
        task_time = task.TaskTime
        resources = ifcopenshell.util.sequence.get_task_resources(task, is_deep=False)

        string_resources = ""
        resources_usage = ""
        for resource in resources:
            string_resources += resource.Name + ", "
            resources_usage += str(resource.Usage.ScheduleUsage) + ", " if resource.Usage else "-, "

        schedule_start = task_time.ScheduleStart if task_time else ""
        schedule_finish = task_time.ScheduleFinish if task_time else ""

        baseline_task = None
        if baseline_schedule:
            for rel in task.Declares:
                for baseline_task in rel.RelatedObjects:
                    if baseline_schedule.id() == ifcopenshell.util.sequence.get_task_work_schedule(baseline_task).id():
                        baseline_task = task
                        break

        if baseline_task and baseline_task.TaskTime:
            compare_start = baseline_task.TaskTime.ScheduleStart
            compare_finish = baseline_task.TaskTime.ScheduleFinish
        else:
            compare_start = schedule_start
            compare_finish = schedule_finish
        task_name = task.Name or "Unnamed"
        task_name = task_name.replace("\n", "")
        data = {
            "pID": task.id(),
            "pName": task_name,
            "pCaption": task_name,
            "pStart": schedule_start,
            "pEnd": schedule_finish,
            "pPlanStart": compare_start,
            "pPlanEnd": compare_finish,
            "pMile": 1 if task.IsMilestone else 0,
            "pRes": string_resources,
            "pComp": 0,
            "pGroup": 1 if task.IsNestedBy else 0,
            "pParent": task.Nests[0].RelatingObject.id() if task.Nests else 0,
            "pOpen": 1,
            "pCost": 1,
            "ifcduration": (
                str(ifcopenshell.util.date.ifc2datetime(task_time.ScheduleDuration))
                if (task_time and task_time.ScheduleDuration)
                else ""
            ),
            "resourceUsage": resources_usage,
        }
        if task_time and task_time.IsCritical:
            data["pClass"] = "gtaskred"
        elif data["pGroup"]:
            data["pClass"] = "ggroupblack"
        elif data["pMile"]:
            data["pClass"] = "gmilestone"
        else:
            data["pClass"] = "gtaskblue"

        data["pDepend"] = ",".join(
            [f"{rel.RelatingProcess.id()}{type_map[rel.SequenceType]}" for rel in task.IsSuccessorFrom or []]
        )
        json.append(data)
        for nested_task in ifcopenshell.util.sequence.get_nested_tasks(task):
            cls.create_new_task_json(nested_task, json, type_map, baseline_schedule)

    @classmethod
    def generate_gantt_browser_chart(
        cls, task_json: list[dict[str, Any]], work_schedule: ifcopenshell.entity_instance
    ) -> None:
        if not bpy.context.scene.WebProperties.is_connected:
            bpy.ops.bim.connect_websocket_server(page="sequencing")
        gantt_data = {"tasks": task_json, "work_schedule": work_schedule.get_info(recursive=True)}
        tool.Web.send_webui_data(data=gantt_data, data_key="gantt_data", event="gantt_data")

    @classmethod
    def is_filter_by_active_schedule(cls) -> bool:
        return bpy.context.scene.BIMWorkScheduleProperties.filter_by_active_schedule

    @classmethod
    def get_tasks_for_product(
        cls, product: ifcopenshell.entity_instance, work_schedule: Optional[ifcopenshell.entity_instance] = None
    ) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
        return ifcopenshell.util.sequence.get_tasks_for_product(product, work_schedule)

    @classmethod
    def load_product_related_tasks(
        cls, task_inputs: list[ifcopenshell.entity_instance], task_ouputs: list[ifcopenshell.entity_instance]
    ) -> None:
        props = bpy.context.scene.BIMWorkScheduleProperties
        props.product_input_tasks.clear()
        props.product_output_tasks.clear()
        for task in task_inputs or []:
            new = props.product_input_tasks.add()
            new.name = task.Name or "Unnamed"
            new.ifc_definition_id = task.id()
        for task in task_ouputs or []:
            new = props.product_output_tasks.add()
            new.name = task.Name or "Unnamed"
            new.ifc_definition_id = task.id()

    @classmethod
    def get_work_schedule_products(
        cls, work_schedule: ifcopenshell.entity_instance
    ) -> list[ifcopenshell.entity_instance]:
        products = []
        for task in ifcopenshell.util.sequence.get_root_tasks(work_schedule):
            products.extend(ifcopenshell.util.sequence.get_task_inputs(task, is_deep=True))
            products.extend(ifcopenshell.util.sequence.get_task_outputs(task, is_deep=True))
        return products

    @classmethod
    def has_task_assignments(cls, product, work_schedule=None):
        task_inputs, task_ouputs = ifcopenshell.util.sequence.get_tasks_for_product(product)
        if work_schedule:
            task_inputs = [task for task in task_inputs or [] if cls.get_work_schedule(task) == work_schedule]
            task_ouputs = [task for task in task_ouputs or [] if cls.get_work_schedule(task) == work_schedule]
        return bool(task_inputs or task_ouputs)

    @classmethod
    def is_sorting_enabled(cls):
        return bpy.context.scene.BIMWorkScheduleProperties.sort_column

    @classmethod
    def is_sort_reversed(cls):
        return bpy.context.scene.BIMWorkScheduleProperties.is_sort_reversed

    @classmethod
    def get_user_predefined_type(cls):
        predefined_type = bpy.context.scene.BIMWorkScheduleProperties.work_schedule_predefined_types
        object_type = None
        if predefined_type == "USERDEFINED":
            object_type = bpy.context.scene.BIMWorkScheduleProperties.object_type
        return predefined_type, object_type

    @classmethod
    def add_animation_camera(cls):
        bpy.ops.object.camera_add()
        camera = bpy.context.active_object
        camera.data.lens = 26
        camera.name = "4D Camera"
        camera.location = mathutils.Vector((15, 0, 15))
        camera.rotation_euler = mathutils.Euler((1.2, 0, 1.5), "XYZ")
        for obj in bpy.context.scene.objects:
            obj.select_set(False)
        for obj in bpy.context.visible_objects:
            if not (obj.hide_get() or obj.hide_render) and obj.type != "LIGHT":
                obj.select_set(True)
        bpy.context.scene.camera = camera
        bpy.ops.view3d.camera_to_view_selected()

    @classmethod
    def save_animation_color_scheme(cls, name: str) -> ifcopenshell.entity_instance:
        props = bpy.context.scene.BIMAnimationProperties
        colour_scheme = {
            "Inputs": {cs.name: cs.color[0:3] for cs in props.task_input_colors},
            "Outputs": {cs.name: cs.color[0:3] for cs in props.task_output_colors},
        }

        group = [g for g in tool.Ifc.get().by_type("IfcGroup") if g.Name == name]
        if group:
            group = group[0]
            description = json.loads(group.Description)
            description["colourscheme"] = colour_scheme
            group.Description = json.dumps(description)
        else:
            description = json.dumps({"type": "BBIM_AnimationColorScheme", "colourscheme": colour_scheme})
            group = tool.Ifc.run("group.add_group", name=name, description=description)
        return group[0]

    @classmethod
    def load_animation_color_scheme(cls, scheme: Optional[ifcopenshell.entity_instance]) -> None:
        if not scheme:
            return
        data = json.loads(scheme.Description)
        if data.get("type") == "BBIM_AnimationColorScheme":
            inputs_color_scheme = data.get("colourscheme").get("Inputs")
            outputs_color_scheme = data.get("colourscheme").get("Outputs")
            props = bpy.context.scene.BIMAnimationProperties
            props.task_input_colors.clear()
            props.task_output_colors.clear()
            for value, colour in inputs_color_scheme.items():
                new = props.task_input_colors.add()
                new.name = str(value)
                new.color = colour[0:3]

            for value, colour in outputs_color_scheme.items():
                new = props.task_output_colors.add()
                new.name = str(value)
                new.color = colour[0:3]

    @classmethod
    def update_task_ICOM(cls, task):
        if not task:
            return
        inputs = cls.get_task_inputs(task)
        outputs = cls.get_task_outputs(task)
        cls.load_task_inputs(inputs)
        cls.load_task_outputs(outputs)
        cls.load_task_resources(task)

    @classmethod
    def refresh_task_resources(cls):
        task = cls.get_highlighted_task()
        if not task:
            return
        cls.load_task_resources(task)

    @classmethod
    def has_duration(cls, task):
        if task.TaskTime and task.TaskTime.ScheduleDuration:
            return True
        return False

    @classmethod
    def get_task_bar_list(cls):
        return json.loads(bpy.context.scene.BIMWorkScheduleProperties.task_bars)

    @classmethod
    def add_task_bar(cls, task_id):
        task_bars = cls.get_task_bar_list()
        task_bars.append(task_id)
        bpy.context.scene.BIMWorkScheduleProperties.task_bars = json.dumps(task_bars)

    @classmethod
    def remove_task_bar(cls, task_id):
        task_bars = cls.get_task_bar_list()
        if task_id in task_bars:
            task_bars.remove(task_id)
            bpy.context.scene.BIMWorkScheduleProperties.task_bars = json.dumps(task_bars)

    @classmethod
    def get_animation_color_scheme(cls):
        if len(bpy.context.scene.BIMAnimationProperties.saved_color_schemes) > 0:
            return tool.Ifc.get().by_id(int(bpy.context.scene.BIMAnimationProperties.saved_color_schemes))
