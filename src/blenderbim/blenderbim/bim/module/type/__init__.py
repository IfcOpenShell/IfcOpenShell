import bpy
from . import ui, prop, operator

classes = (
    operator.AssignType,
    operator.UnassignType,
    operator.EnableEditingType,
    operator.DisableEditingType,
    operator.SelectSimilarType,
    operator.SelectTypeObjects,
    prop.BIMTypeProperties,
    prop.BIMTypeObjectProperties,
    ui.BIM_PT_type,
)


def register():
    bpy.types.Scene.BIMTypeProperties = bpy.props.PointerProperty(type=prop.BIMTypeProperties)
    bpy.types.Object.BIMTypeProperties = bpy.props.PointerProperty(type=prop.BIMTypeObjectProperties)


def unregister():
    del bpy.types.Scene.BIMTypeProperties
    del bpy.types.Object.BIMTypeProperties
