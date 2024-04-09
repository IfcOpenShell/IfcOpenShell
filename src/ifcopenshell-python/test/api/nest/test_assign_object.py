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
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.placement


class TestAssignObject(test.bootstrap.IFC4):
    def test_assigning_a_nesting(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        rel = ifcopenshell.api.run(
            "nest.assign_object", self.file, related_objects=[subelement1, subelement2], relating_object=element
        )
        assert ifcopenshell.util.element.get_nest(subelement1) == element
        assert ifcopenshell.util.element.get_nest(subelement2) == element
        assert rel.is_a("IfcRelNests")

    def test_doing_nothing_if_the_nesting_is_already_assigned(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement], relating_object=element)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement], relating_object=element)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_nesting_relationships_are_updated_if_they_still_have_elements(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        ifcopenshell.api.run(
            "nest.assign_object", self.file, related_objects=[subelement1, subelement2], relating_object=element1
        )
        rel = subelement1.Nests[0]
        assert len(rel.RelatedObjects) == 2
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement1], relating_object=element2)
        assert len(rel.RelatedObjects) == 1

    def test_that_old_nesting_relationships_are_purged_if_no_more_elements_are_nested(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        element2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcSanitaryTerminal")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcValve")
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement1], relating_object=element1)
        rel_id = subelement1.Nests[0].id()
        ifcopenshell.api.run("nest.assign_object", self.file, related_objects=[subelement1], relating_object=element2)
        with pytest.raises(RuntimeError):
            self.file.by_id(rel_id)
