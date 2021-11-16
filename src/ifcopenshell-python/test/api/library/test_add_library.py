import test.bootstrap
import ifcopenshell.api


class TestAddLibrary(test.bootstrap.IFC4):
    def test_adding_a_library(self):
        library = ifcopenshell.api.run("library.add_library", self.file, name="Name")
        assert library.is_a("IfcLibraryInformation")
        assert library.Name == "Name"
