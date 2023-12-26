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
            Items=[self.file.createIfcMappedItem(MappingTarget=representation_map)],
        )
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcShapeRepresentation")) == 1
        assert self.file.by_type("IfcShapeRepresentation")[0].RepresentationType != "MappedRepresentation"
        assert len(self.file.by_type("IfcRepresentationMap")) == 1

    def test_purging_styled_items_assignments_but_keeping_the_surface_style(self):
        item = self.file.createIfcExtrudedAreaSolid()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        surface_style = self.file.createIfcSurfaceStyle()
        styled_item = self.file.createIfcStyledItem(Item=item, Styles=[surface_style])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcStyledItem")) == 0
        assert len(self.file.by_type("IfcSurfaceStyle")) == 1

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

    def test_purging_colour_map(self):
        item = self.file.createIfcTriangulatedFaceSet()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        colour = self.file.createIfcIndexedColourMap(Colours=self.file.createIfcColourRgbList(), MappedTo=item)
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcIndexedColourMap")) == 0
        assert len(self.file.by_type("IfcColourRgbList")) == 0

    def test_purging_texture_coordinates(self):
        item = self.file.createIfcTriangulatedFaceSet()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        image = self.file.createIfcImageTexture()
        texture = self.file.createIfcIndexedTriangleTextureMap(
            TexCoords=self.file.createIfcTextureVertexList(), MappedTo=item, Maps=[image]
        )
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcIndexedTriangleTextureMap")) == 0
        assert len(self.file.by_type("IfcTextureVertexList")) == 0
        assert len(self.file.by_type("IfcImageTexture")) == 0

    def test_purging_texture_coordinates_but_not_images_used_in_other_styles(self):
        item = self.file.createIfcTriangulatedFaceSet()
        representation = self.file.createIfcShapeRepresentation(Items=[item])
        image = self.file.createIfcImageTexture()
        texture = self.file.createIfcIndexedTriangleTextureMap(
            TexCoords=self.file.createIfcTextureVertexList(), MappedTo=item, Maps=[image]
        )
        texture2 = self.file.createIfcIndexedTriangleTextureMap(Maps=[image])
        ifcopenshell.api.run("geometry.remove_representation", self.file, representation=representation)
        assert len(self.file.by_type("IfcIndexedTriangleTextureMap")) == 1
        assert len(self.file.by_type("IfcTextureVertexList")) == 0
        assert len(self.file.by_type("IfcImageTexture")) == 1
