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
    def test_assigning_a_new_object_to_a_resource(self):
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        actor = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcActor")
        rel = ifcopenshell.api.resource.assign_resource(self.file, relating_resource=resource, related_object=actor)
        assert rel.is_a("IfcRelAssignsToResource")
        assert rel.RelatingResource == resource
        assert rel.RelatedObjects == (actor,)

    def test_assigning_the_same_object_twice_does_not_duplicate_related_objects(self):
        # Regression test for #8203: a typo in the duplicate guard
        # ("IfclRelAssignsToResource") meant the guard never matched, so a
        # repeat assignment appended the related object to RelatedObjects again.
        self.file.create_entity("IfcProject")
        resource = ifcopenshell.api.resource.add_resource(self.file, ifc_class="IfcCrewResource")
        actor = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcActor")
        rel1 = ifcopenshell.api.resource.assign_resource(self.file, relating_resource=resource, related_object=actor)
        rel2 = ifcopenshell.api.resource.assign_resource(self.file, relating_resource=resource, related_object=actor)
        assert rel1 == rel2
        assert len(self.file.by_type("IfcRelAssignsToResource")) == 1
        assert rel2.RelatedObjects == (actor,)
