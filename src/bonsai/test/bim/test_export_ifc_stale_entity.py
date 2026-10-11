# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell
import ifcopenshell.api.root

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


class TestSyncAllObjects(NewFile):
    def test_each_synced_element_is_returned_once(self):
        ifc = ifcopenshell.file(schema="IFC4")
        tool.Ifc.set(ifc)
        element = ifcopenshell.api.root.create_entity(ifc, "IfcWall")
        obj = bpy.data.objects.new("Wall", None)
        tool.Ifc.link(element, obj)
        exporter = IfcExporter(None)
        exporter.file = ifc
        exporter.sync_object_placement = lambda obj: element
        assert exporter.sync_all_objects() == [element]


class TestReloadIfcFile(NewFile):
    def test_object_missing_from_the_reloaded_file_is_detached(self, tmp_path):
        old = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(old, "IfcProject")
        wall_type = ifcopenshell.api.root.create_entity(old, "IfcWallType")
        tool.Ifc.set(old)
        obj = bpy.data.objects.new("Type", None)
        tool.Ifc.link(wall_type, obj)
        new = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(new, "IfcProject")
        path = str(tmp_path / "new.ifc")
        new.write(path)
        bpy.ops.bim.reload_ifc_file(filepath=path)
        assert tool.Ifc.get_entity(obj) is None
        assert not tool.Blender.get_object_bim_props(obj).ifc_definition_id
