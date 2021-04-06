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
    prop.WorkPlan,
    prop.BIMWorkPlanProperties,
    prop.Task,
    prop.BIMTaskProperties,
    ui.BIM_PT_work_plans,
    ui.BIM_UL_work_plans,
    ui.BIM_PT_tasks,
    ui.BIM_UL_tasks,
)


def register():
    bpy.types.Scene.BIMTaskProperties = bpy.props.PointerProperty(type=prop.BIMTaskProperties)
    bpy.types.Scene.BIMWorkPlanProperties = bpy.props.PointerProperty(type=prop.BIMWorkPlanProperties)


def unregister():
    del bpy.types.Scene.BIMTaskProperties
    del bpy.types.Scene.BIMWorkPlanProperties
