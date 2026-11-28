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
from unittest.mock import Mock, patch

import bpy

import bonsai.tool as tool
from bonsai.bim.module.cad.workspace import CadTool

NO_DATA = SimpleNamespace(is_loaded=True, data={"pset_data": None})


def test_plain_mesh_fillet_tooltip_describes_the_mesh_fillet():
    context = Mock()
    context.region.type = "UI"
    hotkeys = []

    with (
        patch.object(tool.Geometry, "is_profile_object_active", return_value=False),
        patch("bonsai.bim.module.cad.workspace.RailingData", NO_DATA),
        patch("bonsai.bim.module.cad.workspace.RoofData", NO_DATA),
        patch("bonsai.bim.module.cad.workspace.add_layout_hotkey_operator", lambda *args: hotkeys.append(args)),
    ):
        CadTool.draw_settings(context, Mock(), None)

    tooltips = {args[1]: args[3] for args in hotkeys}
    assert tooltips["Fillet"] == bpy.ops.bim.cad_fillet.__doc__.split("\n", 1)[1].strip()
