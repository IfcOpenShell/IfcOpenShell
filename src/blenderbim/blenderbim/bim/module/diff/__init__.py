import bpy
from . import ui, prop, operator

classes = (
    operator.SelectDiffJsonFile,
    operator.VisualiseDiff,
    operator.SelectDiffOldFile,
    operator.SelectDiffNewFile,
    operator.ExecuteIfcDiff,
    prop.DiffProperties,
    ui.BIM_PT_diff,
)



def register():
    bpy.types.Scene.DiffProperties = bpy.props.PointerProperty(type=prop.DiffProperties)


def unregister():
    del bpy.types.Scene.DiffProperties

