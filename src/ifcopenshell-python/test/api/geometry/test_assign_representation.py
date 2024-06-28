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
import ifcopenshell.api.type
import ifcopenshell.api.root
import ifcopenshell.api.geometry


class TestAssignRepresentation(test.bootstrap.IFC4):
    def test_assigning_to_a_product(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rep = self.file.createIfcShapeRepresentation()
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep)
        assert wall.Representation.Representations == (rep,)

    def test_assigning_to_a_product_with_existing_representations(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rep = self.file.createIfcShapeRepresentation()
        rep2 = self.file.createIfcShapeRepresentation()
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep)
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep2)
        assert wall.Representation.Representations == (rep, rep2)

    def test_assigning_to_a_type_product(self):
        walltype = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        rep = self.file.createIfcShapeRepresentation()
        rep2 = self.file.createIfcShapeRepresentation()
        ifcopenshell.api.geometry.assign_representation(self.file, product=walltype, representation=rep)
        ifcopenshell.api.geometry.assign_representation(self.file, product=walltype, representation=rep2)
        assert walltype.RepresentationMaps[0].MappedRepresentation == rep
        assert walltype.RepresentationMaps[1].MappedRepresentation == rep2

    def test_assigning_to_a_type_will_map_representations_to_instances(self):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        walltype = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[wall], relating_type=walltype)
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        rep2 = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=walltype, representation=rep)
        ifcopenshell.api.geometry.assign_representation(self.file, product=walltype, representation=rep2)
        assert wall.Representation.Representations[0].RepresentationType == "MappedRepresentation"
        assert wall.Representation.Representations[0].Items[0].MappingSource.MappedRepresentation == rep
        assert wall.Representation.Representations[0].Items[0].MappingSource == walltype.RepresentationMaps[0]
        assert wall.Representation.Representations[1].RepresentationType == "MappedRepresentation"
        assert wall.Representation.Representations[1].Items[0].MappingSource.MappedRepresentation == rep2
        assert wall.Representation.Representations[1].Items[0].MappingSource == walltype.RepresentationMaps[1]

    def test_assigning_to_an_instance_with_a_geometric_type_adds_it_to_both_the_instance_and_type(self):
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        rep2 = self.file.createIfcShapeRepresentation(ContextOfItems=context)

        walltype = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.geometry.assign_representation(self.file, product=walltype, representation=rep)

        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[wall], relating_type=walltype)

        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep2)
        assert wall.Representation.Representations[0].RepresentationType == "MappedRepresentation"
        assert wall.Representation.Representations[0].Items[0].MappingSource.MappedRepresentation == rep
        assert walltype.RepresentationMaps[0].MappedRepresentation == rep
        assert wall.Representation.Representations[1].RepresentationType == "MappedRepresentation"
        assert wall.Representation.Representations[1].Items[0].MappingSource.MappedRepresentation == rep2
        assert walltype.RepresentationMaps[1].MappedRepresentation == rep2

    def test_assigning_to_an_instance_with_a_nongeometric_type_only_adds_it_to_the_instance(self):
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        walltype = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[wall], relating_type=walltype)
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=rep)
        assert wall.Representation.Representations[0].RepresentationType != "MappedRepresentation"
        assert wall.Representation.Representations[0] == rep
        assert not walltype.RepresentationMaps


class TestAssignRepresentationIFC2X3(test.bootstrap.IFC2X3, TestAssignRepresentation):
    pass
