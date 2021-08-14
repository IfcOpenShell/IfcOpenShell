import bpy
from . import ui, prop, operator

classes = (
    operator.TogglePsetExpansion,
    operator.EnablePsetEditing,
    operator.DisablePsetEditing,
    operator.EditPset,
    operator.RemovePset,
    operator.AddPset,
    operator.AddQto,
    operator.GuessQuantity,
    prop.PsetProperties,
    prop.MaterialPsetProperties,
    prop.TaskPsetProperties,
    prop.ResourcePsetProperties,
    prop.ProfilePsetProperties,
    ui.BIM_PT_object_psets,
    ui.BIM_PT_object_qtos,
    ui.BIM_PT_material_psets,
    ui.BIM_PT_task_qtos,
    ui.BIM_PT_resource_qtos,
    ui.BIM_PT_profile_psets,
)


def register():
    bpy.types.Object.PsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)
    bpy.types.Material.PsetProperties = bpy.props.PointerProperty(type=prop.MaterialPsetProperties)
    bpy.types.Scene.TaskPsetProperties = bpy.props.PointerProperty(type=prop.TaskPsetProperties)
    bpy.types.Scene.ResourcePsetProperties = bpy.props.PointerProperty(type=prop.ResourcePsetProperties)
    bpy.types.Scene.ProfilePsetProperties = bpy.props.PointerProperty(type=prop.ProfilePsetProperties)


def unregister():
    del bpy.types.Object.PsetProperties
    del bpy.types.Material.PsetProperties
    del bpy.types.Scene.TaskPsetProperties
    del bpy.types.Scene.ResourcePsetProperties
    del bpy.types.Scene.ProfilePsetProperties
