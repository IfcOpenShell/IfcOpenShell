import test.bootstrap
import ifcopenshell.api


class TestMapTypeRepresentations(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_type_has_no_representation_maps(self):
        element = self.file.createIfcWall()
        type = self.file.createIfcWallType()
        ifcopenshell.api.run("type.assign_type", self.file, related_object=element, relating_type=type)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("type.map_type_representations", self.file, related_object=element, relating_type=type)
        assert len([e for e in self.file]) == total_elements

    def test_removing_existing_element_representations_and_mapping_type_representations(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        element = self.file.createIfcWall(
            Representation=self.file.createIfcProductRepresentation(
                Representations=[self.file.createIfcShapeRepresentation(ContextOfItems=context)]
            )
        )
        type = self.file.createIfcWallType(
            RepresentationMaps=[
                self.file.createIfcRepresentationMap(
                    MappedRepresentation=self.file.createIfcShapeRepresentation(ContextOfItems=context)
                )
            ]
        )
        self.file.createIfcRelDefinesByType(RelatingType=type, RelatedObjects=[element])
        ifcopenshell.api.run("type.map_type_representations", self.file, related_object=element, relating_type=type)
        rep = element.Representation.Representations[0]
        assert rep.RepresentationType == "MappedRepresentation"
        assert rep.Items[0].MappingSource == type.RepresentationMaps[0]
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
