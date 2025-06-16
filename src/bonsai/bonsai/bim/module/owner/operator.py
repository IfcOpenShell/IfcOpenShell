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
import ifcopenshell.api.owner
from ifcopenshell.api.owner.add_address import ADDRESS_TYPE
from typing import TYPE_CHECKING, get_args

if TYPE_CHECKING:
    import bpy.stub_internal.rna_enums as rna_enums


class EnableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        person: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.enable_editing_person(tool.Owner, person=tool.Ifc.get().by_id(self.person))
        return {"FINISHED"}


class DisableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.disable_editing_person(tool.Owner)
        return {"FINISHED"}


class AddPerson(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context) -> None:
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
    person: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        person: int

    def _execute(self, context):
        core.remove_person(tool.Ifc, person=tool.Ifc.get().by_id(self.person))


class AddPersonAttribute(bpy.types.Operator):
    bl_idname = "bim.add_person_attribute"
    bl_label = "Add Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=tuple((i, i, "") for i in get_args(tool.Owner.PersonAttributeType)),
    )

    if TYPE_CHECKING:
        name: tool.Owner.PersonAttributeType  # pyright: ignore[reportIncompatibleVariableOverride]

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.add_person_attribute(tool.Owner, name=self.name)
        return {"FINISHED"}


class RemovePersonAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_person_attribute"
    bl_label = "Remove Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=tuple((i, i, "") for i in get_args(tool.Owner.PersonAttributeType)),
    )
    id: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        name: tool.Owner.PersonAttributeType  # pyright: ignore[reportIncompatibleVariableOverride]
        id: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.remove_person_attribute(tool.Owner, name=self.name, id=self.id)
        return {"FINISHED"}


class EnableEditingRole(bpy.types.Operator):
    bl_idname = "bim.enable_editing_role"
    bl_label = "Enable Editing Role"
    bl_options = {"REGISTER", "UNDO"}
    role: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        role: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.enable_editing_role(tool.Owner, role=tool.Ifc.get().by_id(self.role))
        return {"FINISHED"}


class DisableEditingRole(bpy.types.Operator):
    bl_idname = "bim.disable_editing_role"
    bl_label = "Disable Editing Role"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.disable_editing_role(tool.Owner)
        return {"FINISHED"}


class AddRole(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_role"
    bl_label = "Add Role"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        parent: int

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
    role: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        role: int

    def _execute(self, context):
        core.remove_role(tool.Ifc, role=tool.Ifc.get().by_id(self.role))


class AddAddress(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_address"
    bl_label = "Add Address"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]
    ifc_class: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=tuple((i, i, "") for i in get_args(ADDRESS_TYPE)),
    )

    if TYPE_CHECKING:
        parent: int
        ifc_class: ADDRESS_TYPE

    def _execute(self, context):
        core.add_address(tool.Ifc, parent=tool.Ifc.get().by_id(self.parent), ifc_class=self.ifc_class)


class AddAddressAttribute(bpy.types.Operator):
    bl_idname = "bim.add_address_attribute"
    bl_label = "Add Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=tuple((i, i, "") for i in get_args(tool.Owner.AddressAttributeType)),
    )

    if TYPE_CHECKING:
        name: tool.Owner.AddressAttributeType  # pyright: ignore[reportIncompatibleVariableOverride]

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.add_address_attribute(tool.Owner, name=self.name)
        return {"FINISHED"}


class RemoveAddressAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_address_attribute"
    bl_label = "Remove Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.EnumProperty(  # pyright: ignore[reportRedeclaration]
        items=tuple((i, i, "") for i in get_args(tool.Owner.AddressAttributeType)),
    )
    id: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        name: tool.Owner.AddressAttributeType  # pyright: ignore[reportIncompatibleVariableOverride]
        id: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.remove_address_attribute(tool.Owner, name=self.name, id=self.id)
        return {"FINISHED"}


class EnableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.enable_editing_address"
    bl_label = "Enable Editing Address"
    bl_options = {"REGISTER", "UNDO"}
    address: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        address: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.enable_editing_address(tool.Owner, address=tool.Ifc.get().by_id(self.address))
        return {"FINISHED"}


class DisableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.disable_editing_address"
    bl_label = "Disable Editing Address"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.disable_editing_address(tool.Owner)
        return {"FINISHED"}


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
    address: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        address: int

    def _execute(self, context):
        core.remove_address(tool.Ifc, address=tool.Ifc.get().by_id(self.address))


class EnableEditingOrganisation(bpy.types.Operator):
    bl_idname = "bim.enable_editing_organisation"
    bl_label = "Enable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}
    organisation: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        organisation: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.enable_editing_organisation(tool.Owner, organisation=tool.Ifc.get().by_id(self.organisation))
        return {"FINISHED"}


class DisableEditingOrganisation(bpy.types.Operator):
    bl_idname = "bim.disable_editing_organisation"
    bl_label = "Disable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.disable_editing_organisation(tool.Owner)
        return {"FINISHED"}


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
    organisation: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        organisation: int

    def _execute(self, context):
        core.remove_organisation(tool.Ifc, tool.Ifc.get().by_id(self.organisation))


class AddPersonAndOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_person_and_organisation"
    bl_label = "Add Person And Organisation"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]
    organisation: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        person: int
        organisation: int

    def _execute(self, context):
        core.add_person_and_organisation(
            tool.Ifc, person=tool.Ifc.get().by_id(self.person), organisation=tool.Ifc.get().by_id(self.organisation)
        )


class RemovePersonAndOrganisation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_person_and_organisation"
    bl_label = "Remove Person And Organisation"
    bl_options = {"REGISTER", "UNDO"}
    person_and_organisation: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        person_and_organisation: int

    def _execute(self, context):
        core.remove_person_and_organisation(
            tool.Ifc, tool.Owner, person_and_organisation=tool.Ifc.get().by_id(self.person_and_organisation)
        )


class SetUser(bpy.types.Operator):
    bl_idname = "bim.set_user"
    bl_label = "Set User"
    bl_options = {"REGISTER", "UNDO"}
    user: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        user: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.set_user(tool.Owner, user=tool.Ifc.get().by_id(self.user))
        return {"FINISHED"}


class ClearUser(bpy.types.Operator):
    bl_idname = "bim.clear_user"
    bl_label = "Clear User"
    bl_options = {"REGISTER", "UNDO"}
    user: bpy.props.IntProperty()

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.clear_user(tool.Owner)
        return {"FINISHED"}


class AddActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_actor"
    bl_label = "Add Actor"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = tool.Owner.get_owner_props()
        if props.the_actor:
            core.add_actor(tool.Ifc, ifc_class=props.actor_class, actor=tool.Ifc.get().by_id(int(props.the_actor)))


class EnableEditingActor(bpy.types.Operator):
    bl_idname = "bim.enable_editing_actor"
    bl_label = "Enable Editing Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        actor: int

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.enable_editing_actor(tool.Owner, actor=tool.Ifc.get().by_id(self.actor))
        return {"FINISHED"}


class DisableEditingActor(bpy.types.Operator):
    bl_idname = "bim.disable_editing_actor"
    bl_label = "Disable Editing Actor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context) -> "set[rna_enums.OperatorReturnItems]":
        core.disable_editing_actor(tool.Owner)
        return {"FINISHED"}


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
    actor: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        actor: int

    def _execute(self, context):
        core.remove_actor(tool.Ifc, actor=tool.Ifc.get().by_id(self.actor))


class AssignActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_actor"
    bl_label = "Assign Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        actor: int

    def _execute(self, context):
        assert (obj := context.active_object)
        assert (element := tool.Ifc.get_entity(obj))
        core.assign_actor(tool.Ifc, actor=tool.Ifc.get().by_id(self.actor), element=element)


class UnassignActor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_actor"
    bl_label = "Unassign Actor"
    bl_options = {"REGISTER", "UNDO"}
    actor: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        actor: int

    def _execute(self, context):
        assert (obj := context.active_object)
        assert (element := tool.Ifc.get_entity(obj))
        core.unassign_actor(tool.Ifc, actor=tool.Ifc.get().by_id(self.actor), element=element)


class RemoveApplication(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_application"
    bl_label = "Remove Application"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Remove provided IfcApplication."
        "\n\nFor safety will only work on applications without inverses (they are typically marked as '(unused)'."
    )
    application_id: bpy.props.IntProperty()  # pyright: ignore[reportRedeclaration]

    if TYPE_CHECKING:
        application_id: int

    @classmethod
    def description(cls, context, properties) -> str:
        description = cls.bl_description
        application_id: int
        if not (application_id := properties.application_id):
            return description
        ifc_file = tool.Ifc.get()
        application = ifc_file.by_id(application_id)

        application_info = "Additional application info:"
        application_info += f"\n- Developer: {application.ApplicationDeveloper.Name}"
        application_info += f"\n- Version: {application.Version}"
        application_info += f"\n- Identifier: {application.ApplicationIdentifier}"
        application_info += f"\n- Number of inverses: {ifc_file.get_total_inverses(application)}"
        application_info += f"\n(try to remove application to see the full list of inverses in system console)"

        description += f"\n\n{application_info}"
        return description

    def invoke(self, context, event):
        ifc_file = tool.Ifc.get()
        assert (application := ifc_file.by_id(self.application_id))
        if total_inverses := ifc_file.get_total_inverses(application):
            print(f"Present inverses for {application}:")
            for inverse in ifc_file.get_inverse(application):
                print(f"- {inverse}")
            self.report(
                {"ERROR"},
                f"This IfcApplication still has {total_inverses} inverses, deletion is unsafe. "
                "Check system console for the details.",
            )
            return {"CANCELLED"}
        return self.execute(context)

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        ifcopenshell.api.owner.remove_application(ifc_file, ifc_file.by_id(self.application_id))
