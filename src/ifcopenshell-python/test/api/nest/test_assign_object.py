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
import ifcopenshell.api.nest
import ifcopenshell.api.root
import ifcopenshell.util.element
import ifcopenshell.util.placement


class TestAssignObject(test.bootstrap.IFC4):
    def test_assigning_a_nesting(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        rel = ifcopenshell.api.nest.assign_object(
            self.file, related_objects=[subelement1, subelement2], relating_object=element
        )
        assert ifcopenshell.util.element.get_nest(subelement1) == element
        assert ifcopenshell.util.element.get_nest(subelement2) == element
        assert rel.is_a("IfcRelNests")

    def test_doing_nothing_if_the_nesting_is_already_assigned(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement], relating_object=element)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement], relating_object=element)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_nesting_relationships_are_updated_if_they_still_have_elements(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(
            self.file, related_objects=[subelement1, subelement2], relating_object=element1
        )
        rel = subelement1.Decomposes[0] if self.file.schema == "IFC2X3" else subelement1.Nests[0]
        assert len(rel.RelatedObjects) == 2
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement1], relating_object=element2)
        assert len(rel.RelatedObjects) == 1

    def test_that_old_nesting_relationships_are_purged_if_no_more_elements_are_nested(self):
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelement1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement1], relating_object=element1)
        rel_id = (subelement1.Decomposes[0] if self.file.schema == "IFC2X3" else subelement1.Nests[0]).id()
        ifcopenshell.api.nest.assign_object(self.file, related_objects=[subelement1], relating_object=element2)
        with pytest.raises(RuntimeError):
            self.file.by_id(rel_id)

    def test_maintain_assignment_order_in_related_objects(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        subelements = [ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask") for _ in range(5)]
        for i in range(5):
            ifcopenshell.api.nest.assign_object(
                self.file, related_objects=subelements[: i + 1], relating_object=element
            )
            rel = self.file.by_type("IfcRelNests")[0]
            assert rel.RelatedObjects == tuple(subelements[: i + 1])

        # maintain the order in the affected relationships too
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        ifcopenshell.api.nest.assign_object(self.file, related_objects=subelements[2:3], relating_object=element2)
        assert rel.RelatedObjects == tuple(subelements[:2] + subelements[3:])


class TestAssignObjectIFC2X3(test.bootstrap.IFC2X3, TestAssignObject):
    pass
