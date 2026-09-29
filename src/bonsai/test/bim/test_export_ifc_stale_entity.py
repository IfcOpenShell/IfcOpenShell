# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.export_ifc import IfcExporter
from test.bim.bootstrap import NewFile


class TestSyncObjectPlacement(NewFile):
    def test_object_linked_to_a_removed_entity_is_skipped(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        obj = bpy.data.objects.new("Stale", None)
        tool.Blender.get_object_bim_props(obj).ifc_definition_id = 999999
        exporter = IfcExporter(None)
        exporter.file = ifc
        assert exporter.sync_object_placement(obj) is None
