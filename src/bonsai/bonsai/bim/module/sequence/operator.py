# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>
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
import bpy
import json
import time
import calendar
import isodate
import bonsai.core.sequence as core
import bonsai.tool as tool
import bonsai.bim.module.sequence.helper as helper
import ifcopenshell.util.sequence
import ifcopenshell.util.selector
from datetime import datetime
from dateutil import parser, relativedelta
from bonsai.bim.ifc import IfcStore
from bpy_extras.io_utils import ImportHelper


class EnableStatusFilters(bpy.types.Operator):
    bl_idname = "bim.enable_status_filters"
    bl_label = "Enable Status Filters"

    def execute(self, context):
        props = context.scene.BIMStatusProperties
        props.is_enabled = True

        props.statuses.clear()

        statuses = set()
        for element in tool.Ifc.get().by_type("IfcPropertyEnumeratedValue"):
            if element.Name == "Status":
                pset = element.PartOfPset[0]
                if pset.Name.startswith("Pset_") and pset.Name.endswith("Common"):
                    statuses.update(element.EnumerationValues)
                elif pset.Name == "EPset_Status":  # Our secret sauce
                    statuses.update(element.EnumerationValues)
            elif element.Name == "UserDefinedStatus":
                statuses.add(element.NominalValue)

        statuses = ["No Status"] + sorted([s.wrappedValue for s in statuses])

        for status in statuses:
            new = props.statuses.add()
            new.name = status
        return {"FINISHED"}


class DisableStatusFilters(bpy.types.Operator):
    bl_idname = "bim.disable_status_filters"
    bl_label = "Disable Status Filters"
    bl_description = "Deactivate status filters panel.\nCan be used to refresh the displayed statuses"

    def execute(self, context):
        props = context.scene.BIMStatusProperties
        props.is_enabled = False
        return {"FINISHED"}


class ActivateStatusFilters(bpy.types.Operator):
    bl_idname = "bim.activate_status_filters"
    bl_label = "Activate Status Filters"
    bl_description = "Filter and display objects based on currently selected IFC statuses"

    def execute(self, context):
        props = context.scene.BIMStatusProperties

        query = []
        visible_statuses = {s.name for s in props.statuses if s.is_visible}
        for name in visible_statuses:
            if name == "No Status":
                q = f"IfcProduct, /Pset_.*Common/.Status=NULL, EPset_Status.Status=NULL"
            else:
                q = f"IfcProduct, /Pset_.*Common/.Status={name} + IfcProduct, EPset_Status.Status={name}"
            query.append(q)
        query = " + ".join(query)

        if not query:
            self.report({"INFO"}, "No statuses selected.")
            return {"FINISHED"}

        visible_elements = ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query)

        for obj in bpy.context.view_layer.objects:
            element = tool.Ifc.get_entity(obj)
            if not element or not element.is_a("IfcProduct"):
                continue
            obj.hide_set(element not in visible_elements)
        return {"FINISHED"}


class SelectStatusFilter(bpy.types.Operator):
    bl_idname = "bim.select_status_filter"
    bl_label = "Select Status Filter"
    bl_description = "Select elements with currently selected status"
    name: bpy.props.StringProperty()

    def execute(self, context):
        props = context.scene.BIMStatusProperties
        query = f"IfcProduct, /Pset_.*Common/.Status={self.name} + IfcProduct, EPset_Status.Status={self.name}"
        if self.name == "No Status":
            query = f"IfcProduct, /Pset_.*Common/.Status=NULL, EPset_Status.Status=NULL"
        for element in ifcopenshell.util.selector.filter_elements(tool.Ifc.get(), query):
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
        return {"FINISHED"}


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


class EnableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.enable_editing_work_plan"
    bl_label = "Enable Editing Work Plan"
    bl_options = {"REGISTER", "UNDO"}
    work_plan: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_work_plan(tool.Sequence, work_plan=tool.Ifc.get().by_id(self.work_plan))
        return {"FINISHED"}


class DisableEditingWorkPlan(bpy.types.Operator):
    bl_idname = "bim.disable_editing_work_plan"
    bl_options = {"REGISTER", "UNDO"}
    bl_label = "Disable Editing Work Plan"

    def execute(self, context):
        core.disable_editing_work_plan(tool.Sequence)
        return {"FINISHED"}


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
            work_schedule=tool.Ifc.get().by_id(self.work_schedule),
        )


class AddWorkSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_work_schedule"
    bl_label = "Add Work Schedule"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_work_schedule(tool.Ifc, tool.Sequence, name=self.name)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Name")
        self.props = context.scene.BIMWorkScheduleProperties
        layout.prop(self.props, "work_schedule_predefined_types", text="Type")
        if self.props.work_schedule_predefined_types == "USERDEFINED":
            layout.prop(self.props, "object_type", text="Object type")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


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
    bl_label = "Enable Editing Work Schedule Tasks"
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
    # IFC operator is needed because operator is adding a new task time to IFC
    # if it doesn't exist.
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
            tool.Resource,
            task_time=tool.Ifc.get().by_id(context.scene.BIMWorkScheduleProperties.active_task_time_id),
        )


class EnableEditingTask(bpy.types.Operator):
    bl_idname = "bim.enable_editing_task_attributes"
    bl_label = "Enable Editing Task Attributes"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_task_attributes(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
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
                tool.Spatial,
                task=tool.Ifc.get().by_id(self.task),
                products=[tool.Ifc.get().by_id(self.relating_product)],
            )
        else:
            core.assign_products(tool.Ifc, tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task))


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
                tool.Spatial,
                task=tool.Ifc.get().by_id(self.task),
                products=[tool.Ifc.get().by_id(self.relating_product)],
            )
        else:
            core.unassign_products(tool.Ifc, tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task))


class AssignProcess(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_process"
    bl_label = "Assign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, properties):
        return f"Assign selected {properties.related_object_type} to the selected task"

    def _execute(self, context):
        if self.related_object_type == "RESOURCE":
            core.assign_resource(tool.Ifc, tool.Sequence, tool.Resource, task=tool.Ifc.get().by_id(self.task))
        elif self.related_object_type == "PRODUCT":
            if self.related_object:
                core.assign_input_products(
                    tool.Ifc,
                    tool.Sequence,
                    tool.Spatial,
                    task=tool.Ifc.get().by_id(self.task),
                    products=[tool.Ifc.get().by_id(self.related_object)],
                )
            else:
                core.assign_input_products(tool.Ifc, tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task))
        elif self.related_object_type == "CONTROL":
            self.report({"ERROR"}, "Assigning process control is not yet supported")  # TODO


class UnassignProcess(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_process"
    bl_label = "Unassign Process"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    related_object: bpy.props.IntProperty()
    resource: bpy.props.IntProperty()

    @classmethod
    def description(cls, context, properties):
        return f"Unassign selected {properties.related_object_type} from the selected task"

    def _execute(self, context):
        if self.related_object_type == "RESOURCE":
            core.unassign_resource(
                tool.Ifc,
                tool.Sequence,
                tool.Resource,
                task=tool.Ifc.get().by_id(self.task),
                resource=tool.Ifc.get().by_id(self.resource),
            )

        elif self.related_object_type == "PRODUCT":
            if self.related_object:
                core.unassign_input_products(
                    tool.Ifc,
                    tool.Sequence,
                    tool.Spatial,
                    task=tool.Ifc.get().by_id(self.task),
                    products=[tool.Ifc.get().by_id(self.related_object)],
                )
            else:
                core.unassign_input_products(
                    tool.Ifc, tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task)
                )
        elif self.related_object_type == "CONTROL":
            pass  # TODO
        return {"FINISHED"}


class GenerateGanttChart(bpy.types.Operator):
    bl_idname = "bim.generate_gantt_chart"
    bl_label = "Generate Gantt Chart"
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.generate_gantt_chart(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


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


class ImportCSV(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_csv"
    bl_label = "Import CSV"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.csv4d2ifc import Csv2Ifc

        self.file = tool.Ifc.get()
        start = time.time()
        csv2ifc = Csv2Ifc()
        csv2ifc.csv = self.filepath
        csv2ifc.file = self.file
        csv2ifc.execute()
        self.report({"INFO"}, "Imported in %s seconds" % (time.time() - start))


class ImportP6(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_p6"
    bl_label = "Import P6"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.p62ifc import P62Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        p62ifc = P62Ifc()
        p62ifc.xml = self.filepath
        p62ifc.file = self.file
        p62ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p62ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))


class ImportP6XER(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_p6xer"
    bl_label = "Import P6 XER"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xer"
    filter_glob: bpy.props.StringProperty(default="*.xer", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.p6xer2ifc import P6XER2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        p6xer2ifc = P6XER2Ifc()
        p6xer2ifc.xer = self.filepath
        p6xer2ifc.file = self.file
        p6xer2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        p6xer2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))


class ImportPP(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_pp"
    bl_label = "Import Powerproject .pp"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".pp"
    filter_glob: bpy.props.StringProperty(default="*.pp", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.pp2ifc import PP2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        pp2ifc = PP2Ifc()
        pp2ifc.pp = self.filepath
        pp2ifc.file = self.file
        pp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        pp2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))


class ImportMSP(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_msp"
    bl_label = "Import MSP"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        from ifc4d.msp2ifc import MSP2Ifc

        self.file = IfcStore.get_file()
        start = time.time()
        msp2ifc = MSP2Ifc()
        msp2ifc.xml = self.filepath
        msp2ifc.file = self.file
        msp2ifc.work_plan = self.file.by_type("IfcWorkPlan")[0] if self.file.by_type("IfcWorkPlan") else None
        msp2ifc.execute()
        self.report({"INFO"}, "Import finished in {:.2f} seconds".format(time.time() - start))


class ExportMSP(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.export_msp"
    bl_label = "Export MSP"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

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
        self.report({"INFO"}, "Export finished in {:.2f} seconds".format(time.time() - start))
        return {"FINISHED"}


class ExportP6(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.export_p6"
    bl_label = "Export P6"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".xml"
    filter_glob: bpy.props.StringProperty(default="*.xml", options={"HIDDEN"})
    holiday_start_date: bpy.props.StringProperty(default="2022-01-01", name="Holiday Start Date")
    holiday_finish_date: bpy.props.StringProperty(default="2023-01-01", name="Holiday Finish Date")

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

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
        self.report({"INFO"}, "Export finished in {:.2f} seconds".format(time.time() - start))
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


class AssignRecurrencePattern(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_recurrence_pattern"
    bl_label = "Assign Recurrence Pattern"
    bl_options = {"REGISTER", "UNDO"}
    work_time: bpy.props.IntProperty()
    recurrence_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.assign_recurrence_pattern(
            tool.Ifc, work_time=tool.Ifc.get().by_id(self.work_time), recurrence_type=self.recurrence_type
        )
        return {"FINISHED"}


class UnassignRecurrencePattern(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_recurrence_pattern"
    bl_label = "Unassign Recurrence Pattern"
    bl_options = {"REGISTER", "UNDO"}
    recurrence_pattern: bpy.props.IntProperty()

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
        core.enable_editing_task_sequence(tool.Sequence)
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
    bl_label = "Disable Editing Sequence"
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
        core.select_task_outputs(tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task))


class SelectTaskRelatedInputs(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_task_related_inputs"
    bl_label = "Select All Input Products"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_task_inputs(tool.Sequence, tool.Spatial, task=tool.Ifc.get().by_id(self.task))


class VisualiseWorkScheduleDate(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date"
    bl_label = "Visualise Work Schedule Date"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return bool(bpy.context.scene.BIMWorkScheduleProperties.visualisation_start)

    def execute(self, context):
        core.visualise_work_schedule_date(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


class GuessDateRange(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.guess_date_range"
    bl_label = "Guess Work Schedule Date Range"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.guess_date_range(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))


class VisualiseWorkScheduleDateRange(bpy.types.Operator):
    bl_idname = "bim.visualise_work_schedule_date_range"
    bl_label = "Visualise Work Schedule Date Range"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        has_start, has_finish = (
            bpy.context.scene.BIMWorkScheduleProperties.visualisation_start,
            bpy.context.scene.BIMWorkScheduleProperties.visualisation_finish,
        )
        return bool(has_start and has_finish) and not "-" in (has_start, has_finish)

    def execute(self, context):
        core.visualise_work_schedule_date_range(tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule))
        return {"FINISHED"}


class Bonsai_DatePicker(bpy.types.Operator):
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

    def get_scene_prop(self, prop_path: str) -> str:
        scene = bpy.context.scene
        return scene.path_resolve(prop_path)

    def set_scene_prop(self, prop_path: str, value: str) -> None:
        scene = bpy.context.scene
        tool.Blender.set_prop_from_path(scene, prop_path, value)


class Bonsai_DatePickerSetDate(bpy.types.Operator):
    bl_label = "Set Date"
    bl_idname = "bim.datepicker_setdate"
    bl_options = {"REGISTER", "UNDO"}
    selected_date: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.scene.DatePickerProperties.selected_date = self.selected_date
        return {"FINISHED"}


class Bonsai_RedrawDatePicker(bpy.types.Operator):
    bl_label = "Redraw Datepicker Window"
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


class SetupDefaultTaskColumns(bpy.types.Operator):
    bl_idname = "bim.setup_default_task_columns"
    bl_label = "Setip Default Task Columns"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.setup_default_task_columns(tool.Sequence)
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


class CalculateTaskDuration(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_task_duration"
    bl_label = "Calculate Task Duration"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.calculate_task_duration(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class ExpandAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_all_tasks"
    bl_label = "Expands All Tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.expand_all_tasks(tool.Sequence)


class ContractAllTasks(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_all_tasks"
    bl_label = "Expands All Tasks"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Finds the related Task"
    product_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.contract_all_tasks(tool.Sequence)


class AddTaskBars(bpy.types.Operator):
    bl_idname = "bim.add_task_bars"
    bl_label = "Show Task Bars"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Shows the Status of each task"

    def execute(self, context):
        core.add_task_bars(tool.Sequence)
        return {"FINISHED"}


class LoadDefaultAnimationColors(bpy.types.Operator):
    bl_idname = "bim.load_default_animation_color_scheme"
    bl_label = "Load Animation Colors"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_default_animation_color_scheme(tool.Sequence)
        return {"FINISHED"}


class SaveAnimationColorScheme(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.save_animation_color_scheme"
    bl_label = "Save Animation Color Scheme"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Saves the current animation color scheme"
    name: bpy.props.StringProperty()

    def _execute(self, context):
        if not self.name:
            return
        core.save_animation_color_scheme(tool.Sequence, name=self.name)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class LoadAnimationColorScheme(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_animation_color_scheme"
    bl_label = "Load Animation Color Scheme"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Loads the animation color scheme"

    def _execute(self, context):
        group = tool.Ifc.get().by_id(int(context.scene.BIMAnimationProperties.saved_color_schemes))
        core.load_animation_color_scheme(tool.Sequence, scheme=group)

    def draw(self, context):
        props = context.scene.BIMAnimationProperties
        row = self.layout.row()
        row.prop(props, "saved_color_schemes", text="")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class CopyTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.duplicate_task"
    bl_label = "Copy Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def _execute(self, context):
        core.duplicate_task(tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task))


class LoadProductTasks(bpy.types.Operator):
    bl_idname = "bim.load_product_related_tasks"
    bl_label = "Load Product Tasks"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not (obj := context.active_object) or not (obj.BIMObjectProperties.ifc_definition_id):
            cls.poll_message_set("No IFC object is active.")
            return False
        return True

    def execute(self, context):
        result = core.load_product_related_tasks(
            tool.Sequence, product=tool.Ifc.get().by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        )
        if isinstance(result, str):
            self.report({"INFO"}, result)
        else:
            self.report({"INFO"}, f"{len(result)} product tasks loaded.")
        return {"FINISHED"}


class GoToTask(bpy.types.Operator):
    bl_idname = "bim.go_to_task"
    bl_label = "Highlight Task"
    bl_options = {"REGISTER", "UNDO"}
    task: bpy.props.IntProperty()

    def execute(self, context):
        r = core.go_to_task(tool.Sequence, task=tool.Ifc.get().by_id(self.task))
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class SelectWorkScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_work_schedule_products"
    bl_label = "Select Work Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        r = core.select_work_schedule_products(
            tool.Sequence, tool.Spatial, work_schedule=tool.Ifc.get().by_id(self.work_schedule)
        )
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class SelectUnassignedWorkScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_unassigned_work_schedule_products"
    bl_label = "Select Unassigned Work Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        r = core.select_unassigned_work_schedule_products(tool.Ifc, tool.Sequence, tool.Spatial)
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class ReorderTask(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_task_nesting"
    bl_label = "Reorder Nesting"
    bl_options = {"REGISTER", "UNDO"}
    new_index: bpy.props.IntProperty()
    task: bpy.props.IntProperty()

    def _execute(self, context):
        r = core.reorder_task_nesting(
            tool.Ifc, tool.Sequence, task=tool.Ifc.get().by_id(self.task), new_index=self.new_index
        )
        if isinstance(r, str):
            self.report({"WARNING"}, r)


class CreateBaseline(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.create_baseline"
    bl_label = "Create Schedule Baseline"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.create_baseline(
            tool.Ifc, tool.Sequence, work_schedule=tool.Ifc.get().by_id(self.work_schedule), name=self.name
        )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Baseline Name")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class ClearPreviousAnimation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_previous_animation"
    bl_label = "Clear Previous Animation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.clear_previous_animation(tool.Sequence)


class AddAnimationCamera(bpy.types.Operator):
    bl_idname = "bim.add_animation_camera"
    bl_label = "Add Camera to Scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.add_animation_camera(tool.Sequence)
        return {"FINISHED"}
