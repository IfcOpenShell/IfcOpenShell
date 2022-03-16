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

import re
import os
import bpy
import json
import time
import calendar
import isodate
import pystache
import webbrowser
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.sequence
import blenderbim.bim.helper
import blenderbim.bim.module.sequence.helper as helper
from datetime import datetime
from datetime import timedelta
from dateutil import parser, relativedelta
from blenderbim.bim.ifc import IfcStore
from bpy_extras.io_utils import ImportHelper
from ifcopenshell.api.sequence.data import Data
from ifcopenshell.api.resource.data import Data as ResourceData


def animate_text(scene, context):
    data = bpy.data.curves.get("Timeline")
    if not data or not bpy.data.objects.get("Timeline"):
        self.remove_text_animation_handler()
        scene.frame_current
    props = data.BIMDateTextProperties
    start = parser.parse(props.start, dayfirst=True, fuzzy=True)
    finish = parser.parse(props.finish, dayfirst=True, fuzzy=True)
    duration = finish - start
    frame_date = (((scene.frame_current - props.start_frame) / props.total_frames) * duration) + start
    data.body = frame_date.date().isoformat()


class AddWorkPlan(bpy.types.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("sequence.add_work_plan", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkPlan(bpy.types.Operator):
    bl_idname = "bim.edit_work_plan"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Edit Work Plan"

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        attributes = blenderbim.bim.helper.export_attributes(props.work_plan_attributes, self.export_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_plan",
            self.file,
            **{"work_plan": self.file.by_id(props.active_work_plan_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_work_plan()
        return {"FINISHED"}

    def export_attributes(self, attributes, prop):
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


class RemoveWorkPlan(bpy.types.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_plan", self.file, **{"work_plan": self.file.by_id(self.work_plan)})
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        props.work_plan_attributes.clear()

        data = Data.work_plans[self.work_plan]

        blenderbim.bim.helper.import_attributes("IfcWorkPlan", props.work_plan_attributes, data, self.import_attributes)

        props.active_work_plan_id = self.work_plan
        props.editing_type = "ATTRIBUTES"
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name in ["CreationDate", "StartTime", "FinishTime"]:
            prop.string_value = "" if prop.is_null else data[name].isoformat()
            return True


class DisableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_plan"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Work Plan"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.active_work_plan_id = 0
        return {"FINISHED"}


class EnableEditingWorkPlanSchedules(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan_schedules"
    bl_label = "Enable Editing Work Plan Schedules"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        props.active_work_plan_id = self.work_plan
        props.editing_type = "SCHEDULES"
        return {"FINISHED"}


class AssignWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.assign_work_schedule"
    bl_label = "Assign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "aggregate.assign_object",
            self.file,
            **{
                "relating_object": self.file.by_id(self.work_plan),
                "product": self.file.by_id(self.work_schedule),
            },
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.unassign_work_schedule"
    bl_label = "Unassign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "aggregate.unassign_object",
            self.file,
            **{
                "relating_object": self.file.by_id(self.work_plan),
                "product": self.file.by_id(self.work_schedule),
            },
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("sequence.add_work_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.edit_work_schedule"
    bl_label = "Edit Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.work_schedule_attributes, self.export_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_schedule",
            self.file,
            **{"work_schedule": self.file.by_id(props.active_work_schedule_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_work_schedule()
        return {"FINISHED"}

    def export_attributes(self, attributes, prop):
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


class RemoveWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_schedule", self.file, work_schedule=self.file.by_id(self.work_schedule)
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_work_schedule_id = self.work_schedule
        self.props.work_schedule_attributes.clear()
        self.enable_editing_work_schedule()
        self.props.editing_type = "WORK_SCHEDULE"
        return {"FINISHED"}

    def enable_editing_work_schedule(self):
        data = Data.work_schedules[self.work_schedule]

        blenderbim.bim.helper.import_attributes(
            "IfcWorkSchedule", self.props.work_schedule_attributes, data, self.import_attributes
        )

    def import_attributes(self, name, prop, data):
        if name in ["CreationDate", "StartTime", "FinishTime"]:
            prop.string_value = "" if prop.is_null else data[name].isoformat()
            return True


class EnableEditingTasks(bpy.types.Operator):
    bl_idname = "bim.enable_editing_tasks"
    bl_label = "Enable Editing Tasks"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        self.props.active_work_schedule_id = self.work_schedule
        self.tprops.tasks.clear()

        self.contracted_tasks = json.loads(self.props.contracted_tasks)
        self.sort_keys = {
            i: self.get_sort_key(Data.tasks[i]) for i in Data.work_schedules[self.work_schedule]["RelatedObjects"]
        }

        related_object_ids = sorted(self.sort_keys, key=self.natural_sort_key)
        if self.props.is_sort_reversed:
            related_object_ids.reverse()

        for related_object_id in related_object_ids:
            self.create_new_task_li(related_object_id, 0)
        bpy.ops.bim.load_task_properties()
        self.props.editing_type = "TASKS"
        return {"FINISHED"}

    def create_new_task_li(self, related_object_id, level_index):
        task = Data.tasks[related_object_id]
        new = self.tprops.tasks.add()
        new.ifc_definition_id = related_object_id
        new.is_expanded = related_object_id not in self.contracted_tasks
        new.level_index = level_index
        if task["RelatedObjects"]:
            new.has_children = True
            if new.is_expanded:
                self.sort_keys = {i: self.get_sort_key(Data.tasks[i]) for i in task["RelatedObjects"]}
                related_object_ids = sorted(self.sort_keys, key=self.natural_sort_key)
                if self.props.is_sort_reversed:
                    related_object_ids.reverse()
                for related_object_id in related_object_ids:
                    self.create_new_task_li(related_object_id, level_index + 1)

    def get_sort_key(self, task):
        # Sorting only applies to actual tasks, not the WBS
        if task["RelatedObjects"]:
            # Sorry for the hack
            return "0000000000" + (task["Identification"] or "")
        if not self.props.sort_column:
            return task["Identification"] or ""
        column_type, name = self.props.sort_column.split(".")
        if column_type == "IfcTask":
            return task.get(name)
        elif column_type == "IfcTaskTime" and task.get("TaskTime"):
            task_time = Data.task_times[task.get("TaskTime")].get(name)
        return task["Identification"] or ""

    def natural_sort_key(self, i, _nsre=re.compile("([0-9]+)")):
        s = self.sort_keys[i]
        return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


class LoadTaskProperties(bpy.types.Operator):
    bl_idname = "bim.load_task_properties"
    bl_label = "Load Task Properties"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        self.props.is_task_update_enabled = False
        for item in self.tprops.tasks:
            if self.task and item.ifc_definition_id != self.task:
                continue
            task = Data.tasks[item.ifc_definition_id]
            item.name = task["Name"] or "Unnamed"
            item.identification = task["Identification"] or "XXX"
            if self.props.active_task_id:
                item.is_predecessor = self.props.active_task_id in [
                    Data.sequences[r]["RelatedProcess"] for r in task["IsPredecessorTo"]
                ]
                item.is_successor = self.props.active_task_id in [
                    Data.sequences[r]["RelatingProcess"] for r in task["IsSuccessorFrom"]
                ]

            calendar = ifcopenshell.util.sequence.derive_calendar(self.file.by_id(item.ifc_definition_id))
            if calendar:
                calendar = Data.work_calendars[calendar.id()]
            if task["HasAssignmentsWorkCalendar"]:
                item.calendar = calendar["Name"] or "Unnamed"
            else:
                item.calendar = ""
                item.derived_calendar = calendar["Name"] or "Unnamed" if calendar else ""

            if task["TaskTime"]:
                task_time = Data.task_times[task["TaskTime"]]
                item.start = self.canonicalise_time(task_time["ScheduleStart"])
                item.finish = self.canonicalise_time(task_time["ScheduleFinish"])
                item.duration = (
                    isodate.duration_isoformat(task_time["ScheduleDuration"]) if task_time["ScheduleDuration"] else "-"
                )
            else:
                derived_start = helper.derive_date(item.ifc_definition_id, "ScheduleStart", is_earliest=True)
                derived_finish = helper.derive_date(item.ifc_definition_id, "ScheduleFinish", is_latest=True)
                item.derived_start = self.canonicalise_time(derived_start) if derived_start else ""
                item.derived_finish = self.canonicalise_time(derived_finish) if derived_finish else ""
                if derived_start and derived_finish and calendar:
                    derived_duration = ifcopenshell.util.sequence.count_working_days(
                        derived_start, derived_finish, self.file.by_id(calendar["id"])
                    )
                    item.derived_duration = f"P{derived_duration}D"
                item.start = "-"
                item.finish = "-"
                item.duration = "-"

        self.props.is_task_update_enabled = True
        return {"FINISHED"}

    def canonicalise_time(self, time):
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")


class DisableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_schedule"
    bl_label = "Disable Editing Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0
        return {"FINISHED"}


class AddTask(bpy.types.Operator):
    bl_idname = "bim.add_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, parent_task=self.file.by_id(self.task))
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class AddSummaryTask(bpy.types.Operator):
    bl_idname = "bim.add_summary_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, work_schedule=self.file.by_id(self.work_schedule))
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class ExpandTask(bpy.types.Operator):
    bl_idname = "bim.expand_task"
    bl_label = "Expand Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.remove(self.task)
        props.contracted_tasks = json.dumps(contracted_tasks)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class ContractTask(bpy.types.Operator):
    bl_idname = "bim.contract_task"
    bl_label = "Contract Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        contracted_tasks = json.loads(props.contracted_tasks)
        contracted_tasks.append(self.task)
        props.contracted_tasks = json.dumps(contracted_tasks)
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class RemoveTask(bpy.types.Operator):
    bl_idname = "bim.remove_task"
    bl_label = "Remove Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        edited_task_ifc = self.file.by_id(props.active_task_id) if props.active_task_id else None

        ifcopenshell.api.run(
            "sequence.remove_task",
            self.file,
            task=self.file.by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)

        if edited_task_ifc:
            if not any(
                task
                for task in context.scene.BIMTaskTreeProperties.tasks
                if task.ifc_definition_id == props.active_task_id
                and self.file.by_id(props.active_task_id) == edited_task_ifc
            ):  # Task was deleted
                bpy.ops.bim.disable_editing_task()

        return {"FINISHED"}


class EnableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_time"
    bl_label = "Enable Editing Task Time"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()

        task_time_id = Data.tasks[self.task]["TaskTime"] or self.add_task_time().id()

        props.task_time_attributes.clear()

        data = Data.task_times[task_time_id]

        blenderbim.bim.helper.import_attributes("IfcTaskTime", props.task_time_attributes, data, self.import_attributes)
        props.active_task_time_id = task_time_id
        props.active_task_id = self.task
        props.editing_task_type = "TASKTIME"
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if prop.data_type == "string":
            if isinstance(data[name], datetime):
                prop.string_value = "" if prop.is_null else data[name].isoformat()
                return True
            elif isinstance(data[name], isodate.Duration):
                prop.string_value = (
                    "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name], "IfcDuration")
                )
                return True

    def add_task_time(self):
        task_time = ifcopenshell.api.run("sequence.add_task_time", self.file, task=self.file.by_id(self.task))
        Data.load(self.file)
        return task_time


class EditTaskTime(bpy.types.Operator):
    bl_idname = "bim.edit_task_time"
    bl_label = "Edit Task Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.task_time_attributes, self.export_attributes)

        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_task_time",
            self.file,
            **{"task_time": self.file.by_id(props.active_task_time_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_task_time()
        bpy.ops.bim.load_task_properties(task=props.active_task_id)
        return {"FINISHED"}

    def export_attributes(self, attributes, prop):
        if "Start" in prop.name or "Finish" in prop.name or prop.name == "StatusTime":
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "ScheduleDuration":
            if prop.is_null:
                attributes[prop.name] = None
                return True
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task"
    bl_label = "Enable Editing Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        props.task_attributes.clear()
        data = Data.tasks[self.task]

        blenderbim.bim.helper.import_attributes("IfcTask", props.task_attributes, data)
        props.active_task_id = self.task
        props.editing_task_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingTask(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task"
    bl_label = "Disable Editing Task"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_id = 0
        context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        return {"FINISHED"}


class EditTask(bpy.types.Operator):
    bl_idname = "bim.edit_task"
    bl_label = "Edit Task"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.task_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_task", self.file, **{"task": self.file.by_id(props.active_task_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_task()
        bpy.ops.bim.load_task_properties(task=props.active_task_id)
        return {"FINISHED"}


class CopyTaskAttribute(bpy.types.Operator):
    bl_idname = "bim.copy_task_attribute"
    bl_label = "Copy Task Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        value = context.scene.BIMWorkScheduleProperties.task_attributes.get(self.name).get_value()
        self.file = IfcStore.get_file()
        props = context.scene.BIMTaskTreeProperties
        for task in props.tasks:
            if task.is_selected:
                ifcopenshell.api.run(
                    "sequence.edit_task",
                    self.file,
                    task=self.file.by_id(task.ifc_definition_id),
                    attributes={self.name: value},
                )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class AssignPredecessor(bpy.types.Operator):
    bl_idname = "bim.assign_predecessor"
    bl_label = "Assign Predecessor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        rel = ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class AssignSuccessor(bpy.types.Operator):
    bl_idname = "bim.assign_successor"
    bl_label = "Assign Successor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        rel = ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(props.active_task_id),
            related_process=IfcStore.get_file().by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class UnassignPredecessor(bpy.types.Operator):
    bl_idname = "bim.unassign_predecessor"
    bl_label = "Unassign Predecessor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class UnassignSuccessor(bpy.types.Operator):
    bl_idname = "bim.unassign_successor"
    bl_label = "Unassign Successor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=self.file.by_id(props.active_task_id),
            related_process=self.file.by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class AssignProduct(bpy.types.Operator):
    bl_idname = "bim.assign_product"
    bl_label = "Assign Product"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    relating_product: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        relating_products = (
            [bpy.data.objects.get(self.relating_product)] if self.relating_product else context.selected_objects
        )
        for relating_product in relating_products:
            if not relating_product.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "sequence.assign_product",
                self.file,
                relating_product=self.file.by_id(relating_product.BIMObjectProperties.ifc_definition_id),
                related_object=self.file.by_id(self.task),
            )
        Data.load(self.file)
        bpy.ops.bim.load_task_outputs()
        return {"FINISHED"}


class UnassignProduct(bpy.types.Operator):
    bl_idname = "bim.unassign_product"
    bl_label = "Unassign Product"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    relating_product: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        relating_products = (
            [bpy.data.objects.get(self.relating_product)] if self.relating_product else context.selected_objects
        )
        for relating_product in relating_products:
            if not relating_product.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "sequence.unassign_product",
                self.file,
                relating_product=self.file.by_id(relating_product.BIMObjectProperties.ifc_definition_id),
                related_object=self.file.by_id(self.task),
            )
        Data.load(self.file)
        bpy.ops.bim.load_task_outputs()
        return {"FINISHED"}


class AssignProcess(bpy.types.Operator):
    bl_idname = "bim.assign_process"
    bl_label = "Assign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.StringProperty()
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.related_object_type == "RESOURCE":
            self.assign_resource()
        elif self.related_object_type == "PRODUCT":
            self.assign_product(context)
        elif self.related_object_type == "CONTROL":
            pass  # TODO
        return {"FINISHED"}

    def assign_resource(self):
        task = self.file.by_id(self.task)
        resource = self.file.by_id(self.resource)
        subresource = ifcopenshell.api.run(
            "resource.add_resource",
            self.file,
            **{"parent_resource": resource, "ifc_class": resource.is_a(), "name": resource.Name},
        )
        ifcopenshell.api.run(
            "sequence.assign_process", self.file, **{"related_object": subresource, "relating_process": task}
        )
        ResourceData.load(self.file)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        bpy.ops.bim.load_task_resources()

    def assign_product(self, context):
        task = self.file.by_id(self.task)
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            if not related_object.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "sequence.assign_process",
                self.file,
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
                relating_process=task,
            )
        Data.load(self.file)
        bpy.ops.bim.load_task_inputs()


class UnassignProcess(bpy.types.Operator):
    bl_idname = "bim.unassign_process"
    bl_label = "Unassign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.StringProperty()
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        if self.related_object_type == "RESOURCE":
            self.unassign_resource()
        elif self.related_object_type == "PRODUCT":
            self.unassign_product(context)
        elif self.related_object_type == "CONTROL":
            pass  # TODO
        return {"FINISHED"}

    def unassign_resource(self):
        task = self.file.by_id(self.task)
        resource = self.file.by_id(self.resource)
        ifcopenshell.api.run("sequence.unassign_process", self.file, related_object=resource, relating_process=task)
        ifcopenshell.api.run("resource.remove_resource", self.file, resource=resource)
        ResourceData.load(self.file)
        Data.load(self.file)
        bpy.ops.bim.load_resources()
        bpy.ops.bim.load_task_resources()

    def unassign_product(self, context):
        task = self.file.by_id(self.task)
        related_objects = (
            [bpy.data.objects.get(self.related_object)] if self.related_object else context.selected_objects
        )
        for related_object in related_objects:
            if not related_object.BIMObjectProperties.ifc_definition_id:
                continue
            ifcopenshell.api.run(
                "sequence.unassign_process",
                self.file,
                related_object=self.file.by_id(related_object.BIMObjectProperties.ifc_definition_id),
                relating_process=task,
            )
        Data.load(self.file)
        bpy.ops.bim.load_task_inputs()


class GenerateGanttChart(bpy.types.Operator):
    bl_idname = "bim.generate_gantt_chart"
    bl_label = "Generate Gantt Chart"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.json = []
        self.sequence_type_map = {
            None: "FS",
            "START_START": "SS",
            "START_FINISH": "SF",
            "FINISH_START": "FS",
            "FINISH_FINISH": "FF",
            "USERDEFINED": "FS",
            "NOTDEFINED": "FS",
        }
        for task_id in Data.work_schedules[self.work_schedule]["RelatedObjects"]:
            self.create_new_task_json(task_id)
        with open(os.path.join(context.scene.BIMProperties.data_dir, "gantt", "index.html"), "w") as f:
            with open(os.path.join(context.scene.BIMProperties.data_dir, "gantt", "index.mustache"), "r") as t:
                f.write(pystache.render(t.read(), {"json_data": json.dumps(self.json)}))
        webbrowser.open("file://" + os.path.join(context.scene.BIMProperties.data_dir, "gantt", "index.html"))
        return {"FINISHED"}

    def create_new_task_json(self, task_id):
        task = self.file.by_id(task_id)
        data = {
            "pID": task.id(),
            "pName": task.Name,
            "pStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
            "pEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
            "pPlanStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
            "pPlanEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
            "pMile": 1 if task.IsMilestone else 0,
            "pComp": 0,
            "pGroup": 1 if task.IsNestedBy else 0,
            "pParent": task.Nests[0].RelatingObject.id() if task.Nests else 0,
            "pOpen": 1,
            "pCost": 1,
        }
        if task.TaskTime and task.TaskTime.IsCritical:
            data["pClass"] = "gtaskred"
        elif data["pGroup"]:
            data["pClass"] = "ggroupblack"
        elif data["pMile"]:
            data["pClass"] = "gmilestone"
        else:
            data["pClass"] = "gtaskblue"
        data["pDepend"] = ",".join(
            [
                "{}{}".format(rel.RelatingProcess.id(), self.sequence_type_map[rel.SequenceType])
                for rel in task.IsSuccessorFrom or []
            ]
        )
        self.json.append(data)
        for task_id in Data.tasks[task_id]["RelatedObjects"]:
            self.create_new_task_json(task_id)


class AddWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.add_work_calendar"
    bl_label = "Add Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("sequence.add_work_calendar", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.edit_work_calendar"
    bl_label = "Edit Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        attributes = blenderbim.bim.helper.export_attributes(props.work_calendar_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_calendar",
            self.file,
            **{"work_calendar": self.file.by_id(props.active_work_calendar_id), "attributes": attributes},
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_work_calendar()
        return {"FINISHED"}


class RemoveWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.remove_work_calendar"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_calendar", self.file, **{"work_calendar": self.file.by_id(self.work_calendar)}
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar"
    bl_label = "Enable Editing Work Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        self.props.work_calendar_attributes.clear()

        data = Data.work_calendars[self.work_calendar]

        blenderbim.bim.helper.import_attributes("IfcWorkCalendar", self.props.work_calendar_attributes, data)
        self.props.active_work_calendar_id = self.work_calendar
        self.props.editing_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_calendar"
    bl_label = "Disable Editing Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.active_work_calendar_id = 0
        return {"FINISHED"}


class ImportP6(bpy.types.Operator, ImportHelper):
    bl_idname = "import_p6.bim"
    bl_label = "Import P6"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.p62ifc import P62Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        p62ifc = P62Ifc()
        p62ifc.xml = self.filepath
        p62ifc.file = self.file
        p62ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p62ifc.execute()
        Data.load(IfcStore.get_file())
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ImportP6XER(bpy.types.Operator, ImportHelper):
    bl_idname = "import_p6xer.bim"
    bl_label = "Import P6 XER"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xer"
    filter_glob: bpy.props.StringProperty(default="*.xer", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.p6xer2ifc import P6XER2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        p6xer2ifc = P6XER2Ifc()
        p6xer2ifc.xer = self.filepath
        p6xer2ifc.file = self.file
        p6xer2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p6xer2ifc.execute()
        Data.load(IfcStore.get_file())
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ImportPP(bpy.types.Operator, ImportHelper):
    bl_idname = "import_pp.bim"
    bl_label = "Import Powerproject pp"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".pp"
    filter_glob: bpy.props.StringProperty(default="*.pp", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.pp2ifc import PP2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        pp2ifc = PP2Ifc()
        pp2ifc.pp = self.filepath
        pp2ifc.file = self.file
        pp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        pp2ifc.execute()
        Data.load(IfcStore.get_file())
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ImportMSP(bpy.types.Operator, ImportHelper):
    bl_idname = "import_msp.bim"
    bl_label = "Import MSP"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.msp2ifc import MSP2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        msp2ifc = MSP2Ifc()
        msp2ifc.xml = self.filepath
        msp2ifc.file = self.file
        msp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        msp2ifc.execute()
        Data.load(IfcStore.get_file())
        print("Import finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ExportMSP(bpy.types.Operator, ImportHelper):
    bl_idname = "export_msp.bim"
    bl_label = "Export MSP"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.ifc2msp import Ifc2Msp

        self.file = IfcStore.get_file()
        start = time.time()
        ifc2msp = Ifc2Msp()
        ifc2msp.work_schedule = self.file.by_type("IfcWorkSchedule")[0]
        ifc2msp.xml = bpy.path.ensure_ext(self.filepath, ".xml")
        ifc2msp.file = self.file
        ifc2msp.holiday_start_date = parser.parse(self.holiday_start_date).date()
        ifc2msp.holiday_finish_date = parser.parse(self.holiday_finish_date).date()
        ifc2msp.execute()
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ExportP6(bpy.types.Operator, ImportHelper):
    bl_idname = "export_p6.bim"
    bl_label = "Export P6"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = IfcStore.get_file()
        return ifc_file is not None

    def execute(self, context):
        from ifc4d.ifc2p6 import Ifc2P6

        self.file = IfcStore.get_file()
        start = time.time()
        ifc2p6 = Ifc2P6()
        ifc2p6.xml = bpy.path.ensure_ext(self.filepath, ".xml")
        ifc2p6.file = self.file
        ifc2p6.holiday_start_date = parser.parse(self.holiday_start_date).date()
        ifc2p6.holiday_finish_date = parser.parse(self.holiday_finish_date).date()
        ifc2p6.execute()
        print("Export finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class EnableEditingWorkCalendarTimes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar_times"
    bl_label = "Enable Editing Work Calendar Times"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        props.active_work_calendar_id = self.work_calendar
        props.editing_type = "WORKTIMES"
        return {"FINISHED"}


class AddWorkTime(bpy.types.Operator):
    bl_idname = "bim.add_work_time"
    bl_label = "Add Work Time"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    time_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.add_work_time",
            self.file,
            **{"work_calendar": self.file.by_id(self.work_calendar), "time_type": self.time_type},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingWorkTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_time"
    bl_label = "Enable Editing Work Time"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        self.props.work_time_attributes.clear()

        data = Data.work_times[self.work_time]

        blenderbim.bim.helper.import_attributes(
            "IfcWorkTime", self.props.work_time_attributes, data, self.import_attributes
        )

        self.initialise_recurrence_components()
        self.load_recurrence_pattern_data(data)
        self.props.active_work_time_id = self.work_time
        return {"FINISHED"}

    def import_attributes(self, name, prop, data):
        if name in ["Start", "Finish"]:
            prop.string_value = "" if prop.is_null else data[name].isoformat()
            return True

    def initialise_recurrence_components(self):
        if len(self.props.day_components) == 0:
            for i in range(0, 31):
                new = self.props.day_components.add()
                new.name = str(i + 1)
        if len(self.props.weekday_components) == 0:
            for d in ["M", "T", "W", "T", "F", "S", "S"]:
                new = self.props.weekday_components.add()
                new.name = d
        if len(self.props.month_components) == 0:
            for m in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
                new = self.props.month_components.add()
                new.name = m

    def load_recurrence_pattern_data(self, work_time):
        self.props.position = 0
        self.props.interval = 0
        self.props.occurrences = 0
        self.props.start_time = ""
        self.props.end_time = ""
        for component in self.props.day_components:
            component.is_specified = False
        for component in self.props.weekday_components:
            component.is_specified = False
        for component in self.props.month_components:
            component.is_specified = False
        if not work_time["RecurrencePattern"]:
            return
        recurrence_pattern = Data.recurrence_patterns[work_time["RecurrencePattern"]]
        for attribute in ["Position", "Interval", "Occurrences"]:
            if recurrence_pattern[attribute]:
                setattr(self.props, attribute.lower(), recurrence_pattern[attribute])
        for component in recurrence_pattern["DayComponent"] or []:
            self.props.day_components[component - 1].is_specified = True
        for component in recurrence_pattern["WeekdayComponent"] or []:
            self.props.weekday_components[component - 1].is_specified = True
        for component in recurrence_pattern["MonthComponent"] or []:
            self.props.month_components[component - 1].is_specified = True


class DisableEditingWorkTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_time"
    bl_label = "Disable Editing Work Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.active_work_time_id = 0
        return {"FINISHED"}


class EditWorkTime(bpy.types.Operator):
    bl_idname = "bim.edit_work_time"
    bl_label = "Edit Work Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        attributes = blenderbim.bim.helper.export_attributes(self.props.work_time_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_work_time",
            self.file,
            **{"work_time": self.file.by_id(self.props.active_work_time_id), "attributes": attributes},
        )

        work_time = Data.work_times[self.props.active_work_time_id]
        if work_time["RecurrencePattern"]:
            self.edit_recurrence_pattern(work_time["RecurrencePattern"])

        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_work_time()
        return {"FINISHED"}

    def edit_recurrence_pattern(self, recurrence_pattern_id):
        recurrence_pattern = self.file.by_id(recurrence_pattern_id)
        attributes = {
            "Interval": self.props.interval if self.props.interval > 0 else None,
            "Occurrences": self.props.occurrences if self.props.occurrences > 0 else None,
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
            attributes["Position"] = self.props.position if self.props.position != 0 else None
        if "DayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["DayComponent"] = [i + 1 for i, c in enumerate(self.props.day_components) if c.is_specified]
        if "WeekdayComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["WeekdayComponent"] = [
                i + 1 for i, c in enumerate(self.props.weekday_components) if c.is_specified
            ]
        if "MonthComponent" in applicable_data[recurrence_pattern.RecurrenceType]:
            attributes["MonthComponent"] = [i + 1 for i, c in enumerate(self.props.month_components) if c.is_specified]
        ifcopenshell.api.run(
            "sequence.edit_recurrence_pattern",
            self.file,
            **{"recurrence_pattern": recurrence_pattern, "attributes": attributes},
        )


class RemoveWorkTime(bpy.types.Operator):
    bl_idname = "bim.remove_work_time"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_time", self.file, **{"work_time": self.file.by_id(self.work_time)})
        Data.load(self.file)
        return {"FINISHED"}


class AssignRecurrencePattern(bpy.types.Operator):
    bl_idname = "bim.assign_recurrence_pattern"
    bl_label = "Assign Recurrence Pattern"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()
    recurrence_type: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_recurrence_pattern",
            self.file,
            **{"parent": self.file.by_id(self.work_time), "recurrence_type": self.recurrence_type},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class UnassignRecurrencePattern(bpy.types.Operator):
    bl_idname = "bim.unassign_recurrence_pattern"
    bl_label = "Unassign Recurrence Pattern"
    bl_options = {"REGISTER", "UNDO"}
    recurrence_pattern: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_recurrence_pattern",
            self.file,
            **{"recurrence_pattern": self.file.by_id(self.recurrence_pattern)},
        )
        Data.load(self.file)
        return {"FINISHED"}


class AddTimePeriod(bpy.types.Operator):
    bl_idname = "bim.add_time_period"
    bl_label = "Add Time Period"
    bl_options = {"REGISTER", "UNDO"}
    recurrence_pattern: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        self.file = IfcStore.get_file()
        try:
            start_time = parser.parse(self.props.start_time)
            end_time = parser.parse(self.props.end_time)
        except:
            return {"FINISHED"}
        ifcopenshell.api.run(
            "sequence.add_time_period",
            self.file,
            **{
                "recurrence_pattern": self.file.by_id(self.recurrence_pattern),
                "start_time": start_time,
                "end_time": end_time,
            },
        )
        self.props.start_time = ""
        self.props.end_time = ""
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class RemoveTimePeriod(bpy.types.Operator):
    bl_idname = "bim.remove_time_period"
    bl_label = "Remove Time Period"
    bl_options = {"REGISTER", "UNDO"}
    time_period: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_time_period",
            self.file,
            **{"time_period": self.file.by_id(self.time_period)},
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_calendar"
    bl_label = "Enable Editing Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        props.active_task_id = self.task
        props.editing_task_type = "CALENDAR"
        return {"FINISHED"}


class EditTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.edit_task_calendar"
    bl_label = "Edit Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        task = self.file.by_id(self.task)
        ifcopenshell.api.run(
            "control.assign_control",
            self.file,
            **{
                "relating_control": self.file.by_id(self.work_calendar),
                "related_object": task,
            },
        )
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class RemoveTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.remove_task_calendar"
    bl_label = "Remove Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        task = self.file.by_id(self.task)
        ifcopenshell.api.run(
            "control.unassign_control",
            self.file,
            **{
                "relating_control": self.file.by_id(self.work_calendar),
                "related_object": task,
            },
        )
        ifcopenshell.api.run("sequence.cascade_schedule", self.file, task=task)
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class EnableEditingTaskSequence(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_sequence"
    bl_label = "Enable Editing Task Sequence"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        props.active_task_id = self.task
        props.editing_task_type = "SEQUENCE"
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class DisableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task_time"
    bl_label = "Disable Editing Task Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        bpy.ops.bim.disable_editing_task()
        return {"FINISHED"}


class EnableEditingSequenceAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_attributes"
    bl_label = "Enable Editing Sequence Attributes"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_sequence_id = self.sequence
        self.props.editing_sequence_type = "ATTRIBUTES"
        self.props.sequence_attributes.clear()
        self.enable_editing_sequence_attributes()
        return {"FINISHED"}

    def enable_editing_sequence_attributes(self):
        data = Data.sequences[self.sequence]
        blenderbim.bim.helper.import_attributes("IfcRelSequence", self.props.sequence_attributes, data)


class EnableEditingSequenceTimeLag(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_time_lag"
    bl_label = "Enable Editing Sequence Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()
    lag_time: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_sequence_id = self.sequence
        self.props.editing_sequence_type = "TIME_LAG"
        self.props.time_lag_attributes.clear()
        self.enable_editing_attributes()
        return {"FINISHED"}

    def enable_editing_attributes(self):
        data = Data.lag_times[self.lag_time]
        blenderbim.bim.helper.import_attributes(
            "IfcLagTime", self.props.time_lag_attributes, data, self.import_attributes
        )

    def import_attributes(self, name, prop, data):
        if name == "LagValue":
            if isinstance(data[name], isodate.Duration):
                prop.data_type = "string"
                prop.string_value = (
                    "" if prop.is_null else ifcopenshell.util.date.datetime2ifc(data[name], "IfcDuration")
                )
                return True
            else:
                prop.data_type = "float"
                prop.float_value = 0.0 if prop.is_null else data[name]
                return True


class UnassignLagTime(bpy.types.Operator):
    bl_idname = "bim.unassign_lag_time"
    bl_label = "Unassign Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_lag_time", self.file, **{"rel_sequence": self.file.by_id(self.sequence)}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class AssignLagTime(bpy.types.Operator):
    bl_idname = "bim.assign_lag_time"
    bl_label = "Assign Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_lag_time",
            self.file,
            **{"rel_sequence": self.file.by_id(self.sequence), "lag_value": "P0D"},
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditSequenceAttributes(bpy.types.Operator):
    bl_idname = "bim.edit_sequence_attributes"
    bl_label = "Edit Sequence"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.sequence_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_sequence",
            self.file,
            **{"rel_sequence": self.file.by_id(props.active_sequence_id), "attributes": attributes},
        )
        Data.load(self.file)
        bpy.ops.bim.disable_editing_sequence()
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class EditSequenceTimeLag(bpy.types.Operator):
    bl_idname = "bim.edit_sequence_time_lag"
    bl_label = "Edit Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    lag_time: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        attributes = blenderbim.bim.helper.export_attributes(props.time_lag_attributes)
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.edit_lag_time",
            self.file,
            **{"lag_time": self.file.by_id(self.lag_time), "attributes": attributes},
        )
        Data.load(self.file)
        bpy.ops.bim.disable_editing_sequence()
        bpy.ops.bim.load_task_properties()
        return {"FINISHED"}


class DisableEditingSequence(bpy.types.Operator):
    bl_idname = "bim.disable_editing_sequence"
    bl_label = "Disable Editing Sequence Attributes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_sequence_id = 0
        return {"FINISHED"}


class SelectTaskRelatedProducts(bpy.types.Operator):
    bl_idname = "bim.select_task_related_products"
    bl_label = "Select Similar Type"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        related_products = ifcopenshell.api.run(
            "sequence.get_related_products", self.file, **{"related_object": self.file.by_id(self.task)}
        )
        for obj in context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in related_products:
                obj.select_set(True)
        return {"FINISHED"}


class VisualiseWorkScheduleDate(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date"
    bl_label = "Visualise Work Schedule Date"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        self.date = parser.parse(props.visualisation_start, dayfirst=True, fuzzy=True)
        self.preprocess_tasks()
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.hide_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in self.not_yet_started:
                obj.hide_set(True)
            elif obj.BIMObjectProperties.ifc_definition_id in self.started:
                obj.color = (0.0, 1.0, 0.0, 1)
            elif obj.BIMObjectProperties.ifc_definition_id in self.completed:
                pass
            else:
                obj.color = (1.0, 0.0, 0.0, 1)
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}

    def preprocess_tasks(self):
        self.not_yet_started = set()
        self.started = set()
        self.completed = set()
        for rel in self.file.by_id(self.work_schedule).Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTask"):
                    self.preprocess_task(related_object)

    def preprocess_task(self, task):
        for rel in task.IsNestedBy or []:
            for related_object in rel.RelatedObjects:
                self.preprocess_task(related_object)
        start = helper.derive_date(task.id(), "ScheduleStart", is_earliest=True)
        finish = helper.derive_date(task.id(), "ScheduleFinish", is_latest=True)
        if not start or not finish:
            return
        products = [r.RelatingProduct.id() for r in task.HasAssignments or [] if r.is_a("IfcRelAssignsToProduct")]
        if not products:
            return
        if self.date < start:
            self.not_yet_started.update(products)
        elif self.date < finish:
            self.started.update(products)
        else:
            self.completed.update(products)


class VisualiseWorkScheduleDateRange(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date_range"
    bl_label = "Visualise Work Schedule Date Range"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.start = parser.parse(self.props.visualisation_start, dayfirst=True, fuzzy=True)
        self.finish = parser.parse(self.props.visualisation_finish, dayfirst=True, fuzzy=True)
        self.duration = self.finish - self.start
        self.start_frame = 1
        self.total_frames = self.calculate_total_frames(context)
        self.preprocess_tasks()
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product_frames = self.product_frames.get(obj.BIMObjectProperties.ifc_definition_id, [])
            for product_frame in product_frames:
                if product_frame["relationship"] == "input":
                    self.animate_input(obj, product_frame)
                elif product_frame["relationship"] == "output":
                    self.animate_output(obj, product_frame)
        self.add_text_animation_handler()

        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        context.scene.frame_start = self.start_frame
        context.scene.frame_end = int(self.start_frame + self.total_frames)
        # with open("/home/dion/animation.json", "w") as json_file:
        #    guid_frames = {}
        #    for k, v in self.product_frames.items():
        #        guid_frames[self.file.by_id(k).GlobalId] = v
        #    json.dump(guid_frames, json_file)
        return {"FINISHED"}

    def add_text_animation_handler(self):
        data = bpy.data.curves.get("Timeline")
        if not data:
            data = bpy.data.curves.new(type="FONT", name="Timeline")
        obj = bpy.data.objects.get("Timeline")
        if not obj:
            obj = bpy.data.objects.new(name="Timeline", object_data=data)
            bpy.context.scene.collection.objects.link(obj)
        obj.data.BIMDateTextProperties.start_frame = self.start_frame
        obj.data.BIMDateTextProperties.total_frames = int(self.total_frames)
        obj.data.BIMDateTextProperties.start = self.props.visualisation_start
        obj.data.BIMDateTextProperties.finish = self.props.visualisation_finish
        bpy.app.handlers.frame_change_post.append(animate_text)

    def remove_text_animation_handler(self):
        bpy.app.handlers.frame_change_post.remove(animate_text)

    def animate_input(self, obj, product_frame):
        if product_frame["type"] in ["LOGISTIC", "MOVE", "DISPOSAL"]:
            self.animate_movement_from(obj, product_frame)
        else:
            self.animate_consumption(obj, product_frame)

    def animate_output(self, obj, product_frame):
        if product_frame["type"] in ["CONSTRUCTION", "INSTALLATION"]:
            self.animate_creation(obj, product_frame)
        elif product_frame["type"] in ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"]:
            self.animate_destruction(obj, product_frame)
        elif product_frame["type"] in ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"]:
            self.animate_operation(obj, product_frame)
        elif product_frame["type"] in ["LOGISTIC", "MOVE", "DISPOSAL"]:
            self.animate_movement_to(obj, product_frame)
        else:
            self.animate_operation(obj, product_frame)

    def animate_creation(self, obj, product_frame):
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
        obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (0.0, 1.0, 0.0, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_destruction(self, obj, product_frame):
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="color", frame=self.start_frame)
        obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
        obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.color = (1.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    def animate_operation(self, obj, product_frame):
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=self.start_frame)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.color = (0.0, 0.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_movement_to(self, obj, product_frame):
        obj.hide_viewport = True
        obj.hide_render = True
        obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
        obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (1.0, 1.0, 0.0, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_movement_from(self, obj, product_frame):
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=self.start_frame)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"] - 1)
        obj.color = (1.0, 0.5, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    def animate_consumption(self, obj, product_frame):
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=self.start_frame)
        obj.hide_viewport = False
        obj.hide_render = False
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"] - 1)
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"] - 1)
        obj.color = (0.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.hide_viewport = True
        obj.hide_render = True
        obj.color = (0.0, 0.0, 0.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["COMPLETED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["COMPLETED"])

    def calculate_total_frames(self, context):
        if self.props.speed_types == "FRAME_SPEED":
            return self.calculate_using_frames(
                self.start,
                self.finish,
                self.props.speed_animation_frames,
                isodate.parse_duration(self.props.speed_real_duration),
            )
        elif self.props.speed_types == "DURATION_SPEED":
            return self.calculate_using_duration(
                self.start,
                self.finish,
                context.scene.render.fps,
                isodate.parse_duration(self.props.speed_animation_duration),
                isodate.parse_duration(self.props.speed_real_duration),
            )
        elif self.props.speed_types == "MULTIPLIER_SPEED":
            return self.calculate_using_multiplier(
                self.start,
                self.finish,
                context.scene.render.fps,
                self.props.speed_multiplier,
            )

    def calculate_using_multiplier(self, start, finish, fps, multiplier):
        animation_time = (finish - start) / multiplier
        return animation_time.total_seconds() * fps

    def calculate_using_duration(self, start, finish, fps, animation_duration, real_duration):
        return self.calculate_using_multiplier(start, finish, fps, real_duration / animation_duration)

    def calculate_using_frames(self, start, finish, animation_frames, real_duration):
        return ((finish - start) / real_duration) * animation_frames

    def preprocess_tasks(self):
        self.product_frames = {}
        for rel in self.file.by_id(self.work_schedule).Controls or []:
            for related_object in rel.RelatedObjects:
                if related_object.is_a("IfcTask"):
                    self.preprocess_task(related_object)

    def preprocess_task(self, task):
        for rel in task.IsNestedBy or []:
            for related_object in rel.RelatedObjects:
                self.preprocess_task(related_object)
        start = helper.derive_date(task.id(), "ScheduleStart", is_earliest=True)
        finish = helper.derive_date(task.id(), "ScheduleFinish", is_latest=True)
        if not start or not finish:
            return
        for output_id in Data.tasks[task.id()]["Outputs"]:
            self.add_product_frame(output_id, task, start, finish, "output")
        for input_id in Data.tasks[task.id()]["Inputs"]:
            self.add_product_frame(input_id, task, start, finish, "input")

    def add_product_frame(self, product_id, task, start, finish, relationship):
        self.product_frames.setdefault(product_id, []).append(
            {
                "type": task.PredefinedType,
                "relationship": relationship,
                "STARTED": round(self.start_frame + (((start - self.start) / self.duration) * self.total_frames)),
                "COMPLETED": round(self.start_frame + (((finish - self.start) / self.duration) * self.total_frames)),
            }
        )


class BlenderBIM_DatePicker(bpy.types.Operator):
    bl_label = "Date Picker"
    bl_idname = "bim.datepicker"
    bl_options = {"REGISTER", "UNDO"}
    display_date: bpy.props.StringProperty(name="Display Date")
    target_prop: bpy.props.StringProperty(name="Target date prop to set")

    def execute(self, context):
        try:
            value = parser.parse(context.scene.DatePickerProperties.selected_date, dayfirst=True, fuzzy=True)
            self.set_scene_prop(self.target_prop, helper.canonicalise_time(value))
        except:
            pass
        return {"FINISHED"}

    def draw(self, context):
        current_date = parser.parse(context.scene.DatePickerProperties.display_date, dayfirst=True, fuzzy=True)
        current_month = (current_date.year, current_date.month)
        lines = calendar.monthcalendar(*current_month)
        month_title, week_titles = calendar.month(*current_month).splitlines()[:2]

        layout = self.layout
        row = layout.row()
        row.prop(context.scene.DatePickerProperties, "selected_date")

        split = layout.split()
        col = split.row()
        op = col.operator("bim.redraw_datepicker", icon="TRIA_LEFT", text="")
        op.action = "previous"
        col = split.row()
        col.label(text=month_title.strip())
        col = split.row()
        col.alignment = "RIGHT"
        op = col.operator("bim.redraw_datepicker", icon="TRIA_RIGHT", text="")
        op.action = "next"

        row = layout.row(align=True)
        for title in week_titles.split():
            col = row.column(align=True)
            col.alignment = "CENTER"
            col.label(text=title.strip())

        for line in lines:
            row = layout.row(align=True)
            for i in line:
                col = row.column(align=True)
                if i == 0:
                    col.label(text="  ")
                else:
                    op = col.operator("bim.datepicker_setdate", text="{:2d}".format(i))
                    selected_date = "{}/{}/{}".format(i, current_date.month, current_date.year)
                    selected_date = parser.parse(selected_date, dayfirst=True, fuzzy=True)
                    op.selected_date = helper.canonicalise_time(selected_date)

    def invoke(self, context, event):
        self.display_date = self.get_scene_prop(self.target_prop) or helper.canonicalise_time(datetime.now())
        context.scene.DatePickerProperties.display_date = self.display_date
        context.scene.DatePickerProperties.selected_date = self.display_date
        return context.window_manager.invoke_props_dialog(self)

    def get_scene_prop(self, prop_path):
        prop = bpy.context.scene.get(prop_path.split(".")[0])
        for part in prop_path.split(".")[1:]:
            if part:
                prop = prop.get(part)
        return prop

    def set_scene_prop(self, prop_path, value):
        parent = self.get_scene_prop(prop_path[: prop_path.rfind(".")])
        prop = prop_path.split(".")[-1]
        parent[prop] = value


class BlenderBIM_DatePickerSetDate(bpy.types.Operator):
    bl_label = "set date"
    bl_idname = "bim.datepicker_setdate"
    bl_options = {"REGISTER", "UNDO"}
    selected_date: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.DatePickerProperties.selected_date = self.selected_date
        return {"FINISHED"}


class BlenderBIM_RedrawDatePicker(bpy.types.Operator):
    bl_label = "redraw datepicker window"
    bl_idname = "bim.redraw_datepicker"
    bl_options = {"REGISTER", "UNDO"}
    action: bpy.props.StringProperty()

    def invoke(self, context, event):
        current_date = parser.parse(context.scene.DatePickerProperties.display_date, dayfirst=True, fuzzy=True)

        if self.action == "previous":
            date_to_set = current_date - relativedelta.relativedelta(months=1)
        elif self.action == "next":
            date_to_set = current_date + relativedelta.relativedelta(months=1)

        context.scene.DatePickerProperties.display_date = helper.canonicalise_time(date_to_set)

        return {"FINISHED"}


class RecalculateSchedule(bpy.types.Operator):
    bl_idname = "bim.recalculate_schedule"
    bl_label = "Recalculate Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.recalculate_schedule", self.file, work_schedule=self.file.by_id(self.work_schedule)
        )
        Data.load(self.file)
        return {"FINISHED"}


class AddTaskColumn(bpy.types.Operator):
    bl_idname = "bim.add_task_column"
    bl_label = "Add Task Column"
    bl_options = {"REGISTER", "UNDO"}
    column_type: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        new = self.props.columns.add()
        new.name = f"{self.column_type}.{self.name}"
        new.data_type = self.data_type
        return {"FINISHED"}


class RemoveTaskColumn(bpy.types.Operator):
    bl_idname = "bim.remove_task_column"
    bl_label = "Remove Task Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.columns.remove(self.props.columns.find(self.name))
        return {"FINISHED"}


class SetTaskSortColumn(bpy.types.Operator):
    bl_idname = "bim.set_task_sort_column"
    bl_label = "Set Task Sort Column"
    bl_options = {"REGISTER", "UNDO"}
    column: bpy.props.StringProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.sort_column = self.column
        bpy.ops.bim.enable_editing_tasks(work_schedule=self.props.active_work_schedule_id)
        return {"FINISHED"}


class LoadTaskResources(bpy.types.Operator):
    bl_idname = "bim.load_task_resources"
    bl_label = "Load Task Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        ifc_definition_id = self.tprops.tasks[self.props.active_task_index].ifc_definition_id
        self.props.task_resources.clear()
        for resource_id in Data.tasks[ifc_definition_id]["Resources"]:
            resource = self.file.by_id(resource_id)
            new = self.props.task_resources.add()
            new.ifc_definition_id = resource_id
            new.name = resource.Name or "Unnamed"
        return {"FINISHED"}


class LoadTaskInputs(bpy.types.Operator):
    bl_idname = "bim.load_task_inputs"
    bl_label = "Load Task Inputs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        ifc_definition_id = self.tprops.tasks[self.props.active_task_index].ifc_definition_id
        self.props.task_inputs.clear()
        for input_id in Data.tasks[ifc_definition_id]["Inputs"]:
            product = self.file.by_id(input_id)
            new = self.props.task_inputs.add()
            new.ifc_definition_id = input_id
            new.name = product.Name or "Unnamed"
        return {"FINISHED"}


class LoadTaskOutputs(bpy.types.Operator):
    bl_idname = "bim.load_task_outputs"
    bl_label = "Load Task Outputs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        ifc_definition_id = self.tprops.tasks[self.props.active_task_index].ifc_definition_id
        self.props.task_outputs.clear()
        for output_id in Data.tasks[ifc_definition_id]["Outputs"]:
            product = self.file.by_id(output_id)
            new = self.props.task_outputs.add()
            new.ifc_definition_id = output_id
            new.name = product.Name or "Unnamed"
        return {"FINISHED"}


class CalculateTaskDuration(bpy.types.Operator):
    bl_idname = "bim.calculate_task_duration"
    bl_label = "Calculate Task Duration"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.calculate_task_duration", self.file, task=self.file.by_id(self.task))
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}
