# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import bonsai.core.tool
import bonsai.tool as tool
from test.bim.bootstrap import NewFile
from bonsai.tool.owner import Owner as subject


class TestImplementsTool(NewFile):
    def test_run(self):
        assert isinstance(subject(), bonsai.core.tool.Owner)


class TestAddAddressAttribute(NewFile):
    def test_run(self):
        subject().add_address_attribute("AddressLines")
        subject().add_address_attribute("TelephoneNumbers")
        subject().add_address_attribute("FacsimileNumbers")
        subject().add_address_attribute("ElectronicMailAddresses")
        subject().add_address_attribute("MessagingIDs")
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.address_lines) == 1
        assert len(props.telephone_numbers) == 1
        assert len(props.facsimile_numbers) == 1
        assert len(props.electronic_mail_addresses) == 1
        assert len(props.messaging_ids) == 1


class TestAddPersonAttribute(NewFile):
    def test_run(self):
        subject().add_person_attribute("MiddleNames")
        subject().add_person_attribute("PrefixTitles")
        subject().add_person_attribute("SuffixTitles")
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.middle_names) == 1
        assert len(props.prefix_titles) == 1
        assert len(props.suffix_titles) == 1


class TestClearActor(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        actor = ifc.createIfcActor()
        subject().set_actor(actor)
        subject().clear_actor()
        assert bpy.context.scene.BIMOwnerProperties.active_actor_id == 0


class TestClearAddress(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        subject().clear_address()
        assert bpy.context.scene.BIMOwnerProperties.active_address_id == 0


class TestClearOrganisation(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMOwnerProperties
        props.active_organisation_id = 1
        subject().clear_organisation()
        assert props.active_organisation_id == 0


class TestClearPerson(NewFile):
    def test_run(self):
        props = bpy.context.scene.BIMOwnerProperties
        props.active_person_id = 1
        subject().clear_person()
        assert props.active_person_id == 0


class TestClearRole(NewFile):
    def test_run(self):
        role = ifcopenshell.file().createIfcActorRole()
        subject().set_role(role)
        subject().clear_role()
        assert bpy.context.scene.BIMOwnerProperties.active_role_id == 0


class TestClearUser(NewFile):
    def test_run(self):
        TestSetUser().test_run()
        subject.clear_user()
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == 0


class TestExportActorAttributes(NewFile):
    def test_exporting_an_actor(self):
        TestImportActorAttributes().test_importing_an_actor()
        assert subject().export_actor_attributes() == {
            "GlobalId": "GlobalId",
            "Name": "Name",
            "Description": "Description",
            "ObjectType": "ObjectType",
        }

    def test_exporting_an_occupant(self):
        TestImportActorAttributes().test_importing_an_occupant()
        assert subject().export_actor_attributes() == {
            "GlobalId": "GlobalId",
            "Name": "Name",
            "Description": "Description",
            "ObjectType": "ObjectType",
            "PredefinedType": "TENANT",
        }


class TestExportAddressAttributes(NewFile):
    def test_exporting_a_postal_address(self):
        TestImportAddressAttributes().test_importing_a_postal_address()
        assert subject().export_address_attributes() == {
            "Purpose": "USERDEFINED",
            "Description": "Description",
            "UserDefinedPurpose": "UserDefinedPurpose",
            "InternalLocation": "InternalLocation",
            "AddressLines": ["Address", "Lines"],
            "PostalBox": "PostalBox",
            "Town": "Town",
            "Region": "Region",
            "PostalCode": "PostalCode",
            "Country": "Country",
        }

    def test_exporting_a_telecom_address(self):
        TestImportAddressAttributes().test_importing_a_telecom_address()
        assert subject().export_address_attributes() == {
            "Purpose": "USERDEFINED",
            "Description": "Description",
            "UserDefinedPurpose": "UserDefinedPurpose",
            "TelephoneNumbers": ["Telephone", "Numbers"],
            "FacsimileNumbers": ["Facsimile", "Numbers"],
            "PagerNumber": "PagerNumber",
            "ElectronicMailAddresses": ["Electronic", "Mail", "Addresses"],
            "WWWHomePageURL": "WWWHomePageURL",
            "MessagingIDs": ["Messaging", "IDs"],
        }


class TestExportOrganisationAttributes(NewFile):
    def test_run(self):
        TestImportOrganisationAttributes().test_run()
        assert subject().export_organisation_attributes() == {
            "Identification": "Identification",
            "Name": "Name",
            "Description": "Description",
        }


class TestExportPersonAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        person.FamilyName = "family_name"
        person.MiddleNames = ("middle", "names")
        person.PrefixTitles = ("prefix", "titles")
        person.SuffixTitles = ("suffix", "titles")
        subject().set_person(person)
        subject().import_person_attributes()
        assert subject().export_person_attributes() == {
            "Identification": "identification",
            "GivenName": "given_name",
            "FamilyName": "family_name",
            "MiddleNames": ["middle", "names"],
            "PrefixTitles": ["prefix", "titles"],
            "SuffixTitles": ["suffix", "titles"],
        }

    def test_getting_empty_list_attributes_as_none(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        result = subject().export_person_attributes()
        assert result["MiddleNames"] is None
        assert result["PrefixTitles"] is None
        assert result["SuffixTitles"] is None


class TestExportRoleAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        role.UserDefinedRole = "UserDefinedRole"
        role.Description = "Description"
        subject().set_role(role)
        subject().import_role_attributes()
        assert subject().export_role_attributes() == {
            "Role": "USERDEFINED",
            "UserDefinedRole": "UserDefinedRole",
            "Description": "Description",
        }


class TestGetActor(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        actor = ifc.createIfcActor()
        subject().set_actor(actor)
        assert subject().get_actor() == actor


class TestGetAddress(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        assert subject().get_address() == address


class TestGetOrganisation(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        subject().set_organisation(organisation)
        assert subject().get_organisation() == organisation


class TestGetPerson(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        subject().set_person(person)
        assert subject().get_person() == person


class TestGetRole(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        subject().set_role(role)
        assert subject().get_role() == role


class TestGetUser(NewFile):
    def test_run(self):
        assert subject.get_user() is None
        TestSetUser().test_run()
        user = tool.Ifc.get().by_type("IfcPersonAndOrganization")[0]
        assert subject.get_user() == user

    def test_falling_back_to_any_available_user_ifc2x3(self):
        assert subject.get_user() is None
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        user = ifc.createIfcPersonAndOrganization()
        assert subject.get_user() == user
        user2 = ifc.createIfcPersonAndOrganization()
        subject.set_user(user2)
        assert subject.get_user() == user2


class TestImportActorAttributes(NewFile):
    def test_importing_an_actor(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        actor = ifc.createIfcActor()
        actor.GlobalId = "GlobalId"
        actor.Name = "Name"
        actor.Description = "Description"
        actor.ObjectType = "ObjectType"
        subject.set_actor(actor)
        subject.import_actor_attributes(actor)
        props = bpy.context.scene.BIMOwnerProperties
        assert props.actor_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.actor_attributes.get("Name").string_value == "Name"
        assert props.actor_attributes.get("Description").string_value == "Description"
        assert props.actor_attributes.get("ObjectType").string_value == "ObjectType"

    def test_importing_an_occupant(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        actor = ifc.createIfcOccupant()
        actor.GlobalId = "GlobalId"
        actor.Name = "Name"
        actor.Description = "Description"
        actor.ObjectType = "ObjectType"
        actor.PredefinedType = "TENANT"
        subject.set_actor(actor)
        subject.import_actor_attributes(actor)
        props = bpy.context.scene.BIMOwnerProperties
        assert props.actor_attributes.get("GlobalId").string_value == "GlobalId"
        assert props.actor_attributes.get("Name").string_value == "Name"
        assert props.actor_attributes.get("Description").string_value == "Description"
        assert props.actor_attributes.get("ObjectType").string_value == "ObjectType"
        assert props.actor_attributes.get("PredefinedType").enum_value == "TENANT"


class TestImportAddressAttributes(NewFile):
    def test_importing_a_postal_address(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        address = ifc.createIfcPostalAddress()
        address.Purpose = "USERDEFINED"
        address.Description = "Description"
        address.UserDefinedPurpose = "UserDefinedPurpose"
        address.InternalLocation = "InternalLocation"
        address.AddressLines = ["Address", "Lines"]
        address.PostalBox = "PostalBox"
        address.Town = "Town"
        address.Region = "Region"
        address.PostalCode = "PostalCode"
        address.Country = "Country"
        subject().set_address(address)
        subject().import_address_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.address_attributes.get("Purpose").enum_value == "USERDEFINED"
        assert props.address_attributes.get("Description").string_value == "Description"
        assert props.address_attributes.get("UserDefinedPurpose").string_value == "UserDefinedPurpose"
        assert props.address_attributes.get("InternalLocation").string_value == "InternalLocation"
        assert props.address_attributes.get("PostalBox").string_value == "PostalBox"
        assert props.address_attributes.get("Town").string_value == "Town"
        assert props.address_attributes.get("Region").string_value == "Region"
        assert props.address_attributes.get("PostalCode").string_value == "PostalCode"
        assert props.address_attributes.get("Country").string_value == "Country"
        assert len(props.address_lines) == 2
        assert props.address_lines[0].name == "Address"
        assert props.address_lines[1].name == "Lines"

    def test_importing_a_postal_address_twice(self):
        self.test_importing_a_postal_address()
        ifc = tool.Ifc().get()
        address = ifc.createIfcPostalAddress()
        address.Purpose = "OFFICE"
        subject().set_address(address)
        subject().import_address_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.address_attributes.get("Purpose").enum_value == "OFFICE"
        assert len(props.address_lines) == 0

    def test_importing_a_telecom_address(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        address = ifc.createIfcTelecomAddress()
        address.Purpose = "USERDEFINED"
        address.Description = "Description"
        address.UserDefinedPurpose = "UserDefinedPurpose"
        address.TelephoneNumbers = ["Telephone", "Numbers"]
        address.FacsimileNumbers = ["Facsimile", "Numbers"]
        address.PagerNumber = "PagerNumber"
        address.ElectronicMailAddresses = ["Electronic", "Mail", "Addresses"]
        address.WWWHomePageURL = "WWWHomePageURL"
        address.MessagingIDs = ["Messaging", "IDs"]
        subject().set_address(address)
        subject().import_address_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.address_attributes.get("Purpose").enum_value == "USERDEFINED"
        assert props.address_attributes.get("Description").string_value == "Description"
        assert props.address_attributes.get("UserDefinedPurpose").string_value == "UserDefinedPurpose"
        assert [a.name for a in props.telephone_numbers] == ["Telephone", "Numbers"]
        assert [a.name for a in props.facsimile_numbers] == ["Facsimile", "Numbers"]
        assert [a.name for a in props.electronic_mail_addresses] == ["Electronic", "Mail", "Addresses"]
        assert [a.name for a in props.messaging_ids] == ["Messaging", "IDs"]

    def test_importing_a_telecom_address_twice(self):
        self.test_importing_a_telecom_address()
        ifc = tool.Ifc().get()
        address = ifc.createIfcTelecomAddress()
        address.Purpose = "OFFICE"
        subject().set_address(address)
        subject().import_address_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.address_attributes.get("Purpose").enum_value == "OFFICE"
        assert len(props.telephone_numbers) == 0
        assert len(props.facsimile_numbers) == 0
        assert len(props.electronic_mail_addresses) == 0
        assert len(props.messaging_ids) == 0


class TestImportOrganisationAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        organisation.Identification = "Identification"
        organisation.Name = "Name"
        organisation.Description = "Description"
        subject().set_organisation(organisation)
        subject().import_organisation_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.organisation_attributes.get("Identification").string_value == "Identification"
        assert props.organisation_attributes.get("Name").string_value == "Name"
        assert props.organisation_attributes.get("Description").string_value == "Description"

    def test_overwriting_a_previous_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        organisation = ifc.createIfcOrganization()
        organisation.Identification = "Identification"
        organisation.Description = "Description"
        subject().set_organisation(organisation)
        subject().import_organisation_attributes()
        organisation.Identification = "Identification2"
        organisation.Description = None
        subject().import_organisation_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.organisation_attributes.get("Identification").string_value == "Identification2"
        assert props.organisation_attributes.get("Description").string_value == ""


class TestImportPersonAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        person.FamilyName = "family_name"
        person.MiddleNames = ("middle", "names")
        person.PrefixTitles = ("prefix", "titles")
        person.SuffixTitles = ("suffix", "titles")
        subject().set_person(person)
        subject().import_person_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.person_attributes.get("Identification").string_value == "identification"
        assert props.person_attributes.get("GivenName").string_value == "given_name"
        assert props.person_attributes.get("FamilyName").string_value == "family_name"
        assert len(props.middle_names) == 2
        assert props.middle_names[0].name == "middle"
        assert props.middle_names[1].name == "names"
        assert len(props.prefix_titles) == 2
        assert props.prefix_titles[0].name == "prefix"
        assert props.prefix_titles[1].name == "titles"
        assert len(props.suffix_titles) == 2
        assert props.suffix_titles[0].name == "suffix"
        assert props.suffix_titles[1].name == "titles"

    def test_overwriting_a_previous_import(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        person = ifc.createIfcPerson()
        person.Identification = "identification"
        person.GivenName = "given_name"
        subject().set_person(person)
        subject().import_person_attributes()
        person.Identification = "identification2"
        person.GivenName = None
        subject().import_person_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.person_attributes.get("Identification").string_value == "identification2"
        assert props.person_attributes.get("GivenName").string_value == ""


class TestImportRoleAttributes(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        role.UserDefinedRole = "UserDefinedRole"
        role.Description = "Description"
        subject().set_role(role)
        subject().import_role_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.role_attributes.get("Role").enum_value == "USERDEFINED"
        assert props.role_attributes.get("UserDefinedRole").string_value == "UserDefinedRole"
        assert props.role_attributes.get("Description").string_value == "Description"

    def test_importing_twice(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        role = ifc.createIfcActorRole()
        role.Role = "USERDEFINED"
        subject().set_role(role)
        subject().import_role_attributes()
        role.Role = "ARCHITECT"
        subject().import_role_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.role_attributes.get("Role").enum_value == "ARCHITECT"


class TestRemoveAddressAttribute(NewFile):
    TestAddAddressAttribute().test_run()
    subject().remove_address_attribute("AddressLines", 0)
    subject().remove_address_attribute("TelephoneNumbers", 0)
    subject().remove_address_attribute("FacsimileNumbers", 0)
    subject().remove_address_attribute("ElectronicMailAddresses", 0)
    subject().remove_address_attribute("MessagingIDs", 0)
    props = bpy.context.scene.BIMOwnerProperties
    assert len(props.address_lines) == 0
    assert len(props.telephone_numbers) == 0
    assert len(props.facsimile_numbers) == 0
    assert len(props.electronic_mail_addresses) == 0
    assert len(props.messaging_ids) == 0


class TestRemovePersonAttribute(NewFile):
    def test_run(self):
        subject().add_person_attribute("MiddleNames")
        subject().remove_person_attribute("MiddleNames", 0)
        subject().add_person_attribute("PrefixTitles")
        subject().remove_person_attribute("PrefixTitles", 0)
        subject().add_person_attribute("SuffixTitles")
        subject().remove_person_attribute("SuffixTitles", 0)
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.middle_names) == 0
        assert len(props.prefix_titles) == 0
        assert len(props.suffix_titles) == 0


class TestSetActor(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        actor = ifc.createIfcActor()
        subject().set_actor(actor)
        assert bpy.context.scene.BIMOwnerProperties.active_actor_id == actor.id()


class TestSetAddress(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        assert bpy.context.scene.BIMOwnerProperties.active_address_id == address.id()


class TestSetOrganisation(NewFile):
    def test_run(self):
        organisation = ifcopenshell.file().createIfcOrganization()
        subject().set_organisation(organisation)
        assert bpy.context.scene.BIMOwnerProperties.active_organisation_id == organisation.id()


class TestSetPerson(NewFile):
    def test_run(self):
        person = ifcopenshell.file().createIfcPerson()
        subject().set_person(person)
        assert bpy.context.scene.BIMOwnerProperties.active_person_id == person.id()


class TestSetRole(NewFile):
    def test_run(self):
        role = ifcopenshell.file().createIfcActorRole()
        subject().set_role(role)
        assert bpy.context.scene.BIMOwnerProperties.active_role_id == role.id()


class TestSetUser(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        user = ifc.createIfcPersonAndOrganization()
        subject.set_user(user)
        assert bpy.context.scene.BIMOwnerProperties.active_user_id == user.id()
