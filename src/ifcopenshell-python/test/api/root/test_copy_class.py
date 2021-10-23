import numpy
import test.bootstrap
import ifcopenshell.api


class TestCopyClass(test.bootstrap.IFC4):
    def test_copying_a_simple_element(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert new != element
        assert new.GlobalId != element.GlobalId
        assert new.is_a("IfcWall")

    def test_copying_object_placements_so_children_of_the_original_element_dont_reference_the_new_element(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        matrix = numpy.identity(4)
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=element, matrix=matrix.copy())
        ifcopenshell.api.run("geometry.edit_object_placement", self.file, product=subelement, matrix=matrix.copy())
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert subelement.ObjectPlacement.PlacementRelTo == element.ObjectPlacement
        assert subelement.ObjectPlacement.PlacementRelTo != new.ObjectPlacement
        assert element.ObjectPlacement.RelativePlacement != new.ObjectPlacement.RelativePlacement

    def test_copying_psets_so_changing_properties_of_the_new_element_does_not_affect_the_old(self):
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

    def test_copying_a_container_only_and_not_its_contents(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert element.ContainsElements
        assert not new.ContainsElements

    def test_copying_contents_of_a_container_and_maintaining_the_containment_relationship(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=subelement)
        assert new.ContainedInStructure[0].RelatingStructure == element

    def test_copying_a_container_only_and_not_its_decomposition(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuildingStorey")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert element.IsDecomposedBy
        assert not new.IsDecomposedBy

    def test_copying_an_aggregate_only_and_not_its_decomposition(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert element.IsDecomposedBy
        assert not new.IsDecomposedBy

    def test_copying_an_aggregate_decomposition_and_maintaining_the_aggregate_relationship(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcElementAssembly")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBeam")
        ifcopenshell.api.run("aggregate.assign_object", self.file, product=subelement, relating_object=element)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=subelement)
        assert new.Decomposes[0].RelatingObject == element

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

    def test_copying_a_filling(self):
        door = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcDoor")
        opening = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcOpeningElement")
        ifcopenshell.api.run("void.add_filling", self.file, opening=opening, element=door)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=door)
        assert not new.FillsVoids

    def test_copying_material_set_usages(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        material = self.file.createIfcMaterialLayerSetUsage()
        self.file.createIfcRelAssociatesMaterial(RelatedObjects=[element], RelatingMaterial=material)
        new = ifcopenshell.api.run("root.copy_class", self.file, product=element)
        assert new.HasAssociations[0].RelatingMaterial != element.HasAssociations[0].RelatingMaterial
        assert new.HasAssociations[0].RelatingMaterial.is_a("IfcMaterialLayerSetUsage")
