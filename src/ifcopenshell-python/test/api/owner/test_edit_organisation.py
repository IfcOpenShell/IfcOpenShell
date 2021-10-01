import test.bootstrap
import ifcopenshell.api


class TestEditOrganisation(test.bootstrap.IFC4):
    def test_editing_a_organisation(self):
        organisation = self.file.createIfcOrganization()
        ifcopenshell.api.run("owner.edit_organisation", self.file, organisation=organisation, attributes={
            "Identification": "Identification",
            "Name": "Name",
            "Description": "Description",
        })
        assert organisation.Identification == "Identification"
        assert organisation.Name == "Name"
        assert organisation.Description == "Description"
