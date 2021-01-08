import bpy
from . import ui, operator

classes = (
    operator.EnableEditingPerson,
    operator.DisableEditingPerson,
    operator.AddPerson,
    operator.EditPerson,
    operator.RemovePerson,
    ui.BIM_PT_people,
)


def register():
    pass


def unregister():
    pass
