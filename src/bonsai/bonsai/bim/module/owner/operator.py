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
import bonsai.tool as tool
import bonsai.core.owner as core


class EnableEditingPerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_person(tool.Owner, person=tool.Ifc.get().by_id(self.person))


class DisableEditingPerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_person(tool.Owner)


class AddPerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_person(tool.Ifc)


class EditPerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_person"
    bl_label = "Edit Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_person(tool.Ifc, tool.Owner)


class RemovePerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_person"
    bl_label = "Remove Person"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_person(tool.Ifc, person=tool.Ifc.get().by_id(self.person))


class AddPersonAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_person_attribute"
    bl_label = "Add Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_person_attribute(tool.Owner, name=self.name)


class RemovePersonAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_person_attribute"
    bl_label = "Remove Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    id: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_person_attribute(tool.Owner, name=self.name, id=self.id)


class EnableEditingRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_role"
    bl_label = "Enable Editing Role"
    bl_options = {"REGISTER", "UNDO"}
    role: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_role(tool.Owner, role=tool.Ifc.get().by_id(self.role))


class DisableEditingRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_role"
    bl_label = "Disable Editing Role"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_role(tool.Owner)


class AddRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_role"
    bl_label = "Add Role"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_role(tool.Ifc, parent=tool.Ifc.get().by_id(self.parent))


class EditRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_role"
    bl_label = "Edit Role"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_role(tool.Ifc, tool.Owner)


class RemoveRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_role"
    bl_label = "Remove Role"
    bl_options = {"REGISTER", "UNDO"}
    role: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_role(tool.Ifc, role=tool.Ifc.get().by_id(self.role))


class AddAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_address"
    bl_label = "Add Address"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_address(tool.Ifc, parent=tool.Ifc.get().by_id(self.parent), ifc_class=self.ifc_class)


class AddAddressAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_address_attribute"
    bl_label = "Add Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_address_attribute(tool.Owner, name=self.name)


class RemoveAddressAttribute(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_address_attribute"
    bl_label = "Remove Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    id: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_address_attribute(tool.Owner, name=self.name, id=self.id)


class EnableEditingAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_address"
    bl_label = "Enable Editing Address"
    bl_options = {"REGISTER", "UNDO"}
    address: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_address(tool.Owner, address=tool.Ifc.get().by_id(self.address))


class DisableEditingAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_address"
    bl_label = "Disable Editing Address"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_address(tool.Owner)


class EditAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_address"
    bl_label = "Edit Address"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_address(tool.Ifc, tool.Owner)


class RemoveAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_address"
    bl_label = "Remove Address"
    bl_options = {"REGISTER", "UNDO"}
    address: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_address(tool.Ifc, address=tool.Ifc.get().by_id(self.address))


class EnableEditingOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_organisation"
    bl_label = "Enable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}
    organisation: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_organisation(tool.Owner, organisation=tool.Ifc.get().by_id(self.organisation))


class DisableEditingOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_organisation"
    bl_label = "Disable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_organisation(tool.Owner)


class AddOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_organisation"
    bl_label = "Add Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_organisation(tool.Ifc)


class EditOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_organisation"
    bl_label = "Edit Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_organisation(tool.Ifc, tool.Owner)


class RemoveOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_organisation"
    bl_label = "Remove Organisation"
    bl_options = {"REGISTER", "UNDO"}
    organisation: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_organisation(tool.Ifc, tool.Ifc.get().by_id(self.organisation))


class AddPersonAndOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_person_and_organisation"
    bl_label = "Add Person And Organisation"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()
    organisation: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_person_and_organisation(
            tool.Ifc, person=tool.Ifc.get().by_id(self.person), organisation=tool.Ifc.get().by_id(self.organisation)
        )


class RemovePersonAndOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_person_and_organisation"
    bl_label = "Remove Person And Organisation"
    bl_options = {"REGISTER", "UNDO"}
    person_and_organisation: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_person_and_organisation(
            tool.Ifc, tool.Owner, person_and_organisation=tool.Ifc.get().by_id(self.person_and_organisation)
        )


class SetUser(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.set_user"
    bl_label = "Set User"
    bl_options = {"REGISTER", "UNDO"}
    user: bpy.props.IntProperty()

    def _execute(self, context):
        core.set_user(tool.Owner, user=tool.Ifc.get().by_id(self.user))


class ClearUser(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_user"
    bl_label = "Clear User"
    bl_options = {"REGISTER", "UNDO"}
    user: bpy.props.IntProperty()

    def _execute(self, context):
        core.clear_user(tool.Owner)


class AddActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_actor"
    bl_label = "Add Actor"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = bpy.context.scene.BIMOwnerProperties
        if props.the_actor:
            core.add_actor(tool.Ifc, ifc_class=props.actor_class, actor=tool.Ifc.get().by_id(int(props.the_actor)))


class EnableEditingActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_actor"
    bl_label = "Enable Editing Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_actor(tool.Owner, actor=tool.Ifc.get().by_id(self.actor))


class DisableEditingActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_actor"
    bl_label = "Disable Editing Actor"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_actor(tool.Owner)


class EditActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_actor"
    bl_label = "Edit Actor"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_actor(tool.Ifc, tool.Owner)


class RemoveActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_actor"
    bl_label = "Remove Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_actor(tool.Ifc, actor=tool.Ifc.get().by_id(self.actor))


class AssignActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_actor"
    bl_label = "Assign Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_actor(
            tool.Ifc, actor=tool.Ifc.get().by_id(self.actor), element=tool.Ifc.get_entity(context.active_object)
        )


class UnassignActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_actor"
    bl_label = "Unassign Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_actor(
            tool.Ifc, actor=tool.Ifc.get().by_id(self.actor), element=tool.Ifc.get_entity(context.active_object)
        )
