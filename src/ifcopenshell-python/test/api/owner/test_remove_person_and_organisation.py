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
import ifcopenshell.guid


class TestRemovePersonAndOrganisation(test.bootstrap.IFC4):
    def test_removing(self):
        user = self.file.createIfcPersonAndOrganization()
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcPersonAndOrganization")) == 0

    def test_deleting_actors(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcActor(GlobalId=ifcopenshell.guid.new(), TheActor=user)
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcActor")) == 0

    def test_ensuring_document_information_should_not_be_left_in_an_invalid_set_cardinality(self):
        user = self.file.createIfcPersonAndOrganization()
        document_information = self.file.createIfcDocumentInformation(Editors=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert document_information.Editors is None

    def test_deleting_resource_approval_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcResourceApprovalRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcResourceConstraintRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcExternalReferenceRelationship(RelatedResourceObjects=[user])
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0

    def test_deleting_owner_history(self):
        user = self.file.createIfcPersonAndOrganization()
        self.file.createIfcOwnerHistory(OwningUser=user)
        ifcopenshell.api.run("owner.remove_person_and_organisation", self.file, person_and_organisation=user)
        assert len(self.file.by_type("IfcOwnerHistory")) == 0
