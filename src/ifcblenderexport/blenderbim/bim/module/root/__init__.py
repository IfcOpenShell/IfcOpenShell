import bpy
from . import ui, prop, operator

classes = (
    operator.EnableReassignClass,
    operator.DisableReassignClass,
    operator.ReassignClass,
    operator.AssignClass,
    operator.UnassignClass,
    prop.BIMRootProperties,
    ui.BIM_PT_class,
)


def register():
    bpy.types.Scene.BIMRootProperties = bpy.props.PointerProperty(type=prop.BIMRootProperties)


def unregister():
    del bpy.types.Scene.BIMRootProperties
