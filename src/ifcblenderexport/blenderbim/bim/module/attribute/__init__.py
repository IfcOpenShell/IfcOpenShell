import bpy
from . import ui, operator

classes = (
    operator.EnableEditingAttributes,
    operator.DisableEditingAttributes,
    operator.EditAttributes,
    ui.BIM_PT_attributes,
)


def register():
    pass


def unregister():
    pass
