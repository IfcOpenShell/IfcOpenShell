import bpy
from . import ui, prop, operator

classes = (
    operator.AddOpening,
    operator.RemoveOpening,
    operator.AddFilling,
    operator.RemoveFilling,
    prop.VoidProperties,
    ui.BIM_PT_voids,
)


def register():
    bpy.types.Scene.VoidProperties = bpy.props.PointerProperty(type=prop.VoidProperties)


def unregister():
    del bpy.types.Scene.VoidProperties
