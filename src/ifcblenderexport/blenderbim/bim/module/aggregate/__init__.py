import bpy
from . import ui, operator

classes = (
    operator.AssignObject,
    operator.EnableEditingAggregate,
    operator.DisableEditingAggregate,
    ui.BIM_PT_aggregate,
)


def register():
    pass


def unregister():
    pass
