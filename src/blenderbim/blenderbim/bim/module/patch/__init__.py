import bpy
from . import ui, prop, operator

classes = (
    operator.SelectIfcPatchInput,
    operator.SelectIfcPatchOutput,
    operator.ExecuteIfcPatch,
    operator.PopulatePatchArguments,
    prop.BIMPatchProperties,
    ui.BIM_PT_patch,
)


def register():
    bpy.types.Scene.BIMPatchProperties = bpy.props.PointerProperty(type=prop.BIMPatchProperties)


def unregister():
    del bpy.types.Scene.BIMPatchProperties
