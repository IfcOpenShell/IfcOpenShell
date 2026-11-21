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
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.data import AuthoringData
from bonsai.bim.module.model.workspace import EditObjectUI
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class RecordingLayout:
    def __init__(self):
        self.buttons = []

    def operator(self, idname, **kwargs):
        button = SimpleNamespace(idname=idname)
        self.buttons.append(button)
        return button

    def row(self, **kwargs):
        return self

    def __getattr__(self, name):
        return MagicMock()


class RegionContext:
    def __init__(self, region_type):
        self.region = SimpleNamespace(type=region_type)

    def __getattr__(self, name):
        return getattr(bpy.context, name)


def select(*objs):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[-1]


def drawn_buttons(region_type):
    AuthoringData.is_loaded = False
    layout = RecordingLayout()
    EditObjectUI.draw(RegionContext(region_type), layout)
    return [(button.idname, getattr(button, "hotkey", None)) for button in layout.buttons]


class TestVoidEditButtonsAreDrawnLast(NewFile):
    @pytest.mark.parametrize("region_type", ["TOOL_HEADER", "UI"])
    def test_showing_openings_does_not_move_the_other_buttons(self, region_type):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        wall = bpy.context.active_object
        props = tool.Root.get_root_props()
        props.ifc_product = "IfcElement"
        props.ifc_class = "IfcWall"
        bpy.ops.bim.assign_class()
        bpy.ops.mesh.primitive_cube_add()
        select(bpy.context.active_object, wall)
        bpy.ops.bim.add_opening()
        select(wall)

        buttons_with_openings_hidden = drawn_buttons(region_type)
        bpy.ops.bim.show_openings()
        select(wall)
        buttons_with_openings_shown = drawn_buttons(region_type)

        count = len(buttons_with_openings_hidden)
        assert ("bim.hotkey", "A_O") in buttons_with_openings_hidden
        assert buttons_with_openings_shown[:count] == buttons_with_openings_hidden
        assert buttons_with_openings_shown[count:] == [("bim.edit_openings", None), ("bim.hide_openings", None)]
