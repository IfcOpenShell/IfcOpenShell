import bpy
from . import ui, prop, operator

classes = (
    operator.LoadWorkPlans,
    operator.DisableWorkPlanEditingUI,
    operator.AddWorkPlan,
    operator.EditWorkPlan,
    operator.RemoveWorkPlan,
    operator.EnableEditingWorkPlan,
    operator.DisableEditingWorkPlan,
    operator.LoadWorkSchedules,
    operator.DisableWorkScheduleEditingUI,
    operator.AddWorkSchedule,
    operator.EditWorkSchedule,
    operator.RemoveWorkSchedule,
    operator.EnableEditingWorkSchedule,
    operator.DisableEditingWorkSchedule,
    operator.LoadTasks,
    operator.DisableTaskEditingUI,
    operator.LoadWorkCalendars,
    operator.DisableWorkCalendarEditingUI,
    operator.AddWorkCalendar,
    operator.EditWorkCalendar,
    operator.RemoveWorkCalendar,
    operator.EnableEditingWorkCalendar,
    operator.DisableEditingWorkCalendar,
    operator.AddTask,
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.Task,
    prop.WorkSchedule,
    prop.BIMWorkScheduleProperties,
    prop.WorkCalendar,
    prop.BIMWorkCalendarProperties,
    ui.BIM_PT_work_plans,
    ui.BIM_UL_work_plans,
    ui.BIM_PT_work_schedules,
    ui.BIM_UL_work_schedules,
    ui.BIM_PT_work_calendars,
    ui.BIM_UL_work_calendars,
    ui.BIM_UL_tasks,
)

def register():
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)
    bpy.types.Scene.BIMWorkCalendarProperties = bpy.props.PointerProperty(type=prop.BIMWorkCalendarProperties)

def unregister():
    del bpy.types.Scene.BIMWorkPlanProperties
    del bpy.types.Scene.BIMWorkScheduleProperties
    del bpy.types.Scene.BIMWorkCalendarProperties
