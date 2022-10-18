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
import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.helper import draw_attributes
from blenderbim.bim.module.sequence.data import SequenceData
from ifcopenshell.api.resource.data import Data as ResourceData


class BIM_PT_work_plans(Panel):
    bl_label = "IFC Work Plans"
    bl_idname = "BIM_PT_work_plans"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_4D5D"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and file.schema != "IFC2X3"

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()
        self.props = context.scene.BIMWorkPlanProperties

        row = self.layout.row()
        if SequenceData.data["has_work_plans"]:
            row.label(
                text="{} Work Plans Found".format(SequenceData.data["number_of_work_plans_loaded"]),
                icon="TEXT",
            )
        else:
            row.label(text="No Work Plans found.", icon="TEXT")
        row.operator("bim.add_work_plan", icon="ADD", text="")
        for work_plan_id, work_plan in SequenceData.data["work_plans"].items():
            self.draw_work_plan_ui(work_plan_id, work_plan)

    def draw_work_plan_ui(self, work_plan_id, work_plan):
        row = self.layout.row(align=True)
        row.label(text=work_plan["Name"] or "Unnamed", icon="TEXT")

        if self.props.active_work_plan_id == work_plan_id:
            if self.props.editing_type == "ATTRIBUTES":
                row.operator("bim.edit_work_plan", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_plan", text="", icon="CANCEL")
        elif self.props.active_work_plan_id:
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan_id
        else:
            op = row.operator("bim.enable_editing_work_plan_schedules", text="", icon="LINENUMBERS_ON")
            op.work_plan = work_plan_id
            op = row.operator("bim.enable_editing_work_plan", text="", icon="GREASEPENCIL")
            op.work_plan = work_plan_id
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan_id

        if self.props.active_work_plan_id == work_plan_id:
            if self.props.editing_type == "ATTRIBUTES":
                self.draw_editable_ui()
            elif self.props.editing_type == "SCHEDULES":
                self.draw_work_schedule_ui()

    def draw_editable_ui(self):
        draw_attributes(self.props.work_plan_attributes, self.layout)

    def draw_work_schedule_ui(self):
        if not SequenceData.is_loaded:
            SequenceData.load()

        if SequenceData.data["has_work_schedules"]:
            row = self.layout.row(align=True)
            row.prop(self.props, "work_schedules", text="")
            op = row.operator("bim.assign_work_schedule", text="", icon="ADD")
            op.work_plan = self.props.active_work_plan_id
            op.work_schedule = int(self.props.work_schedules)
            for work_schedule_id in SequenceData.data["work_plans"][self.props.active_work_plan_id]["IsDecomposedBy"]:
                work_schedule = SequenceData.data["work_schedules"][work_schedule_id]
                row = self.layout.row(align=True)
                row.label(text=work_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")
                op = row.operator("bim.unassign_work_schedule", text="", icon="X")
                op.work_plan = self.props.active_work_plan_id
                op.work_schedule = int(self.props.work_schedules)
        else:
            row = self.layout.row()
            row.label(text="No schedules found. See Work Schedule Panel", icon="INFO")


class BIM_PT_work_schedules(Panel):
    bl_label = "IFC Work Schedules"
    bl_idname = "BIM_PT_work_schedules"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_4D5D"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties

        row = self.layout.row()
        if SequenceData.data["has_work_schedules"]:
            row.label(
                text="{} Work Schedules Found".format(SequenceData.data["number_of_work_schedules_loaded"]),
                icon="TEXT",
            )
        else:
            row.label(text="No Work Schedules found.", icon="TEXT")
        row.operator("bim.add_work_schedule", text="", icon="ADD")

        for work_schedule_id, work_schedule in SequenceData.data["work_schedules"].items():
            self.draw_work_schedule_ui(work_schedule_id, work_schedule)

    def draw_work_schedule_ui(self, work_schedule_id, work_schedule):
        row = self.layout.row(align=True)
        row.label(text=work_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")

        if self.props.active_work_schedule_id == work_schedule_id:
            if self.props.editing_type == "WORK_SCHEDULE":
                row.operator("bim.edit_work_schedule", text="", icon="CHECKMARK")
            elif self.props.editing_type == "TASKS":
                row.prop(self.props, "should_show_column_ui", text="", icon="SHORTDISPLAY")
                row.prop(self.props, "should_show_visualisation_ui", text="", icon="CAMERA_STEREO")
                row.operator("bim.generate_gantt_chart", text="", icon="NLA").work_schedule = work_schedule_id
                row.operator("bim.recalculate_schedule", text="", icon="FILE_REFRESH").work_schedule = work_schedule_id
                row.operator("bim.add_summary_task", text="", icon="ADD").work_schedule = work_schedule_id
            row.operator("bim.disable_editing_work_schedule", text="", icon="CANCEL")
        else:
            row.operator(
                "bim.enable_editing_work_schedule_tasks", text="", icon="ACTION"
            ).work_schedule = work_schedule_id
            row.operator(
                "bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL"
            ).work_schedule = work_schedule_id
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id

        if self.props.active_work_schedule_id == work_schedule_id:
            if self.props.editing_type == "WORK_SCHEDULE":
                self.draw_editable_work_schedule_ui()
            elif self.props.editing_type == "TASKS":
                if self.props.should_show_column_ui:
                    self.draw_column_ui()
                if self.props.should_show_visualisation_ui:
                    self.draw_visualisation_ui()
                self.draw_editable_task_ui(work_schedule_id)

    def draw_task_operators(self):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        ifc_definition_id = None
        if self.tprops.tasks and self.props.active_task_index < len(self.tprops.tasks):
            task = self.tprops.tasks[self.props.active_task_index]
            ifc_definition_id = task.ifc_definition_id
        if ifc_definition_id:
            if self.props.active_task_id:
                if self.props.editing_task_type == "TASKTIME":
                    row.operator("bim.edit_task_time", text="", icon="CHECKMARK")
                elif self.props.editing_task_type == "ATTRIBUTES":
                    row.operator("bim.edit_task", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_task", text="", icon="CANCEL")
            else:
                row.operator("bim.enable_editing_task_sequence", text="", icon="TRACKING").task = ifc_definition_id
                row.operator("bim.enable_editing_task_time", text="", icon="TIME").task = ifc_definition_id
                row.operator("bim.enable_editing_task_calendar", text="", icon="VIEW_ORTHO").task = ifc_definition_id
                row.operator("bim.enable_editing_task", text="", icon="GREASEPENCIL").task = ifc_definition_id
                row.operator("bim.add_task", text="", icon="ADD").task = ifc_definition_id
                row.operator("bim.remove_task", text="", icon="X").task = ifc_definition_id

    def draw_column_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "column_types", text="")
        column_type = self.props.column_types
        if self.props.column_types == "IfcTask":
            row.prop(self.props, "task_columns", text="")
            name, data_type = self.props.task_columns.split("/")
        elif self.props.column_types == "IfcTaskTime":
            row.prop(self.props, "task_time_columns", text="")
            name, data_type = self.props.task_time_columns.split("/")
        elif self.props.column_types == "Special":
            row.prop(self.props, "other_columns", text="")
            column_type, name = self.props.other_columns.split(".")
            data_type = "string"
        row.operator("bim.set_task_sort_column", text="", icon="SORTALPHA").column = f"{column_type}.{name}"
        row.prop(
            self.props, "is_sort_reversed", text="", icon="SORT_DESC" if self.props.is_sort_reversed else "SORT_ASC"
        )
        op = row.operator("bim.add_task_column", text="", icon="ADD")
        op.column_type = column_type
        op.name = name
        op.data_type = data_type

        self.layout.template_list("BIM_UL_task_columns", "", self.props, "columns", self.props, "active_column_index")

    def draw_visualisation_ui(self):
        row = self.layout.row(align=True)
        op = row.operator("bim.datepicker", text=self.props.visualisation_start or "Start Date", icon="REW")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_start"
        op = row.operator("bim.datepicker", text=self.props.visualisation_finish or "Finish Date", icon="FF")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_finish"
        op = row.operator("bim.visualise_work_schedule_date", text="", icon="RESTRICT_RENDER_OFF")
        op.work_schedule = self.props.active_work_schedule_id
        op = row.operator("bim.visualise_work_schedule_date_range", text="", icon="OUTLINER_OB_CAMERA")
        op.work_schedule = self.props.active_work_schedule_id

        row = self.layout.row(align=True)
        row.prop(self.props, "speed_types", text="")
        if self.props.speed_types == "FRAME_SPEED":
            row.prop(self.props, "speed_animation_frames", text="")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "DURATION_SPEED":
            row.prop(self.props, "speed_animation_duration", text="")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "MULTIPLIER_SPEED":
            row.prop(self.props, "speed_multiplier", text="")

    def draw_editable_work_schedule_ui(self):
        draw_attributes(self.props.work_schedule_attributes, self.layout)

    def draw_editable_task_ui(self, work_schedule_id):
        self.draw_task_operators()
        self.layout.template_list(
            "BIM_UL_tasks",
            "",
            self.tprops,
            "tasks",
            self.props,
            "active_task_index",
        )
        row = self.layout.row()
        row.operator("bim.expand_all_tasks", text="Expand All Tasks")
        row.operator("bim.contract_all_tasks", text="Contract All Tasks")
        if self.props.active_task_id and self.props.editing_task_type == "ATTRIBUTES":
            self.draw_editable_task_attributes_ui()
        elif self.props.active_task_id and self.props.editing_task_type == "CALENDAR":
            self.draw_editable_task_calendar_ui()
        elif self.props.active_task_id and self.props.editing_task_type == "SEQUENCE":
            self.draw_editable_task_sequence_ui()
        elif self.props.active_task_time_id and self.props.editing_task_type == "TASKTIME":
            self.draw_editable_task_time_attributes_ui()

    def draw_editable_task_sequence_ui(self):
        task = SequenceData.data["tasks"][self.props.active_task_id]
        row = self.layout.row()
        row.label(text="{} Predecessors".format(len(task["IsSuccessorFrom"])), icon="BACK")
        for sequence_id in task["IsSuccessorFrom"]:
            self.draw_editable_sequence_ui(SequenceData.data["sequences"][sequence_id], "RelatingProcess")

        row = self.layout.row()
        row.label(text="{} Successors".format(len(task["IsPredecessorTo"])), icon="FORWARD")
        for sequence_id in task["IsPredecessorTo"]:
            self.draw_editable_sequence_ui(SequenceData.data["sequences"][sequence_id], "RelatedProcess")

    def draw_editable_sequence_ui(self, sequence, process_type):
        task = SequenceData.data["tasks"][sequence[process_type]]
        row = self.layout.row(align=True)
        row.label(text=task["Identification"] or "XXX")
        row.label(text=task["Name"] or "Unnamed")
        row.label(text=sequence["SequenceType"] or "N/A")
        if sequence["TimeLag"]:
            row.operator("bim.unassign_lag_time", text="", icon="X").sequence = sequence["id"]
            row.label(text=isodate.duration_isoformat(SequenceData.data["lag_times"][sequence["TimeLag"]]["LagValue"]))
        else:
            row.operator("bim.assign_lag_time", text="Add Time Lag", icon="ADD").sequence = sequence["id"]
        if self.props.active_sequence_id == sequence["id"]:
            if self.props.editing_sequence_type == "ATTRIBUTES":
                row.operator("bim.edit_sequence_attributes", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_sequence", text="", icon="CANCEL")
                self.draw_editable_sequence_attributes_ui()
            elif self.props.editing_sequence_type == "LAG_TIME":
                op = row.operator("bim.edit_sequence_lag_time", text="", icon="CHECKMARK")
                op.lag_time = sequence["TimeLag"]
                row.operator("bim.disable_editing_sequence", text="", icon="CANCEL")
                self.draw_editable_sequence_lag_time_ui()
        else:
            if sequence["TimeLag"]:
                op = row.operator("bim.enable_editing_sequence_lag_time", text="Edit Time Lag", icon="CON_LOCKTRACK")
                op.sequence = sequence["id"]
                op.lag_time = sequence["TimeLag"]
            op = row.operator("bim.enable_editing_sequence_attributes", text="Edit Sequence", icon="GREASEPENCIL")
            op.sequence = sequence["id"]

    def draw_editable_sequence_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.sequence_attributes, self.layout)

    def draw_editable_sequence_lag_time_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.lag_time_attributes, self.layout)

    def draw_editable_task_calendar_ui(self):
        task = SequenceData.data["tasks"][self.props.active_task_id]
        if task["HasAssignmentsWorkCalendar"]:
            row = self.layout.row(align=True)
            calendar = SequenceData.data["work_calendars"][task["HasAssignmentsWorkCalendar"][0]]
            row.label(text=calendar["Name"] or "Unnamed")
            op = row.operator("bim.remove_task_calendar", text="", icon="X")
            op.work_calendar = task["HasAssignmentsWorkCalendar"][0]
            op.task = self.props.active_task_id
        elif SequenceData.data["has_work_calendars"]:
            row = self.layout.row(align=True)
            row.prop(self.props, "work_calendars", text="")
            op = row.operator("bim.edit_task_calendar", text="", icon="ADD")
            op.work_calendar = int(self.props.work_calendars)
            op.task = self.props.active_task_id
        else:
            row = self.layout.row(align=True)
            row.label(text="Must Create a Calendar First. See Work Calendar Panel", icon="INFO")

    def draw_editable_task_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(
            self.props.task_attributes, self.layout, copy_operator="bim.copy_task_attribute"
        )

    def draw_editable_task_time_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.task_time_attributes, self.layout)


class BIM_PT_task_icom(Panel):
    bl_label = "IFC Task ICOM"
    bl_idname = "BIM_PT_task_icom"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_work_schedules"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMWorkScheduleProperties
        if not props.active_work_schedule_id:
            return False
        total_tasks = len(context.scene.BIMTaskTreeProperties.tasks)
        if total_tasks > 0 and props.active_task_index < total_tasks:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        task = self.tprops.tasks[self.props.active_task_index]

        grid = self.layout.grid_flow(columns=3, even_columns=True)

        # Column1
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Inputs")
        total_task_inputs = len(self.props.task_inputs)

        if context.selected_objects:
            op = row2.operator("bim.assign_process", icon="ADD", text="")
            op.task = task.ifc_definition_id
            op.related_object_type = "PRODUCT"
        if total_task_inputs:
            op = row2.operator("bim.unassign_process", icon="REMOVE", text="")
            op.task = task.ifc_definition_id
            op.related_object_type = "PRODUCT"
            if not context.selected_objects and self.props.active_task_input_index < total_task_inputs:
                input_id = self.props.task_inputs[self.props.active_task_input_index].ifc_definition_id
                op.related_object = input_id

        op = row2.operator("bim.select_task_related_inputs", icon="RESTRICT_SELECT_OFF", text="")
        op.task = task.ifc_definition_id

        row2 = col.row()
        row2.template_list("BIM_UL_task_inputs", "", self.props, "task_inputs", self.props, "active_task_input_index")

        # Column2
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Resources")

        op = row2.operator("bim.calculate_task_duration", text="", icon="TEMP")
        op.task = task.ifc_definition_id

        resource_props = context.scene.BIMResourceProperties
        resource_tprops = context.scene.BIMResourceTreeProperties
        total_resources = len(resource_tprops.resources)
        if total_resources and context.scene.BIMResourceProperties.active_resource_index < total_resources:
            resource_id = resource_tprops.resources[resource_props.active_resource_index].ifc_definition_id
            ResourceData.load(IfcStore.get_file())
            resource = ResourceData.resources[resource_id]
            if resource["type"] != "IfcCrewResource":
                op = row2.operator("bim.assign_process", icon="ADD", text="")
                op.task = task.ifc_definition_id
                op.related_object_type = "RESOURCE"

        total_task_resources = len(self.props.task_resources)
        if total_task_resources and self.props.active_task_resource_index < total_task_resources:
            op = row2.operator("bim.unassign_process", icon="REMOVE", text="")
            op.task = task.ifc_definition_id
            op.related_object_type = "RESOURCE"
            op.resource = self.props.task_resources[self.props.active_task_resource_index].ifc_definition_id

        row2 = col.row()
        row2.template_list(
            "BIM_UL_task_resources", "", self.props, "task_resources", self.props, "active_task_resource_index"
        )

        # Column3
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Outputs")
        total_task_outputs = len(self.props.task_outputs)

        if context.selected_objects:
            op = row2.operator("bim.assign_product", icon="ADD", text="")
            op.task = task.ifc_definition_id
        if total_task_outputs:
            op = row2.operator("bim.unassign_product", icon="REMOVE", text="")
            op.task = task.ifc_definition_id
            if not context.selected_objects and self.props.active_task_output_index < total_task_outputs:
                output_id = self.props.task_outputs[self.props.active_task_output_index].ifc_definition_id
                op.relating_product = output_id

        op = row2.operator("bim.select_task_related_products", icon="RESTRICT_SELECT_OFF", text="")
        op.task = task.ifc_definition_id

        row2 = col.row()
        row2.template_list(
            "BIM_UL_task_outputs", "", self.props, "task_outputs", self.props, "active_task_output_index"
        )


class BIM_UL_task_columns(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMWorkScheduleProperties
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")
            if props.sort_column == item.name:
                row.label(text="", icon="SORTALPHA")
            row.operator("bim.remove_task_column", text="", icon="X").name = item.name


class BIM_UL_task_inputs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMWorkScheduleProperties
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")
            # row.operator("bim.remove_task_column", text="", icon="X").name = item.name


class BIM_UL_task_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMWorkScheduleProperties
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")


class BIM_UL_task_outputs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMWorkScheduleProperties
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")


class BIM_UL_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            self.props = context.scene.BIMWorkScheduleProperties
            task = IfcStore.get_file().by_id(item.ifc_definition_id)
            row = layout.row(align=True)

            self.draw_hierarchy(row, item)

            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", emboss=False, text="")
            split2 = split1.split(factor=0.9 - min(0.5, 0.15 * len(self.props.columns)))
            split2.prop(item, "name", emboss=False, text="")

            self.draw_custom_columns(split2, item, task)

            if self.props.active_task_id and self.props.editing_task_type == "ATTRIBUTES":
                row.prop(
                    item,
                    "is_selected",
                    icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT",
                    text="",
                    emboss=False,
                )

            if self.props.active_task_id:
                if self.props.editing_task_type == "SEQUENCE" and self.props.active_task_id != item.ifc_definition_id:
                    if item.is_predecessor:
                        op = row.operator("bim.unassign_predecessor", text="", icon="BACK", emboss=False)
                    else:
                        op = row.operator("bim.assign_predecessor", text="", icon="TRACKING_BACKWARDS", emboss=False)
                    op.task = item.ifc_definition_id

                    if item.is_successor:
                        op = row.operator("bim.unassign_successor", text="", icon="FORWARD", emboss=False)
                    else:
                        op = row.operator("bim.assign_successor", text="", icon="TRACKING_FORWARDS", emboss=False)
                    op.task = item.ifc_definition_id

    def draw_hierarchy(self, row, item):
        for i in range(0, item.level_index):
            row.label(text="", icon="BLANK1")
        if item.has_children:
            if item.is_expanded:
                row.operator(
                    "bim.contract_task", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                ).task = item.ifc_definition_id
            else:
                row.operator(
                    "bim.expand_task", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                ).task = item.ifc_definition_id
        else:
            row.label(text="", icon="DOT")

    def draw_custom_columns(self, row, item, task):
        for column in self.props.columns:
            if column.name == "IfcTaskTime.ScheduleStart":
                if item.derived_start:
                    row.label(text=item.derived_start + "*")
                else:
                    row.prop(item, "start", emboss=False, text="")
            elif column.name == "IfcTaskTime.ScheduleFinish":
                if item.derived_finish:
                    row.label(text=item.derived_finish + "*")
                else:
                    row.prop(item, "finish", emboss=False, text="")
            elif column.name == "IfcTaskTime.ScheduleDuration":
                if item.derived_duration:
                    row.label(text=item.derived_duration + "*")
                else:
                    row.prop(item, "duration", emboss=False, text="")
            elif column.name == "Controls.Calendar":
                if item.derived_calendar:
                    row.label(text=item.derived_calendar + "*")
                else:
                    row.label(text=item.calendar or "-")
            else:
                ifc_class, name = column.name.split(".")
                if ifc_class == "IfcTask":
                    value = getattr(task, name)
                elif ifc_class == "IfcTaskTime":
                    value = getattr(task.TaskTime, name) if task.TaskTime else None
                if value is None:
                    value = "-"
                row.label(text=str(value))


class BIM_PT_work_calendars(Panel):
    bl_label = "IFC Work Calendars"
    bl_idname = "BIM_PT_work_calendars"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_4D5D"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()

        self.props = context.scene.BIMWorkCalendarProperties
        row = self.layout.row()
        if SequenceData.data["has_work_calendars"]:
            row.label(
                text="{} Work Calendars Found".format(SequenceData.data["number_of_work_calendars_loaded"]),
                icon="TEXT",
            )
        else:
            row.label(text="No Work Calendars found.", icon="TEXT")
        row.operator("bim.add_work_calendar", icon="ADD", text="")
        for work_calendar_id, work_calendar in SequenceData.data["work_calendars"].items():
            self.draw_work_calendar_ui(work_calendar_id, work_calendar)

    def draw_work_calendar_ui(self, work_calendar_id, work_calendar):
        row = self.layout.row(align=True)
        row.label(text=work_calendar["Name"] or "Unnamed", icon="VIEW_ORTHO")
        if self.props.active_work_calendar_id == work_calendar_id:
            if self.props.editing_type == "ATTRIBUTES":
                row.operator("bim.edit_work_calendar", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_calendar", text="", icon="CANCEL")
        elif self.props.active_work_calendar_id:
            row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = work_calendar_id
        else:
            op = row.operator("bim.enable_editing_work_calendar_times", text="", icon="MESH_GRID")
            op.work_calendar = work_calendar_id
            op = row.operator("bim.enable_editing_work_calendar", text="", icon="GREASEPENCIL")
            op.work_calendar = work_calendar_id
            row.operator("bim.remove_work_calendar", text="", icon="X").work_calendar = work_calendar_id

        if self.props.active_work_calendar_id == work_calendar_id:
            if self.props.editing_type == "ATTRIBUTES":
                self.draw_editable_ui()
            elif self.props.editing_type == "WORKTIMES":
                self.draw_work_times_ui(work_calendar_id, work_calendar)

    def draw_work_times_ui(self, work_calendar_id, work_calendar):
        row = self.layout.row(align=True)
        op = row.operator("bim.add_work_time", text="Add Work Time", icon="ADD")
        op.work_calendar = work_calendar_id
        op.time_type = "WorkingTimes"
        op = row.operator("bim.add_work_time", text="Add Exception Time", icon="ADD")
        op.work_calendar = work_calendar_id
        op.time_type = "ExceptionTimes"

        for work_time_id in work_calendar["WorkingTimes"]:
            self.draw_work_time_ui(SequenceData.data["work_times"][work_time_id], time_type="WorkingTimes")

        for work_time_id in work_calendar["ExceptionTimes"]:
            self.draw_work_time_ui(SequenceData.data["work_times"][work_time_id], time_type="ExceptionTimes")

    def draw_work_time_ui(self, work_time, time_type):
        row = self.layout.row(align=True)
        row.label(text=work_time["Name"] or "Unnamed", icon="AUTO" if time_type == "WorkingTimes" else "HOME")
        if work_time["Start"] or work_time["Finish"]:
            row.label(text="{} - {}".format(work_time["Start"] or "*", work_time["Finish"] or "*"))
        if self.props.active_work_time_id == work_time["id"]:
            row.operator("bim.edit_work_time", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_time", text="", icon="CANCEL")
        elif self.props.active_work_time_id:
            op = row.operator("bim.remove_work_time", text="", icon="X")
            op.work_time = work_time["id"]
        else:
            op = row.operator("bim.enable_editing_work_time", text="", icon="GREASEPENCIL")
            op.work_time = work_time["id"]
            op = row.operator("bim.remove_work_time", text="", icon="X")
            op.work_time = work_time["id"]

        if self.props.active_work_time_id == work_time["id"]:
            self.draw_editable_work_time_ui(work_time)

    def draw_editable_work_time_ui(self, work_time):
        draw_attributes(self.props.work_time_attributes, self.layout)
        if work_time["RecurrencePattern"]:
            self.draw_editable_recurrence_pattern_ui(
                SequenceData.data["recurrence_patterns"][work_time["RecurrencePattern"]]
            )
        else:
            row = self.layout.row(align=True)
            row.prop(self.props, "recurrence_types", icon="RECOVER_LAST", text="")
            op = row.operator("bim.assign_recurrence_pattern", icon="ADD", text="")
            op.work_time = work_time["id"]
            op.recurrence_type = self.props.recurrence_types

    def draw_editable_recurrence_pattern_ui(self, recurrence_pattern):
        box = self.layout.box()
        row = box.row(align=True)
        row.label(text=recurrence_pattern["RecurrenceType"], icon="RECOVER_LAST")
        op = row.operator("bim.unassign_recurrence_pattern", text="", icon="X")
        op.recurrence_pattern = recurrence_pattern["id"]

        row = box.row(align=True)
        row.prop(self.props, "start_time", text="")
        row.prop(self.props, "end_time", text="")
        op = row.operator("bim.add_time_period", text="", icon="ADD")
        op.recurrence_pattern = recurrence_pattern["id"]

        for time_period_id in recurrence_pattern["TimePeriods"]:
            time_period = SequenceData.data["time_periods"][time_period_id]
            row = box.row(align=True)
            row.label(text="{} - {}".format(time_period["StartTime"], time_period["EndTime"]), icon="TIME")
            op = row.operator("bim.remove_time_period", text="", icon="X")
            op.time_period = time_period_id

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

        if "Position" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            row = box.row()
            row.prop(self.props, "position")

        if "DayComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            for i, component in enumerate(self.props.day_components):
                if i % 7 == 0:
                    row = box.row(align=True)
                row.prop(component, "is_specified", text=component.name)

        if "WeekdayComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            row = box.row(align=True)
            for component in self.props.weekday_components:
                row.prop(component, "is_specified", text=component.name)

        if "MonthComponent" in applicable_data[recurrence_pattern["RecurrenceType"]]:
            for i, component in enumerate(self.props.month_components):
                if i % 4 == 0:
                    row = box.row(align=True)
                row.prop(component, "is_specified", text=component.name)

        row = box.row()
        row.prop(self.props, "interval")
        row = box.row()
        row.prop(self.props, "occurrences")

    def draw_editable_ui(self):
        draw_attributes(self.props.work_calendar_attributes, self.layout)


class BIM_PT_SequenceToolKit(Panel):
    bl_label = "Sequence Toolkit"
    bl_idname = "BIM_PT_Sequence_toolkit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Sequence Toolkit"

    def draw(self, context):
        row = self.layout.row()
        row.operator(
            "bim.highlight_product_related_task", text="Go to Input-related Task ", icon="STYLUS_PRESSURE"
        ).product_type = "Input"
        row = self.layout.row()
        row.operator(
            "bim.highlight_product_related_task", text="Go to Output-related Task ", icon="STYLUS_PRESSURE"
        ).product_type = "Output"
