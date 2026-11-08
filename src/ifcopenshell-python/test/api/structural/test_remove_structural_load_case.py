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
