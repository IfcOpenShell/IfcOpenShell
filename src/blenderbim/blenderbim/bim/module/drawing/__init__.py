import bpy
from . import ui, operator

classes = (
    operator.AddDrawing,
    operator.CreateDrawing,
    ui.BIM_PT_camera,
)


def register():
    pass


def unregister():
    pass
