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

import ifcopenshell.api.structural
import test.bootstrap


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
