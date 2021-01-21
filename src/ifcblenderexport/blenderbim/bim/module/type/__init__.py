import bpy
from . import ui, operator

classes = (
    operator.AssignType,
    operator.UnassignType,
    operator.EnableEditingType,
    operator.DisableEditingType,
    operator.SelectSimilarType,
    ui.BIM_PT_type,
)


def register():
    pass


def unregister():
    pass
