import bpy
from . import ui, prop, operator

classes = (
    operator.SelectGlobalId,
    operator.SelectIfcClass,
    operator.SelectAttribute,
    operator.SelectPset,
    operator.ColourByAttribute,
    operator.ColourByPset,
    operator.ColourByClass,
    operator.ResetObjectColours,
    prop.BIMSearchProperties,
    ui.BIM_PT_search,
)


def register():
    bpy.types.Scene.BIMSearchProperties = bpy.props.PointerProperty(type=prop.BIMSearchProperties)


def unregister():
    del bpy.types.Scene.BIMSearchProperties
