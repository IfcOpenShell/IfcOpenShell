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

"""
Schedule Operators with Task Column Persistence
==============================================

Schedule operators that maintain task values during column operations.
"""

import bpy
import bonsai.tool as tool
import bonsai.core.sequence as core
from .task_column_persistence import (
    snapshot_before_add_column,
    restore_after_add_column,
    save_combined_state,
    restore_combined_state,
    get_backup_stats
)

class AddTaskColumn(bpy.types.Operator):
    """ADD TASK COLUMN with snapshot system integration"""
    bl_idname = "bim.add_task_column_with_persistence"
    bl_label = "Add Task Column"
    bl_description = "Add task column"
    bl_options = {"REGISTER", "UNDO"}

    column_type: bpy.props.StringProperty()
    name: bpy.props.StringProperty()
    data_type: bpy.props.StringProperty()

    def execute(self, context):
        try:
            # Take snapshot before adding column
            snapshot_before_add_column()
            core.add_task_column(tool.Sequence, self.column_type, self.name, self.data_type)

            # Use delayed restore to allow Blender to finish creating new task objects
            def delayed_restore():
                restore_after_add_column()
                # Force UI refresh
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
                return None

            bpy.app.timers.register(delayed_restore, first_interval=0.05)

            stats = get_backup_stats()
            self.report({'INFO'}, f"Column added successfully")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to add column: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class SetupDefaultTaskColumns(bpy.types.Operator):
    """Setup default columns with snapshot system"""
    bl_idname = "bim.setup_default_task_columns_with_persistence"
    bl_label = "Setup Default Task Columns"
    bl_description = "Setup default task columns"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            save_combined_state()
            tool.Sequence.setup_default_task_columns()

            work_schedule = tool.Sequence.get_active_work_schedule()
            if work_schedule:
                tool.Sequence.load_task_tree(work_schedule)
                tool.Sequence.load_task_properties()

            restore_combined_state()
            self.report({'INFO'}, f"Default columns setup completed")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to setup default columns: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class SetTaskSortColumn(bpy.types.Operator):
    """SET TASK SORT COLUMN with snapshot system integration"""
    bl_idname = "bim.set_task_sort_column_with_persistence"
    bl_label = "Set Task Sort Column"
    bl_description = "Set task sort column"
    bl_options = {"REGISTER", "UNDO"}

    column: bpy.props.StringProperty()

    def execute(self, context):
        try:
            save_combined_state()
            core.set_task_sort_column(tool.Sequence, self.column)

            # Use delayed restore to allow Blender to finish creating new task objects
            def delayed_restore():
                restore_combined_state()
                # Force UI refresh
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        area.tag_redraw()
                return None

            bpy.app.timers.register(delayed_restore, first_interval=0.05)

            self.report({'INFO'}, f"Sort column set")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to set sort column: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class ToggleSortReversed(bpy.types.Operator):
    """SORT REVERSED toggle with snapshot system integration"""
    bl_idname = "bim.toggle_sort_reversed_with_persistence"
    bl_label = "Toggle Sort Direction"
    bl_description = "Toggle sort direction"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            save_combined_state()
            ws_props = tool.Sequence.get_work_schedule_props()
            ws_props.is_sort_reversed = not getattr(ws_props, 'is_sort_reversed', False)
            restore_combined_state()
            self.report({'INFO'}, f"Sort direction changed")

        except Exception as e:
            self.report({'ERROR'}, f"Failed to change sort direction: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class TaskColumnSnapshotOperator(bpy.types.Operator):
    """Manual snapshot operator for task columns"""
    bl_idname = "bim.task_column_snapshot"
    bl_label = "Take Snapshot"
    bl_description = "Take a snapshot of current task values"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            save_combined_state()
            self.report({'INFO'}, "Snapshot taken")

        except Exception as e:
            self.report({'ERROR'}, f"Snapshot failed: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class TaskColumnRestoreOperator(bpy.types.Operator):
    """Manual restore operator for task columns"""
    bl_idname = "bim.task_column_restore"
    bl_label = "Restore Snapshot"
    bl_description = "Restore task values from snapshot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        try:
            restore_combined_state()
            stats = get_backup_stats()

            if stats['is_empty']:
                self.report({'WARNING'}, "No snapshot data to restore")
            else:
                self.report({'INFO'}, "Snapshot restored")

        except Exception as e:
            self.report({'ERROR'}, f"Restore failed: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

class TaskColumnSnapshotStatsOperator(bpy.types.Operator):
    """Display snapshot statistics"""
    bl_idname = "bim.task_column_snapshot_stats"
    bl_label = "Snapshot Info"
    bl_description = "Show snapshot information"

    def execute(self, context):
        try:
            stats = get_backup_stats()

            if stats['is_empty']:
                self.report({'INFO'}, "No snapshot data available")
            else:
                self.report({'INFO'}, f"Snapshot: {stats['task_count']} tasks")

        except Exception as e:
            self.report({'ERROR'}, f"Stats failed: {str(e)}")
            return {"CANCELLED"}

        return {"FINISHED"}

# Integration with existing schedule operators
class TaskColumnPanel(bpy.types.Panel):
    """Panel for task column operations"""
    bl_label = "Task Columns"
    bl_idname = "BIM_PT_task_columns"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "BIM_PT_4d_tools"

    @classmethod
    def poll(cls, context):
        return tool.Sequence.get_active_work_schedule()

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("bim.setup_default_task_columns_with_persistence")

        layout.separator()
        row = layout.row()
        row.label(text="Sorting:")

        col = layout.column(align=True)
        ws_props = tool.Sequence.get_work_schedule_props()
        if ws_props and hasattr(ws_props, 'sort_column') and ws_props.sort_column:
            col.label(text=f"Column: {ws_props.sort_column}")

        is_reversed = getattr(ws_props, 'is_sort_reversed', False) if ws_props else False
        icon = "SORT_DESC" if is_reversed else "SORT_ASC"
        direction = "Desc" if is_reversed else "Asc"
        col.operator("bim.toggle_sort_reversed_with_persistence", text=f"Direction: {direction}", icon=icon)

        layout.separator()
        row = layout.row()
        row.label(text="Snapshot:")

        col = layout.column(align=True)
        col.operator("bim.task_column_snapshot")
        col.operator("bim.task_column_restore")
        col.operator("bim.task_column_snapshot_stats")

# Register operators
classes = [
    AddTaskColumn,
    SetupDefaultTaskColumns,
    SetTaskSortColumn,
    ToggleSortReversed,
    TaskColumnSnapshotOperator,
    TaskColumnRestoreOperator,
    TaskColumnSnapshotStatsOperator,
    TaskColumnPanel,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)