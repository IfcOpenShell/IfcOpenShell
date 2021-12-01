# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
from . import ui, prop, operator

classes = (
    operator.AddOrRemoveElementFromCollection,
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
