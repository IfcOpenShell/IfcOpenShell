import bpy
from . import ui, prop, operator

classes = (
    operator.AssignType,
    operator.UnassignType,
    operator.EnableEditingType,
    operator.DisableEditingType,
    operator.SelectSimilarType,
    operator.AddTypeInstance,
    prop.BIMTypeProperties,
    ui.BIM_PT_type,
)


def register():
    bpy.types.Object.BIMTypeProperties = bpy.props.PointerProperty(type=prop.BIMTypeProperties)
    bpy.types.VIEW3D_MT_mesh_add.append(ui.add_object_button)


def unregister():
    del bpy.types.Object.BIMTypeProperties
    bpy.types.VIEW3D_MT_mesh_add.remove(ui.add_object_button)
