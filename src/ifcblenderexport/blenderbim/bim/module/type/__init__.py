import bpy
from . import ui, prop, operator

classes = (
    operator.AssignType,
    operator.UnassignType,
    operator.EnableEditingType,
    operator.DisableEditingType,
    operator.SelectSimilarType,
    prop.BIMTypeProperties,
    ui.BIM_PT_type,
)


def register():
    bpy.types.Object.BIMTypeProperties = bpy.props.PointerProperty(type=prop.BIMTypeProperties)


def unregister():
    del bpy.types.Object.BIMTypeProperties
