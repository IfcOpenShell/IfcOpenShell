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
import test.bootstrap


class TestUnassignStructuralLoadCombination(test.bootstrap.IFC4):
    def setup_cases(self):
        self.dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        self.live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        self.uls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")

    def test_unassigning_the_only_load_case_of_a_relationship(self):
        self.setup_cases()
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls
        )
        assert not self.file.by_type("IfcRelAssignsToGroupByFactor")
        assert not self.uls.IsGroupedBy

    def test_unassigning_a_load_case_that_shares_a_relationship(self):
        self.setup_cases()
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.5
        )
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls, factor=1.5
        )
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls
        )
        assert rel.RelatedObjects == (self.live,)

    def test_unassigning_a_load_case_from_one_combination_only(self):
        self.setup_cases()
        sls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="SLS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        sls_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=sls
        )
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls
        )
        assert self.dead.HasAssignments == (sls_rel,)

    def test_unassigning_a_load_case_not_in_the_combination_does_nothing(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls
        )
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls
        )
        assert rel.RelatedObjects == (self.live,)


class TestUnassignStructuralLoadCombinationIFC4X3(test.bootstrap.IFC4X3, TestUnassignStructuralLoadCombination):
    pass
