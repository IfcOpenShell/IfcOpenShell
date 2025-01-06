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
import ifcopenshell.api.root
import ifcopenshell.api.project


# NOTE: supported only in IFC4+
class TestAssignDeclaration(test.bootstrap.IFC4):
    def get_declared_definitions(self, project: ifcopenshell.entity_instance) -> set[ifcopenshell.entity_instance]:
        definitions = set()
        for declares in project.Declares:
            definitions.update(declares.RelatedDefinitions)
        return definitions

    def test_assign_a_declaration(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        ifcopenshell.api.project.assign_declaration(
            self.file,
            definitions=[element_type, element_type2],
            relating_context=library,
        )
        assert self.get_declared_definitions(library) == {element_type, element_type2}
        assert len(self.file.by_type("IfcRelDeclares")) == 1

    def test_doing_nothing_if_the_library_is_already_assigned(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        ifcopenshell.api.project.assign_declaration(
            self.file, definitions=[element_type, element_type2], relating_context=library
        )
        total_elements = len([e for e in self.file])
        ifcopenshell.api.project.assign_declaration(
            self.file, definitions=[element_type, element_type2], relating_context=library
        )
        assert len([e for e in self.file]) == total_elements

    def test_that_old_relationships_are_updated_if_they_still_contain_elements(self):
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        ifcopenshell.api.project.assign_declaration(self.file, definitions=[element_type], relating_context=library)
        rel = self.file.by_type("IfcRelDeclares")[0]

        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.project.assign_declaration(
            self.file, definitions=[element_type2, element_type3], relating_context=library
        )
        assert len(rel.RelatedDefinitions) == 3
