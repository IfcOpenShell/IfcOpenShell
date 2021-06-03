import bpy
from . import ui, prop, operator

classes = (
    operator.AddWorkPlan,
    operator.EditWorkPlan,
    operator.RemoveWorkPlan,
    operator.EnableEditingWorkPlan,
    operator.DisableEditingWorkPlan,
    operator.EnableEditingWorkPlanSchedules,
    operator.AssignWorkSchedule,
    operator.UnassignWorkSchedule,
    operator.AddWorkSchedule,
    operator.EditWorkSchedule,
    operator.RemoveWorkSchedule,
    operator.EnableEditingWorkSchedule,
    operator.EnableEditingTasks,
    operator.DisableEditingWorkSchedule,
    operator.DisableEditingSequence,
    operator.EditSequenceAttributes,
    operator.EditSequenceTimeLag,
    operator.EnableEditingSequenceAttributes,
    operator.EnableEditingSequenceTimeLag,
    operator.AddWorkCalendar,
    operator.EditWorkCalendar,
    operator.EditWorkTime,
    operator.RemoveWorkCalendar,
    operator.RemoveWorkTime,
    operator.UnassignRecurrencePattern,
    operator.UnassignLagTime,
    operator.RemoveTimePeriod,
    operator.EnableEditingWorkCalendar,
    operator.EnableEditingWorkTime,
    operator.EnableEditingWorkCalendarTimes,
    operator.DisableEditingWorkCalendar,
    operator.DisableEditingWorkTime,
    operator.AddWorkTime,
    operator.AssignLagTime,
    operator.AssignRecurrencePattern,
    operator.AddTimePeriod,
    operator.AddTask,
    operator.AddSummaryTask,
    operator.ExpandTask,
    operator.ContractTask,
    operator.RemoveTask,
    operator.EnableEditingTask,
    operator.DisableEditingTask,
    operator.DisableEditingTaskTime,
    operator.EditTask,
    operator.AssignPredecessor,
    operator.AssignSuccessor,
    operator.UnassignPredecessor,
    operator.UnassignSuccessor,
    operator.EnableEditingTaskTime,
    operator.EnableEditingTaskCalendar,
    operator.EnableEditingTaskSequence,
    operator.EditTaskTime,
    operator.EditTaskCalendar,
    operator.RemoveTaskCalendar,
    operator.AssignProduct,
    operator.UnassignProduct,
    operator.GenerateGanttChart,
    operator.ImportP6,
    operator.ImportMSP,
    operator.LoadTaskProperties,
    operator.SelectTaskRelatedProducts,
    operator.VisualiseWorkScheduleDate,
    operator.VisualiseWorkScheduleDateRange,
    operator.RecalculateSchedule,
    operator.BlenderBIM_DatePicker,
    operator.BlenderBIM_DatePickerSetDate,
    operator.BlenderBIM_RedrawDatePicker,
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.Task,
    prop.BIMWorkScheduleProperties,
    prop.BIMTaskTreeProperties,
    prop.WorkCalendar,
    prop.RecurrenceComponent,
    prop.BIMWorkCalendarProperties,
    prop.DatePickerProperties,
    ui.BIM_PT_work_plans,
    ui.BIM_PT_work_schedules,
    ui.BIM_PT_work_calendars,
    ui.BIM_UL_tasks,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportP6.bl_idname, text="P6 (.xml)")
    self.layout.operator(operator.ImportMSP.bl_idname, text="Microsoft Project (.xml)")


def register():
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)
    bpy.types.Scene.BIMTaskTreeProperties = bpy.props.PointerProperty(type=prop.BIMTaskTreeProperties)
    bpy.types.Scene.BIMWorkCalendarProperties = bpy.props.PointerProperty(type=prop.BIMWorkCalendarProperties)
    bpy.types.Scene.DatePickerProperties = bpy.props.PointerProperty(type=prop.DatePickerProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    del bpy.types.Scene.BIMWorkPlanProperties
    del bpy.types.Scene.BIMWorkScheduleProperties
    del bpy.types.Scene.BIMTaskTreeProperties
    del bpy.types.Scene.BIMWorkCalendarProperties
    del bpy.types.Scene.DatePickerProperties
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
