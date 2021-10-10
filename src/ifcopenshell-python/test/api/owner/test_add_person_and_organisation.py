import test.bootstrap
import ifcopenshell.api


class TestAddPersonAndOrganisation(test.bootstrap.IFC4):
    def test_adding(self):
        person = self.file.createIfcPerson()
        organisation = self.file.createIfcOrganization()
        person_and_organisation = ifcopenshell.api.run(
            "owner.add_person_and_organisation", self.file, person=person, organisation=organisation
        )
