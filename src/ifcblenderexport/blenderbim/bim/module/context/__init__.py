import bpy
from . import ui, operator

classes = (
    operator.AddSubcontext,
    operator.RemoveSubcontext,
    ui.BIM_PT_context,
)


def register():
    pass


def unregister():
    pass
