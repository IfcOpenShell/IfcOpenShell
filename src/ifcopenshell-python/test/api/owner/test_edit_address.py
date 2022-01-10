import test.bootstrap
import ifcopenshell.api


class TestEditAddress(test.bootstrap.IFC4):
    def test_editing_a_postal_address(self):
        address = self.file.createIfcPostalAddress()
        ifcopenshell.api.run(
            "owner.edit_address",
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
        ifcopenshell.api.run(
            "owner.edit_address",
            self.file,
            address=address,
            attributes={
                "Purpose": "OFFICE",
                "Description": "Description",
                "UserDefinedPurpose": "UserDefinedPurpose",
                "TelephoneNumbers": ["Telephone", "Numbers"],
                "FacsimileNumbers": ["Facsimile", "Numbers"],
                "PagerNumber": "PagerNumber",
                "ElectronicMailAddresses": ["Electronic", "Mail", "Addresses"],
                "WWWHomePageURL": "WWWHomePageURL",
                "MessagingIDs": ["Messaging", "IDs"],
            },
        )
        assert address.Purpose == "OFFICE"
        assert address.Description == "Description"
        assert address.UserDefinedPurpose == "UserDefinedPurpose"
        assert address.TelephoneNumbers == ("Telephone", "Numbers")
        assert address.FacsimileNumbers == ("Facsimile", "Numbers")
        assert address.PagerNumber == "PagerNumber"
        assert address.ElectronicMailAddresses == ("Electronic", "Mail", "Addresses")
        assert address.WWWHomePageURL == "WWWHomePageURL"
        assert address.MessagingIDs == ("Messaging", "IDs")
