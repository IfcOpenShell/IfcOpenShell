import bpy
import ifcopenshell.api
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.owner.data import Data


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
    operation : bpy.props.EnumProperty(
        items=(
            ("+", 'Add', "Add item to collection"),
            ("-", 'Remove', "Remove item from collection")
        ),
        default="+",
    )
    collection_path : bpy.props.StringProperty()
    selected_item_idx : bpy.props.IntProperty(default=-1)

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


class EnableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.enable_editing_person"
    bl_label = "Enable Editing Person"
    bl_options = {"REGISTER", "UNDO"}
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_person_id = self.person_id
        data = Data.people[self.person_id]
        name = data["Id"] if self.file.schema == "IFC2X3" else data["Identification"]
        person = props.person
        person.name = name or ""
        person.family_name = data["FamilyName"] or ""
        person.given_name = data["GivenName"] or ""
        populate_collection(person.middle_names, data.get("MiddleNames", None))
        populate_collection(person.prefix_titles, data.get("PrefixTitles", None))
        populate_collection(person.suffix_titles, data.get("SuffixTitles", None))
        return {"FINISHED"}


class DisableEditingPerson(bpy.types.Operator):
    bl_idname = "bim.disable_editing_person"
    bl_label = "Disable Editing Person"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_person_id = 0
        return {"FINISHED"}


class AddPerson(bpy.types.Operator):
    bl_idname = "bim.add_person"
    bl_label = "Add Person"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        ifcopenshell.api.run("owner.add_person", IfcStore.get_file())
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditPerson(bpy.types.Operator):
    bl_idname = "bim.edit_person"
    bl_label = "Edit Person"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        person = props.person
        attributes = {
            "Identification": person.name or None,
            "FamilyName": person.family_name or None,
            "GivenName": person.given_name or None,
            "MiddleNames": flatten_collection(person.middle_names),
            "PrefixTitles": flatten_collection(person.prefix_titles),
            "SuffixTitles": flatten_collection(person.suffix_titles),
        }
        if self.file.schema == "IFC2X3":
            attributes["Id"] = attributes["Identification"]
            del attributes["Identification"]
        ifcopenshell.api.run(
            "owner.edit_person",
            self.file,
            **{"person": self.file.by_id(props.active_person_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_person()
        return {"FINISHED"}


class RemovePerson(bpy.types.Operator):
    bl_idname = "bim.remove_person"
    bl_label = "Remove Person"
    bl_options = {"REGISTER", "UNDO"}
    person_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("owner.remove_person", self.file, **{"person": self.file.by_id(self.person_id)})
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingRole(bpy.types.Operator):
    bl_idname = "bim.enable_editing_role"
    bl_label = "Enable Editing Role"
    bl_options = {"REGISTER", "UNDO"}
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
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_role_id = 0
        return {"FINISHED"}


class AddRole(bpy.types.Operator):
    bl_idname = "bim.add_role"
    bl_label = "Add Role"
    bl_options = {"REGISTER", "UNDO"}
    assigned_object_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "owner.add_role", self.file, **{"assigned_object": self.file.by_id(self.assigned_object_id)}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EditRole(bpy.types.Operator):
    bl_idname = "bim.edit_role"
    bl_label = "Edit Role"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        attributes = {
            "Role": props.role.name,
            "UserDefinedRole": props.role.user_defined_role if props.role.name == "USERDEFINED" else None,
            "Description": props.role.description or None,
        }
        ifcopenshell.api.run(
            "owner.edit_role", self.file, **{"role": self.file.by_id(props.active_role_id), "attributes": attributes}
        )
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_role()
        return {"FINISHED"}


class RemoveRole(bpy.types.Operator):
    bl_idname = "bim.remove_role"
    bl_label = "Remove Role"
    bl_options = {"REGISTER", "UNDO"}
    role_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("owner.remove_role", self.file, **{"role": self.file.by_id(self.role_id)})
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class AddAddress(bpy.types.Operator):
    bl_idname = "bim.add_address"
    bl_label = "Add Address"
    bl_options = {"REGISTER", "UNDO"}
    assigned_object_id: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run(
            "owner.add_address",
            self.file,
            **{"assigned_object": self.file.by_id(self.assigned_object_id), "ifc_class": self.ifc_class}
        )
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


class EnableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.enable_editing_address"
    bl_label = "Enable Editing Address"
    bl_options = {"REGISTER", "UNDO"}
    address_id: bpy.props.IntProperty()

    def execute(self, context):
        self.file = IfcStore.get_file()
        props = context.scene.BIMOwnerProperties
        props.active_address_id = self.address_id
        data = Data.addresses[self.address_id]
        address = props.address
        address.name = data["type"]
        address.purpose = data["Purpose"] or "None"
        address.description = data["Description"] or ""
        address.user_defined_purpose = data["UserDefinedPurpose"] or ""

        if data["type"] == "IfcTelecomAddress":            
            populate_collection(address.telephone_numbers, data.get("TelephoneNumbers", None))
            populate_collection(address.facsimile_numbers, data.get("FacsimileNumbers", None))
            address.pager_number = data["PagerNumber"] or ""
            populate_collection(address.electronic_mail_addresses, data.get("ElectronicMailAddresses", None))
            address.www_home_page_url = data["WWWHomePageURL"] or ""
            if self.file.schema != "IFC2X3":
                populate_collection(address.messaging_ids, data.get("MessagingIDs", None))
        elif data["type"] == "IfcPostalAddress":
            address.internal_location = data["InternalLocation"] or ""
            populate_collection(address.address_lines, data.get("AddressLines", None))
            address.postal_box = data["PostalBox"] or ""
            address.town = data["Town"] or ""
            address.region = data["Region"] or ""
            address.postal_code = data["PostalCode"] or ""
            address.country = data["Country"] or ""
        return {"FINISHED"}


class DisableEditingAddress(bpy.types.Operator):
    bl_idname = "bim.disable_editing_address"
    bl_label = "Disable Editing Address"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.BIMOwnerProperties.active_address_id = 0
        return {"FINISHED"}


class EditAddress(bpy.types.Operator):
    bl_idname = "bim.edit_address"
    bl_label = "Edit Address"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
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
                    "TelephoneNumbers": flatten_collection(props.address.telephone_numbers),
                    "FacsimileNumbers": flatten_collection(props.address.facsimile_numbers),
                    "PagerNumber": props.address.pager_number or None,
                    "ElectronicMailAddresses": flatten_collection(props.address.electronic_mail_addresses),
                    "WWWHomePageURL": props.address.www_home_page_url or None,
                    "MessagingIDs": flatten_collection(props.address.messaging_ids),
                }
            )
            if self.file.schema == "IFC2X3":
                del attributes["MessagingIDs"]
        elif address.is_a("IfcPostalAddress"):
            attributes.update(
                {
                    "InternalLocation": props.address.internal_location or None,
                    "AddressLines": flatten_collection(props.address.address_lines),
                    "PostalBox": props.address.postal_box or None,
                    "Town": props.address.town or None,
                    "Region": props.address.region or None,
                    "PostalCode": props.address.postal_code or None,
                    "Country": props.address.country or None,
                }
            )
        ifcopenshell.api.run("owner.edit_address", self.file, **{"address": address, "attributes": attributes})
        Data.load(IfcStore.get_file())
        bpy.ops.bim.disable_editing_address()
        return {"FINISHED"}


class RemoveAddress(bpy.types.Operator):
    bl_idname = "bim.remove_address"
    bl_label = "Remove Address"
    bl_options = {"REGISTER", "UNDO"}
    address_id: bpy.props.IntProperty()

    def execute(self, context):
        return IfcStore.execute_ifc_operator(self, context)

    def _execute(self, context):
        self.file = IfcStore.get_file()
        ifcopenshell.api.run("owner.remove_address", self.file, **{"address": self.file.by_id(self.address_id)})
        Data.load(IfcStore.get_file())
        return {"FINISHED"}


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
