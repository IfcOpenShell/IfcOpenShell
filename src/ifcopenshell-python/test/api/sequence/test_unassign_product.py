import test.bootstrap
import ifcopenshell.api


class TestUnassignProduct(test.bootstrap.IFC4):
    def test_unassigning_a_product(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.run("sequence.unassign_product", self.file, relating_product=wall, related_object=task)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 0
