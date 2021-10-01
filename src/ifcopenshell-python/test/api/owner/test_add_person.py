import test.bootstrap
import ifcopenshell.api


class TestAddPerson(test.bootstrap.IFC4):
    def test_adding_a_person(self):
        person = ifcopenshell.api.run(
            "owner.add_person",
            self.file,
            identification="Identification",
            family_name="FamilyName",
            given_name="GivenName",
        )
        assert person.Identification == "Identification"
        assert person.FamilyName == "FamilyName"
        assert person.GivenName == "GivenName"
