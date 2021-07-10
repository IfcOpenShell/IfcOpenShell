import bpy
from . import ui, prop, operator

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
    prop.Role,
    prop.Address,
    prop.Person,
    prop.Organisation,
    prop.BIMOwnerProperties,
    ui.BIM_PT_people,
    ui.BIM_PT_organisations,
    ui.BIM_PT_owner,
)


def register():
    bpy.types.Scene.BIMOwnerProperties = bpy.props.PointerProperty(type=prop.BIMOwnerProperties)


def unregister():
    del bpy.types.Scene.BIMOwnerProperties
