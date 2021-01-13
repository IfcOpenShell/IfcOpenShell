import bpy
from . import ui, prop, operator

classes = (
    operator.SelectCobieIfcFile,
    operator.SelectCobieJsonFile,
    operator.ExecuteIfcCobie,
    prop.COBieProperties,
    ui.BIM_PT_cobie,
)


def register():
    bpy.types.Scene.COBieProperties = bpy.props.PointerProperty(type=prop.COBieProperties)


def unregister():
    del bpy.types.Scene.COBieProperties
