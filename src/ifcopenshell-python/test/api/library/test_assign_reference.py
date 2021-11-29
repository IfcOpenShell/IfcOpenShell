import test.bootstrap
import ifcopenshell.api


class TestAssignReference(test.bootstrap.IFC4):
    def test_assigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        product2 = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        assert reference.LibraryRefForObjects[0].RelatedObjects == (product,)
        ifcopenshell.api.run("library.assign_reference", self.file, product=product2, reference=reference)
        assert reference.LibraryRefForObjects[0].RelatedObjects == (product, product2)

    def test_not_assigning_twice(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        assert reference.LibraryRefForObjects[0].RelatedObjects == (product,)


class TestAssignReference(test.bootstrap.IFC2X3):
    def test_assigning_a_reference(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        product2 = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        rel = self.file.by_type("IfcRelAssociatesLibrary")[0]
        assert rel.RelatedObjects == (product,)
        ifcopenshell.api.run("library.assign_reference", self.file, product=product2, reference=reference)
        assert rel.RelatedObjects == (product, product2)

    def test_not_assigning_twice(self):
        reference = self.file.createIfcLibraryReference()
        product = self.file.createIfcWall()
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        ifcopenshell.api.run("library.assign_reference", self.file, product=product, reference=reference)
        rel = self.file.by_type("IfcRelAssociatesLibrary")[0]
        assert rel.RelatedObjects == (product,)
