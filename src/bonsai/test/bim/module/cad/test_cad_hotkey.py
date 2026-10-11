# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace
from unittest.mock import MagicMock

import bpy

import bonsai.tool as tool
from bonsai.bim.module.cad.operator import CadArcFrom2Points
from bonsai.bim.module.cad.workspace import CadHotkey
from test.bim.bootstrap import NewFile


class TestCadHotkey(NewFile):
    def test_the_2_point_arc_hotkey_passes_the_arc_resolution_to_the_arc_operator(self, monkeypatch):
        resolutions = []

        def execute(operator, context):
            resolutions.append(operator.resolution)
            return {"FINISHED"}

        monkeypatch.setattr(CadArcFrom2Points, "execute", execute)
        bpy.ops.mesh.primitive_plane_add()
        tool.Cad.get_cad_props().resolution = 5
        bpy.ops.bim.cad_hotkey(hotkey="S_C")
        assert resolutions == [5]

    def test_the_2_point_arc_redo_panel_shows_the_arc_resolution(self):
        layout = MagicMock()
        bpy.ops.mesh.primitive_plane_add()
        CadHotkey.draw(SimpleNamespace(hotkey="S_C", layout=layout), bpy.context)
        layout.row.return_value.prop.assert_called_once_with(tool.Cad.get_cad_props(), "resolution")
