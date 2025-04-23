# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import test.bootstrap
import ifcopenshell.api.geometry
import ifcopenshell.util.placement


class TestUnassignRepresentation(test.bootstrap.IFC4):
    def test_unassigning_a_product_representation(self):
        representation = self.file.createIfcShapeRepresentation()
        representation2 = self.file.createIfcShapeRepresentation()
        item = self.file.create_entity("IfcExtrudedAreaSolid")
        representation2.Items = (item,)
        wall = self.file.createIfcWall(
            Representation=self.file.createIfcProductDefinitionShape(Representations=[representation, representation2])
        )

        shape_aspect = self.file.create_entity("IfcShapeAspect")
        shape_aspect.ShapeRepresentations = (self.file.createIfcShapeRepresentation(Items=(item,)),)
        shape_aspect.PartOfProductDefinitionShape = wall.Representation

        ifcopenshell.api.geometry.unassign_representation(self.file, product=wall, representation=representation)
        assert representation not in wall.Representation.Representations
        ifcopenshell.api.geometry.unassign_representation(self.file, product=wall, representation=representation2)
        assert not wall.Representation
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0
        assert len(self.file.by_type("IfcShapeAspect")) == 0

    def test_unassigning_a_type_product_representation(self):
        item = self.file.create_entity("IfcExtrudedAreaSolid")
        representation = self.file.createIfcShapeRepresentation(Items=(item,))
        origin = self.file.createIfcAxis2Placement3D()
        repmap = self.file.createIfcRepresentationMap(MappedRepresentation=representation, MappingOrigin=origin)
        walltype = self.file.createIfcWallType(RepresentationMaps=[repmap])

        shape_aspect = self.file.create_entity("IfcShapeAspect")
        shape_aspect.ShapeRepresentations = (self.file.createIfcShapeRepresentation(Items=(item,)),)
        shape_aspect.PartOfProductDefinitionShape = repmap

        ifcopenshell.api.geometry.unassign_representation(self.file, product=walltype, representation=representation)
        assert not walltype.RepresentationMaps
        assert len(self.file.by_type("IfcAxis2Placement3D")) == 0
        assert len(self.file.by_type("IfcRepresentationMap")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert len(self.file.by_type("IfcShapeAspect")) == 0

    def test_unassigning_a_type_product_representation_used_by_instances(self):
        representation = self.file.createIfcShapeRepresentation()
        origin = self.file.createIfcAxis2Placement3D()
        repmap = self.file.createIfcRepresentationMap(MappedRepresentation=representation, MappingOrigin=origin)
        walltype = self.file.createIfcWallType(RepresentationMaps=[repmap])
        mapped_item = self.file.createIfcMappedItem(MappingSource=repmap)
        rep = self.file.createIfcShapeRepresentation(Items=[mapped_item])
        prodrep = self.file.createIfcProductDefinitionShape(Representations=[rep])
        wall = self.file.createIfcWall(Representation=prodrep)
        ifcopenshell.api.geometry.unassign_representation(self.file, product=walltype, representation=representation)
        assert not walltype.RepresentationMaps
        assert len(self.file.by_type("IfcAxis2Placement3D")) == 0
        assert len(self.file.by_type("IfcRepresentationMap")) == 0
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert not wall.Representation
        assert len(self.file.by_type("IfcProductDefinitionShape")) == 0


class TestUnassignRepresentationIFC2X3(test.bootstrap.IFC2X3, TestUnassignRepresentation):
    pass
