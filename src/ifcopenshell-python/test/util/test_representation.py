# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.representation as subject
import test.bootstrap


class TestGetPartOfProduct(test.bootstrap.IFC4):
    def test_returns_representation_for_a_product(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        shape = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        element = self.file.createIfcWall(
            Representation=self.file.create_entity("IfcProductDefinitionShape", Representations=[shape])
        )
        assert subject.get_part_of_product(element, context) == element.Representation

    def test_returns_none_for_a_type_product_with_no_representation_maps(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        type = self.file.createIfcWallType()
        assert type.RepresentationMaps is None
        assert subject.get_part_of_product(type, context) is None

    def test_returns_matching_representation_map_for_a_type_product(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        map = self.file.createIfcRepresentationMap(
            MappedRepresentation=self.file.createIfcShapeRepresentation(ContextOfItems=context)
        )
        type = self.file.createIfcWallType(RepresentationMaps=[map])
        assert subject.get_part_of_product(type, context) == map

    def test_returns_none_when_no_representation_map_matches_the_context(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        other_context = self.file.createIfcGeometricRepresentationSubContext()
        map = self.file.createIfcRepresentationMap(
            MappedRepresentation=self.file.createIfcShapeRepresentation(ContextOfItems=other_context)
        )
        type = self.file.createIfcWallType(RepresentationMaps=[map])
        assert subject.get_part_of_product(type, context) is None


class TestGetPartOfProductIFC2X3(test.bootstrap.IFC2X3):
    def test_returns_none_for_a_type_product_with_no_representation_maps(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        type = self.file.createIfcWallType()
        assert type.RepresentationMaps is None
        assert subject.get_part_of_product(type, context) is None

    def test_returns_none_for_a_type_product_even_with_matching_representation_maps(self):
        # As documented, get_part_of_product always returns None for IFC2X3
        # type products, since IFC2X3 does not fully support shape aspects.
        context = self.file.createIfcGeometricRepresentationSubContext()
        map = self.file.createIfcRepresentationMap(
            MappedRepresentation=self.file.createIfcShapeRepresentation(ContextOfItems=context)
        )
        type = self.file.createIfcWallType(RepresentationMaps=[map])
        assert subject.get_part_of_product(type, context) is None
