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
import ifcopenshell.api.root
import ifcopenshell.util.element


class TestReassignClass(test.bootstrap.IFC4):
    def test_reassigning_a_simple_class(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        n_elements = len([e for e in self.file])
        original_id = element.id()
        new = ifcopenshell.api.root.reassign_class(self.file, product=element, ifc_class="IfcSlab")
        assert len([e for e in self.file]) == n_elements
        assert new.id() == original_id
        assert new.is_a("IfcSlab")

    def test_reassigning_a_predefined_type(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.root.reassign_class(
            self.file, product=element, ifc_class="IfcSlab", predefined_type="FLOOR"
        )
        assert new.PredefinedType == "FLOOR"

    def test_falling_back_to_userdefined_if_the_predefined_type_cannot_be_reassigned_for_occurrence_class(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        new = ifcopenshell.api.root.reassign_class(
            self.file, product=element, ifc_class="IfcSlab", predefined_type="FOO"
        )
        assert new.PredefinedType == "USERDEFINED"
        assert new.ObjectType == "FOO"

    def test_falling_back_to_userdefined_if_the_predefined_type_cannot_be_reassigned_for_type_class(self):
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        new = ifcopenshell.api.root.reassign_class(
            self.file, product=element, ifc_class="IfcSlabType", predefined_type="FOO"
        )
        assert new.PredefinedType == "USERDEFINED"
        assert new.ElementType == "FOO"

    def test_reassign_class_for_type_occurrences(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type)
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type)

        element_type = ifcopenshell.api.root.reassign_class(self.file, product=element_type, ifc_class="IfcSlabType")

        # type occurrences have reassigned classes
        occurrences = ifcopenshell.util.element.get_types(element_type)
        assert len(occurrences) == 2
        assert all(o.is_a("IfcSlab") for o in occurrences)

        # original clases are gone
        assert len(self.file.by_type("IfcWall")) == 0
        assert len(self.file.by_type("IfcWallType")) == 0

    def test_reassigning_type_class_and_its_occurrences_classes_if_entity_was_typed(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element1], relating_type=element_type)
        element2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.type.assign_type(self.file, related_objects=[element2], relating_type=element_type)

        element1 = ifcopenshell.api.root.reassign_class(self.file, product=element1, ifc_class="IfcSlab")

        # occurrence type has reassigned class
        element_type = ifcopenshell.util.element.get_type(element1)
        assert element_type.is_a("IfcSlabType")

        # other type occurrences have reassigned classes
        occurrences = ifcopenshell.util.element.get_types(element_type)
        assert len(occurrences) == 2
        assert all(o.is_a("IfcSlab") for o in occurrences)

        # original clases are gone
        assert len(self.file.by_type("IfcWall")) == 0
        assert len(self.file.by_type("IfcWallType")) == 0


class TestReassignClassIFC2X3(test.bootstrap.IFC2X3, TestReassignClass):
    pass
