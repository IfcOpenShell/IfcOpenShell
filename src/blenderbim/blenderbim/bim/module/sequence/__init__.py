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

import bpy
from . import ui, prop, operator

classes = (
    operator.AddAnimationCamera,
    operator.AddSummaryTask,
    operator.AddTask,
    operator.AddTaskBars,
    operator.AddTaskColumn,
    operator.AddTimePeriod,
    operator.AddWorkCalendar,
    operator.AddWorkPlan,
    operator.AddWorkSchedule,
    operator.AddWorkTime,
    operator.AssignLagTime,
    operator.AssignPredecessor,
    operator.AssignProcess,
    operator.AssignProduct,
    operator.AssignRecurrencePattern,
    operator.AssignSuccessor,
    operator.AssignWorkSchedule,
    operator.Bonsai_DatePicker,
    operator.Bonsai_DatePickerSetDate,
    operator.Bonsai_RedrawDatePicker,
    operator.CalculateTaskDuration,
    operator.ClearPreviousAnimation,
    operator.ContractAllTasks,
    operator.ContractTask,
    operator.CopyTask,
    operator.CopyTaskAttribute,
    operator.CreateBaseline,
    operator.DisableEditingSequence,
    operator.DisableEditingTask,
    operator.DisableEditingTaskTime,
    operator.DisableEditingWorkCalendar,
    operator.DisableEditingWorkPlan,
    operator.DisableEditingWorkSchedule,
    operator.DisableEditingWorkTime,
    operator.EditSequenceAttributes,
    operator.EditSequenceTimeLag,
    operator.EditTask,
    operator.EditTaskCalendar,
    operator.EditTaskTime,
    operator.EditWorkCalendar,
    operator.EditWorkPlan,
    operator.EditWorkSchedule,
    operator.EditWorkTime,
    operator.EnableEditingSequenceAttributes,
    operator.EnableEditingSequenceTimeLag,
    operator.EnableEditingTask,
    operator.EnableEditingTaskCalendar,
    operator.EnableEditingTaskSequence,
    operator.EnableEditingTaskTime,
    operator.EnableEditingWorkCalendar,
    operator.EnableEditingWorkCalendarTimes,
    operator.EnableEditingWorkPlan,
    operator.EnableEditingWorkPlanSchedules,
    operator.EnableEditingWorkSchedule,
    operator.EnableEditingWorkScheduleTasks,
    operator.EnableEditingWorkTime,
    operator.ExpandAllTasks,
    operator.ExpandTask,
    operator.ExportMSP,
    operator.ExportP6,
    operator.GenerateGanttChart,
    operator.GuessDateRange,
    operator.GoToTask,
    operator.ImportCSV,
    operator.ImportMSP,
    operator.ImportP6,
    operator.ImportP6XER,
    operator.ImportPP,
    operator.LoadAnimationColorScheme,
    operator.LoadDefaultAnimationColors,
    operator.LoadProductTasks,
    operator.LoadTaskProperties,
    operator.RecalculateSchedule,
    operator.RemoveTask,
    operator.RemoveTaskCalendar,
    operator.RemoveTaskColumn,
    operator.RemoveTimePeriod,
    operator.RemoveWorkCalendar,
    operator.RemoveWorkPlan,
    operator.RemoveWorkSchedule,
    operator.RemoveWorkTime,
    operator.ReorderTask,
    operator.SaveAnimationColorScheme,
    operator.SelectTaskRelatedInputs,
    operator.SelectTaskRelatedProducts,
    operator.SelectUnassignedWorkScheduleProducts,
    operator.SelectWorkScheduleProducts,
    operator.SetTaskSortColumn,
    operator.SetupDefaultTaskColumns,
    operator.UnassignLagTime,
    operator.UnassignPredecessor,
    operator.UnassignProcess,
    operator.UnassignProduct,
    operator.UnassignRecurrencePattern,
    operator.UnassignSuccessor,
    operator.UnassignWorkSchedule,
    operator.VisualiseWorkScheduleDate,
    operator.VisualiseWorkScheduleDateRange,
    operator.EnableStatusFilters,
    operator.DisableStatusFilters,
    operator.ActivateStatusFilters,
    operator.SelectStatusFilter,
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.Task,
    prop.TaskResource,
    prop.TaskProduct,
    prop.ISODuration,
    prop.IFCStatus,
    prop.BIMStatusProperties,
    prop.BIMWorkScheduleProperties,
    prop.BIMTaskTreeProperties,
    prop.BIMTaskTypeColor,
    prop.BIMAnimationProperties,
    prop.WorkCalendar,
    prop.RecurrenceComponent,
    prop.BIMWorkCalendarProperties,
    prop.DatePickerProperties,
    prop.BIMDateTextProperties,
    ui.BIM_PT_status,
    ui.BIM_PT_work_plans,
    ui.BIM_PT_work_schedules,
    ui.BIM_PT_work_calendars,
    ui.BIM_PT_animation_tools,
    ui.BIM_PT_task_icom,
    ui.BIM_PT_animation_Color_Scheme,
    ui.BIM_UL_task_columns,
    ui.BIM_UL_task_inputs,
    ui.BIM_UL_task_resources,
    ui.BIM_UL_task_outputs,
    ui.BIM_UL_tasks,
    ui.BIM_PT_4D_Tools,
    ui.BIM_UL_animation_colors,
    ui.BIM_UL_product_input_tasks,
    ui.BIM_UL_product_output_tasks,
)


def menu_func_export(self, context):
    self.layout.operator(operator.ExportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operator.ExportMSP.bl_idname, text="Microsoft Project (.xml)")


def menu_func_import(self, context):
    self.layout.operator(operator.ImportCSV.bl_idname, text="Work Schedule (.csv)")
    self.layout.operator(operator.ImportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operator.ImportP6XER.bl_idname, text="P6 (.xer)")
    self.layout.operator(operator.ImportPP.bl_idname, text="Powerproject (.pp)")
    self.layout.operator(operator.ImportMSP.bl_idname, text="Microsoft Project (.xml)")


def register():
    bpy.types.Scene.BIMStatusProperties = bpy.props.PointerProperty(type=prop.BIMStatusProperties)
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)
    bpy.types.Scene.BIMTaskTreeProperties = bpy.props.PointerProperty(type=prop.BIMTaskTreeProperties)
    bpy.types.Scene.BIMWorkCalendarProperties = bpy.props.PointerProperty(type=prop.BIMWorkCalendarProperties)
    bpy.types.Scene.BIMAnimationProperties = bpy.props.PointerProperty(type=prop.BIMAnimationProperties)
    bpy.types.Scene.DatePickerProperties = bpy.props.PointerProperty(type=prop.DatePickerProperties)
    bpy.types.TextCurve.BIMDateTextProperties = bpy.props.PointerProperty(type=prop.BIMDateTextProperties)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    del bpy.types.Scene.BIMStatusProperties
    del bpy.types.Scene.BIMWorkPlanProperties
    del bpy.types.Scene.BIMWorkScheduleProperties
    del bpy.types.Scene.BIMTaskTreeProperties
    del bpy.types.Scene.BIMWorkCalendarProperties
    del bpy.types.Scene.DatePickerProperties
    del bpy.types.Scene.BIMAnimationProperties
    del bpy.types.TextCurve.BIMDateTextProperties
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
