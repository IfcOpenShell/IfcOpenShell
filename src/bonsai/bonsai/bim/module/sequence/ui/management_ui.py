# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021, 2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>, Federico Eraso <feraso@svisuals.net
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



import bpy
from bpy.types import Panel
from typing import Any
import bonsai.tool as tool
from bonsai.bim.helper import draw_attributes
from bonsai.bim.module.sequence.data import WorkPlansData, SequenceData



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
        file = tool.Ifc.get()
        return file and file.schema != "IFC2X3"

    def draw(self, context):
        if not WorkPlansData.is_loaded:
            WorkPlansData.load()
        assert self.layout
        self.props = tool.Sequence.get_work_plan_props()

        row = self.layout.row()
        if WorkPlansData.data["total_work_plans"]:
            row.label(text=f"{WorkPlansData.data['total_work_plans']} Work Plans Found", icon="TEXT")
        else:
            row.label(text="No Work Plans found.", icon="TEXT")
        row.operator("bim.add_work_plan", icon="ADD", text="")
        for work_plan in WorkPlansData.data["work_plans"]:
            self.draw_work_plan_ui(work_plan)

    def draw_work_plan_ui(self, work_plan: dict[str, Any]) -> None:
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

    def draw_editable_ui(self) -> None:
        draw_attributes(self.props.work_plan_attributes, self.layout)

    def draw_work_schedule_ui(self) -> None:
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
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    layout: bpy.types.UILayout

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()

        self.props = tool.Sequence.get_work_calendar_props()
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

    def draw_editable_work_time_ui(self, work_time: dict[str, Any]) -> None:
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
    bl_order = 5
    def draw(self, context):
        self.props = tool.Sequence.get_work_schedule_props()

        # --- Active Work Schedule Info ---
        row = self.layout.row()
        try:
            if self.props.active_work_schedule_id:
                file = tool.Ifc.get()
                if file:
                    ws = file.by_id(self.props.active_work_schedule_id)
                    if ws:
                        row.label(text=f"Active Schedule: {getattr(ws, 'Name', None) or 'Unnamed'}", icon="TIME")
                    else:
                        row.label(text="No valid schedule selected", icon="ERROR")
                else:
                    row.label(text="No IFC file loaded", icon="ERROR")
            else:
                row.label(text="No schedule selected", icon="INFO")
        except Exception:
            row.label(text="No valid schedule selected", icon="ERROR")

        # --- Actions ---
        row = self.layout.row()
        row.operator("bim.load_product_related_tasks", text="Load Tasks", icon="FILE_REFRESH")
        row.prop(self.props, "filter_by_active_schedule", text="Filter by Active Schedule")

        # --- Lists ---
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





