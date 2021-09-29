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
import blenderbim.bim.helper
import blenderbim.tool as tool
from blenderbim.bim.module.owner.data import PeopleData
from bpy.types import Panel
from ifcopenshell.api.owner.data import Data
from blenderbim.bim.ifc import IfcStore


def draw_string_collection(layout, owner, collection_name):
    column = layout.column(align=True)
    collection = getattr(owner, collection_name)
    for i in range(len(collection)):
        if i == 0:
            row = draw_prop_on_new_row(
                column, collection[i], "name", align=True, text=f"{owner.bl_rna.properties[collection_name].name}"
            )
            add_op = row.operator("bim.add_or_remove_element_from_collection", icon="ADD", text="")
            add_op.operation = "+"
            add_op.collection_path = collection.path_from_id()
        else:
            row = draw_prop_on_new_row(column, collection[i], "name", align=True, text=f"#{i + 1}")
            rem_op = row.operator("bim.add_or_remove_element_from_collection", icon="REMOVE", text="")
            rem_op.operation = "-"
            rem_op.collection_path = collection.path_from_id()
            rem_op.selected_item_idx = i


def draw_prop_on_new_row(layout, owner, attribute, align=False, **kwargs):
    row = layout.row(align=align)
    row.prop(owner, attribute, **kwargs)
    return row


def draw_roles_ui(box, assigned_object_id, roles, context):
    props = context.scene.BIMOwnerProperties
    row = box.row(align=True)
    row.label(text="Roles")
    row.operator("bim.add_role", icon="ADD", text="").assigned_object_id = assigned_object_id
    for role_id in roles:
        role = Data.roles[role_id]
        if props.active_role_id == role_id:
            blender_role = props.role
            box2 = box.box()
            row = draw_prop_on_new_row(box2, blender_role, "name", align=True, icon="MOD_CLOTH", text="")
            row.operator("bim.edit_role", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_role", icon="CANCEL", text="")
            if blender_role.name == "USERDEFINED":
                draw_prop_on_new_row(box2, blender_role, "user_defined_role")
            draw_prop_on_new_row(box2, blender_role, "description")
        else:
            row = box.row(align=True)
            row.label(text=role["UserDefinedRole"] or role["Role"])
            row.operator("bim.enable_editing_role", icon="GREASEPENCIL", text="").role_id = role_id
            row.operator("bim.remove_role", icon="X", text="").role_id = role_id


def draw_addresses_ui(box, assigned_object_id, addresses, file, context):
    props = context.scene.BIMOwnerProperties
    row = box.row(align=True)
    row.label(text="Addresses")
    op = row.operator("bim.add_address", icon="LINK_BLEND", text="")
    op.assigned_object_id = assigned_object_id
    op.ifc_class = "IfcTelecomAddress"
    op = row.operator("bim.add_address", icon="APPEND_BLEND", text="")
    op.assigned_object_id = assigned_object_id
    op.ifc_class = "IfcPostalAddress"
    for address_id in addresses:
        address = Data.addresses[address_id]
        if props.active_address_id == address_id:
            blender_address = props.address
            box2 = box.box()
            row = draw_prop_on_new_row(box2, blender_address, "purpose", align=True, icon="MOD_CLOTH", text="")
            row.operator("bim.edit_address", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_address", icon="CANCEL", text="")
            if blender_address.purpose == "USERDEFINED":
                draw_prop_on_new_row(box2, blender_address, "user_defined_purpose")
            draw_prop_on_new_row(box2, blender_address, "description")

            if address["type"] == "IfcTelecomAddress":
                draw_string_collection(box2, blender_address, "telephone_numbers")
                draw_string_collection(box2, blender_address, "facsimile_numbers")
                draw_prop_on_new_row(box2, blender_address, "pager_number")
                draw_string_collection(box2, blender_address, "electronic_mail_addresses")
                draw_prop_on_new_row(box2, blender_address, "www_home_page_url")
                if file.schema != "IFC2X3":
                    draw_string_collection(box2, blender_address, "messaging_ids")
            elif address["type"] == "IfcPostalAddress":
                draw_prop_on_new_row(box2, blender_address, "internal_location")
                draw_string_collection(box2, blender_address, "address_lines")
                draw_prop_on_new_row(box2, blender_address, "postal_box")
                draw_prop_on_new_row(box2, blender_address, "town")
                draw_prop_on_new_row(box2, blender_address, "region")
                draw_prop_on_new_row(box2, blender_address, "postal_code")
                draw_prop_on_new_row(box2, blender_address, "country")
        else:
            row = box.row(align=True)
            row.label(text=address["type"])
            row.operator("bim.enable_editing_address", icon="GREASEPENCIL", text="").address_id = address_id
            row.operator("bim.remove_address", icon="X", text="").address_id = address_id


class BIM_PT_people(bpy.types.Panel):
    bl_label = "IFC People"
    bl_idname = "BIM_PT_people"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return tool.Ifc().get()

    def draw(self, context):
        if not PeopleData.is_loaded:
            PeopleData.load()

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        row = self.layout.row()
        row.operator("bim.add_person", icon="ADD")

        for person in PeopleData.data["people"]:
            self.draw_person(person)

    def draw_person(self, person):
        if person["is_editing"]:
            box = self.layout.box()
            row = box.row(align=True)
            row.operator("bim.edit_person", icon="CHECKMARK")
            row.operator("bim.disable_editing_person", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(person["props"], box)

            for attribute in person["list_attributes"]:
                row = box.row(align=True)
                row.label(text=attribute["name"])
                op = row.operator("bim.add_person_attribute", icon="ADD", text="")
                op.name = attribute["name"]

                for item in attribute["items"]:
                    row = box.row(align=True)
                    row.prop(item["prop"], "name", text="")
                    op = row.operator("bim.remove_person_attribute", icon="REMOVE", text="")
                    op.name = attribute["name"]
                    op.id = item["id"]

            self.draw_roles(box, person)
            self.draw_addresses(box, person)
        else:
            row = self.layout.row(align=True)
            row.label(text=person["name"])
            row.operator("bim.enable_editing_person", icon="GREASEPENCIL", text="").person = person["id"]
            if not person["is_engaged"]:
                row.operator("bim.remove_person", icon="X", text="").person = person["id"]

    def draw_roles(self, box, person):
        row = box.row(align=True)
        row.label(text="Roles")
        op = row.operator("bim.add_role", icon="ADD", text="")
        op.parent = person["id"]

        for role in person["roles"]:
            if role["is_editing"]:
                row = box.row(align=True)
                row.operator("bim.edit_role", icon="CHECKMARK")
                row.operator("bim.disable_editing_role", icon="CANCEL", text="")
                blenderbim.bim.helper.draw_attributes(role["props"], box)
            else:
                row = box.row(align=True)
                row.label(text=role["label"])
                row.operator("bim.enable_editing_role", icon="GREASEPENCIL", text="").role = role["id"]
                row.operator("bim.remove_role", icon="X", text="").role = role["id"]

    def draw_addresses(self, box, person):
        row = box.row(align=True)
        row.label(text="Addresses")
        op = row.operator("bim.add_address", icon="LINK_BLEND", text="")
        op.parent = person["id"]
        op.ifc_class = "IfcTelecomAddress"
        op = row.operator("bim.add_address", icon="APPEND_BLEND", text="")
        op.parent = person["id"]
        op.ifc_class = "IfcPostalAddress"

        for address in person["addresses"]:
            if address["is_editing"]:
                row = box.row(align=True)
                row.operator("bim.edit_address", icon="CHECKMARK")
                row.operator("bim.disable_editing_address", icon="CANCEL", text="")
                blenderbim.bim.helper.draw_attributes(address["props"], box)
                for attribute in address["list_attributes"]:
                    row = box.row(align=True)
                    row.label(text=attribute["name"])
                    op = row.operator("bim.add_address_attribute", icon="ADD", text="")
                    op.name = attribute["name"]

                    for item in attribute["items"]:
                        row = box.row(align=True)
                        row.prop(item["prop"], "name", text="")
                        op = row.operator("bim.remove_address_attribute", icon="REMOVE", text="")
                        op.name = attribute["name"]
                        op.id = item["id"]
            else:
                row = box.row(align=True)
                row.label(text=address["label"])
                row.operator("bim.enable_editing_address", icon="GREASEPENCIL", text="").address = address["id"]
                row.operator("bim.remove_address", icon="X", text="").address = address["id"]


class BIM_PT_organisations(Panel):
    bl_label = "IFC Organisations"
    bl_idname = "BIM_PT_organisations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        self.file = IfcStore.get_file()
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMOwnerProperties

        row = self.layout.row()
        row.operator("bim.add_organisation", icon="ADD")

        for organisation_id, organisation in Data.organisations.items():
            if props.active_organisation_id == organisation_id:
                blender_organisation = props.organisation
                box = self.layout.box()
                row = box.row(align=True)
                row.prop(blender_organisation, "name", icon="USER", text="")
                row.operator("bim.edit_organisation", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_organisation", icon="CANCEL", text="")
                draw_prop_on_new_row(box, blender_organisation, "identification")
                draw_prop_on_new_row(box, blender_organisation, "description")

                draw_roles_ui(box, organisation_id, organisation["Roles"], context)
                draw_addresses_ui(box, organisation_id, organisation["Addresses"], self.file, context)
            else:
                row = self.layout.row(align=True)
                row.label(text=organisation["Name"])
                if organisation["Roles"]:
                    row.label(text=", ".join([Data.roles[r]["Role"] for r in organisation["Roles"]]))
                row.operator(
                    "bim.enable_editing_organisation", icon="GREASEPENCIL", text=""
                ).organisation_id = organisation_id
                if not organisation["is_engaged"]:
                    row.operator("bim.remove_organisation", icon="X", text="").organisation_id = organisation_id


class BIM_PT_owner(Panel):
    bl_label = "IFC Owner History"
    bl_idname = "BIM_PT_owner"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMOwnerProperties

        if not Data.people:
            self.layout.label(text="No people found.")
        else:
            draw_prop_on_new_row(self.layout, props, "user_person")

        if not Data.organisations:
            self.layout.label(text="No organisations found.")
        else:
            draw_prop_on_new_row(self.layout, props, "user_organisation")
