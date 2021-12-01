import test.bootstrap
import ifcopenshell.api


class TestRemoveOpening(test.bootstrap.IFC4):
    def test_removing_a_simple_opening(self):
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.remove_opening", self.file, opening=opening)
        assert len(list(self.file)) == 0

    def test_removing_an_opening_voiding_a_wall(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        ifcopenshell.api.run("void.remove_opening", self.file, opening=opening)
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0
        assert wall

    def test_removing_an_opening_voiding_a_wall_with_a_filling(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        ifcopenshell.api.run("void.remove_opening", self.file, opening=opening)
        assert len(self.file.by_type("IfcOpeningElement")) == 0
        assert len(self.file.by_type("IfcRelVoidsElement")) == 0
        assert len(self.file.by_type("IfcRelFillsElement")) == 0
        assert wall
        assert door
