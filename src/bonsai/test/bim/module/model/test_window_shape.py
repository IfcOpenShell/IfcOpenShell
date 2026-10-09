# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import json

import bpy
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.window import update_window_modifier_representation
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class TestWindowShape(NewFile):
    def add_window(self):
        bpy.ops.bim.create_project()
        bpy.ops.mesh.add_window()
        obj = bpy.context.active_object
        props = tool.Model.get_window_props(obj)
        return obj, props

    def test_round_window_height_follows_the_width(self):
        obj, props = self.add_window()
        props.window_shape = "ROUND"
        props.overall_width = 0.8
        props.overall_height = 1.5
        update_window_modifier_representation(bpy.context)
        element = tool.Ifc.get_entity(obj)
        assert element.OverallWidth == pytest.approx(0.8)
        assert element.OverallHeight == pytest.approx(0.8)

    def test_arch_window_apex_is_at_the_overall_height(self):
        obj, props = self.add_window()
        props.overall_width = 1.0
        props.overall_height = 1.6
        update_window_modifier_representation(bpy.context)
        rectangle_vertex_count = len(obj.data.vertices)
        props.window_shape = "ARCH"
        update_window_modifier_representation(bpy.context)
        element = tool.Ifc.get_entity(obj)
        assert len(obj.data.vertices) > rectangle_vertex_count * 2
        assert element.OverallHeight == pytest.approx(1.6)
        assert obj.dimensions.x == pytest.approx(1.0, abs=1e-2)
        assert obj.dimensions.z == pytest.approx(1.6, abs=2e-2)

    def test_non_rectangular_shape_forces_a_single_panel(self):
        _, props = self.add_window()
        props.window_type = "DOUBLE_PANEL_VERTICAL"
        props.window_shape = "ARCH"
        assert props.window_type == "SINGLE_PANEL"

    def test_shape_is_stored_in_the_window_pset(self):
        obj, props = self.add_window()
        bpy.ops.bim.enable_editing_window()
        props.window_shape = "ROUND"
        bpy.ops.bim.finish_editing_window()
        element = tool.Ifc.get_entity(obj)
        data = json.loads(ifcopenshell.util.element.get_pset(element, "BBIM_Window", "Data"))
        assert data["window_shape"] == "ROUND"
