import bpy
from . import ui, operator

classes = (
    operator.EnableReassignClass,
    operator.DisableReassignClass,
    operator.ReassignClass,
    operator.AssignClass,
    operator.UnassignClass,
    ui.BIM_PT_class,
)


def register():
    pass


def unregister():
    pass
