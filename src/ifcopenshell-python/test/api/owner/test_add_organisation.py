import test.bootstrap
import ifcopenshell.api


class TestAddOrganisation(test.bootstrap.IFC4):
    def test_adding_an_organisation(self):
        org = ifcopenshell.api.run("owner.add_organisation", self.file, identification="Id", name="Name")
        assert org.Identification == "Id"
        assert org.Name == "Name"
