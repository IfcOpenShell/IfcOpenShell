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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestAssignProduct(test.bootstrap.IFC4):
    def test_creating_a_new_relationship(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceMember")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=wall)
        assert rel.is_a("IfcRelAssignsToProduct")
        assert rel.RelatingProduct == member
        assert wall in rel.RelatedObjects

    def test_adding_a_second_object_to_an_existing_relationship(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceMember")
        wall1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        wall2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        rel1 = ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=wall1)
        rel2 = ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=wall2)
        assert rel1 == rel2
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 1
        assert wall1 in rel1.RelatedObjects
        assert wall2 in rel1.RelatedObjects

    def test_does_not_duplicate_an_existing_assignment(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralSurfaceMember")
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=wall)
        ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=wall)
        assert len(self.file.by_type("IfcRelAssignsToProduct")) == 1
        rels = self.file.by_type("IfcRelAssignsToProduct")
        assert len(rels[0].RelatedObjects) == 1


class TestAssignProductIFC2X3(test.bootstrap.IFC2X3, TestAssignProduct):
    pass
