# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
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
import blenderbim.core.sequence as core
import blenderbim.tool as tool
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


class AddWorkPlan(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_plan"
    bl_label = "Add Work Plan"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_work_plan(tool.Ifc)


class EditWorkPlan(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_work_plan"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Edit Work Plan"

    def _execute(self, context):
        core.edit_work_plan(
            tool.Ifc,
            tool.Sequence,
            work_plan=tool.Ifc.get().by_id(context.scene.BIMWorkPlanProperties.active_work_plan_id),
        )


class RemoveWorkPlan(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_work_plan"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_work_plan(tool.Ifc, work_plan=tool.Ifc.get().by_id(self.work_plan))


class EnableEditingWorkPlan(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_work_plan(tool.Sequence, work_plan=tool.Ifc.get().by_id(self.work_plan))


class DisableEditingWorkPlan(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_work_plan"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Work Plan"

    def _execute(self, context):
        core.disable_editing_work_plan(tool.Sequence)


class EnableEditingWorkPlanSchedules(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan_schedules"
    bl_label = "Enable Editing Work Plan Schedules"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_plan_schedules(tool.Sequence, work_plan=tool.Ifc.get().by_id(self.work_plan))
        return {"FINISHED"}


class AssignWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_work_schedule"
    bl_label = "Assign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_work_schedule(
            tool.Ifc,
            tool.Sequence,
            work_plan=tool.Ifc.get().by_id(self.work_plan),
            work_schedule=tool.Ifc.get().by_id(self.work_schedule),
        )


class UnassignWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_work_schedule"
    bl_label = "Unassign Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_work_schedule(
            tool.Ifc,
            work_plan=tool.Ifc.get().by_id(self.work_plan),
            work_schedule=tool.Ifc.get().by_id(self.work_schedule),
        )


class AddWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_work_schedule(tool.Ifc)


class EditWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_work_schedule"
    bl_label = "Edit Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_work_schedule(
            tool.Ifc,
            tool.Sequence,
            work_schedule=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_work_schedule_id),
        )


class RemoveWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_work_schedule"
    bl_label = "Remove Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_work_schedule(tool.Ifc, work_schedule=tool.Ifc.get().by_id(self.work_schedule))


class EnableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule"
    bl_label = "Enable Editing Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_schedule(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


class EnableEditingWorkScheduleTasks(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_schedule_tasks"
    bl_label = "Enable Editing Tasks"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_schedule_tasks(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


class LoadTaskProperties(bpy.types.Operator):
    bl_idname = "bim.load_task_properties"
    bl_label = "Load Task Properties"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_task_properties(tool.Sequence)
        return {"FINISHED"}


class DisableEditingWorkSchedule(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_schedule"
    bl_label = "Disable Editing Work Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_work_schedule(tool.Sequence)
        return {"FINISHED"}


class AddTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_task(tool.Ifc, tool.Sequence, parent_task=tool.Ifc.get().by_id(self.task))


class AddSummaryTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_summary_task"
    bl_label = "Add Task"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_summary_task(tool.Ifc, tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))


class ExpandTask(bpy.types.Operator):
    bl_idname = "bim.expand_task"
    bl_label = "Expand Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.expand_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class ContractTask(bpy.types.Operator):
    bl_idname = "bim.contract_task"
    bl_label = "Contract Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.contract_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class RemoveTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_task"
    bl_label = "Remove Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_task(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class EnableEditingTaskTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_task_time"
    bl_label = "Enable Editing Task Time"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_task_time(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class EditTaskTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_task_time"
    bl_label = "Edit Task Time"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_task_time(
            tool.Ifc,
            tool.Sequence,
            task_time=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_task_time_id),
        )


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task"
    bl_label = "Enable Editing Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class DisableEditingTask(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task"
    bl_label = "Disable Editing Task"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_task(tool.Sequence)
        return {"FINISHED"}


class EditTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_task"
    bl_label = "Edit Task"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_task(
            tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_task_id)
        )


class CopyTaskAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_task_attribute"
    bl_label = "Copy Task Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.copy_task_attribute(tool.Ifc, tool.Sequence, attribute_name=self.name)


class AssignPredecessor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_predecessor"
    bl_label = "Assign Predecessor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_predecessor(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class AssignSuccessor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_successor"
    bl_label = "Assign Successor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_successor(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class UnassignPredecessor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_predecessor"
    bl_label = "Unassign Predecessor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_predecessor(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class UnassignSuccessor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_successor"
    bl_label = "Unassign Successor"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_successor(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class AssignProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_product"
    bl_label = "Assign Product"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    relating_product: bpy.props.IntProperty()

    def _execute(self, context):
        if self.relating_product:
            core.assign_products(
                tool.Ifc,
                tool.Sequence,
                task=tool.Ifc.get().by_id(self.task),
                products=[tool.Ifc.get().by_id(self.relating_product)],
            )
        else:
            core.assign_products(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class UnassignProduct(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_product"
    bl_label = "Unassign Product"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    relating_product: bpy.props.IntProperty()

    def _execute(self, context):
        if self.relating_product:
            core.unassign_products(
                tool.Ifc,
                tool.Sequence,
                task=tool.Ifc.get().by_id(self.task),
                products=[tool.Ifc.get().by_id(self.relating_product)],
            )
        else:
            core.unassign_products(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class AssignProcess(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_process"
    bl_label = "Assign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        if self.related_object_type == "RESOURCE":
            core.assign_resource(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        elif self.related_object_type == "PRODUCT":
            if self.related_object:
                core.assign_input_products(
                    tool.Ifc,
                    tool.Sequence,
                    task=tool.Ifc.get().by_id(self.task),
                    products=[tool.Ifc.get().by_id(self.related_object)],
                )
            else:
                core.assign_input_products(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        elif self.related_object_type == "CONTROL":
            pass  # TODO


class UnassignProcess(bpy.types.Operator):
    bl_idname = "bim.unassign_process"
    bl_label = "Unassign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.IntProperty()
    resource: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        if self.related_object_type == "RESOURCE":
            core.unassign_resource(
                tool.Ifc,
                tool.Sequence,
                task=tool.Ifc.get().by_id(self.task),
                resource=tool.Ifc.get().by_id(self.resource),
            )

        elif self.related_object_type == "PRODUCT":
            if self.related_object:
                core.unassign_input_products(
                    tool.Ifc,
                    tool.Sequence,
                    task=tool.Ifc.get().by_id(self.task),
                    products=[tool.Ifc.get().by_id(self.related_object)],
                )
            else:
                core.unassign_input_products(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        elif self.related_object_type == "CONTROL":
            pass  # TODO
        return {"FINISHED"}


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
        Data.load(self.file)
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
            "pCaption": task.Name,
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
            "ifcduration": task.TaskTime.ScheduleDuration if task.TaskTime else "",
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


class AddWorkCalendar(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_calendar"
    bl_label = "Add Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_work_calendar(tool.Ifc)


class EditWorkCalendar(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_work_calendar"
    bl_label = "Edit Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_work_calendar(
            tool.Ifc,
            tool.Sequence,
            work_calendar=tool.Ifc.get().by_id(context.scene.BIMWorkCalendarProperties.active_work_calendar_id),
        )


class RemoveWorkCalendar(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_work_calendar"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_work_calendar(tool.Ifc, work_calendar=tool.Ifc.get().by_id(self.work_calendar))


class EnableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_calendar"
    bl_label = "Enable Editing Work Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_calendar(tool.Sequence, work_calendar=tool.Ifc.get().by_id(self.work_calendar))
        return {"FINISHED"}


class DisableEditingWorkCalendar(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_calendar"
    bl_label = "Disable Editing Work Calendar"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_work_calendar(tool.Sequence)
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
        core.enable_editing_work_calendar_times(tool.Sequence, work_calendar=tool.Ifc.get().by_id(self.work_calendar))
        return {"FINISHED"}


class AddWorkTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_time"
    bl_label = "Add Work Time"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    time_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_work_time(tool.Ifc, work_calendar=tool.Ifc.get().by_id(self.work_calendar), time_type=self.time_type)


class EnableEditingWorkTime(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_time"
    bl_label = "Enable Editing Work Time"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_time(tool.Sequence, work_time=tool.Ifc.get().by_id(self.work_time))
        return {"FINISHED"}


class DisableEditingWorkTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_time"
    bl_label = "Disable Editing Work Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_work_time(tool.Sequence)
        return {"FINISHED"}


class EditWorkTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_work_time"
    bl_label = "Edit Work Time"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_work_time(tool.Ifc, tool.Sequence)


class RemoveWorkTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_work_time"
    bl_label = "Remove Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_work_time(tool.Ifc, work_time=tool.Ifc.get().by_id(self.work_time))
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
        core.assign_recurrence_pattern(
            tool.Ifc, work_time=tool.Ifc.get().by_id(self.work_time), recurrence_type=self.recurrence_type
        )
        return {"FINISHED"}


class UnassignRecurrencePattern(bpy.types.Operator):
    bl_idname = "bim.unassign_recurrence_pattern"
    bl_label = "Unassign Recurrence Pattern"
    bl_options = {"REGISTER", "UNDO"}
    recurrence_pattern: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        core.unassign_recurrence_pattern(tool.Ifc, recurrence_pattern=tool.Ifc.get().by_id(self.recurrence_pattern))
        return {"FINISHED"}


class AddTimePeriod(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_time_period"
    bl_label = "Add Time Period"
    bl_options = {"REGISTER", "UNDO"}
    recurrence_pattern: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_time_period(tool.Ifc, tool.Sequence, recurrence_pattern=tool.Ifc.get().by_id(self.recurrence_pattern))


class RemoveTimePeriod(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_time_period"
    bl_label = "Remove Time Period"
    bl_options = {"REGISTER", "UNDO"}
    time_period: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_time_period(tool.Ifc, time_period=tool.Ifc.get().by_id(self.time_period))


class EnableEditingTaskCalendar(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_calendar"
    bl_label = "Enable Editing Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_task_calendar(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class EditTaskCalendar(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_task_calendar"
    bl_label = "Edit Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_task_calendar(
            tool.Ifc,
            tool.Sequence,
            task=tool.Ifc.get().by_id(self.task),
            work_calendar=tool.Ifc.get().by_id(self.work_calendar),
        )


class RemoveTaskCalendar(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_task_calendar"
    bl_label = "Remove Task Calendar"
    bl_options = {"REGISTER", "UNDO"}
    work_calendar: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_task_calendar(
            tool.Ifc,
            tool.Sequence,
            task=tool.Ifc.get().by_id(self.task),
            work_calendar=tool.Ifc.get().by_id(self.work_calendar),
        )


class EnableEditingTaskSequence(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_sequence"
    bl_label = "Enable Editing Task Sequence"
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_task_sequence(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        return {"FINISHED"}


class DisableEditingTaskTime(bpy.types.Operator):
    bl_idname = "bim.disable_editing_task_time"
    bl_label = "Disable Editing Task Time"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_task_time(tool.Sequence)
        return {"FINISHED"}


class EnableEditingSequenceAttributes(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_attributes"
    bl_label = "Enable Editing Sequence Attributes"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_sequence_attributes(tool.Sequence, rel_sequence=tool.Ifc.get().by_id(self.sequence))
        return {"FINISHED"}


class EnableEditingSequenceTimeLag(bpy.types.Operator):
    bl_idname = "bim.enable_editing_sequence_lag_time"
    bl_label = "Enable Editing Sequence Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()
    lag_time: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_sequence_lag_time(
            tool.Sequence,
            rel_sequence=tool.Ifc.get().by_id(self.sequence),
            lag_time=tool.Ifc.get().by_id(self.lag_time),
        )
        return {"FINISHED"}


class UnassignLagTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_lag_time"
    bl_label = "Unassign Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_lag_time(tool.Ifc, tool.Sequence, rel_sequence=tool.Ifc.get().by_id(self.sequence))


class AssignLagTime(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_lag_time"
    bl_label = "Assign Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    sequence: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_lag_time(tool.Ifc, rel_sequence=tool.Ifc.get().by_id(self.sequence))


class EditSequenceAttributes(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_sequence_attributes"
    bl_label = "Edit Sequence"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_sequence_attributes(
            tool.Ifc,
            tool.Sequence,
            rel_sequence=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_sequence_id),
        )


class EditSequenceTimeLag(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_sequence_lag_time"
    bl_label = "Edit Time Lag"
    bl_options = {"REGISTER", "UNDO"}
    lag_time: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_sequence_lag_time(tool.Ifc, tool.Sequence, lag_time=tool.Ifc.get().by_id(self.lag_time))


class DisableEditingSequence(bpy.types.Operator):
    bl_idname = "bim.disable_editing_sequence"
    bl_label = "Disable Editing Sequence Attributes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_rel_sequence(tool.Sequence)
        return {"FINISHED"}


class SelectTaskRelatedProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_task_related_products"
    bl_label = "Select All Output Products"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_task_outputs(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class SelectTaskRelatedInputs(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_task_related_inputs"
    bl_label = "Select All Input Products"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_task_inputs(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


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
        start = helper.derive_date(task, "ScheduleStart", is_earliest=True)
        finish = helper.derive_date(task, "ScheduleFinish", is_latest=True)
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
            self.earliest_frame = None
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
        elif product_frame["type"] in ["DEMOLITION", "DISMANTLE", "DISPOSAL", "REMOVAL"]:
            self.animate_destruction(obj, product_frame)
        else:
            self.animate_consumption(obj, product_frame)

    def animate_output(self, obj, product_frame):
        if product_frame["type"] in ["CONSTRUCTION", "INSTALLATION", "NOTDEFINED"]:
            self.animate_creation(obj, product_frame)
        elif product_frame["type"] in ["ATTENDANCE", "MAINTENANCE", "OPERATION", "RENOVATION"]:
            self.animate_operation(obj, product_frame)
        elif product_frame["type"] in ["LOGISTIC", "MOVE", "DISPOSAL"]:
            self.animate_movement_to(obj, product_frame)
        else:
            self.animate_operation(obj, product_frame)

    def animate_creation(self, obj, product_frame):
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (0.0, 1.0, 0.0, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_destruction(self, obj, product_frame):
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.hide_viewport = False
            obj.hide_render = False
            obj.keyframe_insert(data_path="color", frame=self.start_frame)
            obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
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
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"] - 1)
        obj.color = (0.0, 0.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_movement_to(self, obj, product_frame):
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.hide_viewport = True
            obj.hide_render = True
            obj.keyframe_insert(data_path="hide_viewport", frame=self.start_frame)
            obj.keyframe_insert(data_path="hide_render", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
        obj.hide_viewport = False
        obj.hide_render = False
        obj.color = (1.0, 1.0, 0.0, 1)
        obj.keyframe_insert(data_path="hide_viewport", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="hide_render", frame=product_frame["STARTED"])
        obj.keyframe_insert(data_path="color", frame=product_frame["STARTED"])
        obj.color = (1.0, 1.0, 1.0, 1)
        obj.keyframe_insert(data_path="color", frame=product_frame["COMPLETED"])

    def animate_movement_from(self, obj, product_frame):
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
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
        if self.earliest_frame is None or product_frame["STARTED"] < self.earliest_frame:
            obj.color = (1.0, 1.0, 1.0, 1)
            obj.keyframe_insert(data_path="color", frame=self.start_frame)
            self.earliest_frame = product_frame["STARTED"]
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
        start = helper.derive_date(task, "ScheduleStart", is_earliest=True)
        finish = helper.derive_date(task, "ScheduleFinish", is_latest=True)
        if not start or not finish:
            return
        if not Data.is_loaded:
            Data.load(self.file)  # TO DO: REFACTOR OPERATOR
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


class RecalculateSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_schedule"
    bl_label = "Recalculate Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.recalculate_schedule(tool.Ifc, work_schedule=tool.Ifc.get().by_id(self.work_schedule))


class AddTaskColumn(bpy.types.Operator):
    bl_idname = "bim.add_task_column"
    bl_label = "Add Task Column"
    bl_options = {"REGISTER", "UNDO"}
    column_type: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        core.add_task_column(tool.Sequence, self.column_type, self.name, self.data_type)
        return {"FINISHED"}


class RemoveTaskColumn(bpy.types.Operator):
    bl_idname = "bim.remove_task_column"
    bl_label = "Remove Task Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        core.remove_task_column(tool.Sequence, self.name)
        return {"FINISHED"}


class SetTaskSortColumn(bpy.types.Operator):
    bl_idname = "bim.set_task_sort_column"
    bl_label = "Set Task Sort Column"
    bl_options = {"REGISTER", "UNDO"}
    column: bpy.props.StringProperty()

    def execute(self, context):
        core.set_task_sort_column(tool.Sequence, self.column)
        return {"FINISHED"}


class LoadTaskResources(bpy.types.Operator):
    bl_idname = "bim.load_task_resources"
    bl_label = "Load Task Resources"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_task_resources(tool.Sequence)
        return {"FINISHED"}


class LoadTaskInputs(bpy.types.Operator):
    bl_idname = "bim.load_task_inputs"
    bl_label = "Load Task Inputs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_task_inputs(tool.Sequence)
        return {"FINISHED"}


class LoadTaskOutputs(bpy.types.Operator):
    bl_idname = "bim.load_task_outputs"
    bl_label = "Load Task Outputs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_task_outputs(tool.Sequence)
        return {"FINISHED"}


class CalculateTaskDuration(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_task_duration"
    bl_label = "Calculate Task Duration"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.calculate_task_duration(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class HighlightProductRelatedTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.highlight_product_related_task"
    bl_label = "Highlights the related task"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.highlight_product_related_task(tool.Sequence, product_type=self.product_type)


class ExpandAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_all_tasks"
    bl_label = "Expands all tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.expand_all_tasks(tool.Sequence)


class ContractAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_all_tasks"
    bl_label = "Expands all tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.contract_all_tasks(tool.Sequence)
