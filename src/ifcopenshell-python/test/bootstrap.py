import pytest
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.owner.settings


class IFC4:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]


class IFC2X3:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.api.run("project.create_file", version="IFC2X3")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: ifc.createIfcPersonAndOrganization()
        ifcopenshell.api.owner.settings.get_application = lambda ifc: ifc.createIfcApplication()
