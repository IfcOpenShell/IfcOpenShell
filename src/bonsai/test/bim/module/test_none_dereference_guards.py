# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root

import bonsai.tool as tool
from bonsai.bim.module.classification.data import ReferencesData
from test.bim.bootstrap import NewFile


class TestNoneDereferenceGuards(NewFile):
    def test_classification_without_name(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        classification = ifc.createIfcClassification()
        assert ReferencesData.classifications() == [(str(classification.id()), "Unnamed", "")]

    def test_select_type_without_blender_object(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        wall_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWallType")
        assert bpy.ops.bim.select_type(relating_type=wall_type.id()) == {"CANCELLED"}
