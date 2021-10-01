import test.bootstrap
import ifcopenshell.api


class TestRemoveAddress(test.bootstrap.IFC4):
    def test_removing_an_address(self):
        postal = self.file.createIfcPostalAddress()
        telecom = self.file.createIfcTelecomAddress()
        ifcopenshell.api.run("owner.remove_address", self.file, address=postal)
        ifcopenshell.api.run("owner.remove_address", self.file, address=telecom)
        assert len(self.file.by_type("IfcAddress")) == 0

    def test_ensuring_organisation_cardinality_is_valid(self):
        address = self.file.createIfcPostalAddress()
        organisation = self.file.createIfcOrganization()
        organisation.Addresses = [address]
        ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        assert organisation.Addresses is None

    def test_ensuring_person_cardinality_is_valid(self):
        address = self.file.createIfcPostalAddress()
        person = self.file.createIfcPerson()
        person.Addresses = [address]
        ifcopenshell.api.run("owner.remove_address", self.file, address=address)
        assert person.Addresses is None
