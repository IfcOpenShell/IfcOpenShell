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

import numpy
import pytest

import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import ifcopenshell.util.structural as subject
import test.bootstrap


class StructuralModel:
    def make_frame(self):
        self.model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        self.beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        self.column = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        self.knee = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        self.foot = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        for member, connection in ((self.beam, self.knee), (self.column, self.knee), (self.column, self.foot)):
            ifcopenshell.api.structural.add_structural_member_connection(
                self.file, relating_structural_member=member, related_structural_connection=connection
            )
        ifcopenshell.api.structural.assign_structural_analysis_model(
            self.file, products=[self.beam, self.column, self.knee, self.foot], structural_analysis_model=self.model
        )

    def add_action(self, item):
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        return ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=item, ifc_class="IfcStructuralPointAction"
        )


class TestGetAnalysisModels(test.bootstrap.IFC4, StructuralModel):
    def test_the_model_of_an_item(self):
        self.make_frame()
        assert subject.get_analysis_models(self.beam) == [self.model]

    def test_an_item_in_no_model(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        group = ifcopenshell.api.group.add_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[member], group=group)
        assert subject.get_analysis_models(member) == []

    def test_the_model_of_a_load_group(self):
        self.make_frame()
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        self.model.LoadedBy = [group]
        assert subject.get_analysis_models(group) == [self.model]


class TestGetModelItems(test.bootstrap.IFC4, StructuralModel):
    def test_run(self):
        self.make_frame()
        assert set(subject.get_model_items(self.model)) == {self.beam, self.column, self.knee, self.foot}


class TestGetMemberConnections(test.bootstrap.IFC4, StructuralModel):
    def test_run(self):
        self.make_frame()
        assert subject.get_member_connections(self.beam) == [self.knee]
        assert set(subject.get_member_connections(self.column)) == {self.knee, self.foot}


class TestGetConnectionMembers(test.bootstrap.IFC4, StructuralModel):
    def test_run(self):
        self.make_frame()
        assert set(subject.get_connection_members(self.knee)) == {self.beam, self.column}
        assert subject.get_connection_members(self.foot) == [self.column]


class TestGetItemActivities(test.bootstrap.IFC4, StructuralModel):
    def test_run(self):
        self.make_frame()
        action = self.add_action(self.knee)
        assert subject.get_item_activities(self.knee) == [action]
        assert subject.get_item_activities(self.foot) == []


class TestGetGroupActivities(test.bootstrap.IFC4, StructuralModel):
    def test_activities_of_a_load_case_and_its_load_groups(self):
        self.make_frame()
        direct = self.add_action(self.knee)
        nested = self.add_action(self.foot)
        case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Point loads")
        ifcopenshell.api.group.assign_group(self.file, products=[direct, group], group=case)
        ifcopenshell.api.group.assign_group(self.file, products=[nested], group=group)
        assert set(subject.get_group_activities(case)) == {direct, nested}
        assert subject.get_group_activities(group) == [nested]

    def test_a_combination_has_no_activities_of_its_own(self):
        self.make_frame()
        case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        ifcopenshell.api.group.assign_group(self.file, products=[self.add_action(self.knee)], group=case)
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=case, load_combination=combination, factor=1.5
        )
        assert subject.get_group_activities(combination) == []


class TestGetCombinationFactors(test.bootstrap.IFC4):
    def test_run(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        wind = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Wind")
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        for case, factor in ((dead, 1.35), (live, 1.5), (wind, 1.5)):
            ifcopenshell.api.structural.assign_structural_load_combination(
                self.file, load_case=case, load_combination=combination, factor=factor
            )
        assert subject.get_combination_factors(combination) == {dead: 1.35, live: 1.5, wind: 1.5}

    def test_a_plain_assignment_is_a_factor_of_one_and_the_coefficient_applies(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        combination.Coefficient = 2.0
        ifcopenshell.api.group.assign_group(self.file, products=[dead], group=combination)
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=live, load_combination=combination, factor=1.5
        )
        assert subject.get_combination_factors(combination) == {dead: 2.0, live: 3.0}

    def test_a_case_assigned_twice_has_the_sum_of_its_factors(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        for factor in (1.0, 0.35):
            self.file.createIfcRelAssignsToGroupByFactor(
                ifcopenshell.guid.new(), RelatedObjects=[dead], RelatingGroup=combination, Factor=factor
            )
        assert subject.get_combination_factors(combination) == {dead: 1.35}


class TestGetCombinationFactorsIFC2X3(test.bootstrap.IFC2X3):
    def add_group(self, predefined_type, coefficient=None):
        return self.file.createIfcStructuralLoadGroup(
            ifcopenshell.guid.new(),
            PredefinedType=predefined_type,
            ActionType="NOTDEFINED",
            ActionSource="NOTDEFINED",
            Coefficient=coefficient,
        )

    def test_a_load_combination_group_gives_its_cases_its_coefficient(self):
        dead = self.add_group("LOAD_CASE")
        live = self.add_group("LOAD_CASE")
        combination = self.add_group("LOAD_COMBINATION")
        for case, coefficient in ((dead, 1.35), (live, 1.5)):
            group = self.add_group("LOAD_COMBINATION_GROUP", coefficient)
            ifcopenshell.api.group.assign_group(self.file, products=[case], group=group)
            ifcopenshell.api.group.assign_group(self.file, products=[group], group=combination)
        assert subject.get_combination_factors(combination) == {dead: 1.35, live: 1.5}

    def test_the_coefficient_of_the_combination_applies_too(self):
        dead = self.add_group("LOAD_CASE")
        combination = self.add_group("LOAD_COMBINATION", 2.0)
        group = self.add_group("LOAD_COMBINATION_GROUP")
        ifcopenshell.api.group.assign_group(self.file, products=[dead], group=group)
        ifcopenshell.api.group.assign_group(self.file, products=[group, dead], group=combination)
        assert subject.get_combination_factors(combination) == {dead: 4.0}


class TestGetCombinationFactorsOfLoadGroups(test.bootstrap.IFC4):
    """RFEM writes each factor of a combination as a load group of type LOAD_GROUP, its Coefficient the factor"""

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
        self.groups = []
        for case, coefficient in ((self.q, 1.5), (self.wx, 0.9)):
            group = self.add_group("LOAD_GROUP", coefficient=coefficient)
            self.group([case], group)
            self.groups.append(group)
        self.group(self.groups, self.combination)

    def test_a_load_group_gives_its_cases_its_coefficient(self):
        self.setup_rfem()
        assert subject.get_combination_factors(self.combination) == {self.q: 1.5, self.wx: 0.9}

    def test_the_factor_groups_of_a_combination(self):
        self.setup_rfem()
        assert set(subject.get_combination_factor_groups(self.combination)) == set(self.groups)
        assert all(subject.is_factor_group(g) for g in self.groups)
        assert not subject.is_factor_group(self.q)

    def test_leaving_out_the_coefficient_of_the_combination(self):
        self.setup_rfem()
        self.combination.Coefficient = 2.0
        assert subject.get_combination_factors(self.combination) == {self.q: 3.0, self.wx: 1.8}
        assert subject.get_combination_factors(self.combination, include_coefficient=False) == {
            self.q: 1.5,
            self.wx: 0.9,
        }

    def test_groups_within_groups(self):
        self.setup_rfem()
        outer = self.add_group("LOAD_GROUP", coefficient=2.0)
        self.group([self.groups[0]], outer)
        self.group([outer], self.combination)
        groups = subject.get_combination_factor_groups(self.combination)
        # Q's group is in the combination, and in the outer group too: it comes after the outer group.
        assert groups.index(outer) < groups.index(self.groups[0])
        # Q is in the combination at 1.5, and again through the outer group at 2.0 x 1.5.
        assert subject.get_combination_factors(self.combination) == {self.q: 4.5, self.wx: 0.9}

    def test_a_group_that_groups_itself_is_counted_once(self):
        self.setup_rfem()
        self.group([self.groups[0]], self.groups[0])
        assert subject.get_combination_factors(self.combination) == {self.q: 1.5, self.wx: 0.9}


class TestGetModelLoadGroupsAndCases(test.bootstrap.IFC4, StructuralModel):
    def test_a_model_loaded_by_load_cases(self):
        self.make_frame()
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        self.model.LoadedBy = [dead, live]
        assert subject.get_model_load_groups(self.model) == [dead, live]
        assert subject.get_model_load_cases(self.model) == [dead, live]

    def test_a_model_loaded_by_load_combinations(self):
        self.make_frame()
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        uls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        sls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="SLS")
        for combination, factors in ((uls, (1.35, 1.5)), (sls, (1.0, 1.0))):
            for case, factor in zip((dead, live), factors):
                ifcopenshell.api.structural.assign_structural_load_combination(
                    self.file, load_case=case, load_combination=combination, factor=factor
                )
        self.model.LoadedBy = [uls, sls]
        assert subject.get_model_load_groups(self.model) == [uls, sls]
        assert set(subject.get_model_load_cases(self.model)) == {dead, live}
        assert len(subject.get_model_load_cases(self.model)) == 2

    def test_a_model_loaded_by_nothing(self):
        self.make_frame()
        assert subject.get_model_load_groups(self.model) == []
        assert subject.get_model_load_cases(self.model) == []


class TestGetStructuralMembersAndBuildingElements(test.bootstrap.IFC4):
    def test_linked_with_the_member_as_relating_product(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=beam)
        assert subject.get_building_elements(member) == [beam]
        assert subject.get_structural_members(beam) == [member]

    def test_linked_with_the_element_as_relating_product(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        ifcopenshell.api.structural.assign_product(self.file, relating_product=beam, related_object=member)
        assert subject.get_building_elements(member) == [beam]
        assert subject.get_structural_members(beam) == [member]

    def test_other_assignments_are_not_links(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        other = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        ifcopenshell.api.structural.assign_product(self.file, relating_product=member, related_object=other)
        assert subject.get_building_elements(member) == []
        assert subject.get_structural_members(beam) == []


class TestGetStructuralMembersAndBuildingElementsIFC2X3(
    test.bootstrap.IFC2X3, TestGetStructuralMembersAndBuildingElements
):
    def test_linked_by_a_structural_element_connection(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        beam = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBeam")
        rel = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcRelConnectsStructuralElement")
        rel.RelatingElement = beam
        rel.RelatedStructuralMember = member
        assert subject.get_building_elements(member) == [beam]
        assert subject.get_structural_members(beam) == [member]


class TestGetActivityItem(test.bootstrap.IFC4, StructuralModel):
    def test_run(self):
        self.make_frame()
        assert subject.get_activity_item(self.add_action(self.knee)) == self.knee

    def test_an_activity_on_no_item(self):
        activity = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointAction")
        assert subject.get_activity_item(activity) is None


class TestGetActivityLoadCases(test.bootstrap.IFC4, StructuralModel):
    def test_directly_and_through_a_load_group(self):
        self.make_frame()
        activity = self.add_action(self.knee)
        case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        other = ifcopenshell.api.structural.add_structural_load_case(self.file)
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=case)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=group)
        ifcopenshell.api.group.assign_group(self.file, products=[group], group=other)
        assert subject.get_activity_load_cases(activity) == [case, other]

    def test_not_through_a_load_combination(self):
        self.make_frame()
        activity = self.add_action(self.knee)
        case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=case)
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=case, load_combination=combination, factor=1.5
        )
        assert subject.get_activity_load_cases(activity) == [case]

    def test_an_activity_in_no_load_case(self):
        self.make_frame()
        assert subject.get_activity_load_cases(self.add_action(self.knee)) == []


class TestGetGlobalAxes(test.bootstrap.IFC4, StructuralModel):
    def make_placement(self, z, x):
        origin = self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        axes = self.file.createIfcAxis2Placement3D(
            origin, self.file.createIfcDirection(z), self.file.createIfcDirection(x)
        )
        return self.file.createIfcLocalPlacement(None, axes)

    def test_the_project_axes_by_default(self):
        self.make_frame()
        assert numpy.allclose(subject.get_global_axes(self.add_action(self.knee)), numpy.eye(3))

    def test_the_shared_placement_of_the_model(self):
        self.make_frame()
        # As some programs write them: Z down, Y turned to keep the axes right-handed.
        self.model.SharedPlacement = self.make_placement((0.0, 0.0, -1.0), (1.0, 0.0, 0.0))
        activity = self.add_action(self.knee)
        activity.ObjectPlacement = self.make_placement((0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
        axes = subject.get_global_axes(activity)
        assert numpy.allclose(axes, [[1, 0, 0], [0, -1, 0], [0, 0, -1]])

    def test_the_shared_placement_of_the_model_loaded_by_its_load_case(self):
        item = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        model.SharedPlacement = self.make_placement((0.0, 0.0, -1.0), (1.0, 0.0, 0.0))
        case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        model.LoadedBy = [case]
        activity = self.add_action(item)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=case)
        assert numpy.allclose(subject.get_global_axes(activity)[:, 2], [0, 0, -1])

    def test_the_activity_placement_without_a_shared_placement(self):
        self.make_frame()
        activity = self.add_action(self.knee)
        activity.ObjectPlacement = self.make_placement((0.0, 0.0, 1.0), (0.0, 1.0, 0.0))
        assert numpy.allclose(subject.get_global_axes(activity)[:, 0], [0, 1, 0])


class TestGetBoundaryConditionClass(test.bootstrap.IFC4):
    def test_each_connection_takes_its_own_class(self):
        for connection_class, condition_class in (
            ("IfcStructuralPointConnection", "IfcBoundaryNodeCondition"),
            ("IfcStructuralCurveConnection", "IfcBoundaryEdgeCondition"),
            ("IfcStructuralSurfaceConnection", "IfcBoundaryFaceCondition"),
        ):
            connection = ifcopenshell.api.root.create_entity(self.file, ifc_class=connection_class)
            assert subject.get_boundary_condition_class(connection) == condition_class

    def test_a_member_is_refused(self):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        with pytest.raises(ValueError):
            subject.get_boundary_condition_class(member)
