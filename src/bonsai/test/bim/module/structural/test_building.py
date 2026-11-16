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
        bpy.ops.bim.load_structural_analysis_models()  # The picker offers the highlighted model's choices.
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

    def test_offering_only_buildings_not_served_yet(self):
        from bonsai.bim.module.structural.data import StructuralAnalysisModelsData
        from bonsai.bim.module.structural.prop import get_buildings

        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        served = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuilding", name="Building A")
        other = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuilding", name="Building B")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc)
        ifcopenshell.api.structural.assign_to_building(ifc, structural_analysis_model=model, building=served)
        bpy.ops.bim.load_structural_analysis_models()
        props = tool.Structural.get_structural_props()
        StructuralAnalysisModelsData.is_loaded = False
        assert [item[0] for item in get_buildings(props, bpy.context)] == [str(other.id())]
