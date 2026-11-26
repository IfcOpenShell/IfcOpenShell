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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import ifcopenshell.util.structural
import test.bootstrap


class TestRemoveStructuralLoadCase(test.bootstrap.IFC4):
    def test_removing_a_load_case(self):
        # Files made by the API in IFC4 have no OwnerHistory
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcStructuralLoadCase")

    def test_removing_a_load_case_and_its_grouping_relationship(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        self.file.createIfcRelAssignsToGroup(
            ifcopenshell.guid.new(), RelatedObjects=[load_group], RelatingGroup=load_case
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcStructuralLoadCase")
        assert not self.file.by_type("IfcRelAssignsToGroup")

    def test_removing_a_load_case_from_the_models_it_loads(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        model.LoadedBy = [dead, live]
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert model.LoadedBy == (live,)

    def test_removing_a_load_case_from_its_combinations(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        uls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=dead, load_combination=uls, factor=1.35
        )
        live_rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=live, load_combination=uls, factor=1.5
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert self.file.by_type("IfcRelAssignsToGroupByFactor") == (live_rel,)

    def test_keeping_a_combination_relationship_shared_with_another_load_case(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        sls = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="SLS")
        ifcopenshell.api.structural.assign_structural_load_combination(self.file, load_case=dead, load_combination=sls)
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=live, load_combination=sls
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert rel.RelatedObjects == (live,)
        assert rel.RelatingGroup == sls

    def test_removing_a_load_case_unassigns_it_from_analysis_models(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        other = ifcopenshell.api.structural.add_structural_load_case(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[load_case, other], structural_analysis_model=model
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert model.LoadedBy == (other,)

    def test_removing_the_last_load_case_of_a_model_unsets_loaded_by(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[load_case], structural_analysis_model=model
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert model.LoadedBy is None

    def add_point_load(self, group, name="P"):
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection", name=name)
        load = ifcopenshell.api.structural.add_structural_load(
            self.file, name="10 kN", ifc_class="IfcStructuralLoadSingleForce"
        )
        activity = ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=group)
        return point, load, activity

    def test_removing_the_activities_in_a_load_case(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        point, load, activity = self.add_point_load(load_case)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcStructuralActivity")
        assert not self.file.by_type("IfcRelConnectsStructuralActivity")
        # The point and the load definition, which other activities may share, are kept.
        assert point.id() and load.id()

    def test_removing_the_load_groups_in_a_load_case_with_their_activities(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        ifcopenshell.api.group.assign_group(self.file, products=[load_group], group=load_case)
        self.add_point_load(load_group)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcStructuralLoadGroup")
        assert not self.file.by_type("IfcStructuralActivity")

    def test_keeping_an_activity_that_another_load_case_also_groups(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        point, load, activity = self.add_point_load(dead)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=live)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert self.file.by_type("IfcStructuralActivity") == (activity,)
        assert [r.RelatingGroup for r in activity.HasAssignments] == [live]

    def test_removing_an_activity_in_a_load_case_and_in_a_load_group_in_it(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        ifcopenshell.api.group.assign_group(self.file, products=[load_group], group=load_case)
        point, load, activity = self.add_point_load(load_case)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=load_group)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcStructuralLoadGroup")
        assert not self.file.by_type("IfcStructuralActivity")

    def test_keeping_an_activity_in_a_load_group_in_it_that_another_load_case_also_groups(self):
        dead = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        live = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Live")
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        ifcopenshell.api.group.assign_group(self.file, products=[load_group], group=dead)
        point, load, activity = self.add_point_load(dead)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=load_group)
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=live)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert self.file.by_type("IfcStructuralActivity") == (activity,)
        assert [r.RelatingGroup for r in activity.HasAssignments] == [live]

    def add_load_group(self, predefined_type, name=None, coefficient=None):
        return self.file.createIfcStructuralLoadGroup(
            ifcopenshell.guid.new(),
            Name=name,
            PredefinedType=predefined_type,
            ActionType="NOTDEFINED",
            ActionSource="NOTDEFINED",
            Coefficient=coefficient,
        )

    def test_removing_a_load_case_from_the_load_groups_that_give_it_its_factor(self):
        # As RFEM writes combinations: a load group of type LOAD_GROUP for each factor
        q = self.add_load_group("LOAD_CASE", "Q")
        wx = self.add_load_group("LOAD_CASE", "Wx")
        combination = self.add_load_group("LOAD_COMBINATION", "Load Combination 1")
        factor_groups = []
        for case, coefficient in ((q, 1.5), (wx, 0.9)):
            group = self.add_load_group("LOAD_GROUP", coefficient=coefficient)
            ifcopenshell.api.group.assign_group(self.file, products=[case], group=group)
            factor_groups.append(group)
        self.file.createIfcRelAssignsToGroup(
            ifcopenshell.guid.new(), RelatedObjects=factor_groups, RelatingGroup=combination
        )
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=q)
        assert set(self.file.by_type("IfcStructuralLoadGroup")) == {wx, combination, factor_groups[1]}
        assert ifcopenshell.util.structural.get_combination_factors(combination) == {wx: 0.9}
        assert all(rel.RelatedObjects for rel in self.file.by_type("IfcRelAssignsToGroup"))

    def test_keeping_a_load_group_giving_a_factor_to_another_load_case_too(self):
        q = self.add_load_group("LOAD_CASE", "Q")
        wx = self.add_load_group("LOAD_CASE", "Wx")
        combination = self.add_load_group("LOAD_COMBINATION", "Load Combination 1")
        group = self.add_load_group("LOAD_GROUP", coefficient=1.5)
        ifcopenshell.api.group.assign_group(self.file, products=[q, wx], group=group)
        ifcopenshell.api.group.assign_group(self.file, products=[group], group=combination)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=q)
        assert ifcopenshell.util.structural.get_combination_factors(combination) == {wx: 1.5}

    def test_removing_the_property_sets_of_a_load_case(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=load_case, name="Pset_Custom")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Note": "Kept nowhere"})
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcPropertySet")
        assert not self.file.by_type("IfcRelDefinesByProperties")


class TestRemoveStructuralLoadCaseIFC2X3(test.bootstrap.IFC2X3):
    def add_load_group(self, predefined_type, coefficient=None):
        return self.file.createIfcStructuralLoadGroup(
            ifcopenshell.guid.new(),
            PredefinedType=predefined_type,
            ActionType="NOTDEFINED",
            ActionSource="NOTDEFINED",
            Coefficient=coefficient,
        )

    def test_removing_a_load_case_from_its_load_combination_groups(self):
        # IFC2X3 has no IfcRelAssignsToGroupByFactor: a LOAD_COMBINATION_GROUP gives each factor
        dead = self.add_load_group("LOAD_CASE")
        live = self.add_load_group("LOAD_CASE")
        combination = self.add_load_group("LOAD_COMBINATION")
        for case, coefficient in ((dead, 1.35), (live, 1.5)):
            group = self.add_load_group("LOAD_COMBINATION_GROUP", coefficient)
            ifcopenshell.api.group.assign_group(self.file, products=[case], group=group)
            ifcopenshell.api.group.assign_group(self.file, products=[group], group=combination)
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=dead)
        assert len(self.file.by_type("IfcStructuralLoadGroup")) == 3
        assert ifcopenshell.util.structural.get_combination_factors(combination) == {live: 1.5}
        # An IFC2X3 group must group something
        assert all(rel.RelatedObjects for rel in self.file.by_type("IfcRelAssignsToGroup"))
        assert all(
            g.IsGroupedBy for g in self.file.by_type("IfcStructuralLoadGroup") if g.PredefinedType != "LOAD_CASE"
        )
