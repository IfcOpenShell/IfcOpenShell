# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.resource
import ifcopenshell.api.root
import test.bootstrap


class TestAssignResource(test.bootstrap.IFC4):
    def test_run(self):
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        product = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingElementProxy")

        rel = ifcopenshell.api.resource.assign_resource(
            self.file, relating_resource=resource, related_object=product
        )
        assert rel.is_a("IfcRelAssignsToResource")
        assert rel.RelatingResource == resource
        assert list(rel.RelatedObjects) == [product]

    def test_assigning_twice_does_not_duplicate_the_related_object(self):
        # Regression test for #8203: the duplicate-assignment guard checked for
        # a misspelled class "IfclRelAssignsToResource", so it never matched and
        # the same object was appended to RelatedObjects a second time.
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        product = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuildingElementProxy")

        rel1 = ifcopenshell.api.resource.assign_resource(
            self.file, relating_resource=resource, related_object=product
        )
        rel2 = ifcopenshell.api.resource.assign_resource(
            self.file, relating_resource=resource, related_object=product
        )

        assert rel1 == rel2
        assert len(self.file.by_type("IfcRelAssignsToResource")) == 1
        assert list(rel2.RelatedObjects) == [product]


class TestAssignResourceIFC2X3(test.bootstrap.IFC2X3, TestAssignResource):
    pass


class TestAssignResourceIFC4X3(test.bootstrap.IFC4X3, TestAssignResource):
    pass
