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

    def test_removing_the_property_sets_of_a_load_case(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="Dead")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=load_case, name="Pset_Custom")
        ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Note": "Kept nowhere"})
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert not self.file.by_type("IfcPropertySet")
        assert not self.file.by_type("IfcRelDefinesByProperties")
