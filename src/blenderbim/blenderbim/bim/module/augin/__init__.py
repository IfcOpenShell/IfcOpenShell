import bpy
from . import ui, prop, operator

classes = (
    prop.AuginProperties,
    ui.BIM_PT_augin,
    operator.AuginLogin,
    operator.AuginCreateNewModel,
    operator.AuginReset,
)


def register():
    bpy.types.Scene.AuginProperties = bpy.props.PointerProperty(type=prop.AuginProperties)


def unregister():
    del bpy.types.Scene.AuginProperties
