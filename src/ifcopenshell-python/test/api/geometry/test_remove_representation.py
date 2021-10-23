import test.bootstrap
import ifcopenshell.api


class TestRemoveRepresentation(test.bootstrap.IFC4):
    def test_removing_a_single_unused_shape_representation(self):
        representation = self.file.createIfcShapeRepresentation()
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcShapeRepresentation")) == 0

    def test_not_removing_a_shape_representation_in_use(self):
        representation = self.file.createIfcShapeRepresentation()
        self.file.createIfcProductRepresentation(Representations=[representation])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1

    def test_removing_a_mapped_representation_fully(self):
        representation = self.file.createIfcShapeRepresentation(
            RepresentationType="MappedRepresentation",
            Items=[
                self.file.createIfcMappedItem(
                    MappingTarget=self.file.createIfcRepresentationMap(
                        MappedRepresentation=self.file.createIfcShapeRepresentation()
                    )
                )
            ],
        )
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcShapeRepresentation")) == 0

    def test_removing_only_the_representation_mapping_if_the_map_has_other_users(self):
        representation_map = self.file.createIfcRepresentationMap(
            MappedRepresentation=self.file.createIfcShapeRepresentation()
        )
        self.file.createIfcWallType(RepresentationMaps=[representation_map])
        representation = self.file.createIfcShapeRepresentation(
            RepresentationType="MappedRepresentation",
            Items=[
                self.file.createIfcMappedItem(
                    MappingTarget=representation_map
                )
            ],
        )
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert self.file.by_type("IfcShapeRepresentation")[0].RepresentationType != "MappedRepresentation"
        assert len(self.file.by_type("IfcRepresentationMap")) == 1

    def test_purging_styled_items(self):
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        styled_item = self.file.createIfcStyledItem(Item=item)
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcStyledItem")) == 0

    def test_not_purging_styled_items_if_used_elsewhere(self):
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        styled_item = self.file.createIfcStyledItem(Item=item)
        representation2 = self.file.createIfcShapeRepresentation(Items=[item])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcStyledItem")) == 1

    def test_purging_presentation_layers(self):
        representation = self.file.createIfcShapeRepresentation()
        layer = self.file.createIfcPresentationLayerAssignment(AssignedItems=[representation])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcPresentationLayerAssignment")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 0

    def test_not_purging_presentation_layers_still_in_use(self):
        representation = self.file.createIfcShapeRepresentation()
        representation2 = self.file.createIfcShapeRepresentation()
        layer = self.file.createIfcPresentationLayerAssignment(AssignedItems=[representation, representation2])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcPresentationLayerAssignment")) == 1
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1

    def test_not_purging_geometric_representation_contexts(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        representation = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcGeometricRepresentationContext")) == 1
