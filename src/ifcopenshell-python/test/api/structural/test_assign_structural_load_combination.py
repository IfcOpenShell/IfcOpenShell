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

import pytest

import ifcopenshell.api.group
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


class TestAssignStructuralLoadCombination(test.bootstrap.IFC4):
    def setup_cases(self):
        self.dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        self.live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        self.uls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")

    def test_assigning_a_load_case_with_a_factor(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        assert rel.is_a("IfcRelAssignsToGroupByFactor")
        assert rel.RelatingGroup == self.uls
        assert rel.RelatedObjects == (self.dead,)
        assert rel.Factor == 1.35

    def test_assigning_a_load_case_with_a_factor_of_one_by_default(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls
        )
        assert rel.Factor == 1.0

    def test_load_cases_with_different_factors_have_a_relationship_each(self):
        self.setup_cases()
        dead_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        live_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls, factor=1.5
        )
        assert dead_rel != live_rel
        assert set(self.uls.IsGroupedBy) == {dead_rel, live_rel}

    def test_load_cases_with_the_same_factor_share_a_relationship(self):
        self.setup_cases()
        dead_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.5
        )
        live_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls, factor=1.5
        )
        assert dead_rel == live_rel
        assert set(dead_rel.RelatedObjects) == {self.dead, self.live}

    def test_assigning_a_load_case_twice_does_nothing(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        again = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        assert again == rel
        assert rel.RelatedObjects == (self.dead,)
        assert len(self.file.by_type("IfcRelAssignsToGroupByFactor")) == 1

    def test_changing_the_factor_of_a_load_case(self):
        self.setup_cases()
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.0
        )
        assert self.file.by_type("IfcRelAssignsToGroupByFactor") == (rel,)
        assert rel.Factor == 1.0
        assert rel.RelatedObjects == (self.dead,)

    def test_changing_the_factor_of_a_load_case_that_shares_a_relationship(self):
        self.setup_cases()
        shared = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.5
        )
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls, factor=1.5
        )
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        assert shared.RelatedObjects == (self.live,)
        assert rel.RelatedObjects == (self.dead,)
        assert rel.Factor == 1.35

    def test_assigning_a_load_case_to_two_combinations(self):
        self.setup_cases()
        sls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="SLS")
        uls_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        sls_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=sls, factor=1.0
        )
        assert uls_rel.Factor == 1.35
        assert sls_rel.Factor == 1.0
        assert set(self.dead.HasAssignments) == {uls_rel, sls_rel}

    def test_a_load_group_of_type_load_case_is_a_load_case(self):
        self.setup_cases()
        wind = self.file.createIfcStructuralLoadGroup(
            ifcopenshell.guid.new(),
            Name="Wind",
            PredefinedType="LOAD_CASE",
            ActionType="VARIABLE_Q",
            ActionSource="WIND_W",
        )
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=wind, load_combination=self.uls, factor=1.5
        )
        assert rel.RelatedObjects == (wind,)
        assert rel.Factor == 1.5

    def test_only_load_cases_can_be_combined(self):
        self.setup_cases()
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        with pytest.raises(ValueError):
            ifcopenshell.api.structural.assign_structural_load_combination(
                self.file, load_case=load_group, load_combination=self.uls
            )

    def test_only_combinations_can_be_assigned_to(self):
        self.setup_cases()
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        with pytest.raises(ValueError):
            ifcopenshell.api.structural.assign_structural_load_combination(
                self.file, load_case=self.dead, load_combination=load_group
            )


class TestAssignStructuralLoadCombinationIFC4X3(test.bootstrap.IFC4X3, TestAssignStructuralLoadCombination):
    pass


class TestAssignStructuralLoadCombinationInFactorGroups(test.bootstrap.IFC4, FactorGroups):
    def test_a_load_case_in_a_factor_group_is_grouped_by_factor_instead(self):
        self.setup_rfem()
        q_group = self.q_group.id()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination, factor=1.5
        )
        assert rel.is_a("IfcRelAssignsToGroupByFactor")
        assert rel.RelatingGroup == self.combination
        assert rel.RelatedObjects == (self.q,)
        assert rel.Factor == 1.5
        # Its group, left grouping nothing, is removed; the other is kept.
        assert q_group not in [g.id() for g in self.file.by_type("IfcStructuralLoadGroup")]
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.q: 1.5, self.wx: 0.9}

    def test_every_load_case_grouped_by_factor(self):
        self.setup_rfem()
        for case, factor in ((self.q, 1.5), (self.wx, 0.9)):
            ifcopenshell.api.structural.assign_structural_load_combination(
                self.file, load_case=case, load_combination=self.combination, factor=factor
            )
        assert all(rel.is_a("IfcRelAssignsToGroupByFactor") for rel in self.combination.IsGroupedBy)
        assert [g.Name for g in self.file.by_type("IfcStructuralLoadGroup")] == ["Q", "Wx", "Load Combination 1"]
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.q: 1.5, self.wx: 0.9}

    def test_a_load_case_both_in_a_factor_group_and_by_factor(self):
        self.setup_rfem()
        self.file.createIfcRelAssignsToGroupByFactor(
            ifcopenshell.guid.new(), RelatedObjects=[self.q], RelatingGroup=self.combination, Factor=1.0
        )
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.q, load_combination=self.combination, factor=1.0
        )
        assert ifcopenshell.util.structural.get_combination_factors(self.combination) == {self.q: 1.0, self.wx: 0.9}
        assert rel.RelatedObjects == (self.q,)


class TestAssignStructuralLoadCombinationIFC2X3(test.bootstrap.IFC2X3, FactorGroups):
    def setup_cases(self):
        self.dead = self.add_group("LOAD_CASE", "Dead")
        self.live = self.add_group("LOAD_CASE", "Live")
        self.uls = self.add_group("LOAD_COMBINATION", "ULS")

    def test_a_load_case_is_given_its_factor_by_a_load_combination_group(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        group = rel.RelatingGroup
        assert rel.RelatedObjects == (self.dead,)
        assert group.PredefinedType == "LOAD_COMBINATION_GROUP"
        assert group.Coefficient == 1.35
        assert self.uls.IsGroupedBy[0].RelatedObjects == (group,)
        assert ifcopenshell.util.structural.get_combination_factors(self.uls) == {self.dead: 1.35}

    def test_load_cases_with_the_same_factor_share_a_group(self):
        self.setup_cases()
        dead_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.5
        )
        live_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.live, load_combination=self.uls, factor=1.5
        )
        assert dead_rel == live_rel
        assert set(dead_rel.RelatedObjects) == {self.dead, self.live}

    def test_load_cases_with_different_factors_share_the_combinations_one_relationship(self):
        self.setup_cases()
        for case, factor in ((self.dead, 1.35), (self.live, 1.5)):
            ifcopenshell.api.structural.assign_structural_load_combination(
                self.file, load_case=case, load_combination=self.uls, factor=factor
            )
        # IFC2X3 allows a group one IfcRelAssignsToGroup.
        assert len(self.uls.IsGroupedBy) == 1
        assert len(self.uls.IsGroupedBy[0].RelatedObjects) == 2
        assert ifcopenshell.util.structural.get_combination_factors(self.uls) == {self.dead: 1.35, self.live: 1.5}

    def test_assigning_a_load_case_twice_does_nothing(self):
        self.setup_cases()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        again = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        )
        assert again == rel
        assert len(self.file.by_type("IfcStructuralLoadGroup")) == 4

    def test_changing_the_factor_of_a_load_case(self):
        self.setup_cases()
        old = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.35
        ).RelatingGroup.id()
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.0
        )
        assert rel.RelatingGroup.Coefficient == 1.0
        assert old not in [g.id() for g in self.file.by_type("IfcStructuralLoadGroup")]
        assert ifcopenshell.util.structural.get_combination_factors(self.uls) == {self.dead: 1.0}

    def test_a_group_another_combination_shares_is_not_changed(self):
        self.setup_cases()
        sls = self.add_group("LOAD_COMBINATION", "SLS")
        shared = self.add_group("LOAD_COMBINATION_GROUP", coefficient=1.5)
        self.group([self.live], shared)
        ifcopenshell.api.group.assign_group(self.file, products=[shared], group=self.uls)
        ifcopenshell.api.group.assign_group(self.file, products=[shared], group=sls)
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=self.dead, load_combination=self.uls, factor=1.5
        )
        assert rel.RelatingGroup != shared
        assert ifcopenshell.util.structural.get_combination_factors(sls) == {self.live: 1.5}
        assert ifcopenshell.util.structural.get_combination_factors(self.uls) == {self.dead: 1.5, self.live: 1.5}
