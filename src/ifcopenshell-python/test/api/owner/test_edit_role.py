import test.bootstrap
import ifcopenshell.api


class TestEditRole(test.bootstrap.IFC4):
    def test_editing_a_role(self):
        role = self.file.createIfcActorRole()
        ifcopenshell.api.run(
            "owner.edit_role",
            self.file,
            role=role,
            attributes={"Role": "ARCHITECT", "UserDefinedRole": "UserDefinedRole", "Description": "Description"},
        )
        assert role.Role == "ARCHITECT"
        assert role.UserDefinedRole == "UserDefinedRole"
        assert role.Description == "Description"
