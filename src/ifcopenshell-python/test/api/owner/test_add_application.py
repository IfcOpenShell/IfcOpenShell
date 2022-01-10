import test.bootstrap
import ifcopenshell.api


class TestAddApplication(test.bootstrap.IFC4):
    def test_adding_the_ifcopenshell_application(self):
        application = ifcopenshell.api.run("owner.add_application", self.file)
        developer = application.ApplicationDeveloper
        assert application.Version == ifcopenshell.version
        assert application.ApplicationFullName == "IfcOpenShell"
        assert application.ApplicationIdentifier == "IfcOpenShell"
        assert developer.is_a("IfcOrganization")
        assert developer.Identification == "IfcOpenShell"
        assert developer.Name == "IfcOpenShell"
        assert (
            developer.Description
            == "IfcOpenShell is an open source software library that helps users and software developers to work with IFC data."
        )
        assert developer.Roles[0].Role == "USERDEFINED"
        assert developer.Roles[0].UserDefinedRole == "CONTRIBUTOR"
        assert developer.Addresses[0].is_a("IfcTelecomAddress")
        assert developer.Addresses[0].Purpose == "USERDEFINED"
        assert developer.Addresses[0].UserDefinedPurpose == "WEBPAGE"
        assert developer.Addresses[0].WWWHomePageURL == "https://ifcopenshell.org"
