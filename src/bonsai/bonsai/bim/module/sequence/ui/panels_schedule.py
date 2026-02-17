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
import isodate
from bpy.types import Panel
from typing import Any
import bonsai.tool as tool
import bonsai.bim.helper
from bonsai.bim.helper import draw_attributes
from bonsai.bim.module.sequence.data import SequenceData, WorkScheduleData, TaskICOMData

# Import the UIList of tasks from our new module
from .lists_ui import BIM_UL_tasks



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
        return tool.Ifc.get()

    def draw(self, context):
        self.props = tool.Sequence.get_status_props()
        assert self.layout

        if not self.props.is_enabled:
            row = self.layout.row()
            row.operator("bim.enable_status_filters", icon="GREASEPENCIL")
            return

        row = self.layout.row(align=True)
        row.label(text="Elements Statuses:")
        row.operator("bim.activate_status_filters", icon="FILE_REFRESH", text="")
        row.operator("bim.disable_status_filters", icon="CANCEL", text="")

        box = self.layout.box()
        for status in self.props.statuses:
            row = box.row(align=True)
            row.label(text=status.name)
            # Check if status has elements (simplified without StatusData)
            if hasattr(status, 'has_elements') and status.has_elements:
                row.label(text="", icon="ASSET_MANAGER")
            row.prop(status, "is_visible", text="", emboss=False, icon="HIDE_OFF" if status.is_visible else "HIDE_ON")
            row.operator("bim.select_status_filter", icon="RESTRICT_SELECT_OFF", text="").status = status.name
            row.operator("bim.assign_status", icon="BRUSH_DATA", text="").status = status.name


class BIM_PT_work_schedules(Panel):
    bl_label = "Work Schedules"
    bl_idname = "BIM_PT_work_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @classmethod
    def poll(cls, context):
        file = tool.Ifc.get()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not SequenceData.is_loaded:
            SequenceData.load()
        if not WorkScheduleData.is_loaded:
            WorkScheduleData.load()
        self.props = tool.Sequence.get_work_schedule_props()
        self.tprops = tool.Sequence.get_task_tree_props()

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
            row.operator("bim.import_work_schedule_csv", text="", icon="IMPORT")

        for work_schedule_id, work_schedule in SequenceData.data["work_schedules"].items():
            self.draw_work_schedule_ui(work_schedule_id, work_schedule)

    def draw_work_schedule_ui(self, work_schedule_id: int, work_schedule: dict[str, Any]) -> None:
        assert self.layout
        # BASELINE schedules should be editable normally.
        # Only use readonly UI for specific cases, not for the BASELINE type
        # if work_schedule["PredefinedType"] == "BASELINE":
        #     self.draw_readonly_work_schedule_ui(work_schedule_id)
        # else:
        row = self.layout.row(align=True)
        if self.props.active_work_schedule_id == work_schedule_id:
            row.label(
                text="Currently editing: {}[{}]".format(work_schedule["Name"], work_schedule["PredefinedType"]),
                icon="LINENUMBERS_ON",
            )
            if self.props.editing_type == "WORK_SCHEDULE":
                row.operator("bim.edit_work_schedule", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_work_schedule", text="", icon="CANCEL")
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
                
                
                row1.prop(self.props, "should_show_column_ui", text="Schedule Columns", toggle=True, icon="SHORTDISPLAY")
                row1.prop(self.props.filters, "show_filters", text="Filter Tasks", toggle=True, icon="FILTER")

                # --- COPY 3D AND SYNC 3D BUTTONS ---
                row_io = col.row(align=True)
                row_io.alignment = 'RIGHT'
                row_io.operator("bim.copy_3d", text="Copy 3D", icon="DUPLICATE")
                row_io.operator("bim.sync_3d", text="Sync 3D", icon="FILE_REFRESH")
                # --- COPY 3D AND SYNC 3D BUTTONS ---
                
                row2 = col.row(align=True)
                row.operator("bim.disable_editing_work_schedule", text="Cancel", icon="CANCEL")
        else:
            # Show the 4 buttons for any schedule
            grid = self.layout.grid_flow(columns=2, even_columns=True)
            col1 = grid.column()
            col1.label(
                text="{}[{}]".format(work_schedule["Name"], work_schedule["PredefinedType"]) or "Unnamed",
                icon="LINENUMBERS_ON",
            )
            col2 = grid.column()
            row = col2.row(align=True)
            row.alignment = "RIGHT"
            row.operator("bim.enable_editing_work_schedule_tasks", text="", icon="ACTION").work_schedule = (
                work_schedule_id
            )
            row.operator("bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL").work_schedule = (
                work_schedule_id
            )
            row.operator("bim.copy_work_schedule", text="", icon="DUPLICATE").work_schedule = work_schedule_id
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id
            
        # Additional UI when this specific schedule is being edited
        if self.props.active_work_schedule_id == work_schedule_id:
            if self.props.editing_type == "WORK_SCHEDULE":
                self.draw_editable_work_schedule_ui()
            elif self.props.editing_type == "TASKS":
                self.draw_baseline_ui(work_schedule_id)
                self.draw_column_ui()
                # RETURN TO THE ORIGINAL SYSTEM - Only call if activated
                if getattr(self.props.filters, "show_filters", False):
                    self.draw_filter_ui()
                self.draw_editable_task_ui(work_schedule_id)

    def draw_task_operators(self) -> None:
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

    def draw_column_ui(self) -> None:
        if not self.props.should_show_column_ui:
            return
        assert self.layout
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
    # Replace the existing draw_filter_ui method in ui.py with this one

    def draw_filter_ui(self) -> None:
        """Draws the filter configuration panel with the final corrected structure."""
        props = self.props

        if not getattr(props.filters, "show_filters", False):
            return

        main_box = self.layout.box()

        # 1. Static title "Smart Filter"
        header_row = main_box.row(align=True)
        header_row.label(text="Smart Filter", icon="FILTER")


        # Date source selector for filters, making it more accessible.
        date_source_row = main_box.row(align=True)
        date_source_row.label(text="Filter Date Source:")
        date_source_row.prop(props, "date_source_type", text="")
     

        # 2. Active filters panel
        active_filters_box = main_box.box()
        row = active_filters_box.row(align=True)
        row.prop(props.filters, "logic", text="")
    
        # Presets Menu
        row.operator_menu_enum("bim.apply_lookahead_filter", "time_window", text="WLA", icon="TIME")
      
        row.operator("bim.add_task_filter", text="", icon='ADD')
        row.operator("bim.remove_task_filter", text="", icon='REMOVE')

        row.separator()
        row.operator("bim.apply_task_filters", text="Apply Filters", icon="FILE_REFRESH")
        row.operator("bim.clear_all_task_filters", text="Clean", icon="CANCEL")
       

        active_filters_box.template_list(
            "BIM_UL_task_filters", "",
            props.filters, "rules",
            props.filters, "active_rule_index"
        )

        active_filters_count = len([r for r in props.filters.rules if r.is_active])
        if active_filters_count > 0:
            info_row = active_filters_box.row()
            info_row.label(text=f"[INFO] {active_filters_count} active filter(s)", icon='INFO')

        # 3. Saved Filters Panel (now collapsible)
        saved_filters_box = main_box.box()
        row = saved_filters_box.row(align=True)

        # The title is now a button to show/hide the section
        icon = 'TRIA_DOWN' if props.filters.show_saved_filters else 'TRIA_RIGHT'
        row.prop(props.filters, "show_saved_filters", text="Saved Filters", icon=icon, emboss=False)
        # --- END OF MODIFICATION ---

        # The content is only drawn if the section is expanded
        if props.filters.show_saved_filters:
            saved_filters_box.template_list(
                "BIM_UL_saved_filter_sets", "",
                props, "saved_filter_sets",
                props, "active_saved_filter_set_index"
            )

            row_ops = saved_filters_box.row(align=True)
            row_ops.enabled = len(props.saved_filter_sets) > 0

            load_op = row_ops.operator("bim.load_filter_set", text="Load", icon="FILE_TICK")
            load_op.set_index = props.active_saved_filter_set_index

            update_op = row_ops.operator("bim.update_saved_filter_set", text="Update", icon="FILE_REFRESH")
            update_op.set_index = props.active_saved_filter_set_index
           

            remove_op = row_ops.operator("bim.remove_filter_set", text="Remove", icon="TRASH")
            remove_op.set_index = props.active_saved_filter_set_index

            row_io = saved_filters_box.row(align=True)
            row_io.operator("bim.save_filter_set", text="Save Current", icon="PINNED")
            row_io.operator("bim.import_filter_set", text="Import Library", icon="IMPORT")
            row_io.operator("bim.export_filter_set", text="Export Library", icon="EXPORT")




    def draw_editable_work_schedule_ui(self):
        draw_attributes(self.props.work_schedule_attributes, self.layout)

    def draw_editable_task_ui(self, work_schedule_id: int) -> None:
        assert self.layout

        # The call to self.draw_filter_ui() was removed from here
        # as it is correctly called in draw_work_schedule_ui()
        
        row = self.layout.row(align=True) 
        row.label(text="Task Tools")
        

        row = self.layout.row(align=True)
        
        # 1. Split the row. The first column (left) will be for the checkbox.
        #    We use a small factor to give it limited space.
        split = row.split(factor=0.15)
        
        # 2. Place the checkbox in the left column.
        #    It is now contained and cannot stretch beyond this 25%.
        col_izquierda = split.column()
        col_izquierda.prop(self.props, "should_select_3d_on_task_click", text="3D Task", icon="RESTRICT_SELECT_OFF")
        
        # 3. Use the second column for the buttons on the right.
        col_derecha = split.column()
        
        # 4. Create a sub-row INSIDE the right column to align the buttons.
        sub_fila_botones = col_derecha.row(align=True)
        sub_fila_botones.alignment = 'RIGHT' # This sticks them to the right of THEIR column.
        
        sub_fila_botones.operator("bim.refresh_task_output_counts", text="", icon="FILE_REFRESH")
        sub_fila_botones.operator("bim.add_summary_task", text="Add Summary Task", icon="ADD").work_schedule = work_schedule_id
        sub_fila_botones.operator("bim.expand_all_tasks", text="Expand All")
        sub_fila_botones.operator("bim.contract_all_tasks", text="Contract All")
        row = self.layout.row(align=True)
        self.draw_task_operators()
        BIM_UL_tasks.draw_header(self.layout)
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
        # Draw attributes but inject Animation Color Schemes after 'Priority'
        try:
            attrs = [a for a in self.props.task_attributes if a.name != "PredefinedType"]
        except Exception:
            attrs = list(self.props.task_attributes)

        # Split at Priority
        before = []
        after = []
        found = False
        for a in attrs:
            before.append(a)
            if a.name == "Priority":
                found = True
                break
        if found:
            after = attrs[len(before):]

        import bonsai.bim.helper as _h
        _h.draw_attributes(before, self.layout, copy_operator="bim.copy_task_attribute")


        # --- Draw PredefinedType exactly below Priority (as in Blender 4.2.1) ---
        try:
            _predef = None
            for _a in self.props.task_attributes:
                if getattr(_a, "name", "") == "PredefinedType":
                    _predef = _a
                    break
            if _predef is not None:
                _h.draw_attributes([_predef], self.layout, copy_operator="bim.copy_task_attribute")
        except Exception:
            pass
        # --- end PredefinedType ---

        # Ensures that the active task has its DEFAULT group synchronized when drawn
        try:
            from ..prop.animation import UnifiedColorTypeManager

            tprops = tool.Sequence.get_task_tree_props()
            if tprops.tasks and self.props.active_task_index < len(tprops.tasks):
                active_task_pg = tprops.tasks[self.props.active_task_index]
                # Call to the central logic to synchronize at the time of drawing
                # Only if there are no custom groups
                user_groups = UnifiedColorTypeManager.get_user_created_groups(bpy.context)
                if not user_groups: 
                    UnifiedColorTypeManager.sync_default_group_to_predefinedtype(bpy.context, active_task_pg)
        except Exception as e:
            # It should not break the UI if something fails
            print(f"⚠ Error synchronizing DEFAULT in the UI: {e}")
        # === Custom Appearance Groups ===
        try:
            if self.tprops.tasks and self.props.active_task_index < len(self.tprops.tasks):
                _task = self.tprops.tasks[self.props.active_task_index]
                animation_props = tool.Sequence.get_animation_props()

                # Use the correctly implemented functions
                all_groups = UnifiedColorTypeManager.get_all_groups(bpy.context)
                user_groups = UnifiedColorTypeManager.get_user_created_groups(bpy.context)

                # Show information of selected tasks
                selected_count = len([task for task in self.tprops.tasks if getattr(task, 'is_selected', False)])

                # Always show the section if there are available groups
                if all_groups:
                    box = self.layout.box()

                    # Header with information
                    header_row = box.row(align=True)
                    header_row.label(text="colortype Group Assignment:", icon="GROUP")

                    # Information of selected tasks
                    if selected_count > 0:
                        info_row = box.row()
                        info_row.label(text=f"📋 {selected_count} tasks selected for copying", icon='INFO')

                        # Copy button
                        copy_row = box.row(align=True)
                        copy_op = copy_row.operator("bim.copy_task_custom_colortype_group", text="Copy Configuration to Selected", icon="COPYDOWN")
                        copy_op.enabled = selected_count > 0

                    # Custom group selector (only custom groups)
                    if user_groups:
                        row = box.row(align=True)
                        row.label(text="Custom Group:")
                        row.prop(animation_props, "task_colortype_group_selector", text="")

                        # Show profile selector if a group is selected
                        current_group = getattr(animation_props, 'task_colortype_group_selector', '')
                        if current_group and current_group != "DEFAULT":
                            row = box.row(align=True)
                            row.label(text="colortype:")
                            row.prop(_task, "selected_colortype_in_active_group", text="")

                            # Toggle to enable/disable
                            if getattr(_task, "selected_colortype_in_active_group", ""):
                                row = box.row(align=True)
                                row.prop(_task, "use_active_colortype_group", text="Enable custom assignment")
                        else:
                            # Show message when no group is selected
                            info_row = box.row()
                            info_row.label(text="[INFO] Select a custom group to assign colortypes", icon='INFO')
                    else:
                        # Message when there are no custom groups
                        info_row = box.row()
                        info_row.label(text="[INFO] No custom groups available. Create one in Animation Color Scheme.", icon='INFO')

                # Collapsible section of saved profiles (simplified)
                row_saved = self.layout.row(align=True)
                icon = 'TRIA_DOWN' if self.props.show_saved_colortypes_section else 'TRIA_RIGHT'
                row_saved.prop(self.props, "show_saved_colortypes_section", text="colortype Assignments Summary", icon=icon, emboss=False)

                if self.props.show_saved_colortypes_section:
                    sumbox = self.layout.box()

                    # Show assignments of the current task
                    if hasattr(_task, "colortype_group_choices") and _task.colortype_group_choices:
                        # Sort: DEFAULT first, then alphabetically
                        sorted_choices = sorted(_task.colortype_group_choices,
                                                key=lambda x: (x.group_name != "DEFAULT", x.group_name))

                        for choice in sorted_choices:
                            row = sumbox.row(align=True)

                            # Different icon for DEFAULT vs custom
                            icon = 'PINNED' if choice.group_name == "DEFAULT" else 'DOT'
                            if choice.enabled:
                                icon = 'RADIOBUT_ON' if choice.group_name != "DEFAULT" else 'PINNED'

                            # Show information
                            colortype_name = choice.selected_colortype or "(no colortype)"
                            status = "✓" if choice.enabled else "○"

                            row.label(text=f"{status} {choice.group_name} → {colortype_name}", icon=icon)
                    else:
                        # Initialize if there is no data
                        info_row = sumbox.row()
                        info_row.label(text="No colortype assignments found", icon='INFO')
                        init_button = sumbox.row()
                        init_button.operator('bim.initialize_colortype_system', text="Initialize colortype Assignments", icon='PLUS')

        except Exception as e:
            # Fallback si algo falla
            # Fallback if something fails
            error_box = self.layout.box()
            error_box.label(text=f"colortype system error: {str(e)}", icon='ERROR')
            error_box.operator('bim.initialize_colortype_system', text="Repair colortype System", icon='TOOL_SETTINGS')
    
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
                # self.draw_filter_ui() - esto puede estar causando el problema
                self.layout.template_list(
                    "BIM_UL_tasks",
                    "",
                    self.tprops,
                    "tasks",
                    self.props,
                    "active_task_index",
                )
        else:
            # dd a bar with 4 buttons for BASELINE when it is not active
            # This is similar to lines 254-271 but for the BASELINE case
            # This function should no longer be used for BASELINE schedules
            # BASELINEs now use the normal UI to allow full editing
            work_schedule = SequenceData.data["work_schedules"].get(work_schedule_id, {})
            grid = self.layout.grid_flow(columns=2, even_columns=True)
            col1 = grid.column()
            col1.label(
                text="{}[{}]".format(work_schedule.get("Name", "Unnamed"), work_schedule.get("PredefinedType", "BASELINE")),
                icon="LINENUMBERS_ON",
            )
            col2 = grid.column()
            row = col2.row(align=True)
            row.alignment = "RIGHT"
            # The 4 specific buttons that should appear for readonly cases
            row.operator("bim.enable_editing_work_schedule_tasks", text="", icon="ACTION").work_schedule = work_schedule_id
            row.operator("bim.enable_editing_work_schedule", text="", icon="GREASEPENCIL").work_schedule = work_schedule_id
            row.operator("bim.copy_work_schedule", text="", icon="DUPLICATE").work_schedule = work_schedule_id
            row.operator("bim.remove_work_schedule", text="", icon="X").work_schedule = work_schedule_id


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
        props = tool.Sequence.get_work_schedule_props()
        if not props.active_work_schedule_id:
            return False
        tprops = tool.Sequence.get_task_tree_props()
        total_tasks = len(tprops.tasks)
        if total_tasks > 0 and props.active_task_index < total_tasks:
            return True
        return False

    def draw(self, context):
        if not TaskICOMData.is_loaded:
            TaskICOMData.load()

        self.props = tool.Sequence.get_work_schedule_props()
        self.tprops = tool.Sequence.get_task_tree_props()
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


class BIM_PT_variance_analysis(Panel):
    bl_label = "Variance Analysis"
    bl_idname = "BIM_PT_variance_analysis"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_sequence"

    @classmethod
    def poll(cls, context):
        props = tool.Sequence.get_work_schedule_props()
        # Only show if a schedule is being edited for tasks
        return props.active_work_schedule_id and props.editing_type == "TASKS"

    def draw(self, context):
        layout = self.layout
        props = tool.Sequence.get_work_schedule_props()

        row = layout.row(align=True)
        row.prop(props, "variance_source_a", text="Compare")
        row.prop(props, "variance_source_b", text="With")
        row.operator("bim.calculate_schedule_variance", text="Calculate", icon="PLAY")
        row.operator("bim.clear_schedule_variance", text="", icon="TRASH")
        
        # Variance color mode controls
        is_variance_active = context.scene.get('BIM_VarianceColorModeActive', False)
        if is_variance_active:
            col = layout.column(align=True)
            col.separator()
            variance_row = col.row(align=True)
            variance_row.label(text="Variance Mode Active", icon="RESTRICT_COLOR_OFF")
            variance_row.operator("bim.deactivate_variance_color_mode", text="Deactivate", icon="CANCEL")

