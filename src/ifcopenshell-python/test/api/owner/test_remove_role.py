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
import ifcopenshell.api.owner


class TestRemoveRoleIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_a_role(self):
        role = self.file.createIfcActorRole()
        ifcopenshell.api.owner.remove_role(self.file, role=role)
        assert len(self.file.by_type("IfcActorRole")) == 0

    def test_ensuring_organisation_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        organisation = self.file.createIfcOrganization()
        organisation.Roles = [role]
        ifcopenshell.api.owner.remove_role(self.file, role=role)
        assert organisation.Roles is None

    def test_ensuring_person_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        person = self.file.createIfcPerson()
        person.Roles = [role]
        ifcopenshell.api.owner.remove_role(self.file, role=role)
        assert person.Roles is None

    def test_ensuring_person_and_organisation_cardinality_is_valid(self):
        role = self.file.createIfcActorRole()
        person_and_organisation = self.file.createIfcPersonAndOrganization()
        person_and_organisation.Roles = [role]
        ifcopenshell.api.owner.remove_role(self.file, role=role)
        assert person_and_organisation.Roles is None


class TestRemoveRoleIFC4(test.bootstrap.IFC4, TestRemoveRoleIFC2X3):
    def test_deleting_resource_approval_relationships(self):
        organisation = self.file.create_entity("IfcOrganization")
        self.file.create_entity("IfcResourceApprovalRelationship", RelatedResourceObjects=[organisation])
        ifcopenshell.api.owner.remove_organisation(self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        organisation = self.file.create_entity("IfcOrganization")
        self.file.create_entity("IfcResourceConstraintRelationship", RelatedResourceObjects=[organisation])
        ifcopenshell.api.owner.remove_organisation(self.file, organisation=organisation)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        organisation = self.file.create_entity("IfcOrganization")
        self.file.create_entity("IfcExternalReferenceRelationship", RelatedResourceObjects=[organisation])
        ifcopenshell.api.owner.remove_organisation(self.file, organisation=organisation)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0
