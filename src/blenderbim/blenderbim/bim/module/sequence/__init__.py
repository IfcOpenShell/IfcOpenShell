import bpy
from . import ui, prop, operator

classes = (
    operator.LoadTasks,
    operator.DisableTaskEditingUI,
    prop.Task,
    prop.BIMTaskProperties,
    ui.BIM_PT_tasks,
    ui.BIM_UL_tasks,
)


def register():
    bpy.types.Scene.BIMTaskProperties = bpy.props.PointerProperty(type=prop.BIMTaskProperties)


def unregister():
    del bpy.types.Scene.BIMTaskProperties
