# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

import isodate
import bonsai.bim.helper
from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.helper import draw_attributes
from bonsai.bim.module.sequence.data import (
    WorkPlansData,
    WorkScheduleData,
    SequenceData,
    TaskICOMData,
    AnimationColorSchemeData,
)


class BIM_PT_status(Panel):
    bl_label = "Status"
    bl_idname = "BIM_PT_status"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_status"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        self.props = context.scene.BIMStatusProperties

        if not self.props.is_enabled:
            row = self.layout.row()
            row.operator("bim.enable_status_filters", icon="GREASEPENCIL")
            return

        row = self.layout.row(align=True)
        row.label(text="Statuses found in the project:")
        row.operator("bim.disable_status_filters", icon="CANCEL", text="")

        for status in self.props.statuses:
            row = self.layout.row()
            row.label(text=status.name)
            row.prop(status, "is_visible", text="", emboss=False, icon="HIDE_OFF" if status.is_visible else "HIDE_ON")
            row.operator("bim.select_status_filter", icon="RESTRICT_SELECT_OFF", text="").name = status.name


class BIM_PT_work_plans(Panel):
    bl_label = "Work Plans"
    bl_idname = "BIM_PT_work_plans"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and file.schema != "IFC2X3"

    def draw(self, context):
        if not WorkPlansData.is_loaded:
            WorkPlansData.load()
        self.props = context.scene.BIMWorkPlanProperties

        row = self.layout.row()
        if WorkPlansData.data["total_work_plans"]:
            row.label(text=f"{WorkPlansData.data['total_work_plans']} Work Plans Found", icon="TEXT")
        else:
            row.label(text="No Work Plans found.", icon="TEXT")
        row.operator("bim.add_work_plan", icon="ADD", text="")
        for work_plan in WorkPlansData.data["work_plans"]:
            self.draw_work_plan_ui(work_plan)

    def draw_work_plan_ui(self, work_plan):
        row = self.layout.row(align=True)
        row.label(text=work_plan["name"], icon="TEXT")
        if self.props.active_work_plan_id == work_plan["id"]:
            if self.props.editing_type == "ATTRIBUTES":
                row.operator("bim.edit_work_plan", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_work_plan", text="Cancel", icon="CANCEL")
        elif self.props.active_work_plan_id:
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan["id"]
        else:
            op = row.operator("bim.enable_editing_work_plan_schedules", text="", icon="LINENUMBERS_ON")
            op.work_plan = work_plan["id"]
            op = row.operator("bim.enable_editing_work_plan", text="", icon="GREASEPENCIL")
            op.work_plan = work_plan["id"]
            row.operator("bim.remove_work_plan", text="", icon="X").work_plan = work_plan["id"]

        if self.props.active_work_plan_id == work_plan["id"]:
            if self.props.editing_type == "ATTRIBUTES":
                self.draw_editable_ui()
            elif self.props.editing_type == "SCHEDULES":
                self.draw_work_schedule_ui()

    def draw_editable_ui(self):
        draw_attributes(self.props.work_plan_attributes, self.layout)

    def draw_work_schedule_ui(self):
        if WorkPlansData.data["has_work_schedules"]:
            row = self.layout.row(align=True)
            row.prop(self.props, "work_schedules", text="")
            op = row.operator("bim.assign_work_schedule", text="", icon="ADD")
            op.work_plan = self.props.active_work_plan_id
            op.work_schedule = int(self.props.work_schedules)
            for work_schedule in WorkPlansData.data["active_work_plan_schedules"]:
                row = self.layout.row(align=True)
                row.label(text=work_schedule["name"], icon="LINENUMBERS_ON")
                op = row.operator("bim.unassign_work_schedule", text="", icon="X")
                op.work_plan = self.props.active_work_plan_id
                op.work_schedule = work_schedule["id"]
        else:
            row = self.layout.row()
            row.label(text="No schedules found. See Work Schedule Panel", icon="INFO")


class BIM_PT_work_schedules(Panel):
    bl_label = "Work Schedules"
    bl_idname = "BIM_PT_work_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()
        if not WorkScheduleData.is_loaded:
            WorkScheduleData.load()
        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties

        if not self.props.active_work_schedule_id:
            row = self.layout.row(align=True)
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
        if work_schedule["PredefinedType"] == "BASELINE":
            self.draw_readonly_work_schedule_ui(work_schedule_id)
        else:
            row = self.layout.row(align=True)
            if self.props.active_work_schedule_id == work_schedule_id:
                row.label(
                    text="Currently editing: {}[{}]".format(work_schedule["Name"], work_schedule["PredefinedType"]),
                    icon="LINENUMBERS_ON",
                )
                if self.props.editing_type == "WORK_SCHEDULE":
                    row.operator("bim.edit_work_schedule", text="Apply", icon="CHECKMARK")
                elif self.props.editing_type == "TASKS":
                    grid = self.layout.grid_flow(columns=2, even_columns=True)
                    col = grid.column()
                    row1 = col.row(align=True)
                    row1.alignment = "LEFT"
                    row1.label(text="Schedule tools")
                    row1 = col.row(align=True)
                    row1.alignment = "RIGHT"
                    row1.operator("bim.generate_gantt_chart", text="Generate Gantt", icon="NLA").work_schedule = (
                        work_schedule_id
                    )
                    row1.operator(
                        "bim.recalculate_schedule", text="Re-calculate Schedule", icon="FILE_REFRESH"
                    ).work_schedule = work_schedule_id
                    row2 = col.row(align=True)
                    row2.alignment = "RIGHT"
                    row2.operator(
                        "bim.select_work_schedule_products", text="Select Assigned", icon="RESTRICT_SELECT_OFF"
                    ).work_schedule = work_schedule_id
                    row2.operator(
                        "bim.select_unassigned_work_schedule_products",
                        text="Select Unassigned",
                        icon="RESTRICT_SELECT_OFF",
                    ).work_schedule = work_schedule_id
                    if WorkScheduleData.data["can_have_baselines"]:
                        row3 = col.row()
                        row3.alignment = "RIGHT"
                        row3.prop(self.props, "should_show_schedule_baseline_ui", icon="RESTRICT_INSTANCED_OFF")
                    col = grid.column()
                    row1 = col.row(align=True)
                    row1.alignment = "LEFT"
                    row1.label(text="Settings")
                    row1 = col.row(align=True)
                    row1.alignment = "RIGHT"
                    row1.prop(self.props, "should_show_column_ui", text="Schedule Columns", icon="SHORTDISPLAY")
                    row2 = col.row(align=True)
                    row.operator("bim.disable_editing_work_schedule", text="Cancel", icon="CANCEL")
            if not self.props.active_work_schedule_id:
                grid = self.layout.grid_flow(columns=2, even_columns=True)
                col1 = grid.column()
                col1.label(
                    text="{}[{}]".format(work_schedule["Name"], work_schedule["PredefinedType"]) or "Unnamed",
                    icon="LINENUMBERS_ON",
                )
                col2 = grid.column()
                row = col2.row(align=True)
                row.operator("bim.enable_editing_work_schedule_tasks", text="Tasks", icon="ACTION").work_schedule = (
                    work_schedule_id
                )
                row.operator(
                    "bim.enable_editing_work_schedule", text="Attributes", icon="GREASEPENCIL"
                ).work_schedule = work_schedule_id
                row.operator("bim.remove_work_schedule", text="Delete", icon="X").work_schedule = work_schedule_id
            if self.props.active_work_schedule_id == work_schedule_id:
                if self.props.editing_type == "WORK_SCHEDULE":
                    self.draw_editable_work_schedule_ui()
                elif self.props.editing_type == "TASKS":
                    self.draw_baseline_ui(work_schedule_id)
                    self.draw_column_ui()
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
                row.operator("bim.disable_editing_task", text="Cancel", icon="CANCEL")
            elif self.props.editing_task_type == "SEQUENCE":
                row.operator("bim.disable_editing_task", text="Cancel", icon="CANCEL")
            else:
                row.prop(self.props, "show_task_operators", text="Edit", icon="GREASEPENCIL")
                if self.props.show_task_operators:
                    row2 = self.layout.row(align=True)
                    row2.alignment = "RIGHT"

                    row2.prop(self.props, "enable_reorder", text="", icon="SORTALPHA")
                    row2.operator("bim.enable_editing_task_sequence", text="", icon="TRACKING")
                    row2.operator("bim.enable_editing_task_time", text="", icon="TIME").task = ifc_definition_id
                    row2.operator("bim.enable_editing_task_calendar", text="", icon="VIEW_ORTHO").task = (
                        ifc_definition_id
                    )
                    row2.operator("bim.enable_editing_task_attributes", text="", icon="GREASEPENCIL").task = (
                        ifc_definition_id
                    )
                row.operator("bim.add_task", text="Add", icon="ADD").task = ifc_definition_id
                row.operator("bim.duplicate_task", text="Copy", icon="DUPLICATE").task = ifc_definition_id
                row.operator("bim.remove_task", text="Delete", icon="X").task = ifc_definition_id

    def draw_column_ui(self):
        if not self.props.should_show_column_ui:
            return
        row = self.layout.row()
        row.operator("bim.setup_default_task_columns", text="Setup Default Columns", icon="ANCHOR_BOTTOM")
        row.alignment = "RIGHT"
        row = self.layout.row(align=True)
        row.prop(self.props, "column_types", text="")
        column_type = self.props.column_types
        if column_type == "IfcTask":
            row.prop(self.props, "task_columns", text="")
            name, data_type = self.props.task_columns.split("/")
        elif column_type == "IfcTaskTime":
            row.prop(self.props, "task_time_columns", text="")
            name, data_type = self.props.task_time_columns.split("/")
        elif column_type == "Special":
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

    def draw_editable_work_schedule_ui(self):
        draw_attributes(self.props.work_schedule_attributes, self.layout)

    def draw_editable_task_ui(self, work_schedule_id):
        row = self.layout.row(align=True)
        row.label(text="Task Tools")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.add_summary_task", text="Add Summary Task", icon="ADD").work_schedule = work_schedule_id
        row.operator("bim.expand_all_tasks", text="Expand All")
        row.operator("bim.contract_all_tasks", text="Contract All")
        row = self.layout.row(align=True)
        self.draw_task_operators()
        self.layout.template_list(
            "BIM_UL_tasks",
            "",
            self.tprops,
            "tasks",
            self.props,
            "active_task_index",
        )
        if self.props.active_task_id and self.props.editing_task_type == "ATTRIBUTES":
            self.draw_editable_task_attributes_ui()
        elif self.props.active_task_id and self.props.editing_task_type == "CALENDAR":
            self.draw_editable_task_calendar_ui()
        elif self.props.highlighted_task_id and self.props.editing_task_type == "SEQUENCE":
            self.draw_editable_task_sequence_ui()
        elif self.props.active_task_time_id and self.props.editing_task_type == "TASKTIME":
            self.draw_editable_task_time_attributes_ui()

    def draw_editable_task_sequence_ui(self):
        task = SequenceData.data["tasks"][self.props.highlighted_task_id]
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
        row.operator("bim.go_to_task", text="", icon="RESTRICT_SELECT_OFF").task = task["id"]
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
                row.operator("bim.disable_editing_sequence", text="Cancel", icon="CANCEL")
                self.draw_editable_sequence_attributes_ui()
            elif self.props.editing_sequence_type == "LAG_TIME":
                op = row.operator("bim.edit_sequence_lag_time", text="", icon="CHECKMARK")
                op.lag_time = sequence["TimeLag"]
                row.operator("bim.disable_editing_sequence", text="Cancel", icon="CANCEL")
                self.draw_editable_sequence_lag_time_ui()
        else:
            if sequence["TimeLag"]:
                op = row.operator("bim.enable_editing_sequence_lag_time", text="Edit Time Lag", icon="CON_LOCKTRACK")
                op.sequence = sequence["id"]
                op.lag_time = sequence["TimeLag"]
            op = row.operator("bim.enable_editing_sequence_attributes", text="Edit Sequence", icon="GREASEPENCIL")
            op.sequence = sequence["id"]
            if process_type == "RelatingProcess":
                op = row.operator("bim.unassign_predecessor", text="", icon="X")
            elif process_type == "RelatedProcess":
                op = row.operator("bim.unassign_successor", text="", icon="X")
            op.task = task["id"]

    def draw_editable_sequence_attributes_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.sequence_attributes, self.layout)

    def draw_editable_sequence_lag_time_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.lag_time_attributes, self.layout)

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
        bonsai.bim.helper.draw_attributes(
            self.props.task_attributes, self.layout, copy_operator="bim.copy_task_attribute"
        )

    def draw_editable_task_time_attributes_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.task_time_attributes, self.layout)

    def draw_baseline_ui(self, work_schedule_id):
        if not self.props.should_show_schedule_baseline_ui:
            return
        row3 = self.layout.row()
        row3.alignment = "RIGHT"
        row3.operator("bim.create_baseline", text="Add Baseline", icon="ADD").work_schedule = work_schedule_id
        if WorkScheduleData.data["active_work_schedule_baselines"]:
            for baseline in WorkScheduleData.data["active_work_schedule_baselines"]:
                baseline_row = self.layout.row()
                baseline_row.alignment = "RIGHT"
                baseline_row.label(
                    text="{} @ {}".format(baseline["name"], baseline["date"]), icon="RESTRICT_INSTANCED_OFF"
                )
                baseline_row.operator("bim.generate_gantt_chart", text="Compare", icon="NLA").work_schedule = baseline[
                    "id"
                ]
                baseline_row.operator(
                    "bim.enable_editing_work_schedule_tasks", text="Display Schedule", icon="ACTION"
                ).work_schedule = baseline["id"]
                baseline_row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = baseline["id"]

    def draw_readonly_work_schedule_ui(self, work_schedule_id):
        if self.props.active_work_schedule_id == work_schedule_id:
            row = self.layout.row()
            row.alignment = "RIGHT"
            row.operator("bim.disable_editing_work_schedule", text="Disable editing", icon="CANCEL")
            grid = self.layout.grid_flow(columns=2, even_columns=True)
            col = grid.column()
            row1 = col.row(align=True)
            row1.alignment = "LEFT"
            row1.label(text="Settings")
            row1 = col.row(align=True)
            row1.alignment = "RIGHT"
            row1.prop(self.props, "should_show_column_ui", text="Schedule Columns", icon="SHORTDISPLAY")
            row2 = col.row(align=True)
            if self.props.editing_type == "TASKS":
                self.draw_column_ui()
                self.layout.template_list(
                    "BIM_UL_tasks",
                    "",
                    self.tprops,
                    "tasks",
                    self.props,
                    "active_task_index",
                )


class BIM_PT_animation_tools(Panel):
    bl_label = "Animation Tools"
    bl_idname = "BIM_PT_animation_tools"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_work_schedules"
    bl_order = 4

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMWorkScheduleProperties
        if props.active_work_schedule_id:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        self.animation_props = context.scene.BIMAnimationProperties
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.props, "should_show_visualisation_ui", text="Animation Settings", icon="SETTINGS")
        row.prop(self.props, "should_show_snapshot_ui", text="Snapshot Settings", icon="SETTINGS")
        if self.props.should_show_visualisation_ui:
            self.draw_visualisation_ui()
        if self.props.should_show_snapshot_ui:
            self.draw_snapshot_ui()
        self.draw_processing_options()

    def draw_processing_options(self):
        row = self.layout.row(align=True)
        row.alignment = "LEFT"
        row.label(text="Processing Tools")
        row = self.layout.row()
        row.alignment = "RIGHT"
        row.operator("bim.add_animation_camera", text="Add Camera", icon="CAMERA_DATA")
        row.operator("bim.clear_previous_animation", text="Reset Animation", icon="TRACKING_CLEAR_FORWARDS")

    def draw_visualisation_ui(self):
        if not AnimationColorSchemeData.is_loaded:
            AnimationColorSchemeData.load()

        row = self.layout.row(align=True)
        row.label(text="Start Date/ Date Range:", icon="CAMERA_DATA")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        op = row.operator("bim.datepicker", text=self.props.visualisation_start or "Start Date", icon="REW")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_start"
        op = row.operator("bim.datepicker", text=self.props.visualisation_finish or "Finish Date", icon="FF")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_finish"
        op = row.operator("bim.guess_date_range", text="Guess", icon="FILE_REFRESH")
        op.work_schedule = self.props.active_work_schedule_id

        row = self.layout.row(align=True)
        row.label(text="Speed Settings")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.props, "speed_types", text="")
        if self.props.speed_types == "FRAME_SPEED":
            row.prop(self.props, "speed_animation_frames", text="")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "DURATION_SPEED":
            row.prop(self.props, "speed_animation_duration", text="")
            row.label(text="->")
            row.prop(self.props, "speed_real_duration", text="")
        elif self.props.speed_types == "MULTIPLIER_SPEED":
            row.prop(self.props, "speed_multiplier", text="")
        row = self.layout.row(align=True)
        row.label(text="Display Settings")
        row = self.layout.row()
        row.alignment = "RIGHT"
        row.prop(self.animation_props, "should_show_task_bar_options", text="Task Bars", icon="NLA_PUSHDOWN")
        if self.animation_props.should_show_task_bar_options:
            row = self.layout.row()
            row.label(text="Task Bar Options", icon="NLA_PUSHDOWN")
            row.alignment = "LEFT"
            row = self.layout.row(align=True)
            row.prop(self.props, "should_show_task_bar_selection", text="Enable Selection", icon="NLA_PUSHDOWN")
            row.operator("bim.add_task_bars", text="Generate bars", icon="NLA_PUSHDOWN")

            grid = self.layout.grid_flow(columns=2, even_columns=True)
            # Column1
            col = grid.column()

            row = col.row(align=True)
            row.prop(self.animation_props, "color_progress")

            row = col.row(align=True)
            row.prop(self.animation_props, "color_full")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        if AnimationColorSchemeData.data["saved_color_schemes"]:
            row.prop(self.animation_props, "saved_color_schemes", text="Color Scheme", icon="SEQUENCE_COLOR_04")
        else:
            row.label(text="No Color Scheme Saved", icon="INFO")
        op = row.operator("bim.visualise_work_schedule_date_range", text="Create Animation", icon="OUTLINER_OB_CAMERA")
        op.work_schedule = self.props.active_work_schedule_id

    def draw_snapshot_ui(self):
        row = self.layout.row(align=True)
        row.label(text="Date of Snapshot:", icon="CAMERA_STEREO")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        op = row.operator("bim.datepicker", text=self.props.visualisation_start or "Date", icon="PROP_PROJECTED")
        op.target_prop = "BIMWorkScheduleProperties.visualisation_start"
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        op = row.operator("bim.visualise_work_schedule_date", text="Create SnapShot", icon="CAMERA_STEREO")
        op.work_schedule = self.props.active_work_schedule_id


class BIM_PT_animation_Color_Scheme(Panel):
    bl_label = "Animation Color Scheme"
    bl_idname = "BIM_PT_animation_Color_Scheme"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not AnimationColorSchemeData.is_loaded:
            AnimationColorSchemeData.load()

        self.animation_props = context.scene.BIMAnimationProperties
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.load_default_animation_color_scheme", text="Load default", icon="SEQUENCE_COLOR_04")
        if AnimationColorSchemeData.data["saved_color_schemes"]:
            row.operator("bim.load_animation_color_scheme", text="Load Scheme", icon="IMPORT")
        row.operator("bim.save_animation_color_scheme", text="Save Scheme", icon="EXPORT")

        grid = self.layout.grid_flow(columns=2, even_columns=True)
        col = grid.column()
        row1 = col.row(align=True)
        row1.label(text="INPUT COLORS", icon="COLLECTION_COLOR_01")
        row1 = col.row()
        row1.template_list(
            "BIM_UL_animation_colors",
            "",
            self.animation_props,
            "task_input_colors",
            self.animation_props,
            "active_color_component_inputs_index",
        )
        col = grid.column()
        row1 = col.row(align=True)
        row1.label(text="OUTPUT COLORS", icon="COLLECTION_COLOR_04")
        row1 = col.row()
        row1.template_list(
            "BIM_UL_animation_colors",
            "",
            self.animation_props,
            "task_output_colors",
            self.animation_props,
            "active_color_component_outputs_index",
        )


class BIM_PT_task_icom(Panel):
    bl_label = "Task ICOM"
    bl_idname = "BIM_PT_task_icom"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_work_schedules"
    bl_order = 1

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
        if not TaskICOMData.is_loaded:
            TaskICOMData.load()

        self.props = context.scene.BIMWorkScheduleProperties
        self.tprops = context.scene.BIMTaskTreeProperties
        task = self.tprops.tasks[self.props.active_task_index]

        grid = self.layout.grid_flow(columns=3, even_columns=True)

        # Column1
        col = grid.column()

        row2 = col.row(align=True)
        total_task_inputs = len(self.props.task_inputs)
        row2.label(text="Inputs ({})".format(total_task_inputs))

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

        op = row2.operator("bim.select_task_related_inputs", icon="RESTRICT_SELECT_OFF", text="Select")
        op.task = task.ifc_definition_id

        row2 = col.row()
        row2.prop(self.props, "show_nested_inputs", text="Show Nested")
        row2 = col.row()
        row2.template_list("BIM_UL_task_inputs", "", self.props, "task_inputs", self.props, "active_task_input_index")

        # Column2
        col = grid.column()

        row2 = col.row(align=True)
        total_task_resources = len(self.props.task_resources)
        row2.label(text="Resources ({})".format(total_task_resources))
        op = row2.operator("bim.calculate_task_duration", text="", icon="TEMP")
        op.task = task.ifc_definition_id

        if TaskICOMData.data["can_active_resource_be_assigned"]:
            op = row2.operator("bim.assign_process", icon="ADD", text="")
            op.task = task.ifc_definition_id
            op.related_object_type = "RESOURCE"

        if total_task_resources and self.props.active_task_resource_index < total_task_resources:
            op = row2.operator("bim.unassign_process", icon="REMOVE", text="")
            op.task = task.ifc_definition_id
            op.related_object_type = "RESOURCE"
            op.resource = self.props.task_resources[self.props.active_task_resource_index].ifc_definition_id

        row2 = col.row()
        row2.prop(self.props, "show_nested_resources", text="Show Nested")

        row2 = col.row()
        row2.template_list(
            "BIM_UL_task_resources", "", self.props, "task_resources", self.props, "active_task_resource_index"
        )

        # Column3
        col = grid.column()

        row2 = col.row(align=True)
        total_task_outputs = len(self.props.task_outputs)
        row2.label(text="Outputs ({})".format(total_task_outputs))

        if context.selected_objects:
            op = row2.operator("bim.assign_product", icon="ADD", text="")
            op.task = task.ifc_definition_id
        if total_task_outputs:
            op = row2.operator("bim.unassign_product", icon="REMOVE", text="")
            op.task = task.ifc_definition_id
            if (
                total_task_outputs
                and not context.selected_objects
                and self.props.active_task_output_index < total_task_outputs
            ):
                output_id = self.props.task_outputs[self.props.active_task_output_index].ifc_definition_id
                op.relating_product = output_id

        op = row2.operator("bim.select_task_related_products", icon="RESTRICT_SELECT_OFF", text="Select")
        op.task = task.ifc_definition_id
        row2 = col.row()
        row2.prop(self.props, "show_nested_outputs", text="Show Nested")
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
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.select_product", text="", icon="RESTRICT_SELECT_OFF")
            op.product = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")
            # row.operator("bim.remove_task_column", text="", icon="X").name = item.name


class BIM_UL_task_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.operator("bim.go_to_resource", text="", icon="STYLUS_PRESSURE").resource = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")
            row.prop(item, "schedule_usage", emboss=False, text="")


class BIM_UL_animation_colors(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row()
            row.prop(item, "color", text="")
            row.label(text=item.name)


class BIM_UL_task_outputs(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.select_product", text="", icon="RESTRICT_SELECT_OFF")
            op.product = item.ifc_definition_id
            row.prop(item, "name", emboss=False, text="")


class BIM_UL_product_input_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.go_to_task", text="", icon="STYLUS_PRESSURE")
            op.task = item.ifc_definition_id
            row.split(factor=0.8)
            row.label(text=item.name)


class BIM_UL_product_output_tasks(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.go_to_task", text="", icon="STYLUS_PRESSURE")
            op.task = item.ifc_definition_id
            row.split(factor=0.8)
            row.label(text=item.name)


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
            if self.props.should_show_task_bar_selection:
                row.prop(
                    item,
                    "has_bar_visual",
                    icon="COLLECTION_COLOR_04" if item.has_bar_visual else "OUTLINER_COLLECTION",
                    text="",
                    emboss=False,
                )
            if self.props.enable_reorder:
                self.draw_order_operator(row, item.ifc_definition_id)
            if self.props.editing_task_type == "SEQUENCE" and self.props.highlighted_task_id != item.ifc_definition_id:
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

    def draw_order_operator(self, row, ifc_definition_id):
        task = SequenceData.data["tasks"][ifc_definition_id]
        if task["NestingIndex"] is not None:
            if task["NestingIndex"] == 0:
                op = row.operator("bim.reorder_task_nesting", icon="TRIA_DOWN", text="")
                op.task = ifc_definition_id
                op.new_index = task["NestingIndex"] + 1
            elif task["NestingIndex"] > 0:
                op = row.operator("bim.reorder_task_nesting", icon="TRIA_UP", text="")
                op.task = ifc_definition_id
                op.new_index = task["NestingIndex"] - 1

    def draw_hierarchy(self, row, item):
        for i in range(0, item.level_index):
            row.label(text="", icon="BLANK1")
        if item.has_children:
            if item.is_expanded:
                row.operator("bim.contract_task", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN").task = (
                    item.ifc_definition_id
                )
            else:
                row.operator("bim.expand_task", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT").task = (
                    item.ifc_definition_id
                )
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
    bl_label = "Work Calendars"
    bl_idname = "BIM_PT_work_calendars"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

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
                row.operator("bim.edit_work_calendar", icon="CHECKMARK")
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
            row.operator("bim.disable_editing_work_time", text="Cancel", icon="CANCEL")
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


class BIM_PT_4D_Tools(Panel):
    bl_label = "4D Tools"
    bl_idname = "BIM_PT_4D_Tools"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    def draw(self, context):
        self.props = context.scene.BIMWorkScheduleProperties
        row = self.layout.row()
        row.operator("bim.load_product_related_tasks", text="Load Tasks", icon="FILE_REFRESH")
        row.prop(self.props, "filter_by_active_schedule", text="Filter by Active Schedule")
        grid = self.layout.grid_flow(columns=2, even_columns=True)
        col1 = grid.column()
        col1.label(text="Product Input Tasks")
        col1.template_list(
            "BIM_UL_product_input_tasks",
            "",
            self.props,
            "product_input_tasks",
            self.props,
            "active_product_input_task_index",
        )

        col2 = grid.column()
        col2.label(text="Product Output Tasks")
        col2.template_list(
            "BIM_UL_product_output_tasks",
            "",
            self.props,
            "product_output_tasks",
            self.props,
            "active_product_output_task_index",
        )
