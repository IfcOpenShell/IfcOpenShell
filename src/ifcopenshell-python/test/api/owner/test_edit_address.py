# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.owner


class TestEditAddress(test.bootstrap.IFC4):
    def test_editing_a_postal_address(self):
        address = self.file.createIfcPostalAddress()
        ifcopenshell.api.owner.edit_address(
            self.file,
            address=address,
            attributes={
                "Purpose": "OFFICE",
                "Description": "Description",
                "UserDefinedPurpose": "UserDefinedPurpose",
                "InternalLocation": "InternalLocation",
                "AddressLines": ["Address", "Lines"],
                "PostalBox": "PostalBox",
                "Town": "Town",
                "Region": "Region",
                "PostalCode": "PostalCode",
                "Country": "Country",
            },
        )
        assert address.Purpose == "OFFICE"
        assert address.Description == "Description"
        assert address.UserDefinedPurpose == "UserDefinedPurpose"
        assert address.InternalLocation == "InternalLocation"
        assert address.AddressLines == ("Address", "Lines")
        assert address.PostalBox == "PostalBox"
        assert address.Town == "Town"
        assert address.Region == "Region"
        assert address.PostalCode == "PostalCode"
        assert address.Country == "Country"

    def test_editing_a_telecom_address(self):
        address = self.file.createIfcTelecomAddress()
        attributes = {
            "Purpose": "OFFICE",
            "Description": "Description",
            "UserDefinedPurpose": "UserDefinedPurpose",
            "TelephoneNumbers": ["Telephone", "Numbers"],
            "FacsimileNumbers": ["Facsimile", "Numbers"],
            "PagerNumber": "PagerNumber",
            "ElectronicMailAddresses": ["Electronic", "Mail", "Addresses"],
            "WWWHomePageURL": "WWWHomePageURL",
        }
        if self.file.schema != "IFC2X3":
            attributes["MessagingIDs"] = ["Messaging", "IDs"]

        ifcopenshell.api.owner.edit_address(
            self.file,
            address=address,
            attributes=attributes,
        )
        assert address.Purpose == "OFFICE"
        assert address.Description == "Description"
        assert address.UserDefinedPurpose == "UserDefinedPurpose"
        assert address.TelephoneNumbers == ("Telephone", "Numbers")
        assert address.FacsimileNumbers == ("Facsimile", "Numbers")
        assert address.PagerNumber == "PagerNumber"
        assert address.ElectronicMailAddresses == ("Electronic", "Mail", "Addresses")
        assert address.WWWHomePageURL == "WWWHomePageURL"
        if self.file.schema != "IFC2X3":
            assert address.MessagingIDs == ("Messaging", "IDs")


class TestEditAddressIFC2X3(test.bootstrap.IFC2X3, TestEditAddress):
    pass
