import bpy
from . import ui, operator

classes = (
    operator.AddOpening,
    operator.RemoveOpening,
    ui.BIM_PT_voids,
)


def register():
    pass


def unregister():
    pass
