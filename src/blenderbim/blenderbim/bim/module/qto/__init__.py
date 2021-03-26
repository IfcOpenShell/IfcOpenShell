import bpy
from . import ui, prop, operator

classes = (
    operator.CalculateEdgeLengths,
    operator.CalculateFaceAreas,
    operator.CalculateObjectVolumes,
    prop.BIMQtoProperties,
    ui.BIM_PT_qto_utilities,
)


def register():
    bpy.types.Scene.BIMQtoProperties = bpy.props.PointerProperty(type=prop.BIMQtoProperties)


def unregister():
    del bpy.types.Scene.BIMQtoProperties
