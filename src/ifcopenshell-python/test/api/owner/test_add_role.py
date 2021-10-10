import test.bootstrap
import ifcopenshell.api


class TestAddRole(test.bootstrap.IFC4):
    def test_adding_a_role_to_a_person(self):
        person = self.file.createIfcPerson()
        role = ifcopenshell.api.run("owner.add_role", self.file, assigned_object=person)
        assert role.is_a("IfcActorRole")
        assert role.Role == "ARCHITECT"
        assert person.Roles == (role,)

    def test_adding_a_role_to_an_organisation(self):
        organisation = self.file.createIfcOrganization()
        role = ifcopenshell.api.run("owner.add_role", self.file, assigned_object=organisation)
        assert role.is_a("IfcActorRole")
        assert role.Role == "ARCHITECT"
        assert organisation.Roles == (role,)
