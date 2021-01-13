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
    ui.BIM_PT_object_psets,
    ui.BIM_PT_object_qtos,
)


def register():
    bpy.types.Object.PsetProperties = bpy.props.PointerProperty(type=prop.PsetProperties)


def unregister():
    del bpy.types.Object.PsetProperties
