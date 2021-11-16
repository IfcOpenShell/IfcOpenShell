import test.bootstrap
import ifcopenshell.api


class TestAddReference(test.bootstrap.IFC4):
    def test_adding_a_reference(self):
        library = ifcopenshell.api.run("library.add_library", self.file, name="Name")
        reference = ifcopenshell.api.run("library.add_reference", self.file, library=library)
        assert reference.is_a("IfcLibraryReference")
        assert reference.ReferencedLibrary == library
