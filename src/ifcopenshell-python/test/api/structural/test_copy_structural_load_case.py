# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz <ryan@openingdesign.com>
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
import ifcopenshell.util.element
import test.bootstrap


def get_members(group):
    return [o for rel in group.IsGroupedBy for o in rel.RelatedObjects]


class TestCopyStructuralLoadCase(test.bootstrap.IFC4):
    def add_point_load(self, group, name):
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection", name=name)
        load = ifcopenshell.api.structural.add_structural_load(
            self.file, name="10 kN", ifc_class="IfcStructuralLoadSingleForce"
        )
        activity = ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.group.assign_group(self.file, products=[activity], group=group)
        return point, load, activity

    def test_copying_a_load_case_and_its_attributes(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(
            self.file, name="Dead", action_type="PERMANENT_G", action_source="DEAD_LOAD_G"
        )
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        assert copy.is_a("IfcStructuralLoadCase") and copy != load_case
        assert copy.GlobalId != load_case.GlobalId
        assert copy.Name == "Dead (copy)"
        assert copy.ActionType == "PERMANENT_G" and copy.ActionSource == "DEAD_LOAD_G"

    def test_naming_the_copy(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="About A")
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case, name="About B")
        assert copy.Name == "About B"

    def test_the_copy_loads_the_same_analysis_models(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[load_case], structural_analysis_model=model
        )
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        assert set(model.LoadedBy) == {load_case, copy}

    def test_copying_activities_onto_the_same_items_sharing_their_loads(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        point, load, activity = self.add_point_load(load_case, "A")
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        (copied,) = get_members(copy)
        assert copied.is_a("IfcStructuralPointAction") and copied != activity
        assert copied.AppliedLoad == load
        assert copied.AssignedToStructuralItem[0].RelatingElement == point
        assert get_members(load_case) == [activity]

    def test_copying_load_groups_into_the_copy(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        load_group = ifcopenshell.api.structural.add_structural_load_group(self.file, name="Slab")
        ifcopenshell.api.group.assign_group(self.file, products=[load_group], group=load_case)
        point, load, activity = self.add_point_load(load_group, "A")
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        (copied_group,) = get_members(copy)
        assert copied_group.is_a("IfcStructuralLoadGroup") and copied_group != load_group
        assert copied_group.Name == "Slab"
        (copied,) = get_members(copied_group)
        assert copied != activity and copied.AppliedLoad == load
        assert get_members(load_group) == [activity]

    def test_copying_property_sets_as_the_copys_own(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        point, load, activity = self.add_point_load(load_case, "A")
        for element in (load_case, activity):
            pset = ifcopenshell.api.pset.add_pset(self.file, product=element, name="Pset_Custom")
            ifcopenshell.api.pset.edit_pset(self.file, pset=pset, properties={"Note": "Original"})
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        (copied,) = get_members(copy)
        for original, element in ((load_case, copy), (activity, copied)):
            pset = ifcopenshell.util.element.get_pset(element, "Pset_Custom")
            assert pset["Note"] == "Original"
            ifcopenshell.api.pset.edit_pset(self.file, pset=self.file.by_id(pset["id"]), properties={"Note": "Copy"})
            assert ifcopenshell.util.element.get_pset(original, "Pset_Custom", "Note") == "Original"

    def test_the_copy_joins_no_load_combination(self):
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file)
        combination = ifcopenshell.api.structural.add_structural_load_combination(self.file, name="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(
            self.file, load_case=load_case, load_combination=combination, factor=1.35
        )
        copy = ifcopenshell.api.structural.copy_structural_load_case(self.file, load_case=load_case)
        assert not copy.HasAssignments
        assert get_members(combination) == [load_case]
