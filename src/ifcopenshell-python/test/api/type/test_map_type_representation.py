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
import ifcopenshell.api.type


class TestMapTypeRepresentations(test.bootstrap.IFC4):
    def test_doing_nothing_if_the_type_has_no_representation_maps(self):
        element = self.file.createIfcWall()
        type = self.file.createIfcWallType()
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=type)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.type.map_type_representations(self.file, related_object=element, relating_type=type)
        assert len([e for e in self.file]) == total_elements

    def test_removing_existing_element_representations_and_mapping_type_representations(self):
        context = self.file.createIfcGeometricRepresentationSubContext()
        element = self.file.createIfcWall(
            Representation=self.file.create_entity(
                "IfcProductDefinitionShape",
                Representations=[self.file.createIfcShapeRepresentation(ContextOfItems=context)],
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
        ifcopenshell.api.type.map_type_representations(self.file, related_object=element, relating_type=type)
        rep = element.Representation.Representations[0]
        assert rep.RepresentationType == "MappedRepresentation"
        assert rep.Items[0].MappingSource == type.RepresentationMaps[0]
        assert len(self.file.by_type("IfcShapeRepresentation")) == 2


class TestMapTypeRepresentationsIFC2X3(test.bootstrap.IFC2X3, TestMapTypeRepresentations):
    pass
