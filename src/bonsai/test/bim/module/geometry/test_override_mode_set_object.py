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

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile, NewIfc

pytestmark = pytest.mark.geometry


def enter_edit_mode_on_new_mesh():
    bpy.ops.mesh.primitive_cube_add()
    bpy.ops.object.mode_set(mode="EDIT")
    assert bpy.context.mode == "EDIT_MESH"


class TestOverrideModeSetObjectWithoutIfc(NewFile):
    def test_direct_profile_edit_exits_edit_mode(self):
        enter_edit_mode_on_new_mesh()
        bpy.ops.bim.direct_profile_edit()
        assert bpy.context.mode == "OBJECT"

    def test_executing_without_invoke_exits_edit_mode(self):
        enter_edit_mode_on_new_mesh()
        bpy.ops.bim.override_mode_set_object()
        assert bpy.context.mode == "OBJECT"


class TestOverrideModeSetObjectWithIfc(NewIfc):
    def test_direct_profile_edit_exits_edit_mode(self):
        assert tool.Ifc.get()
        enter_edit_mode_on_new_mesh()
        bpy.ops.bim.direct_profile_edit()
        assert bpy.context.mode == "OBJECT"

    def test_executing_without_invoke_exits_edit_mode(self):
        assert tool.Ifc.get()
        enter_edit_mode_on_new_mesh()
        bpy.ops.bim.override_mode_set_object()
        assert bpy.context.mode == "OBJECT"
