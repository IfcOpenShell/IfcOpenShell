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
from blenderbim.bim.module.owner.data import PeopleData, OrganisationsData, OwnerData


def draw_roles(box, parent):
    row = box.row(align=True)
    row.label(text="Roles")
    op = row.operator("bim.add_role", icon="ADD", text="")
    op.parent = parent["id"]

    for role in parent["roles"]:
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


def draw_addresses(box, parent):
    row = box.row(align=True)
    row.label(text="Addresses")
    op = row.operator("bim.add_address", icon="LINK_BLEND", text="")
    op.parent = parent["id"]
    op.ifc_class = "IfcTelecomAddress"
    op = row.operator("bim.add_address", icon="APPEND_BLEND", text="")
    op.parent = parent["id"]
    op.ifc_class = "IfcPostalAddress"

    for address in parent["addresses"]:
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


class BIM_PT_people(bpy.types.Panel):
    bl_label = "IFC People"
    bl_idname = "BIM_PT_people"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

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

            draw_roles(box, person)
            draw_addresses(box, person)
        else:
            row = self.layout.row(align=True)
            row.label(text=person["name"])
            row.operator("bim.enable_editing_person", icon="GREASEPENCIL", text="").person = person["id"]
            if not person["is_engaged"]:
                row.operator("bim.remove_person", icon="X", text="").person = person["id"]


class BIM_PT_organisations(bpy.types.Panel):
    bl_label = "IFC Organisations"
    bl_idname = "BIM_PT_organisations"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not OrganisationsData.is_loaded:
            OrganisationsData.load()

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False

        row = self.layout.row()
        row.operator("bim.add_organisation", icon="ADD")

        for organisation in OrganisationsData.data["organisations"]:
            self.draw_organisation(organisation)

    def draw_organisation(self, organisation):
        if organisation["is_editing"]:
            box = self.layout.box()
            row = box.row(align=True)
            row.operator("bim.edit_organisation", icon="CHECKMARK")
            row.operator("bim.disable_editing_organisation", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(organisation["props"], box)

            draw_roles(box, organisation)
            draw_addresses(box, organisation)
        else:
            row = self.layout.row(align=True)
            row.label(text=organisation["name"])
            op = row.operator("bim.enable_editing_organisation", icon="GREASEPENCIL", text="")
            op.organisation = organisation["id"]
            if not organisation["is_engaged"]:
                row.operator("bim.remove_organisation", icon="X", text="").organisation = organisation["id"]


class BIM_PT_owner(bpy.types.Panel):
    bl_label = "IFC Owner History"
    bl_idname = "BIM_PT_owner"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_project_setup"

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get()

    def draw(self, context):
        if not OwnerData.is_loaded:
            OwnerData.load()

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMOwnerProperties

        if not OwnerData.data["user_person"]:
            self.layout.label(text="No people found.")
        else:
            row = self.layout.row()
            row.prop(props, "user_person")

        if not OwnerData.data["user_organisation"]:
            self.layout.label(text="No organisations found.")
        else:
            row = self.layout.row()
            row.prop(props, "user_organisation")

        if OwnerData.data["can_add_user"]:
            row = self.layout.row()
            op = row.operator("bim.add_person_and_organisation", icon="ADD")
            op.person = int(props.user_person)
            op.organisation = int(props.user_organisation)

        for user in OwnerData.data["users"]:
            row = self.layout.row(align=True)
            if user["is_active"]:
                row.label(text=user["label"], icon="USER")
                row.operator("bim.clear_user", icon="KEYFRAME", text="").user = user["id"]
            else:
                row.label(text=user["label"])
                row.operator("bim.set_user", icon="KEYFRAME_HLT", text="").user = user["id"]
            op = row.operator("bim.remove_person_and_organisation", icon="X", text="")
            op.person_and_organisation = user["id"]
