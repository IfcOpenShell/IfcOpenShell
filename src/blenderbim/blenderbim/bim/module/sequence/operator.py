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


class AddWorkPlan(bpy.types.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_plan", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkPlan(bpy.types.Operator):
    bl_idname = "bim.edit_work_plan"
    bl_label = "Edit Work Plan"

    def execute(self, context):
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
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "Duration" or prop.name == "TotalFloat":
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True


class RemoveWorkPlan(bpy.types.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_plan", self.file, **{"work_plan": self.file.by_id(self.work_plan)})
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        while len(props.work_plan_attributes) > 0:
            props.work_plan_attributes.remove(0)

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
    bl_label = "Disable Editing Work Plan"

    def execute(self, context):
        context.scene.BIMWorkPlanProperties.active_work_plan_id = 0
        return {"FINISHED"}


class EnableEditingWorkPlanSchedules(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan_schedules"
    bl_label = "Enable Editing Work Plan Schedules"
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkPlanProperties
        props.active_work_plan_id = self.work_plan
        props.editing_type = "SCHEDULES"
        return {"FINISHED"}


class AssignWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.assign_work_schedule"
    bl_label = "Assign Work Schedule"
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
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
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
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

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_schedule", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.edit_work_schedule"
    bl_label = "Edit Work Schedule"

    def execute(self, context):
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
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "Duration" or prop.name == "TotalFloat":
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True


class RemoveWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_schedule", self.file, work_schedule=self.file.by_id(self.work_schedule)
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_work_schedule_id = self.work_schedule
        while len(self.props.work_schedule_attributes) > 0:
            self.props.work_schedule_attributes.remove(0)
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
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        self.props.active_work_schedule_id = self.work_schedule
        while len(self.tprops.tasks) > 0:
            self.tprops.tasks.remove(0)

        self.contracted_tasks = json.loads(self.props.contracted_tasks)
        self.sort_keys = {
            i: Data.tasks[i]["Identification"] or "" for i in Data.work_schedules[self.work_schedule]["RelatedObjects"]
        }

        for related_object_id in sorted(self.sort_keys, key=self.natural_sort_key):
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
                self.sort_keys = {i: Data.tasks[i]["Identification"] or "" for i in task["RelatedObjects"]}
                for related_object_id in sorted(self.sort_keys, key=self.natural_sort_key):
                    self.create_new_task_li(related_object_id, level_index + 1)

    def natural_sort_key(self, i, _nsre=re.compile("([0-9]+)")):
        s = self.sort_keys[i]
        return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


class LoadTaskProperties(bpy.types.Operator):
    bl_idname = "bim.load_task_properties"
    bl_label = "Load Task Properties"
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

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_work_schedule_id = 0
        return {"FINISHED"}


class AddTask(bpy.types.Operator):
    bl_idname = "bim.add_task"
    bl_label = "Add Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, **{"parent_task": self.file.by_id(self.task)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class AddSummaryTask(bpy.types.Operator):
    bl_idname = "bim.add_summary_task"
    bl_label = "Add Task"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.add_task", self.file, **{"work_schedule": self.file.by_id(self.work_schedule)})
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class ExpandTask(bpy.types.Operator):
    bl_idname = "bim.expand_task"
    bl_label = "Expand Task"
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
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_task",
            self.file,
            task=IfcStore.get_file().by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.enable_editing_tasks(work_schedule=props.active_work_schedule_id)
        return {"FINISHED"}


class EnableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_time"
    bl_label = "Enable Editing Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()

        task_time_id = Data.tasks[self.task]["TaskTime"] or self.add_task_time().id()

        while len(props.task_time_attributes) > 0:
            props.task_time_attributes.remove(0)

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
        Data.load(IfcStore.get_file())
        return task_time


class EditTaskTime(bpy.types.Operator):
    bl_idname = "bim.edit_task_time"
    bl_label = "Edit Task Time"

    def execute(self, context):
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
            attributes[prop.name] = helper.parse_datetime(prop.string_value)
            return True
        elif prop.name == "ScheduleDuration":
            attributes[prop.name] = helper.parse_duration(prop.string_value)
            return True


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task"
    bl_label = "Enable Editing Task"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        while len(props.task_attributes) > 0:
            props.task_attributes.remove(0)

        data = Data.tasks[self.task]

        blenderbim.bim.helper.import_attributes("IfcTask", props.task_attributes, data)
        props.active_task_id = self.task
        props.editing_task_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingTask(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task"
    bl_label = "Disable Editing Task"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_id = 0
        context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        return {"FINISHED"}


class EditTask(bpy.types.Operator):
    bl_idname = "bim.edit_task"
    bl_label = "Edit Task"

    def execute(self, context):
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


class AssignPredecessor(bpy.types.Operator):
    bl_idname = "bim.assign_predecessor"
    bl_label = "Assign Predecessor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties(task=self.task)
        return {"FINISHED"}


class AssignSuccessor(bpy.types.Operator):
    bl_idname = "bim.assign_successor"
    bl_label = "Assign Successor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.assign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(props.active_task_id),
            related_process=IfcStore.get_file().by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties(task=self.task)
        return {"FINISHED"}


class UnassignPredecessor(bpy.types.Operator):
    bl_idname = "bim.unassign_predecessor"
    bl_label = "Unassign Predecessor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=IfcStore.get_file().by_id(self.task),
            related_process=IfcStore.get_file().by_id(props.active_task_id),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties(task=self.task)
        return {"FINISHED"}


class UnassignSuccessor(bpy.types.Operator):
    bl_idname = "bim.unassign_successor"
    bl_label = "Unassign Successor"
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_sequence",
            self.file,
            relating_process=self.file.by_id(props.active_task_id),
            related_process=self.file.by_id(self.task),
        )
        Data.load(self.file)
        bpy.ops.bim.load_task_properties(task=self.task)
        return {"FINISHED"}


class AssignProduct(bpy.types.Operator):
    bl_idname = "bim.assign_product"
    bl_label = "Assign Product"
    task: bpy.props.IntProperty()
    related_product: bpy.props.StringProperty()

    def execute(self, context):
        related_products = (
            [bpy.data.objects.get(self.related_product)] if self.related_product else bpy.context.selected_objects
        )
        for related_product in related_products:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "sequence.assign_product",
                self.file,
                relating_product=self.file.by_id(related_product.BIMObjectProperties.ifc_definition_id),
                related_object=self.file.by_id(self.task),
            )
        Data.load(self.file)
        return {"FINISHED"}


class UnassignProduct(bpy.types.Operator):
    bl_idname = "bim.unassign_product"
    bl_label = "Unassign Product"
    task: bpy.props.IntProperty()
    related_product: bpy.props.StringProperty()

    def execute(self, context):
        related_products = (
            [bpy.data.objects.get(self.related_product)] if self.related_product else bpy.context.selected_objects
        )
        for related_product in related_products:
            self.file = IfcStore.get_file()
            ifcopenshell.api.run(
                "sequence.unassign_product",
                self.file,
                relating_product=self.file.by_id(related_product.BIMObjectProperties.ifc_definition_id),
                related_object=self.file.by_id(self.task),
            )
        Data.load(self.file)
        return {"FINISHED"}


class GenerateGanttChart(bpy.types.Operator):
    bl_idname = "bim.generate_gantt_chart"
    bl_label = "Generate Gantt Chart"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.json = []
        for task_id in Data.work_schedules[self.work_schedule]["RelatedObjects"]:
            self.create_new_task_json(task_id)
        with open(os.path.join(bpy.context.scene.BIMProperties.data_dir, "gantt", "index.html"), "w") as f:
            with open(os.path.join(bpy.context.scene.BIMProperties.data_dir, "gantt", "index.mustache"), "r") as t:
                f.write(pystache.render(t.read(), {"json_data": json.dumps(self.json)}))
        webbrowser.open("file://" + os.path.join(bpy.context.scene.BIMProperties.data_dir, "gantt", "index.html"))
        return {"FINISHED"}

    def create_new_task_json(self, task_id):
        task = self.file.by_id(task_id)
        self.json.append(
            {
                "pID": task.id(),
                "pName": task.Name,
                "pStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
                "pEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
                "pPlanStart": task.TaskTime.ScheduleStart if task.TaskTime else "",
                "pPlanEnd": task.TaskTime.ScheduleFinish if task.TaskTime else "",
                "pClass": "ggroupblack",
                "pMile": 1 if task.IsMilestone else 0,
                "pComp": 0,
                "pGroup": 1,
                "pParent": task.Nests[0].RelatingObject.id() if task.Nests else 0,
                "pOpen": 1,
                "pCost": 1,
            }
        )
        for task_id in Data.tasks[task_id]["RelatedObjects"]:
            self.create_new_task_json(task_id)


class AddWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.add_work_calendar"
    bl_label = "Add Work Calendar"

    def execute(self, context):
        ifcopenshell.api.run("sequence.add_work_calendar", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.edit_work_calendar"
    bl_label = "Edit Work Calendar"

    def execute(self, context):
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
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.remove_work_calendar", self.file, **{"work_calendar": self.file.by_id(self.work_calendar)}
        )
        Data.load(self.file)
        return {"FINISHED"}


class EnableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar"
    bl_label = "Enable Editing Work Calendar"
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        while len(self.props.work_calendar_attributes) > 0:
            self.props.work_calendar_attributes.remove(0)

        data = Data.work_calendars[self.work_calendar]

        blenderbim.bim.helper.import_attributes("IfcWorkCalendar", self.props.work_calendar_attributes, data)
        self.props.active_work_calendar_id = self.work_calendar
        self.props.editing_type = "ATTRIBUTES"
        return {"FINISHED"}


class DisableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_calendar"
    bl_label = "Disable Editing Work Calendar"

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.active_work_calendar_id = 0
        return {"FINISHED"}


class ImportP6(bpy.types.Operator, ImportHelper):
    bl_idname = "import_p6.bim"
    bl_label = "Import P6"
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    def execute(self, context):
        from ifcp6.p62ifc import P62Ifc

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


class ImportMSP(bpy.types.Operator, ImportHelper):
    bl_idname = "import_msp.bim"
    bl_label = "Import MSP"
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    def execute(self, context):
        from ifcp6.msp2ifc import MSP2Ifc

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


class EnableEditingWorkCalendarTimes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar_times"
    bl_label = "Enable Editing Work Calendar Times"
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkCalendarProperties
        props.active_work_calendar_id = self.work_calendar
        props.editing_type = "WORKTIMES"
        return {"FINISHED"}


class AddWorkTime(bpy.types.Operator):
    bl_idname = "bim.add_work_time"
    bl_label = "Add Work Time"
    work_calendar: bpy.props.IntProperty()
    time_type: bpy.props.StringProperty()

    def execute(self, context):
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
    work_time: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkCalendarProperties
        while len(self.props.work_time_attributes) > 0:
            self.props.work_time_attributes.remove(0)

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

    def execute(self, context):
        context.scene.BIMWorkCalendarProperties.active_work_time_id = 0
        return {"FINISHED"}


class EditWorkTime(bpy.types.Operator):
    bl_idname = "bim.edit_work_time"
    bl_label = "Edit Work Time"

    def execute(self, context):
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
    work_time: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("sequence.remove_work_time", self.file, **{"work_time": self.file.by_id(self.work_time)})
        Data.load(self.file)
        return {"FINISHED"}


class AssignRecurrencePattern(bpy.types.Operator):
    bl_idname = "bim.assign_recurrence_pattern"
    bl_label = "Assign Recurrence Pattern"
    work_time: bpy.props.IntProperty()
    recurrence_type: bpy.props.StringProperty()

    def execute(self, context):
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
    recurrence_pattern: bpy.props.IntProperty()

    def execute(self, context):
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
    recurrence_pattern: bpy.props.IntProperty()

    def execute(self, context):
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
    time_period: bpy.props.IntProperty()

    def execute(self, context):
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
    task: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.BIMWorkScheduleProperties
        props.active_task_id = self.task
        props.editing_task_type = "CALENDAR"
        return {"FINISHED"}


class EditTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.edit_task_calendar"
    bl_label = "Edit Task Calendar"
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "control.assign_control",
            self.file,
            **{
                "relating_control": self.file.by_id(self.work_calendar),
                "related_object": self.file.by_id(self.task),
            },
        )
        Data.load(IfcStore.get_file())
        if Data.tasks[self.task]["RelatedObjects"]:
            bpy.ops.bim.load_task_properties()
        else:
            bpy.ops.bim.load_task_properties(task=self.task)
        return {"FINISHED"}


class RemoveTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.remove_task_calendar"
    bl_label = "Remove Task Calendar"
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "control.unassign_control",
            self.file,
            **{
                "relating_control": self.file.by_id(self.work_calendar),
                "related_object": self.file.by_id(self.task),
            },
        )
        Data.load(IfcStore.get_file())
        if Data.tasks[self.task]["RelatedObjects"]:
            bpy.ops.bim.load_task_properties()
        else:
            bpy.ops.bim.load_task_properties(task=self.task)
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

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_task_time_id = 0
        bpy.ops.bim.disable_editing_task()
        return {"FINISHED"}


class EnableEditingSequenceAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_attributes"
    bl_label = "Enable Editing Sequence Attributes"
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_sequence_id = self.sequence
        self.props.editing_sequence_type = "ATTRIBUTES"
        while len(self.props.sequence_attributes) > 0:
            self.props.sequence_attributes.remove(0)
        self.enable_editing_sequence_attributes()
        return {"FINISHED"}

    def enable_editing_sequence_attributes(self):
        data = Data.sequences[self.sequence]
        blenderbim.bim.helper.import_attributes("IfcRelSequence", self.props.sequence_attributes, data)


class EnableEditingSequenceTimeLag(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_time_lag"
    bl_label = "Enable Editing Sequence Time Lag"
    sequence: bpy.props.IntProperty()
    lag_time: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.props.active_sequence_id = self.sequence
        self.props.editing_sequence_type = "TIME_LAG"
        while len(self.props.time_lag_attributes) > 0:
            self.props.time_lag_attributes.remove(0)
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
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "sequence.unassign_lag_time", self.file, **{"rel_sequence": self.file.by_id(self.sequence)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AssignLagTime(bpy.types.Operator):
    bl_idname = "bim.assign_lag_time"
    bl_label = "Assign Time Lag"
    sequence: bpy.props.IntProperty()

    def execute(self, context):
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

    def execute(self, context):
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
        return {"FINISHED"}


class EditSequenceTimeLag(bpy.types.Operator):
    bl_idname = "bim.edit_sequence_time_lag"
    bl_label = "Edit Time Lag"
    lag_time: bpy.props.IntProperty()

    def execute(self, context):
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
        return {"FINISHED"}


class DisableEditingSequence(bpy.types.Operator):
    bl_idname = "bim.disable_editing_sequence"
    bl_label = "Disable Editing Sequence Attributes"

    def execute(self, context):
        context.scene.BIMWorkScheduleProperties.active_sequence_id = 0
        return {"FINISHED"}


class SelectTaskRelatedProducts(bpy.types.Operator):
    bl_idname = "bim.select_task_related_products"
    bl_label = "Select Similar Type"
    task: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        related_products = ifcopenshell.api.run(
            "sequence.get_related_products", self.file, **{"related_object": self.file.by_id(self.task)}
        )
        for obj in bpy.context.visible_objects:
            obj.select_set(False)
            if obj.BIMObjectProperties.ifc_definition_id in related_products:
                obj.select_set(True)
        return {"FINISHED"}


class VisualiseWorkScheduleDate(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date"
    bl_label = "Visualise Work Schedule Date"
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
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        self.props = context.scene.BIMWorkScheduleProperties
        self.start = parser.parse(self.props.visualisation_start, dayfirst=True, fuzzy=True)
        self.finish = parser.parse(self.props.visualisation_finish, dayfirst=True, fuzzy=True)
        self.duration = self.finish - self.start
        self.start_frame = 1
        self.total_frames = self.calculate_total_frames()
        self.preprocess_tasks()
        for obj in bpy.data.objects:
            if not obj.BIMObjectProperties.ifc_definition_id:
                continue
            product_frames = self.product_frames.get(obj.BIMObjectProperties.ifc_definition_id)
            if not product_frames:
                continue
            obj.hide_viewport = True
            obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
            obj.hide_viewport = False
            obj.color = (0.0, 1.0, 0.0, 1)
            obj.keyframe_insert(data_path="hide_viewport", frame=product_frames["STARTED"])
            obj.keyframe_insert(data_path="color", frame=product_frames["STARTED"])
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=product_frames["COMPLETED"])
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        context.scene.frame_start = self.start_frame
        context.scene.frame_end = self.start_frame + self.total_frames
        return {"FINISHED"}

    def calculate_total_frames(self):
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
                bpy.context.scene.render.fps,
                isodate.parse_duration(self.props.speed_animation_duration),
                isodate.parse_duration(self.props.speed_real_duration),
            )
        elif self.props.speed_types == "MULTIPLIER_SPEED":
            return self.calculate_using_multiplier(
                self.start,
                self.finish,
                bpy.context.scene.render.fps,
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
        product_ids = [r.RelatingProduct.id() for r in task.HasAssignments or [] if r.is_a("IfcRelAssignsToProduct")]
        for product_id in product_ids:
            self.product_frames[product_id] = {
                "STARTED": round(self.start_frame + (((start - self.start) / self.duration) * self.total_frames)),
                "COMPLETED": round(self.start_frame + (((finish - self.start) / self.duration) * self.total_frames)),
            }


class BlenderBIM_DatePicker(bpy.types.Operator):
    bl_label = "Date Picker"
    bl_idname = "bim.datepicker"
    display_date: bpy.props.StringProperty(name="Display Date")
    selected_date: bpy.props.StringProperty(name="Selected Date")
    target_prop: bpy.props.StringProperty(name="Target date prop to set")

    def execute(self, context):
        helper.set_scene_prop(self.target_prop, self.selected_date)
        return {"FINISHED"}

    def draw(self, context):
        self.selected_date = helper.get_scene_prop("DatePickerProperties.selected_date") or helper.canonicalise_time(datetime.now())
        current_date = parser.parse(context.scene.DatePickerProperties.display_date, dayfirst=True, fuzzy=True)
        current_month = (current_date.year, current_date.month)
        lines = calendar.monthcalendar(*current_month)
        month_title, week_titles = calendar.month(*current_month).splitlines()[:2]

        layout = self.layout
        row = layout.row()
        row.prop(self, "selected_date")

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
        self.display_date = helper.get_scene_prop(self.target_prop) or helper.canonicalise_time(datetime.now())
        context.scene.DatePickerProperties.display_date = self.display_date
        context.scene.DatePickerProperties.selected_date = self.display_date
        return context.window_manager.invoke_props_dialog(self)


class BlenderBIM_DatePickerSetDate(bpy.types.Operator):
    bl_label = "set date"
    bl_idname = "bim.datepicker_setdate"
    selected_date: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.DatePickerProperties.selected_date = self.selected_date
        return {"FINISHED"}


class BlenderBIM_RedrawDatePicker(bpy.types.Operator):
    bl_label = "redraw datepicker window"
    bl_idname = "bim.redraw_datepicker"
    action: bpy.props.StringProperty()

    def invoke(self, context, event):
        current_date = parser.parse(context.scene.DatePickerProperties.display_date, dayfirst=True, fuzzy=True)

        if self.action == "previous":
            date_to_set = current_date - relativedelta.relativedelta(months=1)
        elif self.action == "next":
            date_to_set = current_date + relativedelta.relativedelta(months=1)

        context.scene.DatePickerProperties.display_date = helper.canonicalise_time(date_to_set)

        return {"FINISHED"}
