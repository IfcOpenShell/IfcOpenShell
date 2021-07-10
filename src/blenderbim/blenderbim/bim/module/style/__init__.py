import bpy
from . import ui, prop, operator

classes = (
    operator.AddStyle,
    operator.EnableEditingStyle,
    operator.DisableEditingStyle,
    operator.EditStyle,
    operator.RemoveStyle,
    operator.UpdateStyleColours,
    operator.UnlinkStyle,
    prop.BIMStyleProperties,
    ui.BIM_PT_style,
    ui.BIM_PT_style_attributes,
)


def register():
    bpy.types.Material.BIMStyleProperties = bpy.props.PointerProperty(type=prop.BIMStyleProperties)


def unregister():
    del bpy.types.Material.BIMStyleProperties
