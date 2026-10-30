# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.georeference
import ifcopenshell.api.root
import ifcopenshell.guid

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.georeference.data import GeoreferenceData
from bonsai.bim.module.pset_template.data import PsetTemplatesData
from bonsai.bim.module.structural.data import LoadGroupDecorationData
from test.bim.bootstrap import NewFile


class TestUnnamedEntityData(NewFile):
    def test_projected_crs_map_unit_without_name(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        ifcopenshell.api.context.add_context(ifc, context_type="Model")
        ifcopenshell.api.georeference.add_georeferencing(ifc)
        crs = ifc.by_type("IfcProjectedCRS")[0]
        crs.MapUnit = ifc.createIfcSIUnit(UnitType="LENGTHUNIT")
        assert GeoreferenceData.projected_crs()["MapUnit"] == ""

    def test_pset_template_without_name(self):
        template_file = ifcopenshell.file(schema="IFC4")
        template_file.create_entity("IfcPropertySetTemplate", GlobalId=ifcopenshell.guid.new())
        IfcStore.pset_template_file = template_file
        PsetTemplatesData.data = {"pset_template_files": [("a", "a", "a")]}
        assert PsetTemplatesData.pset_templates()[0][1] == "Unnamed"

    def test_load_group_without_name(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        group = ifc.create_entity(
            "IfcStructuralLoadGroup", GlobalId=ifcopenshell.guid.new(), PredefinedType="LOAD_CASE"
        )
        ifc.create_entity(
            "IfcStructuralAnalysisModel",
            GlobalId=ifcopenshell.guid.new(),
            PredefinedType="LOADING_3D",
            LoadedBy=[group],
        )
        tool.Structural.get_structural_props().activity_type = "Action"
        assert LoadGroupDecorationData.load_groups_to_show() == [(str(group.id()), ".   L.Case:    ", "")]
