# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.structural
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
