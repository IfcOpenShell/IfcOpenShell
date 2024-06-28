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

import pytest
import test.bootstrap
import ifcopenshell.api.owner
import ifcopenshell.guid


class TestRemovePersonIFC2X3(test.bootstrap.IFC2X3):
    def test_removing_a_person(self):
        person = self.file.createIfcPerson()
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcPerson")) == 0

    def test_removing_roles_and_addresses_only_used_by_the_person(self):
        role = self.file.createIfcActorRole()
        address = self.file.createIfcPostalAddress()
        person = self.file.createIfcPerson()
        person.Roles = [role]
        person.Addresses = [address]
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcPerson")) == 0
        assert len(self.file.by_type("IfcActorRole")) == 0
        assert len(self.file.by_type("IfcPostalAddress")) == 0

    def test_not_removing_roles_and_addresses_used_elsewhere(self):
        role = self.file.createIfcActorRole()
        address = self.file.createIfcPostalAddress()
        person = self.file.createIfcPerson()
        person2 = self.file.createIfcPerson()
        person.Roles = [role]
        person.Addresses = [address]
        person2.Roles = [role]
        person2.Addresses = [address]
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcPerson")) == 1
        assert len(self.file.by_type("IfcActorRole")) == 1
        assert len(self.file.by_type("IfcPostalAddress")) == 1

    def test_ensuring_work_controls_should_not_be_left_in_an_invalid_set_cardinality(self):
        person = self.file.createIfcPerson()
        work_control = self.file.createIfcWorkControl(Creators=[person])
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert work_control.Creators is None

    def test_ensuring_inventory_should_not_be_left_in_an_invalid_set_cardinality(self):
        person = self.file.createIfcPerson()
        inventory = self.file.createIfcInventory(ResponsiblePersons=[person])
        inventory_id = inventory.id()
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        if self.file.schema != "IFC2X3":
            assert inventory.ResponsiblePersons is None
        else:
            with pytest.raises(RuntimeError):
                self.file.by_id(inventory_id)

    def test_deleting_person_and_organisations(self):
        person = self.file.createIfcPerson()
        self.file.createIfcPersonAndOrganization(ThePerson=person)
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcPersonAndOrganization")) == 0

    def test_deleting_actors(self):
        person = self.file.createIfcPerson()
        self.file.createIfcActor(GlobalId=ifcopenshell.guid.new(), TheActor=person)
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcActor")) == 0

    def test_ensuring_document_information_should_not_be_left_in_an_invalid_set_cardinality(self):
        person = self.file.createIfcPerson()
        document_information = self.file.createIfcDocumentInformation(Editors=[person])
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert document_information.Editors is None


class TestRemovePersonIFC4(test.bootstrap.IFC4, TestRemovePersonIFC2X3):
    # IfcResourceLevelRelationships were added in IFC4
    def test_deleting_resource_approval_relationships(self):
        person = self.file.create_entity("IfcPerson")
        self.file.create_entity("IfcResourceApprovalRelationship", RelatedResourceObjects=[person])
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcResourceApprovalRelationship")) == 0

    def test_deleting_resource_constraint_relationships(self):
        person = self.file.create_entity("IfcPerson")
        self.file.create_entity("IfcResourceConstraintRelationship", RelatedResourceObjects=[person])
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcResourceConstraintRelationship")) == 0

    def test_deleting_external_reference_relationships(self):
        person = self.file.create_entity("IfcPerson")
        self.file.create_entity("IfcExternalReferenceRelationship", RelatedResourceObjects=[person])
        ifcopenshell.api.owner.remove_person(self.file, person=person)
        assert len(self.file.by_type("IfcExternalReferenceRelationship")) == 0
