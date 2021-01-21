import bpy
from . import ui, prop, operator

classes = (
    operator.EnableEditingAttributes,
    operator.DisableEditingAttributes,
    operator.EditAttributes,
    prop.BIMAttributeProperties,
    ui.BIM_PT_object_attributes,
    ui.BIM_PT_material_attributes,
)


def register():
    bpy.types.Object.BIMAttributeProperties = bpy.props.PointerProperty(type=prop.BIMAttributeProperties)
    bpy.types.Material.BIMAttributeProperties = bpy.props.PointerProperty(type=prop.BIMAttributeProperties)


def unregister():
    del bpy.types.Object.BIMAttributeProperties
    del bpy.types.Material.BIMAttributeProperties
