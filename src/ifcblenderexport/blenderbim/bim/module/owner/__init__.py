import bpy
from . import ui, operator

classes = (
    operator.EnableEditingPerson,
    operator.DisableEditingPerson,
    operator.AddPerson,
    operator.EditPerson,
    operator.RemovePerson,
    operator.EnableEditingOrganisation,
    operator.DisableEditingOrganisation,
    operator.AddOrganisation,
    operator.EditOrganisation,
    operator.RemoveOrganisation,
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
    ui.BIM_PT_organisations,
)


def register():
    pass


def unregister():
    pass
