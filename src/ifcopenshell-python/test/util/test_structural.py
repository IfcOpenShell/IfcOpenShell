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
