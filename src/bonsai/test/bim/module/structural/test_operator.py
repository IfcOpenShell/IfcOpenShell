# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestLoadBoundaryConditions(NewFile):
    def test_filtering_duplicate_names(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Fixed")
        ifc.createIfcBoundaryNodeCondition(Name="Pinned")
        props = tool.Structural.get_structural_props()
        props.filtered_boundary_conditions = True
        bpy.ops.bim.load_boundary_conditions()
        assert sorted(c.name for c in props.boundary_conditions) == ["Pinned"]


class TestLoadCaseSelfWeight(NewFile):
    def test_edit_and_clear_self_weight(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        load_case = ifc.createIfcStructuralLoadCase(
            GlobalId=ifcopenshell.guid.new(),
            Name="Dead Load",
            PredefinedType="LOAD_CASE",
            ActionType="PERMANENT_G",
            ActionSource="DEAD_LOAD_G",
        )
        props = tool.Structural.get_structural_props()

        bpy.ops.bim.enable_editing_structural_load_case(load_case=load_case.id())
        assert props.load_case_has_self_weight is False
        assert tuple(props.load_case_self_weight) == (0.0, 0.0, -1.0)

        props.load_case_has_self_weight = True
        props.load_case_self_weight = (0.5, 0.0, -1.0)
        bpy.ops.bim.edit_structural_load_case()
        assert list(load_case.SelfWeightCoefficients) == [0.5, 0.0, -1.0]

        bpy.ops.bim.enable_editing_structural_load_case(load_case=load_case.id())
        assert props.load_case_has_self_weight is True
        assert tuple(props.load_case_self_weight) == (0.5, 0.0, -1.0)

        props.load_case_has_self_weight = False
        bpy.ops.bim.edit_structural_load_case()
        assert load_case.SelfWeightCoefficients is None
