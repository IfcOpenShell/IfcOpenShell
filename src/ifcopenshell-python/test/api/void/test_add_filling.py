import test.bootstrap
import ifcopenshell.api


class TestAddFilling(test.bootstrap.IFC4):
    def test_adding_a_filling(self):
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        assert door.FillsVoids[0].RelatingOpeningElement == opening

    def test_adding_a_filling_twice(self):
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        assert door.FillsVoids[0].RelatingOpeningElement == opening
        assert len(opening.HasFillings) == 1

    def test_adding_a_filling_which_is_already_filling_another_opening(self):
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        opening1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        opening2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening1, element=door)
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening2, element=door)
        assert not opening1.HasFillings
        assert opening2.HasFillings[0].RelatedBuildingElement == door
