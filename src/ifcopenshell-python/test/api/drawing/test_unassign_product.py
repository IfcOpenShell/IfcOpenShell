import test.bootstrap
import ifcopenshell.api


class TestUnassignProduct(test.bootstrap.IFC4):
    def test_unassigning_a_product(self):
        wall = self.file.createIfcWall()
        label = self.file.createIfcAnnotation()
        ifcopenshell.api.run("drawing.assign_product", self.file, relating_product=wall, related_object=label)
        ifcopenshell.api.run("drawing.unassign_product", self.file, relating_product=wall, related_object=label)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 0
