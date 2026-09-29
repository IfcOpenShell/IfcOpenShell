# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell

import bonsai.bim.schema
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewFile


class TestSavePsetTemplateFile(NewFile):
    def test_schema_reload_uses_the_schema_identifier(self, monkeypatch, tmp_path):
        tool.Ifc.set(ifcopenshell.file(schema="IFC4X3_ADD2"))
        IfcStore.pset_template_file = ifcopenshell.file(schema="IFC4")
        IfcStore.pset_template_path = str(tmp_path / "template.ifc")
        reloaded = []
        monkeypatch.setattr(bonsai.bim.schema, "reload", reloaded.append)
        bpy.ops.bim.save_pset_template_file()
        assert reloaded == ["IFC4X3_ADD2"]
