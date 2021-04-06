import bpy
from . import ui, prop, operator

classes = (
    operator.LoadWorkPlans,
    operator.DisableWorkPlanEditingUI,
    operator.LoadTasks,
    operator.DisableTaskEditingUI,
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
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.WorkSchedule,
    prop.BIMWorkScheduleProperties,
    prop.Task,
    prop.BIMTaskProperties,
    ui.BIM_PT_work_plans,
    ui.BIM_UL_work_plans,
    ui.BIM_PT_work_schedules,
    ui.BIM_UL_work_schedules,
    ui.BIM_PT_tasks,
    ui.BIM_UL_tasks,
)


def register():
    bpy.types.Scene.BIMTaskProperties = bpy.props.PointerProperty(type=prop.BIMTaskProperties)
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)
    bpy.types.Scene.BIMWorkScheduleProperties = bpy.props.PointerProperty(type=prop.BIMWorkScheduleProperties)


def unregister():
    del bpy.types.Scene.BIMTaskProperties
    del bpy.types.Scene.BIMWorkPlanProperties
    del bpy.types.Scene.BIMWorkScheduleProperties
