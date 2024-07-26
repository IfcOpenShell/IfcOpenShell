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
import ifcopenshell.api.root
import ifcopenshell.api.type
import ifcopenshell.api.material
import ifcopenshell.api.geometry
import ifcopenshell.util.element


class TestUnassignType(test.bootstrap.IFC4):
    def test_unassigning_a_type(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1, element2], relating_type=element_type)
        ifcopenshell.api.type.unassign_type(self.file, related_objects=[element1, element2])
        assert ifcopenshell.util.element.get_type(element1) is None
        assert ifcopenshell.util.element.get_type(element2) is None

    def test_the_rel_is_kept_if_there_are_more_typed_elements(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type)
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type)
        ifcopenshell.api.type.unassign_type(self.file, related_objects=[element1])
        assert len(self.file.by_type("IfcRelDefinesByType")) == 1

    def test_the_rel_is_purged_if_there_are_no_more_typed_elements(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        context = self.file.createIfcGeometricRepresentationContext()
        rep = self.file.createIfcShapeRepresentation(ContextOfItems=context)
        ifcopenshell.api.geometry.assign_representation(self.file, product=element_type, representation=rep)
        ifcopenshell.api.material.assign_material(self.file, products=[element_type], type="IfcMaterialLayerSet")

        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element], relating_type=element_type)
        ifcopenshell.api.type.unassign_type(self.file, related_objects=[element])
        assert len(self.file.by_type("IfcRelDefinesByType")) == 0


class TestUnassignTypeIFC2X3(test.bootstrap.IFC2X3, TestUnassignType):
    pass
