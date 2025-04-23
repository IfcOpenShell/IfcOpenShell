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
from typing import Union


# NOTE: supported only in IFC4+
class TestUnassignDeclaration(test.bootstrap.IFC4):
    def get_context(self, definition: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        rel = next(iter(definition.HasContext), None)
        if rel is not None:
            return rel.RelatingContext

    def test_unassigning_a_definition(self):
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.project.assign_declaration(
            self.file, definitions=[element_type, element_type2], relating_context=library
        )
        ifcopenshell.api.project.unassign_declaration(
            self.file,
            definitions=[element_type, element_type2],
            relating_context=library,
        )
        assert self.get_context(element_type) == None
        assert len(self.file.by_type("IfcRelDeclares")) == 0

    def test_doing_nothing_if_there_was_no_declaration(self):
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        element_type = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.project.unassign_declaration(
            self.file,
            definitions=[element_type, element_type2],
            relating_context=library,
        )
        assert self.get_context(element_type) == None
        assert self.get_context(element_type2) == None

    def test_updating_the_rel_when_a_reference_is_removed_with_multipled_elements(self):
        library = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProjectLibrary")
        element_type1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        element_type3 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWallType")
        ifcopenshell.api.project.assign_declaration(self.file, definitions=[element_type1], relating_context=library)
        rel = self.file.by_type("IfcRelDeclares")[0]

        ifcopenshell.api.project.assign_declaration(
            self.file,
            definitions=[element_type2, element_type3],
            relating_context=library,
        )
        ifcopenshell.api.project.unassign_declaration(
            self.file,
            definitions=[element_type1, element_type2],
            relating_context=library,
        )
        assert rel.RelatedDefinitions == (element_type3,)
