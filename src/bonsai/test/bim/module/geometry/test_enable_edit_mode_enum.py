# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from bonsai.bim.module.geometry.data import ViewportData
from bonsai.bim.module.geometry.operator import OverrideModeSetEdit, OverrideModeSetObject
from test.bim.bootstrap import NewFile


class TestEnableEditModeWithoutEditInEnum(NewFile):
    @pytest.mark.parametrize("operator", [OverrideModeSetEdit, OverrideModeSetObject])
    def test_mode_enum_without_edit_is_tolerated(self, operator, monkeypatch):
        monkeypatch.setattr(tool.Blender, "toggle_edit_mode", lambda context: set())
        monkeypatch.setattr(ViewportData, "data", {"mode": [("OBJECT", "Object", "")]})
        monkeypatch.setattr(ViewportData, "is_loaded", True)
        operator.enable_edit_mode(object(), bpy.context)
        props = tool.Geometry.get_geometry_props()
        assert props.mode == "OBJECT"
        assert props.is_changing_mode is False
