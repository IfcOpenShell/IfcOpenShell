import numpy
import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.placement


class TestUnassignRepresentation(test.bootstrap.IFC4):
    def test_unassigning_a_product_representation(self):
        representation = self.file.createIfcShapeRepresentation()
        representation2 = self.file.createIfcShapeRepresentation()
        wall = self.file.createIfcWall(
            Representation=self.file.createIfcProductDefinitionShape(Representations=[representation, representation2])
        )
        ifcopenshell.api.run("geometry.unassign_representation", self.file, product=wall, representation=representation)
        assert representation not in wall.Representation.Representations
        ifcopenshell.api.run(
            "geometry.unassign_representation", self.file, product=wall, representation=representation2
        )
        assert not wall.Representation
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0

    def test_unassigning_a_type_product_representation(self):
        representation = self.file.createIfcShapeRepresentation()
        origin = self.file.createIfcAxis2Placement3D()
        repmap = self.file.createIfcRepresentationMap(MappedRepresentation=representation, MappingOrigin=origin)
        walltype = self.file.createIfcWallType(RepresentationMaps=[repmap])
        ifcopenshell.api.run(
            "geometry.unassign_representation", self.file, product=walltype, representation=representation
        )
        assert not walltype.RepresentationMaps
        assert len(self.file.by_type("IfcAxis2Placement3D")) == 0
        assert len(self.file.by_type("IfcRepresentationMap")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1

    def test_unassigning_a_type_product_representation_used_by_instances(self):
        representation = self.file.createIfcShapeRepresentation()
        origin = self.file.createIfcAxis2Placement3D()
        repmap = self.file.createIfcRepresentationMap(MappedRepresentation=representation, MappingOrigin=origin)
        walltype = self.file.createIfcWallType(RepresentationMaps=[repmap])
        mapped_item = self.file.createIfcMappedItem(MappingSource=repmap)
        rep = self.file.createIfcShapeRepresentation(Items=[mapped_item])
        prodrep = self.file.createIfcProductDefinitionShape(Representations=[rep])
        wall = self.file.createIfcWall(Representation=prodrep)
        ifcopenshell.api.run(
            "geometry.unassign_representation", self.file, product=walltype, representation=representation
        )
        assert not walltype.RepresentationMaps
        assert len(self.file.by_type("IfcAxis2Placement3D")) == 0
        assert len(self.file.by_type("IfcRepresentationMap")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert not wall.Representation
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0
