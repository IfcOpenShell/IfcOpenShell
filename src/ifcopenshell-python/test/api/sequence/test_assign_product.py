import test.bootstrap
import ifcopenshell.api


class TestAssignProduct(test.bootstrap.IFC4):
    def test_assigning_a_product(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        task2 = self.file.createIfcTask()
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=wall, related_object=task)
        assert wall.ReferencedBy[0].RelatedObjects == (task,)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=wall, related_object=task2)
        assert wall.ReferencedBy[0].RelatedObjects == (task, task2)

    def test_not_assigning_twice(self):
        wall = self.file.createIfcWall()
        task = self.file.createIfcTask()
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=wall, related_object=task)
        ifcopenshell.api.run("sequence.assign_product", self.file, relating_product=wall, related_object=task)
        assert wall.ReferencedBy[0].RelatedObjects == (task,)
