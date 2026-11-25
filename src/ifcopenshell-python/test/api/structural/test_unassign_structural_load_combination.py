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
import ifcopenshell.util.structural
import test.bootstrap


class FactorGroups:
    """RFEM's load combinations in IFC4: each factor a load group of type LOAD_GROUP, its Coefficient the factor"""

    def add_group(self, predefined_type, name=None, coefficient=None):
        return self.file.createIfcStructuralLoadGroup(
            ifcopenshell.guid.new(),
            Name=name,
            PredefinedType=predefined_type,
            ActionType="NOTDEFINED",
            ActionSource="NOTDEFINED",
            Coefficient=coefficient,
        )

    def group(self, products, group):
        self.file.createIfcRelAssignsToGroup(ifcopenshell.guid.new(), RelatedObjects=products, RelatingGroup=group)

    def setup_rfem(self):
        self.q = self.add_group("LOAD_CASE", "Q")
        self.wx = self.add_group("LOAD_CASE", "Wx")
        self.combination = self.add_group("LOAD_COMBINATION", "Load Combination 1")
        self.q_group = self.add_group("LOAD_GROUP", coefficient=1.5)
        self.wx_group = self.add_group("LOAD_GROUP", coefficient=0.9)
        self.group([self.q], self.q_group)
        self.group([self.wx], self.wx_group)
        self.group([self.q_group, self.wx_group], self.combination)


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


class TestUnassignStructuralLoadCombinationFromFactorGroups(test.bootstrap.IFC4, FactorGroups):
    def test_unassigning_a_load_case_from_its_factor_group(self):
        self.setup_rfem()
        q_group = self.q_group.id()
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination
        )
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.wx: 0.9}
        assert q_group not in [g.id() for g in self.file.by_type("IfcStructuralLoadGroup")]
        assert not self.q.HasAssignments

    def test_a_factor_group_with_other_load_cases_is_kept(self):
        self.setup_rfem()
        self.group([self.wx], self.q_group)
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination
        )
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.wx: 1.5 + 0.9}

    def test_a_factor_group_another_combination_shares_is_kept_there(self):
        self.setup_rfem()
        other = self.add_group("LOAD_COMBINATION", "Load Combination 2")
        self.group([self.q_group], other)
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination
        )
        # The group is emptied of Q, and so is left in neither combination's factors, but it is not removed.
        assert self.q_group in self.file.by_type("IfcStructuralLoadGroup")
        assert self.q_group not in ifcopenshell.util.structural.get_combination_factor_groups(self.combination)
        assert self.q_group in ifcopenshell.util.structural.get_combination_factor_groups(other)

    def test_groups_emptied_within_groups_are_removed(self):
        self.setup_rfem()
        outer = self.add_group("LOAD_GROUP", coefficient=2.0)
        self.group([self.q_group], outer)
        self.group([outer], self.combination)
        ids = {self.q_group.id(), outer.id()}
        ifcopenshell.api.structural.unassign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination
        )
        assert not ids & {g.id() for g in self.file.by_type("IfcStructuralLoadGroup")}
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.wx: 0.9}
