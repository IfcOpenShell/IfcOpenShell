# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestOpenLayout(NewFile):
    def test_missing_layout_file_is_reported(self):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        bpy.ops.bim.load_sheets()
        bpy.ops.bim.add_sheet()
        sheet_item = tool.Drawing.get_active_sheet_item()
        sheet = tool.Ifc.get().by_id(sheet_item.ifc_definition_id)
        layout_path = Path(tool.Drawing.get_document_uri(sheet, "LAYOUT"))
        layout_path.unlink()
        with pytest.raises(RuntimeError, match="missing layout"):
            bpy.ops.bim.open_layout()
