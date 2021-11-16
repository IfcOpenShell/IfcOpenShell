import test.bootstrap
import ifcopenshell.api


class TestRemoveReference(test.bootstrap.IFC4):
    def test_removing_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        ifcopenshell.api.run("library.remove_reference", self.file, reference=reference)
        assert len(self.file.by_type("IfcLibraryReference")) == 0
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0
