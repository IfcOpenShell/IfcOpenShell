# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.group
import ifcopenshell.api.root
import ifcopenshell.api.structural

import bonsai.tool as tool
from bonsai.bim.module.structural.data import StructuralAnalysisModelsData, StructuralItemLoadsData
from test.bim.bootstrap import NewFile


class TestStructuralItemLoadsData(NewFile):
    def setup_item(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc_file)
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
        model = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        point = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcStructuralPointConnection", name="P1")
        obj = bpy.data.objects.new("P1", bpy.data.meshes.new("P1"))
        bpy.context.scene.collection.objects.link(obj)
        tool.Ifc.link(point, obj)
        bpy.context.view_layer.objects.active = obj
        return ifc_file, model, point

    def apply(self, ifc_file, point, name, x, z, group=None):
        load = ifcopenshell.api.structural.add_structural_load(
            ifc_file, name=name, ifc_class="IfcStructuralLoadSingleForce"
        )
        load.ForceX, load.ForceZ = x, z
        activity = ifcopenshell.api.structural.add_structural_activity(
            ifc_file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        if group:
            ifcopenshell.api.group.assign_group(ifc_file, products=[activity], group=group)
        return activity

    def test_loads_by_load_case_with_their_resultant(self):
        ifc_file, model, point = self.setup_item()
        dead = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Dead")
        wind = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Wind")
        gusts = ifcopenshell.api.structural.add_structural_load_group(ifc_file, name="Gusts")
        ifcopenshell.api.group.assign_group(ifc_file, products=[gusts], group=wind)
        model.LoadedBy = [dead, wind]
        first = self.apply(ifc_file, point, "A", 300.0, 0.0, dead)
        second = self.apply(ifc_file, point, "B", 0.0, 400.0, dead)
        self.apply(ifc_file, point, "C", 10.0, 0.0, gusts)
        self.apply(ifc_file, point, "D", 0.0, -1.0)

        cases = StructuralItemLoadsData.load_cases()
        assert [case["name"] for case in cases] == ["Dead", "No load case", "Wind"]
        dead_case = cases[0]
        assert [load["activity"] for load in dead_case["loads"]] == [first.id(), second.id()]
        assert dead_case["resultant"].startswith("R = 500.00 N")
        # A load in a load group within the case is listed under the case, named with its group.
        assert cases[2]["loads"][0]["group"] == "Gusts"

    def test_load_cases_of_the_model_that_do_not_load_the_item(self):
        ifc_file, model, point = self.setup_item()
        dead = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Dead")
        snow = ifcopenshell.api.structural.add_structural_load_case(ifc_file, name="Snow")
        model.LoadedBy = [dead, snow]
        self.apply(ifc_file, point, "A", 300.0, 0.0, dead)
        assert StructuralItemLoadsData.unloaded_cases() == ["Snow"]

    def test_the_analysis_models_listed_for_an_item(self):
        ifc_file, model, point = self.setup_item()
        other = ifcopenshell.api.structural.add_structural_analysis_model(ifc_file)
        ifcopenshell.api.structural.assign_structural_analysis_model(
            ifc_file, products=[point], structural_analysis_model=model
        )
        StructuralAnalysisModelsData.load()
        data = StructuralAnalysisModelsData.data
        assert {m["id"] for m in data["models"]} == {model.id(), other.id()}
        assert data["active_model_ids"] == [model.id()]
