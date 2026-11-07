# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.structural
import ifcopenshell.guid
import test.bootstrap


class TestRemoveStructuralLoadGroup(test.bootstrap.IFC4):
    def test_removing_a_load_combination_of_several_load_cases(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        uls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=dead, load_combination=uls, factor=1.5
        )
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=live, load_combination=uls, factor=1.5
        )
        ifcopenshell.api.structural.remove_structural_load_group(self.file, load_group=uls)
        assert not self.file.by_type("IfcStructuralLoadGroup", include_subtypes=False)
        assert not self.file.by_type("IfcRelAssignsToGroup")
        assert set(self.file.by_type("IfcStructuralLoadCase")) == {dead, live}

    def test_removing_a_load_group_from_a_load_case_with_other_groups(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        slab = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        wall = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Wall")
        rel = self.file.createIfcRelAssignsToGroup(
            ifcopenshell.guid.new(), RelatedObjects=[slab, wall], RelatingGroup=dead
        )
        ifcopenshell.api.structural.remove_structural_load_group(self.file, load_group=slab)
        assert rel.RelatedObjects == (wall,)
        assert rel.RelatingGroup == dead


class TestRemoveStructuralLoadGroupIFC4X3(test.bootstrap.IFC4X3, TestRemoveStructuralLoadGroup):
    pass
