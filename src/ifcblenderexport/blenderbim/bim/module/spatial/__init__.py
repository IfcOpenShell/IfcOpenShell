import bpy
from . import ui, operator

classes = (
    operator.AssignContainer,
    operator.RemoveContainer,
    operator.EnableEditingContainer,
    operator.DisableEditingContainer,
    ui.BIM_PT_spatial,
)


def register():
    pass


def unregister():
    pass
