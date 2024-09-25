# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element


class TestTransaction(test.bootstrap.IFC4):
    def test_that_nothing_happens_without_a_transaction(self):
        wall = self.file.createIfcWall()
        self.file.undo()
        assert wall

    def test_that_you_can_undo_and_redo_creation(self):
        unchanged = self.file.createIfcWall()
        self.file.begin_transaction()
        wall = self.file.createIfcWall()
        self.file.end_transaction()
        self.file.undo()
        assert unchanged
        with pytest.raises(RuntimeError):
            self.file.by_id(2)
        self.file.redo()
        self.file.by_id(2)

    def test_that_you_can_undo_and_redo_editing(self):
        element = self.file.createIfcWall(Name="foo")
        self.file.begin_transaction()
        element.Name = "bar"
        self.file.end_transaction()
        self.file.undo()
        assert element.Name == "foo"
        self.file.redo()
        assert element.Name == "bar"

    def test_that_you_can_undo_and_redo_deletion(self):
        element = self.file.createIfcWall(GlobalId="id")
        self.file.begin_transaction()
        self.file.remove(element)
        self.file.end_transaction()
        self.file.undo()
        assert self.file.by_id(1)
        self.file.redo()
        with pytest.raises(RuntimeError):
            self.file.by_id(1)

    def test_that_you_can_undo_and_redo_deletion_with_inverse_relationships(self):
        element = self.file.createIfcWall(GlobalId="id")
        rel = self.file.createIfcRelAggregates()
        rel.RelatingObject = element
        self.file.begin_transaction()
        self.file.remove(element)
        self.file.end_transaction()
        self.file.undo()
        assert rel.RelatingObject == self.file.by_id(1)
        self.file.redo()
        assert rel.RelatingObject is None

    def test_that_you_can_undo_and_redo_batched_deletion_with_inverse_relationships(self):
        element = self.file.createIfcWall(GlobalId="id")
        rel = self.file.createIfcRelAggregates()
        rel.RelatingObject = element
        self.file.begin_transaction()
        self.file.batch()
        self.file.remove(element)
        self.file.unbatch()
        self.file.end_transaction()
        self.file.undo()
        assert rel.RelatingObject == self.file.by_id(1)
        self.file.redo()
        assert rel.RelatingObject is None

    def test_that_you_can_undo_and_redo_deletion_with_aggregated_inverse_relationships(self):
        element = self.file.createIfcWall(GlobalId="id")
        rel = self.file.createIfcRelAggregates()
        rel.RelatedObjects = [element]
        self.file.begin_transaction()
        self.file.remove(element)
        self.file.end_transaction()
        self.file.undo()
        assert rel.RelatedObjects == (self.file.by_id(1),)
        self.file.redo()
        assert len(rel.RelatedObjects) == 0

    def test_the_editing_of_invalid_default_values(self):
        element = self.file.createIfcWall()  # This element is invalid, as GlobalId is None
        self.file.begin_transaction()
        element.GlobalId = "id"
        self.file.end_transaction()
        self.file.undo()

    def test_setting_the_history_size(self):
        self.file.set_history_size(2)
        self.file.begin_transaction()
        self.file.end_transaction()
        self.file.begin_transaction()
        self.file.end_transaction()
        self.file.begin_transaction()
        self.file.end_transaction()
        assert len(self.file.history) == 2
        self.file.set_history_size(1)
        assert len(self.file.history) == 1

    def test_discarding_the_active_transaction(self):
        self.file.begin_transaction()
        self.file.discard_transaction()
        self.file.end_transaction()
        assert len(self.file.history) == 0

    def test_redoing_without_anything_in_the_redo_stack(self):
        self.file.redo()

    def test_that_you_can_undo_and_redo_added_elements(self):
        g = ifcopenshell.file()
        element = g.createIfcWall()
        self.file.begin_transaction()
        self.file.add(element)
        self.file.end_transaction()
        self.file.undo()
        assert len(list(self.file)) == 0
        self.file.redo()
        assert len(list(self.file)) == 1

    def test_that_you_can_undo_and_redo_added_subelements(self):
        g = ifcopenshell.file()
        owner = g.createIfcOwnerHistory()
        element = g.createIfcWall(OwnerHistory=owner)
        self.file.begin_transaction()
        self.file.add(element)
        self.file.end_transaction()
        self.file.undo()
        assert len(list(self.file)) == 0
        self.file.redo()
        assert len(list(self.file)) == 2


class TestFile(test.bootstrap.IFC4):
    def test_creating_a_new_file(self):
        f = ifcopenshell.file(schema="IFC4")
        assert f.schema == "IFC4"
        assert f.schema_identifier == "IFC4"
        assert f.schema_version == (4, 0, 0, 0)

    def test_creating_an_ifc4x3_file(self):
        f = ifcopenshell.file(schema="IFC4X3")
        assert f.schema == "IFC4X3"
        assert f.schema_identifier == "IFC4X3_ADD2"
        assert f.schema_version == (4, 3, 2, 0)

    def test_creating_a_specific_version(self):
        f = ifcopenshell.file(schema_version=(4, 3, 2, 0))
        assert f.schema == "IFC4X3"
        assert f.schema_identifier == "IFC4X3_ADD2"
        assert f.schema_version == (4, 3, 2, 0)

    def test_creating_an_entity(self):
        element = self.file.create_entity("IfcPerson")
        assert element.is_a("IfcPerson")
        element = self.file.create_entity("IfcPerson", "identification")
        assert element.Identification == "identification"
        element = self.file.create_entity("IfcPerson", Identification="identification")
        assert element.Identification == "identification"
        element = self.file.create_entity("IfcPerson", Identification="identification", id=42)
        assert element.id() == 42
        element = self.file.createIfcPerson()
        assert element.is_a("IfcPerson")

    def test_getting_an_element_by_id(self):
        element = self.file.createIfcWall("id")
        assert self.file.by_id(1) == element
        assert self.file.by_id("id") == element

    def test_getting_an_element_by_guid(self):
        element = self.file.createIfcWall("id")
        assert self.file.by_guid(1) == element
        assert self.file.by_guid("id") == element

    def test_adding_an_element(self):
        g = ifcopenshell.file()
        element = g.createIfcWall()
        result = self.file.add(element)
        assert result.is_a() == element.is_a()

    def test_getting_elements_by_type(self):
        wall = self.file.createIfcWall()
        slab = self.file.createIfcSlab()
        assert self.file.by_type("IfcWall") == [wall]

    def test_getting_elements_by_exact_type(self):
        wall = self.file.createIfcWall()
        assert self.file.by_type("IfcElement") == [wall]
        assert len(self.file.by_type("IfcElement", include_subtypes=False)) == 0

    def test_traversing_direct_attributes_of_an_element(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(OwnerHistory=owner)
        assert self.file.traverse(element) == [element, owner]

    def test_traversing_direct_attributes_of_an_element_to_a_limited_level(self):
        app = self.file.createIfcApplication()
        owner = self.file.createIfcOwnerHistory(OwningApplication=app)
        element = self.file.createIfcWall(OwnerHistory=owner)
        assert self.file.traverse(element, max_levels=1) == [element, owner]

    def test_getting_inverse_references_of_an_element(self):
        owner = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(OwnerHistory=owner)
        assert self.file.get_inverse(owner) == {element}

    def test_getting_multiple_inverses_if_an_element_is_referenced_twice_by_the_same_element(self):
        user = self.file.createIfcPersonAndOrganization()
        owner = self.file.createIfcOwnerHistory(OwningUser=user, LastModifyingUser=user)
        assert self.file.get_inverse(user, allow_duplicate=True) == [owner, owner]

    def test_removing_an_element(self):
        element = self.file.createIfcWall(GlobalId="global_id")
        self.file.remove(element)
        assert len(list(self.file)) == 0

    def test_removing_an_element_and_its_references_are_cleared(self):
        history = self.file.createIfcOwnerHistory()
        element = self.file.createIfcWall(GlobalId="global_id", OwnerHistory=history)
        self.file.remove(history)
        assert element.OwnerHistory is None

    def test_removing_an_element_and_its_references_are_cleared_regardless_of_cardinality(self):
        wall = self.file.createIfcWall(GlobalId="global_id")
        rel = self.file.createIfcRelAggregates(RelatingObject=wall)
        self.file.remove(wall)
        assert rel.RelatingObject == None

    def test_removing_an_element_and_its_aggregate_references_are_modified(self):
        person = self.file.createIfcPerson()
        role = self.file.createIfcActorRole()
        role2 = self.file.createIfcActorRole()
        person.Roles = [role, role2]
        self.file.remove(role)
        assert person.Roles == (role2,)

    def test_removing_an_element_and_optional_empty_aggregate_references_are_set_to_null(self):
        person = self.file.createIfcPerson()
        role = self.file.createIfcActorRole()
        person.Roles = [role]
        self.file.remove(role)
        assert person.Roles is None

    def test_removing_an_element_and_mandatory_empty_aggregate_references_remain_regardless_of_cardinality(self):
        wall = self.file.createIfcWall(GlobalId="global_id")
        rel = self.file.createIfcRelAggregates(RelatedObjects=[wall])
        self.file.remove(wall)
        assert rel.RelatedObjects == tuple()

    def test_batched_removing_an_element(self):
        element = self.file.createIfcWall(GlobalId="global_id")
        self.file.batch()
        self.file.remove(element)
        self.file.unbatch()
        assert len(list(self.file)) == 0

    def test_creating_ifc_data_from_a_string(self):
        element = self.file.createIfcWall()
        g = ifcopenshell.file.from_string(self.file.wrapped_data.to_string())
        assert g.by_id(1).is_a("IfcWall")

    def test_assigning_header(self):
        f = ifcopenshell.file(schema="IFC4")
        f.header.file_name.name = "test"
        g = ifcopenshell.file(schema="IFC4")
        g.assign_header_from(f)
        assert g.header.file_name.name == "test"
