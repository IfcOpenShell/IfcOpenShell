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

# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class TestExtendToUndersideHotkey(NewFile):
    def test_non_wall_elements_get_a_clear_error(self):
        bpy.ops.bim.create_project()
        objs = []
        for name in ("Column A", "Column B"):
            bpy.ops.mesh.primitive_cube_add()
            obj = bpy.context.active_object
            obj.name = name
            bpy.ops.bim.assign_class(ifc_class="IfcColumn", predefined_type="COLUMN", userdefined_type="")
            objs.append(obj)
        bpy.ops.object.select_all(action="DESELECT")
        for obj in objs:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        assert tool.Ifc.get_entity(objs[0])

        with pytest.raises(RuntimeError, match="Extend to underside works with layered walls"):
            bpy.ops.bim.hotkey(hotkey="S_E")
