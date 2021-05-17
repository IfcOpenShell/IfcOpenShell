import bpy
from . import ui, prop, operator, handler

classes = (
    operator.AddDrawing,
    operator.CreateDrawing,
    operator.AddAnnotation,
    prop.Variable,
    prop.Drawing,
    prop.Schedule,
    prop.DrawingStyle,
    prop.Sheet,
    prop.DocProperties,
    prop.BIMCameraProperties,
    prop.BIMTextProperties,
    ui.BIM_PT_camera,
)


def register():
    bpy.types.Scene.DocProperties = bpy.props.PointerProperty(type=prop.DocProperties)
    bpy.types.Camera.BIMCameraProperties = bpy.props.PointerProperty(type=prop.BIMCameraProperties)
    bpy.types.TextCurve.BIMTextProperties = bpy.props.PointerProperty(type=prop.BIMTextProperties)
    bpy.app.handlers.load_post.append(handler.toggleDecorationsOnLoad)


def unregister():
    del bpy.types.Scene.DocProperties
    del bpy.types.Camera.BIMCameraProperties
    del bpy.types.TextCurve.BIMTextProperties
    bpy.app.handlers.load_post.remove(handler.toggleDecorationsOnLoad)
