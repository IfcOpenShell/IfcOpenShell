import test.bootstrap
import ifcopenshell.api


class TestCopyClass(test.bootstrap.IFC4):
    def test_copying_a_simple_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert new != element
        assert new.GlobalId != element.GlobalId
        assert new.is_a("IfcWall")

    def test_copying_an_element_with_properties(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        pset = ifcopenshell.api.run("pset.add_pset", self.file, product=element, name="Foobar")
        ifcopenshell.api.run("pset.edit_pset", self.file, pset=pset, properties={"foo": "bar"})
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        pset = element.IsDefinedBy[0].RelatingPropertyDefinition
        new_pset = new.IsDefinedBy[0].RelatingPropertyDefinition
        assert element.IsDefinedBy[0] != new.IsDefinedBy[0]
        assert pset != new_pset
        assert pset.Name == new_pset.Name
        assert pset.HasProperties[0] != new_pset.HasProperties[0]
        assert pset.HasProperties[0].Name == new_pset.HasProperties[0].Name
        assert pset.HasProperties[0].NominalValue.wrappedValue == new_pset.HasProperties[0].NominalValue.wrappedValue

    def test_copying_an_aggregate_only_and_not_its_decomposition(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert element.IsDecomposedBy
        assert not new.IsDecomposedBy

    def test_not_copying_any_representations_because_life_is_hard(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        element.Representation = self.file.createIfcProductDefinitionShape()
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert new.Representation is None
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWallType")
        element.RepresentationMaps = [self.file.createIfcRepresentationMap()]
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert new.RepresentationMaps is None

    def test_copying_an_opening_voiding_an_element(self):
        wall = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_opening", self.file, opening=opening, element=wall)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=opening)
        assert opening.VoidsElements[0] != new.VoidsElements[0]
        assert new.VoidsElements[0].RelatingBuildingElement == wall

    def test_copying_an_opening_with_a_filling(self):
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=opening)
        assert not new.HasFillings
