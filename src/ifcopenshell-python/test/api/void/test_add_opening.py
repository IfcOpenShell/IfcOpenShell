import test.bootstrap
import ifcopenshell.api


class TestAddOpening(test.bootstrap.IFC4):
    def test_adding_an_opening(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening

    def test_adding_an_opening_twice(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert wall.HasOpenings[0].RelatedOpeningElement == opening
        assert len(wall.HasOpenings) == 1

    def test_adding_an_opening_which_is_already_voiding_another_element(self):
        slab = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSlab")
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=slab)
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        assert not slab.HasOpenings
        assert wall.HasOpenings[0].RelatedOpeningElement == opening
