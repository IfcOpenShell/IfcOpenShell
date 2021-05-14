import bpy
from . import ui, operator

classes = (
    operator.AddDrawing,
    operator.CreateDrawing,
    operator.AddAnnotation,
    ui.BIM_PT_camera,
)


def register():
    pass


def unregister():
    pass
