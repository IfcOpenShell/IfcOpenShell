# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural
import ifcopenshell.guid
import pytest

import bonsai.tool as tool
from bonsai.bim.module.structural.data import LoadGroupDecorationData, StructuralLoadCombinationsData
from bonsai.bim.module.structural.operator import get_load_combination_factors
from test.bim.bootstrap import NewFile


class LoadCombinationFile(NewFile):
    def make_file(self, with_model: bool = True) -> ifcopenshell.file:
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        self.dead = ifcopenshell.api.structural.add_structural_load_case(ifc, name="Dead", action_type="PERMANENT_G")
        self.imposed = ifcopenshell.api.structural.add_structural_load_case(
            ifc, name="Imposed", action_type="VARIABLE_Q"
        )
        self.model = None
        if with_model:
            self.model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
            tool.Structural.get_structural_props().current_structural_analysis_model_id = self.model.id()
        return ifc

    def factor_rows(self) -> dict[str, tuple[bool, float]]:
        props = tool.Structural.get_structural_props()
        return {row.name: (row.is_included, round(row.factor, 6)) for row in props.load_combination_factors}

    def set_row(self, name: str, is_included: bool, factor: float = 1.0) -> None:
        props = tool.Structural.get_structural_props()
        row = next(row for row in props.load_combination_factors if row.name == name)
        row.is_included = is_included
        row.factor = factor


class TestAddStructuralLoadCombination(LoadCombinationFile):
    def test_adding_a_combination_to_the_current_model_and_editing_it(self):
        ifc = self.make_file()
        bpy.ops.bim.add_structural_load_combination()
        (combination,) = [g for g in ifc.by_type("IfcStructuralLoadGroup") if g.PredefinedType == "LOAD_COMBINATION"]
        assert combination.Name == "Load Combination"
        assert list(self.model.LoadedBy) == [combination]
        props = tool.Structural.get_structural_props()
        assert props.active_load_combination_id == combination.id()
        assert self.factor_rows() == {"Dead": (False, 1.0), "Imposed": (False, 1.0)}

    def test_adding_a_combination_without_a_model(self):
        ifc = self.make_file(with_model=False)
        bpy.ops.bim.add_structural_load_combination()
        (combination,) = [g for g in ifc.by_type("IfcStructuralLoadGroup") if g.PredefinedType == "LOAD_COMBINATION"]
        assert not combination.LoadGroupFor


class TestEditStructuralLoadCombination(LoadCombinationFile):
    def test_attributes_shown(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1", purpose="ULS")
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        props = tool.Structural.get_structural_props()
        names = [a.name for a in props.load_combination_attributes]
        assert "Name" in names and "Purpose" in names
        for hidden in ("PredefinedType", "ActionType", "ActionSource", "Coefficient", "ObjectType"):
            assert hidden not in names

    def test_a_coefficient_set_in_the_file_is_shown(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        combination.Coefficient = 0.9
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        props = tool.Structural.get_structural_props()
        assert "Coefficient" in [a.name for a in props.load_combination_attributes]

    def test_setting_changing_and_removing_factors(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1")
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        self.set_row("Dead", True, 1.35)
        self.set_row("Imposed", True, 1.5)
        bpy.ops.bim.edit_structural_load_combination()
        assert get_load_combination_factors(combination) == {self.dead: 1.35, self.imposed: 1.5}
        props = tool.Structural.get_structural_props()
        assert props.active_load_combination_id == 0

        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        assert self.factor_rows() == {"Dead": (True, 1.35), "Imposed": (True, 1.5)}
        self.set_row("Dead", True, 1.0)
        self.set_row("Imposed", False)
        bpy.ops.bim.edit_structural_load_combination()
        assert get_load_combination_factors(combination) == {self.dead: 1.0}

    def test_cases_with_the_same_factor_share_a_relationship(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        self.set_row("Dead", True, 1.5)
        self.set_row("Imposed", True, 1.5)
        bpy.ops.bim.edit_structural_load_combination()
        (rel,) = combination.IsGroupedBy
        assert rel.Factor == 1.5 and set(rel.RelatedObjects) == {self.dead, self.imposed}

    def test_saving_unchanged_factors_changes_nothing(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        rel = ifcopenshell.api.structural.assign_structural_load_combination(
            ifc, load_case=self.dead, load_combination=combination, factor=1.35
        )
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        bpy.ops.bim.edit_structural_load_combination()
        assert list(combination.IsGroupedBy) == [rel]

    def test_attribute_edits_are_saved(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        props = tool.Structural.get_structural_props()
        props.load_combination_attributes["Name"].string_value = "SLS characteristic"
        props.load_combination_attributes["Purpose"].string_value = "SLS"
        bpy.ops.bim.edit_structural_load_combination()
        assert combination.Name == "SLS characteristic"
        assert combination.Purpose == "SLS"

    def test_a_case_grouped_twice_counts_for_the_sum(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        for factor in (1.0, 0.35):
            ifc.createIfcRelAssignsToGroupByFactor(
                GlobalId=ifcopenshell.guid.new(), RelatedObjects=[self.dead], RelatingGroup=combination, Factor=factor
            )
        ifc.createIfcRelAssignsToGroup(
            GlobalId=ifcopenshell.guid.new(), RelatedObjects=[self.imposed], RelatingGroup=combination
        )
        assert get_load_combination_factors(combination) == {self.dead: pytest.approx(1.35), self.imposed: 1.0}


class TestRemoveStructuralLoadCombination(LoadCombinationFile):
    def test_removing_keeps_the_load_cases(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc)
        ifcopenshell.api.structural.assign_structural_load_combination(
            ifc, load_case=self.dead, load_combination=combination, factor=1.35
        )
        ifcopenshell.api.structural.assign_structural_load_group(
            ifc, load_groups=[combination], structural_analysis_model=self.model
        )
        bpy.ops.bim.remove_structural_load_combination(load_combination=combination.id())
        assert not [g for g in ifc.by_type("IfcStructuralLoadGroup") if g.PredefinedType == "LOAD_COMBINATION"]
        assert not ifc.by_type("IfcRelAssignsToGroupByFactor")
        assert set(ifc.by_type("IfcStructuralLoadCase")) == {self.dead, self.imposed}


class TestStructuralLoadCombinationsData(LoadCombinationFile):
    def test_listing_combinations(self):
        ifc = self.make_file()
        empty = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="Empty")
        uls = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1", purpose="ULS")
        ifcopenshell.api.structural.assign_structural_load_combination(ifc, load_case=self.dead, load_combination=uls)
        ifcopenshell.api.structural.assign_structural_load_group(
            ifc, load_groups=[uls], structural_analysis_model=self.model
        )
        StructuralLoadCombinationsData.load()
        data = {c["name"]: c for c in StructuralLoadCombinationsData.data["load_combinations"]}
        assert set(data) == {"Empty", "ULS 1"}
        assert data["Empty"]["total_load_cases"] == 0 and data["Empty"]["model_ids"] == []
        assert data["ULS 1"]["purpose"] == "ULS"
        assert data["ULS 1"]["total_load_cases"] == 1
        assert data["ULS 1"]["model_ids"] == [self.model.id()]
        assert empty.id() != uls.id()

    def test_combinations_can_be_shown_without_a_model(self):
        ifc = self.make_file(with_model=False)
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1")
        LoadGroupDecorationData.load()
        ids = [i[0] for i in LoadGroupDecorationData.data["load_groups_to_show"]]
        assert str(combination.id()) in ids and str(self.dead.id()) in ids


class TestLoadGroupsTypedLoadCase(LoadCombinationFile):
    """A load case may be an IfcStructuralLoadGroup of type LOAD_CASE, as RFEM writes them"""

    def make_file(self, with_model: bool = True) -> ifcopenshell.file:
        ifc = super().make_file(with_model)
        self.wind = ifc.createIfcStructuralLoadGroup(
            GlobalId=ifcopenshell.guid.new(),
            Name="Wind",
            PredefinedType="LOAD_CASE",
            ActionType="VARIABLE_Q",
            ActionSource="WIND_W",
        )
        return ifc

    def test_editing_its_factor(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1")
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        assert self.factor_rows() == {"Dead": (False, 1.0), "Imposed": (False, 1.0), "Wind": (False, 1.0)}
        self.set_row("Wind", True, 1.5)
        bpy.ops.bim.edit_structural_load_combination()
        assert get_load_combination_factors(combination) == {self.wind: 1.5}
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        assert self.factor_rows()["Wind"] == (True, 1.5)

    def test_it_is_counted_in_the_list(self):
        ifc = self.make_file()
        combination = ifcopenshell.api.structural.add_structural_load_combination(ifc, name="ULS 1")
        for case in (self.dead, self.wind):
            ifcopenshell.api.structural.assign_structural_load_combination(
                ifc, load_case=case, load_combination=combination
            )
        StructuralLoadCombinationsData.load()
        (data,) = StructuralLoadCombinationsData.data["load_combinations"]
        assert data["total_load_cases"] == 2


class TestFactorGroups(LoadCombinationFile):
    """RFEM writes a combination's factors in IFC4 as load groups typed LOAD_GROUP, their Coefficient the factor"""

    def add_group(self, ifc, predefined_type, name=None, coefficient=None):
        return ifc.createIfcStructuralLoadGroup(
            GlobalId=ifcopenshell.guid.new(),
            Name=name,
            PredefinedType=predefined_type,
            ActionType="NOTDEFINED",
            ActionSource="NOTDEFINED",
            Coefficient=coefficient,
        )

    def make_rfem(self):
        ifc = self.make_file()
        self.combination = self.add_group(ifc, "LOAD_COMBINATION", "Load Combination 1")
        groups = []
        for case, coefficient in ((self.dead, 1.5), (self.imposed, 0.9)):
            group = self.add_group(ifc, "LOAD_GROUP", coefficient=coefficient)
            ifc.createIfcRelAssignsToGroup(ifcopenshell.guid.new(), RelatedObjects=[case], RelatingGroup=group)
            groups.append(group)
        ifc.createIfcRelAssignsToGroup(ifcopenshell.guid.new(), RelatedObjects=groups, RelatingGroup=self.combination)
        self.model.LoadedBy = [self.combination]
        return ifc

    def test_the_factors_are_shown(self):
        self.make_rfem()
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=self.combination.id())
        assert self.factor_rows() == {"Dead": (True, 1.5), "Imposed": (True, 0.9)}

    def test_the_load_cases_are_counted_in_the_list(self):
        self.make_rfem()
        StructuralLoadCombinationsData.load()
        (data,) = StructuralLoadCombinationsData.data["load_combinations"]
        assert data["total_load_cases"] == 2

    def test_saving_gives_the_factors_as_ifc4_does(self):
        ifc = self.make_rfem()
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=self.combination.id())
        self.set_row("Imposed", True, 1.05)
        bpy.ops.bim.edit_structural_load_combination()
        assert get_load_combination_factors(self.combination) == {self.dead: 1.5, self.imposed: 1.05}
        # Every load case, changed or not, is grouped by factor, and the load groups are gone.
        assert all(rel.is_a("IfcRelAssignsToGroupByFactor") for rel in self.combination.IsGroupedBy)
        assert not [g for g in ifc.by_type("IfcStructuralLoadGroup") if g.PredefinedType == "LOAD_GROUP"]

    def test_saving_in_ifc2x3_keeps_load_combination_groups(self):
        ifc = ifcopenshell.file(schema="IFC2X3")
        tool.Ifc.set(ifc)
        # IFC2X3 needs an owner, which Bonsai finds in the file.
        ifc.createIfcPersonAndOrganization(ifc.createIfcPerson(), ifc.createIfcOrganization())
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        dead = self.add_group(ifc, "LOAD_CASE", "Dead")
        combination = self.add_group(ifc, "LOAD_COMBINATION", "ULS")
        group = self.add_group(ifc, "LOAD_COMBINATION_GROUP", coefficient=1.35)
        ifcopenshell.api.group.assign_group(ifc, products=[dead], group=group)
        ifcopenshell.api.group.assign_group(ifc, products=[group], group=combination)
        bpy.ops.bim.enable_editing_structural_load_combination(load_combination=combination.id())
        assert self.factor_rows() == {"Dead": (True, 1.35)}
        self.set_row("Dead", True, 1.5)
        bpy.ops.bim.edit_structural_load_combination()
        assert get_load_combination_factors(combination) == {dead: 1.5}
        (rel,) = dead.HasAssignments
        assert rel.RelatingGroup.PredefinedType == "LOAD_COMBINATION_GROUP"
        assert rel.RelatingGroup.Coefficient == 1.5


class TestShowingAFactorGroupCombination(TestFactorGroups):
    """RFEM leaves LoadedBy empty: its combinations are inferred for the model, as its load cases are"""

    def make_rfem(self):
        ifc = super().make_rfem()
        self.model.LoadedBy = None
        point = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[point], structural_analysis_model=self.model
        )
        for case in (self.dead, self.imposed):
            load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class="IfcStructuralLoadSingleForce")
            activity = ifcopenshell.api.structural.add_structural_activity(
                ifc, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
            )
            ifcopenshell.api.group.assign_group(ifc, products=[activity], group=case)
        return ifc

    def test_the_combination_is_one_of_the_models_load_groups(self):
        self.make_rfem()
        assert set(tool.Structural.get_load_cases(self.model)) == {self.dead, self.imposed, self.combination}

    def test_its_loads_can_be_shown(self):
        self.make_rfem()
        LoadGroupDecorationData.load()
        shown = [label for _, label, _ in LoadGroupDecorationData.data["load_groups_to_show"]]
        # Under the combination, its load cases, not the unnamed groups that give their factors.
        i = shown.index("Load Combination 1 (combination)")
        assert sorted(shown[i + 1 : i + 3]) == ["    Dead", "    Imposed"]
        assert bpy.ops.bim.show_structural_load_case(load_case=self.combination.id()) == {"FINISHED"}
        assert tool.Structural.get_structural_props().load_group_to_show == str(self.combination.id())

    def test_a_combination_with_a_case_of_another_model_is_left_out(self):
        ifc = self.make_rfem()
        other = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        point = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc, products=[point], structural_analysis_model=other
        )
        load = ifcopenshell.api.structural.add_structural_load(ifc, ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.group.assign_group(ifc, products=[activity], group=self.imposed)
        assert set(tool.Structural.get_load_cases(self.model)) == {self.dead}
