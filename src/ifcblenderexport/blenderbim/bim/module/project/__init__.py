import bpy
from . import ui, prop, operator

classes = (
    operator.CreateProject,
    operator.ValidateIfcFile,
    prop.BIMProjectProperties,
    ui.BIM_PT_project,
)


def register():
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)


def unregister():
    del bpy.types.Scene.BIMProjectProperties
