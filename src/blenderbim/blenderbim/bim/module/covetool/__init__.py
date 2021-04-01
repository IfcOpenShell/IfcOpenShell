import bpy
from . import ui, prop, operator

classes = (
    prop.CoveToolProject,
    prop.CoveToolSimpleAnalysis,
    prop.CoveToolProperties,
    ui.BIM_UL_covetool_projects,
    ui.BIM_PT_covetool,
    operator.Login,
    operator.RunSimpleAnalysis,
    operator.RunAnalysis,
)


def register():
    bpy.types.Scene.CoveToolProperties = bpy.props.PointerProperty(type=prop.CoveToolProperties)


def unregister():
    del bpy.types.Scene.CoveToolProperties
