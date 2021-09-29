# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import test.bim.bootstrap
import blenderbim.core.tool
import blenderbim.tool as tool
from blenderbim.tool.address_editor import AddressEditor as subject


class TestImplementsTool(test.bim.bootstrap.NewFile):
    def test_run(self):
        assert isinstance(subject(), blenderbim.core.tool.AddressEditor)


class TestSetAddress(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        assert bpy.context.scene.BIMOwnerProperties.active_address_id == address.id()


class TestImportAttributes(test.bim.bootstrap.NewFile):
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
        subject().import_attributes()
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
        subject().import_attributes()
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
        subject().import_attributes()
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
        subject().import_attributes()
        props = bpy.context.scene.BIMOwnerProperties
        assert props.address_attributes.get("Purpose").enum_value == "OFFICE"
        assert len(props.telephone_numbers) == 0
        assert len(props.facsimile_numbers) == 0
        assert len(props.electronic_mail_addresses) == 0
        assert len(props.messaging_ids) == 0


class TestClearAddress(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        subject().clear_address()
        assert bpy.context.scene.BIMOwnerProperties.active_address_id == 0


class TestGetAddress(test.bim.bootstrap.NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc().set(ifc)
        address = ifc.createIfcPostalAddress()
        subject().set_address(address)
        assert subject().get_address() == address


class TestExportAttributes(test.bim.bootstrap.NewFile):
    def test_exporting_a_postal_address(self):
        TestImportAttributes().test_importing_a_postal_address()
        assert subject().export_attributes() == {
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
        TestImportAttributes().test_importing_a_telecom_address()
        assert subject().export_attributes() == {
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


class TestAddAttribute(test.bim.bootstrap.NewFile):
    def test_run(self):
        subject().add_attribute("AddressLines")
        subject().add_attribute("TelephoneNumbers")
        subject().add_attribute("FacsimileNumbers")
        subject().add_attribute("ElectronicMailAddresses")
        subject().add_attribute("MessagingIDs")
        props = bpy.context.scene.BIMOwnerProperties
        assert len(props.address_lines) == 1
        assert len(props.telephone_numbers) == 1
        assert len(props.facsimile_numbers) == 1
        assert len(props.electronic_mail_addresses) == 1
        assert len(props.messaging_ids) == 1


class TestRemoveAddress(test.bim.bootstrap.NewFile):
    TestAddAttribute().test_run()
    subject().remove_attribute("AddressLines", 0)
    subject().remove_attribute("TelephoneNumbers", 0)
    subject().remove_attribute("FacsimileNumbers", 0)
    subject().remove_attribute("ElectronicMailAddresses", 0)
    subject().remove_attribute("MessagingIDs", 0)
    props = bpy.context.scene.BIMOwnerProperties
    assert len(props.address_lines) == 0
    assert len(props.telephone_numbers) == 0
    assert len(props.facsimile_numbers) == 0
    assert len(props.electronic_mail_addresses) == 0
    assert len(props.messaging_ids) == 0
