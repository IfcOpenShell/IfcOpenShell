import pytest
import ifcopenshell
import ifcopenshell.api


class IFC4:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file")


class IFC2X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: ifc.createIfcPersonAndOrganization()
        ifcopenshell.api.owner.settings.get_application = lambda ifc: ifc.createIfcApplication()
