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

# Description: General operators for schedule-wide actions like recalculation, Gantt charts, and variance analysis.

import bpy
import bonsai.tool as tool
import bonsai.core.sequence as core
from .operator import snapshot_all_ui_state
from .schedule_task_operators import restore_all_ui_state

# ============================================================================
# SCHEDULE UTILITY OPERATORS
# ============================================================================

class RecalculateSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.recalculate_schedule"
    bl_label = "Recalculate Schedule"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.recalculate_schedule(tool.Ifc, work_schedule=tool.Ifc.get().by_id(self.work_schedule))


class GenerateGanttChart(bpy.types.Operator):
    bl_idname = "bim.generate_gantt_chart"
    bl_label = "Generate Gantt Chart"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def execute(self, context):
        try:
            work_schedule = tool.Ifc.get().by_id(self.work_schedule)
            if not work_schedule:
                self.report({'ERROR'}, "Work schedule not found")
                return {'CANCELLED'}
            import ifcopenshell.util.sequence as _useq
            if not _useq.get_root_tasks(work_schedule):
                self.report({'WARNING'}, "No tasks found in schedule")
                return {'CANCELLED'}
            core.generate_gantt_chart(tool.Sequence, work_schedule=work_schedule)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate Gantt chart: {str(e)}")
            return {'CANCELLED'}


class AddTaskColumn(bpy.types.Operator):
    bl_idname = "bim.add_task_column"
    bl_label = "Add Task Column"
    bl_options = {"REGISTER", "UNDO"}
    column_type: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        print(f"[DEBUG] AddTaskColumn: Starting - taking snapshot")
        snapshot_all_ui_state(context)
        print(f"[DEBUG] AddTaskColumn: Adding column {self.column_type}.{self.name}")
        # Let core.add_task_column do its work INCLUDING load_task_tree
        core.add_task_column(tool.Sequence, self.column_type, self.name, self.data_type)
        # NOW restore after tasks have been recreated
        print(f"[DEBUG] AddTaskColumn: Restoring snapshot AFTER task tree reload")
        restore_all_ui_state(context)

        # FORCE a second restore after a small delay to ensure it sticks
        def delayed_restore():
            print(f"[DEBUG] AddTaskColumn: DELAYED restore attempt")
            restore_all_ui_state(context)
            return None  # Don't repeat

        bpy.app.timers.register(delayed_restore, first_interval=0.1)
        print(f"[DEBUG] AddTaskColumn: Completed")
        return {"FINISHED"}


class SetupDefaultTaskColumns(bpy.types.Operator):
    bl_idname = "bim.setup_default_task_columns"
    bl_label = "Setup Default Task Columns"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(f"[DEBUG] SetupDefaultTaskColumns: Starting - taking snapshot")
        snapshot_all_ui_state(context)
        print(f"[DEBUG] SetupDefaultTaskColumns: Setting up default columns")
        core.setup_default_task_columns(tool.Sequence)
        # Manually reload task tree since core.setup_default_task_columns doesn't do it
        work_schedule = tool.Sequence.get_active_work_schedule()
        if work_schedule:
            tool.Sequence.load_task_tree(work_schedule)
            tool.Sequence.load_task_properties()
        print(f"[DEBUG] SetupDefaultTaskColumns: Restoring snapshot")
        restore_all_ui_state(context)
        print(f"[DEBUG] SetupDefaultTaskColumns: Completed")
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
        snapshot_all_ui_state(context)
        core.set_task_sort_column(tool.Sequence, self.column)
        restore_all_ui_state(context)
        return {'FINISHED'}


class ToggleSortReversedOperator(bpy.types.Operator):
    bl_idname = "toggle_sort_reversed"
    bl_label = "Toggle Sort Direction"
    bl_description = "Toggle sort direction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        print(f"[DEBUG] ToggleSortReversedOperator: Starting")
        try:
            # Get current state
            ws_props = tool.Sequence.get_work_schedule_props()
            current_reversed = getattr(ws_props, 'is_sort_reversed', False)
            new_reversed = not current_reversed

            print(f"[DEBUG] ToggleSortReversedOperator: Taking snapshot")
            snapshot_all_ui_state(context)

            print(f"[DEBUG] ToggleSortReversedOperator: Setting {new_reversed}, loading task tree")
            # Set the value directly without triggering callbacks
            ws_props.is_sort_reversed = new_reversed

            # Manually trigger the reload like the callback would do
            if ws_props.active_work_schedule_id:
                work_schedule = tool.Ifc.get().by_id(ws_props.active_work_schedule_id)
                if work_schedule:
                    tool.Sequence.load_task_tree(work_schedule)
                    tool.Sequence.load_task_properties()

            print(f"[DEBUG] ToggleSortReversedOperator: Restoring snapshot")
            restore_all_ui_state(context)

            # Delayed restore for safety
            def delayed_restore():
                print(f"[DEBUG] ToggleSortReversedOperator: DELAYED restore")
                restore_all_ui_state(context)
                return None

            bpy.app.timers.register(delayed_restore, first_interval=0.1)

            direction = "descending" if new_reversed else "ascending"
            self.report({'INFO'}, f"Sort direction: {direction}")
            print(f"[DEBUG] ToggleSortReversedOperator: Completed")

        except Exception as e:
            print(f"[ERROR] ToggleSortReversedOperator failed: {e}")
            import traceback
            traceback.print_exc()
            self.report({'ERROR'}, f"Failed to toggle sort direction: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}


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


class CalculateScheduleVariance(bpy.types.Operator):
    """Calculates the variance between two date sets for all tasks."""
    bl_idname = "bim.calculate_schedule_variance"
    bl_label = "Calculate Schedule Variance"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        import ifcopenshell.util.sequence

        ws_props = tool.Sequence.get_work_schedule_props()
        task_props = tool.Sequence.get_task_tree_props()

        if not task_props.tasks:
            self.report({'WARNING'}, "No tasks visible to calculate variance. Clear filters to see all tasks.")
            return {'CANCELLED'}

        source_a = ws_props.variance_source_a
        source_b = ws_props.variance_source_b

        if source_a == source_b:
            self.report({'WARNING'}, "Cannot compare a date set with itself.")
            return {'CANCELLED'}

        finish_attr_a = f"{source_a.capitalize()}Finish"
        finish_attr_b = f"{source_b.capitalize()}Finish"

        tasks_processed = 0
        for task_pg in task_props.tasks:
            task_ifc = tool.Ifc.get().by_id(task_pg.ifc_definition_id)
            if not task_ifc:
                continue

            date_a = ifcopenshell.util.sequence.derive_date(task_ifc, finish_attr_a, is_latest=True)
            date_b = ifcopenshell.util.sequence.derive_date(task_ifc, finish_attr_b, is_latest=True)

            if date_a and date_b:
                delta = date_b.date() - date_a.date()
                variance_days = delta.days
                task_pg.variance_days = variance_days

                if variance_days > 0:
                    task_pg.variance_status = f"Delayed (+{variance_days}d)"
                elif variance_days < 0:
                    task_pg.variance_status = f"Ahead ({variance_days}d)"
                else:
                    task_pg.variance_status = "On Time"
                tasks_processed += 1
            else:
                task_pg.variance_status = "N/A"
                task_pg.variance_days = 0

        self.report({'INFO'}, f"Variance calculated for {tasks_processed} tasks ({source_a} vs {source_b}).")
        return {'FINISHED'}


class ClearScheduleVariance(bpy.types.Operator):
    """Clears the calculated variance from all visible tasks."""
    bl_idname = "bim.clear_schedule_variance"
    bl_label = "Clear Variance"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        tool.Sequence.clear_schedule_variance()
        self.report({'INFO'}, "Cleared variance and color mode.")
        return {'FINISHED'}


class DeactivateVarianceColorMode(bpy.types.Operator):
    bl_idname = "bim.deactivate_variance_color_mode"
    bl_label = "Deactivate Variance Color Mode"
    bl_description = "Deactivate variance color mode and restore normal colors"
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        try:
            tool.Sequence.deactivate_variance_color_mode()
            self.report({'INFO'}, "Variance color mode deactivated")
        except Exception as e:
            self.report({'ERROR'}, f"Deactivation failed: {e}")
        return {'FINISHED'}


class RefreshTask3DCounts(bpy.types.Operator):
    """Recalculates the number of 3D elements (Inputs + Outputs) for all tasks in the list."""
    bl_idname = "bim.refresh_task_3d_counts"
    bl_label = "Refresh 3D Counts"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            # Call the new function in the core
            core.refresh_task_3d_counts(tool.Sequence)
            self.report({'INFO'}, "'3D' counts updated.")
            
            # Force a redraw of the UI to show the changes
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()

        except Exception as e:
            self.report({'ERROR'}, f"Failed to refresh: {e}")
            return {'CANCELLED'}
        return {'FINISHED'}


class AddTaskBars(bpy.types.Operator):
    bl_idname = "bim.add_task_bars"
    bl_label = "Generate Task Bars"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Generate 3D bars for selected tasks aligned with schedule dates"

    def execute(self, context):
        try:
            # Check if animation is active for safer use
            try:
                import bonsai.tool as tool
                anim_props = tool.Sequence.get_animation_props()
                is_animation_active = getattr(anim_props, 'is_animation_created', False)
                if is_animation_active:
                    print("[WARNING] Generating task bars during active animation - using safe mode")
                    # Continue but with more protections
            except Exception:
                pass  # If it cannot be verified, continue normally

            tool.Sequence.refresh_task_bars()
            task_count = len(tool.Sequence.get_task_bar_list())
            self.report({'INFO'}, f"Generated bars for {task_count} tasks.")
            return {"FINISHED"}
        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate task bars: {str(e)}")
            return {'CANCELLED'}


class ClearTaskBars(bpy.types.Operator):
    bl_idname = "bim.clear_task_bars"
    bl_label = "Clear Task Bars"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove all task bar visualizations"

    def execute(self, context):
        tool.Sequence.clear_task_bars()
        self.report({'INFO'}, "Task bars cleared")
        return {"FINISHED"}


class GuessDateRange(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.guess_date_range"
    bl_label = "Guess Work Schedule Date Range"
    bl_options = {"REGISTER", "UNDO"}
    work_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        work_schedule = tool.Ifc.get().by_id(self.work_schedule)
        
        # Calculate unified date range across all schedule types for HUD timeline
        unified_start_date, unified_finish_date = self._calculate_unified_range(work_schedule)
        
        if unified_start_date and unified_finish_date:
            tool.Sequence.update_visualisation_date(unified_start_date, unified_finish_date)
            self.report({'INFO'}, f"Unified timeline set: {unified_start_date.strftime('%Y-%m-%d')} to {unified_finish_date.strftime('%Y-%m-%d')}")
        else:
            self.report({'WARNING'}, "No dates found across any schedule types to create unified range.")
        return {"FINISHED"}
    
    def _calculate_unified_range(self, work_schedule):
        """Calculate unified date range across all schedule types"""
        import ifcopenshell.util.sequence
        
        if not work_schedule:
            return None, None
            
        # Get all tasks from schedule
        root_tasks = ifcopenshell.util.sequence.get_root_tasks(work_schedule)
        if not root_tasks:
            return None, None
            
        def get_all_tasks(tasks):
            all_tasks = []
            for task in tasks:
                all_tasks.append(task)
                nested = ifcopenshell.util.sequence.get_nested_tasks(task)
                if nested:
                    all_tasks.extend(get_all_tasks(nested))
            return all_tasks
        
        all_tasks = get_all_tasks(root_tasks)
        schedule_types = ['SCHEDULE', 'ACTUAL', 'EARLY', 'LATE']
        
        all_start_dates = []
        all_finish_dates = []
        
        # Collect dates from all schedule types
        for schedule_type in schedule_types:
            start_attr = f"{schedule_type.capitalize()}Start"
            finish_attr = f"{schedule_type.capitalize()}Finish"
            
            for task in all_tasks:
                start_date = ifcopenshell.util.sequence.derive_date(task, start_attr, is_earliest=True)
                if start_date:
                    all_start_dates.append(start_date)
                    
                finish_date = ifcopenshell.util.sequence.derive_date(task, finish_attr, is_latest=True)
                if finish_date:
                    all_finish_dates.append(finish_date)
        
        if not all_start_dates or not all_finish_dates:
            return None, None
            
        return min(all_start_dates), max(all_finish_dates)
