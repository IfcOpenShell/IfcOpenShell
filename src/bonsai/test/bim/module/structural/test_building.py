# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.structural

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAssignStructuralAnalysisModelToBuilding(NewFile):
    def test_assigning_and_unassigning_a_building(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        building = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuilding", name="Building A")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        props = tool.Structural.get_structural_props()
        props.building = str(building.id())
        bpy.ops.bim.assign_structural_analysis_model_to_building(structural_analysis_model=model.id())
        assert [b for rel in model.ServicesBuildings for b in rel.RelatedBuildings] == [building]

        bpy.ops.bim.unassign_structural_analysis_model_from_building(
            structural_analysis_model=model.id(), building=building.id()
        )
        assert not ifc.by_type("IfcRelServicesBuildings")

    def test_doing_nothing_without_a_building(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        bpy.ops.bim.assign_structural_analysis_model_to_building(structural_analysis_model=model.id())
        assert not ifc.by_type("IfcRelServicesBuildings")
