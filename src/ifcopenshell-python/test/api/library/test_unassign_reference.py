import test.bootstrap
import ifcopenshell.api


class TestUnassignReference(test.bootstrap.IFC4):
    def test_unassigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        product2 = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        ifcopenshell.api.run("library.unassign_reference", self.file, product=product, reference=reference)
        assert len(self.file.by_type("IfcRelAssociatesLibrary")) == 0
