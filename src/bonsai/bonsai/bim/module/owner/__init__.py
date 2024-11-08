# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import ui, prop, operator

classes = (
    operator.AddActor,
    operator.AddAddress,
    operator.AddAddressAttribute,
    operator.AddOrganisation,
    operator.AddPerson,
    operator.AddPersonAndOrganisation,
    operator.AddPersonAttribute,
    operator.AddRole,
    operator.AssignActor,
    operator.ClearUser,
    operator.DisableEditingActor,
    operator.DisableEditingAddress,
    operator.DisableEditingOrganisation,
    operator.DisableEditingPerson,
    operator.DisableEditingRole,
    operator.EditActor,
    operator.EditAddress,
    operator.EditOrganisation,
    operator.EditPerson,
    operator.EditRole,
    operator.EnableEditingActor,
    operator.EnableEditingAddress,
    operator.EnableEditingOrganisation,
    operator.EnableEditingPerson,
    operator.EnableEditingRole,
    operator.RemoveActor,
    operator.RemoveAddress,
    operator.RemoveAddressAttribute,
    operator.RemoveOrganisation,
    operator.RemovePerson,
    operator.RemovePersonAndOrganisation,
    operator.RemovePersonAttribute,
    operator.RemoveRole,
    operator.SetUser,
    operator.UnassignActor,
    prop.BIMOwnerProperties,
    ui.BIM_PT_people,
    ui.BIM_PT_organisations,
    ui.BIM_PT_owner,
    ui.BIM_PT_actor,
    ui.BIM_PT_object_actor,
)


def register():
    bpy.types.Scene.BIMOwnerProperties = bpy.props.PointerProperty(type=prop.BIMOwnerProperties)


def unregister():
    del bpy.types.Scene.BIMOwnerProperties
