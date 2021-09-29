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
import ifcopenshell.api
import blenderbim.tool as tool
import blenderbim.core.owner as core
import blenderbim.bim.module.owner.data
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.owner.data import Data


# TODO: Just testing
class Operator:
    def execute(self, context):
        IfcStore.execute_ifc_operator(self, context)
        blenderbim.bim.module.owner.data.PeopleData.is_loaded = False
        return {"FINISHED"}


def flatten_collection(collection):
    return [v.name for v in collection] if collection else None


def populate_collection(collection, collection_data):
    collection.clear()
    if collection_data:
        for value in collection_data:
            collection.add().name = value
    else:
        collection.add()


class AddOrRemoveElementFromCollection(bpy.types.Operator):
    bl_idname = "bim.add_or_remove_element_from_collection"
    bl_label = "Add or Remove Element From Collection"
    bl_options = {"REGISTER", "UNDO"}
    operation: bpy.props.EnumProperty(
        items=(("+", "Add", "Add item to collection"), ("-", "Remove", "Remove item from collection")),
        default="+",
    )
    collection_path: bpy.props.StringProperty()
    selected_item_idx: bpy.props.IntProperty(default=-1)

    def execute(self, context):
        # Ugly but I hate using eval()
        collection = context.scene
        for attr in self.collection_path.split("."):
            if hasattr(collection, attr):
                collection = getattr(collection, attr)
        if self.operation == "+" and hasattr(collection, "add"):
            collection.add()
        elif hasattr(collection, "remove") and 0 <= self.selected_item_idx < len(collection):
            collection.remove(self.selected_item_idx)
        return {"FINISHED"}


class EnableEditingPerson(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_person(tool.PersonEditor(), person=tool.Ifc().get().by_id(self.person))


class DisableEditingPerson(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_person(tool.PersonEditor())


class AddPerson(bpy.types.Operator, Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_person(tool.Ifc())


class EditPerson(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_person"
    bl_label = "Edit Person"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_person(tool.Ifc(), tool.PersonEditor())


class RemovePerson(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_person"
    bl_label = "Remove Person"
    bl_options = {"REGISTER", "UNDO"}
    person: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_person(tool.Ifc(), person=tool.Ifc().get().by_id(self.person))


class AddPersonAttribute(bpy.types.Operator, Operator):
    bl_idname = "bim.add_person_attribute"
    bl_label = "Add Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_person_attribute(tool.PersonEditor(), name=self.name)


class RemovePersonAttribute(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_person_attribute"
    bl_label = "Remove Person Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    id: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_person_attribute(tool.PersonEditor(), name=self.name, id=self.id)


class EnableEditingRole(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_role"
    bl_label = "Enable Editing Role"
    bl_options = {"REGISTER", "UNDO"}
    role: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_role(tool.RoleEditor(), role=tool.Ifc().get().by_id(self.role))


class DisableEditingRole(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_role"
    bl_label = "Disable Editing Role"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_role(tool.RoleEditor())


class AddRole(bpy.types.Operator, Operator):
    bl_idname = "bim.add_role"
    bl_label = "Add Role"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_role(tool.Ifc(), parent=tool.Ifc().get().by_id(self.parent))


class EditRole(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_role"
    bl_label = "Edit Role"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_role(tool.Ifc(), tool.RoleEditor())


class RemoveRole(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_role"
    bl_label = "Remove Role"
    bl_options = {"REGISTER", "UNDO"}
    role: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_role(tool.Ifc(), role=tool.Ifc().get().by_id(self.role))


class AddAddress(bpy.types.Operator, Operator):
    bl_idname = "bim.add_address"
    bl_label = "Add Address"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_address(tool.Ifc(), parent=tool.Ifc().get().by_id(self.parent), ifc_class=self.ifc_class)


class AddAddressAttribute(bpy.types.Operator, Operator):
    bl_idname = "bim.add_address_attribute"
    bl_label = "Add Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_address_attribute(tool.AddressEditor, name=self.name)


class RemoveAddressAttribute(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_address_attribute"
    bl_label = "Remove Address Attribute"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()
    id: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_address_attribute(tool.AddressEditor, name=self.name, id=self.id)


class EnableEditingAddress(bpy.types.Operator, Operator):
    bl_idname = "bim.enable_editing_address"
    bl_label = "Enable Editing Address"
    bl_options = {"REGISTER", "UNDO"}
    address: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_address(tool.AddressEditor(), address=tool.Ifc().get().by_id(self.address))


class DisableEditingAddress(bpy.types.Operator, Operator):
    bl_idname = "bim.disable_editing_address"
    bl_label = "Disable Editing Address"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_address(tool.AddressEditor())


class EditAddress(bpy.types.Operator, Operator):
    bl_idname = "bim.edit_address"
    bl_label = "Edit Address"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_address(tool.Ifc, tool.AddressEditor)


class RemoveAddress(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_address"
    bl_label = "Remove Address"
    bl_options = {"REGISTER", "UNDO"}
    address: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_address(tool.Ifc(), address=tool.Ifc().get().by_id(self.address))


class EnableEditingOrganisation(bpy.types.Operator):
    bl_idname = "bim.enable_editing_organisation"
    bl_label = "Enable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}
    organisation_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_organisation_id = self.organisation_id
        data = Data.organisations[self.organisation_id]
        identification = data["Id"] if self.file.schema == "IFC2X3" else data["Identification"]
        props.organisation.identification = identification or ""
        props.organisation.name = data["Name"]
        props.organisation.description = data["Description"] or ""
        return {"FINISHED"}


class DisableEditingOrganisation(bpy.types.Operator):
    bl_idname = "bim.disable_editing_organisation"
    bl_label = "Disable Editing Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_organisation_id = 0
        return {"FINISHED"}


class AddOrganisation(bpy.types.Operator):
    bl_idname = "bim.add_organisation"
    bl_label = "Add Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("owner.add_organisation", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditOrganisation(bpy.types.Operator):
    bl_idname = "bim.edit_organisation"
    bl_label = "Edit Organisation"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        attributes = {
            "Identification": props.organisation.identification or None,
            "Name": props.organisation.name,
            "Description": props.organisation.description or None,
        }
        if self.file.schema == "IFC2X3":
            attributes["Id"] = attributes["Identification"]
            del attributes["Identification"]
        ifcopenshell.api.run(
            "owner.edit_organisation",
            self.file,
            **{"organisation": self.file.by_id(props.active_organisation_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_organisation()
        return {"FINISHED"}


class RemoveOrganisation(bpy.types.Operator):
    bl_idname = "bim.remove_organisation"
    bl_label = "Remove Organisation"
    bl_options = {"REGISTER", "UNDO"}
    organisation_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "owner.remove_organisation", self.file, **{"organisation": self.file.by_id(self.organisation_id)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
