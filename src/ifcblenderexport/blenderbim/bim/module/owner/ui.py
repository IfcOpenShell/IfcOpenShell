import bpy
from bpy.types import Panel
from blenderbim.bim.module.owner.data import Data
from blenderbim.bim.ifc import IfcStore


def draw_roles_ui(box, assigned_object_id, roles):
    props = bpy.context.scene.BIMOwnerProperties
    row = box.row(align=True)
    row.label(text="Roles")
    row.operator("bim.add_role", icon="ADD", text="").assigned_object_id = assigned_object_id
    for role_id in roles:
        role = Data.roles[role_id]
        if props.active_role_id == role_id:
            blender_role = props.role
            box2 = box.box()
            row = box2.row(align=True)
            row.prop(blender_role, "name", icon="MOD_CLOTH", text="")
            row.operator("bim.edit_role", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_role", icon="X", text="")
            if blender_role.name == "USERDEFINED":
                row = box2.row()
                row.prop(blender_role, "user_defined_role")
            row = box2.row()
            row.prop(blender_role, "description")
        else:
            row = box.row(align=True)
            row.label(text=role["UserDefinedRole"] or role["Role"])
            row.operator("bim.enable_editing_role", icon="GREASEPENCIL", text="").role_id = role_id
            row.operator("bim.remove_role", icon="X", text="").role_id = role_id


def draw_addresses_ui(box, assigned_object_id, addresses, file):
    props = bpy.context.scene.BIMOwnerProperties
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
            row = box2.row(align=True)
            row.prop(blender_address, "purpose", icon="MOD_CLOTH", text="")
            row.operator("bim.edit_address", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_address", icon="X", text="")
            if blender_address.purpose == "USERDEFINED":
                row = box2.row()
                row.prop(blender_address, "user_defined_purpose")
            row = box2.row()
            row.prop(blender_address, "description")

            if address["type"] == "IfcTelecomAddress":
                row = box2.row()
                row.prop(blender_address, "telephone_numbers")
                row = box2.row()
                row.prop(blender_address, "facsimile_numbers")
                row = box2.row()
                row.prop(blender_address, "pager_number")
                row = box2.row()
                row.prop(blender_address, "electronic_mail_addresses")
                row = box2.row()
                row.prop(blender_address, "www_home_page_url")
                if file.schema != "IFC2X3":
                    row = box2.row()
                    row.prop(blender_address, "messaging_ids")
            elif address["type"] == "IfcPostalAddress":
                row = box2.row()
                row.prop(blender_address, "internal_location")
                row = box2.row()
                row.prop(blender_address, "address_lines")
                row = box2.row()
                row.prop(blender_address, "postal_box")
                row = box2.row()
                row.prop(blender_address, "town")
                row = box2.row()
                row.prop(blender_address, "region")
                row = box2.row()
                row.prop(blender_address, "postal_code")
                row = box2.row()
                row.prop(blender_address, "country")
        else:
            row = box.row(align=True)
            row.label(text=address["type"])
            row.operator("bim.enable_editing_address", icon="GREASEPENCIL", text="").address_id = address_id
            row.operator("bim.remove_address", icon="X", text="").address_id = address_id



class BIM_PT_people(Panel):
    bl_label = "IFC People"
    bl_idname = "BIM_PT_people"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load()

        self.file = IfcStore.get_file()
        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMOwnerProperties

        row = self.layout.row()
        row.operator("bim.add_person", icon="ADD")

        for person_id, person in Data.people.items():
            if props.active_person_id == person_id:
                blender_person = props.person
                box = self.layout.box()
                row = box.row(align=True)
                row.prop(blender_person, "name", icon="USER", text="")
                row.operator("bim.edit_person", icon="CHECKMARK", text="")
                row.operator("bim.disable_editing_person", icon="X", text="")
                row = box.row()
                row.prop(blender_person, "family_name")
                row = box.row()
                row.prop(blender_person, "given_name")
                row = box.row()
                row.prop(blender_person, "middle_names")
                row = box.row()
                row.prop(blender_person, "prefix_titles")
                row = box.row()
                row.prop(blender_person, "suffix_titles")

                draw_roles_ui(box, person_id, person["Roles"])
                draw_addresses_ui(box, person_id, person["Addresses"], self.file)
            else:
                row = self.layout.row(align=True)
                name = person["Id"] if self.file.schema == "IFC2X3" else person["Identification"]
                name = name or "*"
                if person["GivenName"] or person["FamilyName"]:
                    full_name = "{} {}".format(person["GivenName"] or "", person["FamilyName"] or "").strip()
                    name += f" ({full_name})"
                row.label(text=name)
                if person["Roles"]:
                    row.label(text=", ".join([Data.roles[r]["Role"] for r in person["Roles"]]))
                row.operator("bim.enable_editing_person", icon="GREASEPENCIL", text="").person_id = person_id
                if not person["is_engaged"]:
                    row.operator("bim.remove_person", icon="X", text="").person_id = person_id


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
            Data.load()

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
                row.operator("bim.disable_editing_organisation", icon="X", text="")
                row = box.row()
                row.prop(blender_organisation, "identification")
                row = box.row()
                row.prop(blender_organisation, "description")

                draw_roles_ui(box, organisation_id, organisation["Roles"])
                draw_addresses_ui(box, organisation_id, organisation["Addresses"], self.file)
            else:
                row = self.layout.row(align=True)
                row.label(text=organisation["Name"])
                if organisation["Roles"]:
                    row.label(text=", ".join([Data.roles[r]["Role"] for r in organisation["Roles"]]))
                row.operator("bim.enable_editing_organisation", icon="GREASEPENCIL", text="").organisation_id = organisation_id
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
            Data.load()

        self.layout.use_property_split = True
        self.layout.use_property_decorate = False
        props = context.scene.BIMOwnerProperties

        if not Data.people:
            self.layout.label(text="No people found.")
        else:
            row = self.layout.row()
            row.prop(props, "user_person")

        if not Data.organisations:
            self.layout.label(text="No organisations found.")
        else:
            row = self.layout.row()
            row.prop(props, "user_organisation")
