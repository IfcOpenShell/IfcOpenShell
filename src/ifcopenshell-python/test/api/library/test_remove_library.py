import test.bootstrap
import ifcopenshell.api


class TestRemoveLibrary(test.bootstrap.IFC4):
    def test_removing_a_library(self):
        library = self.file.createIfcLibraryInformation()
        ifcopenshell.api.run("library.remove_library", self.file, library=library)
        assert len(self.file.by_type("IfcLibraryInformation")) == 0

    def test_removing_a_library_and_all_references(self):
        library = self.file.createIfcLibraryInformation()
        reference1 = self.file.createIfcLibraryReference(ReferencedLibrary=library)
        reference2 = self.file.createIfcLibraryReference(ReferencedLibrary=library)
        self.file.createIfcRelAssociatesLibrary(GlobalId='foo', RelatingLibrary=library)
        self.file.createIfcRelAssociatesLibrary(GlobalId='bar', RelatingLibrary=reference1)
        ifcopenshell.api.run("library.remove_library", self.file, library=library)
        assert len(self.file.by_type("IfcLibraryReference")) == 0
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0
