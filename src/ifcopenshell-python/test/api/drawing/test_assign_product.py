import test.bootstrap
import ifcopenshell.api


class TestAssignProduct(test.bootstrap.IFC4):
    def test_assigning_a_product(self):
        wall = self.file.createIfcWall()
        label = self.file.createIfcAnnotation()
        label2 = self.file.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=wall, related_object=label)
        assert wall.ReferencedBy[0].RelatedObjects == (label,)
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=wall, related_object=label2)
        assert wall.ReferencedBy[0].RelatedObjects == (label, label2)

    def test_not_assigning_twice(self):
        wall = self.file.createIfcWall()
        label = self.file.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=wall, related_object=label)
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=wall, related_object=label)
        assert wall.ReferencedBy[0].RelatedObjects == (label,)
