import bpy
from . import ui, prop, operator

classes = (
    operator.ProfileImportIFC,
    operator.CreateAllShapes,
    operator.CreateShapeFromStepId,
    operator.SelectHighPolygonMeshes,
    operator.InspectFromStepId,
    operator.InspectFromObject,
    operator.RewindInspector,
    prop.BIMDebugProperties,
    ui.BIM_PT_debug,
)


def register():
    bpy.types.Scene.BIMDebugProperties = bpy.props.PointerProperty(type=prop.BIMDebugProperties)


def unregister():
    del bpy.types.Scene.BIMDebugProperties
