import bpy
from . import ui, prop, operator

classes = (
    operator.LoadSystems,
    operator.DisableSystemEditingUI,
    operator.AddSystem,
    operator.EditSystem,
    operator.RemoveSystem,
    operator.AssignSystem,
    operator.UnassignSystem,
    operator.EnableEditingSystem,
    operator.DisableEditingSystem,
    operator.SelectSystemProducts,
    prop.System,
    prop.BIMSystemProperties,
    ui.BIM_PT_systems,
    ui.BIM_UL_systems,
)


def register():
    bpy.types.Scene.BIMSystemProperties = bpy.props.PointerProperty(type=prop.BIMSystemProperties)


def unregister():
    del bpy.types.Scene.BIMSystemProperties
