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

import bpy
from . import ui, prop, operator

classes = (
    operator.HighlightProductRelatedTask,
    operator.ExpandAllTasks,
    operator.ContractAllTasks,
    operator.AddSummaryTask,
    operator.AddTask,
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
    operator.BlenderBIM_DatePicker,
    operator.BlenderBIM_DatePickerSetDate,
    operator.BlenderBIM_RedrawDatePicker,
    operator.CalculateTaskDuration,
    operator.ContractTask,
    operator.CopyTaskAttribute,
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
    operator.EnableEditingWorkScheduleTasks,
    operator.EnableEditingWorkCalendar,
    operator.EnableEditingWorkCalendarTimes,
    operator.EnableEditingWorkPlan,
    operator.EnableEditingWorkPlanSchedules,
    operator.EnableEditingWorkSchedule,
    operator.EnableEditingWorkTime,
    operator.ExpandTask,
    operator.ExportMSP,
    operator.ExportP6,
    operator.GenerateGanttChart,
    operator.ImportMSP,
    operator.ImportP6,
    operator.ImportP6XER,
    operator.ImportPP,
    operator.LoadTaskInputs,
    operator.LoadTaskOutputs,
    operator.LoadTaskProperties,
    operator.LoadTaskResources,
    operator.RecalculateSchedule,
    operator.RemoveTask,
    operator.RemoveTaskCalendar,
    operator.RemoveTaskColumn,
    operator.RemoveTimePeriod,
    operator.RemoveWorkCalendar,
    operator.RemoveWorkPlan,
    operator.RemoveWorkSchedule,
    operator.RemoveWorkTime,
    operator.SelectTaskRelatedProducts,
    operator.SelectTaskRelatedInputs,
    operator.SetTaskSortColumn,
    operator.UnassignLagTime,
    operator.UnassignPredecessor,
    operator.UnassignProcess,
    operator.UnassignProduct,
    operator.UnassignRecurrencePattern,
    operator.UnassignSuccessor,
    operator.UnassignWorkSchedule,
    operator.VisualiseWorkScheduleDate,
    operator.VisualiseWorkScheduleDateRange,
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.Task,
    prop.TaskResource,
    prop.TaskProduct,
    prop.BIMWorkScheduleProperties,
    prop.BIMTaskTreeProperties,
    prop.WorkCalendar,
    prop.RecurrenceComponent,
    prop.BIMWorkCalendarProperties,
    prop.DatePickerProperties,
    prop.BIMDateTextProperties,
    prop.BIMDuration,
    ui.BIM_PT_work_plans,
    ui.BIM_PT_work_schedules,
    ui.BIM_PT_work_calendars,
    ui.BIM_PT_task_icom,
    ui.BIM_UL_task_columns,
    ui.BIM_UL_task_inputs,
    ui.BIM_UL_task_resources,
    ui.BIM_UL_task_outputs,
    ui.BIM_UL_tasks,
    ui.BIM_PT_SequenceToolKit,
)


def menu_func_export(self, context):
    self.layout.operator(operator.ExportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operator.ExportMSP.bl_idname, text="Microsoft Project (.xml)")


def menu_func_import(self, context):
    self.layout.operator(operator.ImportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operator.ImportP6XER.bl_idname, text="P6 (.xer)")
    self.layout.operator(operator.ImportPP.bl_idname, text="Powerproject (.pp)")
    self.layout.operator(operator.ImportMSP.bl_idname, text="Microsoft Project (.xml)")


def register():
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)
    bpy.types.Scene.BIMTaskTreeProperties = bpy.props.PointerProperty(type=prop.BIMTaskTreeProperties)
    bpy.types.Scene.BIMWorkCalendarProperties = bpy.props.PointerProperty(type=prop.BIMWorkCalendarProperties)
    bpy.types.Scene.DatePickerProperties = bpy.props.PointerProperty(type=prop.DatePickerProperties)
    bpy.types.Scene.BIMDuration = bpy.props.PointerProperty(type=prop.BIMDuration)
    bpy.types.TextCurve.BIMDateTextProperties = bpy.props.PointerProperty(type=prop.BIMDateTextProperties)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    del bpy.types.Scene.BIMWorkPlanProperties
    del bpy.types.Scene.BIMWorkScheduleProperties
    del bpy.types.Scene.BIMTaskTreeProperties
    del bpy.types.Scene.BIMWorkCalendarProperties
    del bpy.types.Scene.DatePickerProperties
    del bpy.types.Scene.BIMDuration
    del bpy.types.TextCurve.BIMDateTextProperties
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
