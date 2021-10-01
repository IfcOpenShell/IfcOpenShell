import test.bootstrap
import ifcopenshell.api


class TestRemoveAddress(test.bootstrap.IFC4):
    def test_removing_an_address(self):
        postal = self.file.createIfcPostalAddress()
        telecom = self.file.createIfcTelecomAddress()
        ifcopenshell.api.run("owner.remove_address", self.file, address=postal)
        ifcopenshell.api.run("owner.remove_address", self.file, address=telecom)
        assert len(self.file.by_type("IfcAddress")) == 0
