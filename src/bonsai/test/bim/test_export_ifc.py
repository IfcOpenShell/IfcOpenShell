from unittest.mock import MagicMock, patch

import ifcopenshell

import bonsai.tool as tool
from bonsai.bim.export_ifc import IfcExporter


class TestSyncObjectPlacement:
    def test_missing_instance_returns_none(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        exporter = IfcExporter(MagicMock())
        exporter.file = ifc_file

        obj = MagicMock()
        bim_props = MagicMock()
        bim_props.ifc_definition_id = 7548

        with patch.object(tool.Blender, "get_object_bim_props", return_value=bim_props):
            assert exporter.sync_object_placement(obj) is None

    def test_zero_definition_id_returns_none(self):
        ifc_file = ifcopenshell.file(schema="IFC4")
        exporter = IfcExporter(MagicMock())
        exporter.file = ifc_file

        obj = MagicMock()
        bim_props = MagicMock()
        bim_props.ifc_definition_id = 0

        with patch.object(tool.Blender, "get_object_bim_props", return_value=bim_props):
            assert exporter.sync_object_placement(obj) is None
