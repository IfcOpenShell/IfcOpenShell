import bpy
from . import ui, operator

classes = (
    operator.EnableEditingPerson,
    operator.DisableEditingPerson,
    operator.AddPerson,
    operator.EditPerson,
    operator.RemovePerson,
    operator.EnableEditingRole,
    operator.DisableEditingRole,
    operator.AddRole,
    operator.EditRole,
    operator.RemoveRole,
    operator.EnableEditingAddress,
    operator.DisableEditingAddress,
    operator.AddAddress,
    operator.EditAddress,
    operator.RemoveAddress,
    ui.BIM_PT_people,
)


def register():
    pass


def unregister():
    pass
