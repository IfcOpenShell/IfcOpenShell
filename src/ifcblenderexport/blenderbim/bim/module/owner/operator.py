import bpy
import json
import ifcopenshell.api.owner.add_person as add_person
import ifcopenshell.api.owner.edit_person as edit_person
import ifcopenshell.api.owner.remove_person as remove_person
import ifcopenshell.api.owner.add_organisation as add_organisation
import ifcopenshell.api.owner.edit_organisation as edit_organisation
import ifcopenshell.api.owner.remove_organisation as remove_organisation
import ifcopenshell.api.owner.add_role as add_role
import ifcopenshell.api.owner.edit_role as edit_role
import ifcopenshell.api.owner.remove_role as remove_role
import ifcopenshell.api.owner.add_address as add_address
import ifcopenshell.api.owner.edit_address as edit_address
import ifcopenshell.api.owner.remove_address as remove_address
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.owner.data import Data


class EnableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_person_id = self.person_id
        data = Data.people[self.person_id]
        name = data["Id"] if self.file.schema == "IFC2X3" else data["Identification"]
        props.person.name = name or ""
        props.person.family_name = data["FamilyName"] or ""
        props.person.given_name = data["GivenName"] or ""
        props.person.middle_names = json.dumps(data["MiddleNames"]) if data["MiddleNames"] else ""
        props.person.prefix_titles = json.dumps(data["PrefixTitles"]) if data["PrefixTitles"] else ""
        props.person.suffix_titles = json.dumps(data["SuffixTitles"]) if data["SuffixTitles"] else ""
        return {"FINISHED"}


class DisableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_person_id = 0
        return {"FINISHED"}


class AddPerson(bpy.types.Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"

    def execute(self, context):
        add_person.Usecase(IfcStore.get_file()).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditPerson(bpy.types.Operator):
    bl_idname = "bim.edit_person"
    bl_label = "Edit Person"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        attributes = {
            "Identification": props.person.name or None,
            "FamilyName": props.person.family_name or None,
            "GivenName": props.person.given_name or None,
            "MiddleNames": json.loads(props.person.middle_names) if props.person.middle_names else None,
            "PrefixTitles": json.loads(props.person.prefix_titles) if props.person.prefix_titles else None,
            "SuffixTitles": json.loads(props.person.suffix_titles) if props.person.suffix_titles else None,
        }
        if self.file.schema == "IFC2X3":
            attributes["Id"] = attributes["Identification"]
            del attributes["Identification"]
        edit_person.Usecase(
            self.file, {"person": self.file.by_id(props.active_person_id), "attributes": attributes}
        ).execute()
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_person()
        return {"FINISHED"}


class RemovePerson(bpy.types.Operator):
    bl_idname = "bim.remove_person"
    bl_label = "Remove Person"
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_person.Usecase(self.file, {"person": self.file.by_id(self.person_id)}).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingRole(bpy.types.Operator):
    bl_idname = "bim.enable_editing_role"
    bl_label = "Enable Editing Role"
    role_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_role_id = self.role_id
        data = Data.roles[self.role_id]
        props.role.name = data["Role"]
        props.role.user_defined_role = data["UserDefinedRole"] or ""
        props.role.description = data["Description"] or ""
        return {"FINISHED"}


class DisableEditingRole(bpy.types.Operator):
    bl_idname = "bim.disable_editing_role"
    bl_label = "Disable Editing Role"

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_role_id = 0
        return {"FINISHED"}


class AddRole(bpy.types.Operator):
    bl_idname = "bim.add_role"
    bl_label = "Add Role"
    assigned_object_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        add_role.Usecase(self.file, {"assigned_object": self.file.by_id(self.assigned_object_id)}).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditRole(bpy.types.Operator):
    bl_idname = "bim.edit_role"
    bl_label = "Edit Role"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        attributes = {
            "Role": props.role.name,
            "UserDefinedRole": props.role.user_defined_role if props.role.name == "USERDEFINED" else None,
            "Description": props.role.description or None,
        }
        edit_role.Usecase(
            self.file, {"role": self.file.by_id(props.active_role_id), "attributes": attributes}
        ).execute()
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_role()
        return {"FINISHED"}


class RemoveRole(bpy.types.Operator):
    bl_idname = "bim.remove_role"
    bl_label = "Remove Role"
    role_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_role.Usecase(self.file, {"role": self.file.by_id(self.role_id)}).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddAddress(bpy.types.Operator):
    bl_idname = "bim.add_address"
    bl_label = "Add Address"
    assigned_object_id: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        add_address.Usecase(
            self.file, {"assigned_object": self.file.by_id(self.assigned_object_id), "ifc_class": self.ifc_class}
        ).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.enable_editing_address"
    bl_label = "Enable Editing Address"
    address_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_address_id = self.address_id
        data = Data.addresses[self.address_id]
        props.address.name = data["type"]
        props.address.purpose = data["Purpose"] or "None"
        props.address.description = data["Description"] or ""
        props.address.user_defined_purpose = data["UserDefinedPurpose"] or ""

        if data["type"] == "IfcTelecomAddress":
            props.address.telephone_numbers = json.dumps(data["TelephoneNumbers"]) if data["TelephoneNumbers"] else ""
            props.address.facsimile_numbers = json.dumps(data["FacsimileNumbers"]) if data["FacsimileNumbers"] else ""
            props.address.pager_number = data["PagerNumber"] or ""
            props.address.electronic_mail_addresses = (
                json.dumps(data["ElectronicMailAddresses"]) if data["ElectronicMailAddresses"] else ""
            )
            props.address.www_home_page_url = data["WWWHomePageURL"] or ""
            if self.file.schema != "IFC2X3":
                props.address.messaging_ids = json.dumps(data["MessagingIDs"]) if data["MessagingIDs"] else ""
        elif data["type"] == "IfcPostalAddress":
            props.address.internal_location = data["InternalLocation"] or ""
            props.address.address_lines = json.dumps(data["AddressLines"]) if data["AddressLines"] else ""
            props.address.postal_box = data["PostalBox"] or ""
            props.address.town = data["Town"] or ""
            props.address.region = data["Region"] or ""
            props.address.postal_code = data["PostalCode"] or ""
            props.address.country = data["Country"] or ""
        return {"FINISHED"}


class DisableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.disable_editing_address"
    bl_label = "Disable Editing Address"

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_address_id = 0
        return {"FINISHED"}


class EditAddress(bpy.types.Operator):
    bl_idname = "bim.edit_address"
    bl_label = "Edit Address"

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        attributes = {
            "Purpose": props.address.purpose,
            "UserDefinedPurpose": props.address.user_defined_purpose
            if props.address.purpose == "USERDEFINED"
            else None,
            "Description": props.address.description or None,
        }
        address = self.file.by_id(props.active_address_id)
        if address.is_a("IfcTelecomAddress"):
            attributes.update(
                {
                    "TelephoneNumbers": json.loads(props.address.telephone_numbers)
                    if props.address.telephone_numbers
                    else None,
                    "FacsimileNumbers": json.loads(props.address.facsimile_numbers)
                    if props.address.facsimile_numbers
                    else None,
                    "PagerNumber": props.address.pager_number or None,
                    "ElectronicMailAddresses": json.loads(props.address.electronic_mail_addresses)
                    if props.address.electronic_mail_addresses
                    else None,
                    "WWWHomePageURL": props.address.www_home_page_url or None,
                    "MessagingIDs": json.loads(props.address.messaging_ids) if props.address.messaging_ids else None,
                }
            )
            if self.file.schema == "IFC2X3":
                del attributes["MessagingIDs"]
        elif address.is_a("IfcPostalAddress"):
            attributes.update({
                "InternalLocation": props.address.internal_location or None,
                "AddressLines": json.loads(props.address.address_lines) if props.address.address_lines else None,
                "PostalBox": props.address.postal_box or None,
                "Town": props.address.town or None,
                "Region": props.address.region or None,
                "PostalCode": props.address.postal_code or None,
                "Country": props.address.country or None,
            })
        edit_address.Usecase(self.file, {"address": address, "attributes": attributes}).execute()
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_address()
        return {"FINISHED"}


class RemoveAddress(bpy.types.Operator):
    bl_idname = "bim.remove_address"
    bl_label = "Remove Address"
    address_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_address.Usecase(self.file, {"address": self.file.by_id(self.address_id)}).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingOrganisation(bpy.types.Operator):
    bl_idname = "bim.enable_editing_organisation"
    bl_label = "Enable Editing Organisation"
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

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_organisation_id = 0
        return {"FINISHED"}


class AddOrganisation(bpy.types.Operator):
    bl_idname = "bim.add_organisation"
    bl_label = "Add Organisation"

    def execute(self, context):
        add_organisation.Usecase(IfcStore.get_file()).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditOrganisation(bpy.types.Operator):
    bl_idname = "bim.edit_organisation"
    bl_label = "Edit Organisation"

    def execute(self, context):
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
        edit_organisation.Usecase(
            self.file, {"organisation": self.file.by_id(props.active_organisation_id), "attributes": attributes}
        ).execute()
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_organisation()
        return {"FINISHED"}


class RemoveOrganisation(bpy.types.Operator):
    bl_idname = "bim.remove_organisation"
    bl_label = "Remove Organisation"
    organisation_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        remove_organisation.Usecase(self.file, {"organisation": self.file.by_id(self.organisation_id)}).execute()
        Data.load(IfcStore.get_file())
        return {"FINISHED"}
