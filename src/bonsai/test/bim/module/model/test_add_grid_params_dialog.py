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

"""Regression coverage for #6232: ``bim.add_grid`` must prompt for its U/V
count and spacing parameters via a props dialog when invoked from the UI
button, instead of silently creating a default 3x3 / 10m grid that only
surfaces its parameters in the easy-to-miss F9 redo panel."""

import bpy
import ifcopenshell
import pytest

import bonsai.tool as tool
from bonsai.bim.module.model.grid import BIM_OT_add_object
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.model


class TestAddGridParamsDialog(NewFile):
    def test_operator_has_invoke_that_raises_a_props_dialog(self):
        # The whole point of the fix: clicking "Add Grids" must invoke a
        # dialog rather than fall straight through to execute() with the
        # class defaults.
        assert "invoke" in vars(BIM_OT_add_object)
        assert "draw" in vars(BIM_OT_add_object)

    def test_execute_with_custom_params_creates_matching_axes(self):
        # Scripted / EXEC_DEFAULT callers (macros, other operators) must be
        # unaffected by the new invoke(): execute() still runs the same
        # underlying logic with whatever properties are passed to it.
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        result = bpy.ops.bim.add_grid(total_u=5, u_spacing=5.0, total_v=2, v_spacing=10.0)

        assert result == {"FINISHED"}
        grid = ifc.by_type("IfcGrid")[0]
        # UAxes / VAxes inverse relationships live on the grid itself.
        assert len(grid.UAxes) == 5
        assert len(grid.VAxes) == 2

        # U axes are horizontal segments (both endpoints share the same Y);
        # their shared Y coordinate is the axis's position, spaced u_spacing apart.
        u_positions = sorted(
            obj.data.vertices[0].co.y
            for obj in bpy.data.objects
            if obj.name.startswith("IfcGridAxis/")
            and obj.data
            and obj.data.vertices[0].co.y == obj.data.vertices[1].co.y
        )
        # 5 U axes at 5-unit spacing: 0, 5, 10, 15, 20.
        expected = [0.0, 5.0, 10.0, 15.0, 20.0]
        assert u_positions == pytest.approx(expected)

    def test_execute_defaults_still_produce_3x3_grid(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()

        result = bpy.ops.bim.add_grid()

        assert result == {"FINISHED"}
        grid = ifc.by_type("IfcGrid")[0]
        assert len(grid.UAxes) == 3
        assert len(grid.VAxes) == 3
