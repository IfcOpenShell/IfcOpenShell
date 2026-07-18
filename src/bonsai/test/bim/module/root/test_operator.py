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

"""Regression tests for #7453: converting an arbitrary mesh into an IfcWall
must line up the mesh's actual longest horizontal dimension with Bonsai's
wall-length convention (local +X = length/axis, local Y = thickness, see
``tool.Model.get_wall_axis``), instead of blindly trusting whichever local
axis the mesh happened to be authored along. Getting this wrong swaps the
wall's effective length and thickness for every downstream consumer of that
convention (window/door snapping, layer offsets, etc)."""

import bpy
import pytest
from mathutils import Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.root


def _convert_cube_to_wall(dimensions: tuple[float, float, float]) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, dimensions[2] / 2))
    obj = bpy.context.active_object
    obj.dimensions = dimensions
    bpy.context.view_layer.update()
    bpy.ops.bim.assign_class(ifc_class="IfcWall", predefined_type="", userdefined_type="")
    return obj


def _local_xy_extents(obj: bpy.types.Object) -> tuple[float, float]:
    xs = [v[0] for v in obj.bound_box]
    ys = [v[1] for v in obj.bound_box]
    return max(xs) - min(xs), max(ys) - min(ys)


class TestAssignClassWallOrientation(NewIfc):
    def test_swapped_footprint_is_reoriented_so_local_x_is_the_long_axis(self):
        # Authored with the long (3m) dimension along local Y and the short
        # (300mm) dimension along local X - the exact #7453 repro shape.
        obj = _convert_cube_to_wall((0.3, 3.0, 3.0))

        x_extent, y_extent = _local_xy_extents(obj)
        assert x_extent == pytest.approx(3.0, abs=1e-3), "local X should now carry the wall's long dimension"
        assert y_extent == pytest.approx(0.3, abs=1e-3), "local Y should now carry the wall's short dimension"

        element = tool.Ifc.get_entity(obj)
        layers = tool.Model.get_material_layer_parameters(element)
        axes = tool.Model.get_wall_axis(obj, layers=layers)
        reference_length = (axes["reference"][1] - axes["reference"][0]).length
        assert reference_length == pytest.approx(
            3.0, abs=1e-3
        ), "wall axis snapping must use the real 3m length, not the 300mm thickness"

        # World-space footprint (what the user actually sees/authored) must be unchanged.
        world_pts = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
        world_x = max(p[0] for p in world_pts) - min(p[0] for p in world_pts)
        world_y = max(p[1] for p in world_pts) - min(p[1] for p in world_pts)
        assert world_x == pytest.approx(0.3, abs=1e-3)
        assert world_y == pytest.approx(3.0, abs=1e-3)

    def test_already_correct_footprint_is_left_untouched(self):
        # Long dimension already along local X - must not be rotated at all.
        obj = _convert_cube_to_wall((3.0, 0.3, 3.0))

        x_extent, y_extent = _local_xy_extents(obj)
        assert x_extent == pytest.approx(3.0, abs=1e-3)
        assert y_extent == pytest.approx(0.3, abs=1e-3)
        assert tuple(obj.rotation_euler) == (0.0, 0.0, 0.0)

    def test_square_footprint_is_left_as_is(self):
        # No unambiguous "longer" axis - must not crash and must not rotate.
        obj = _convert_cube_to_wall((2.0, 2.0, 3.0))

        x_extent, y_extent = _local_xy_extents(obj)
        assert x_extent == pytest.approx(2.0, abs=1e-3)
        assert y_extent == pytest.approx(2.0, abs=1e-3)

    def test_non_wall_class_is_not_reoriented(self):
        # The convention (and this fix) is wall-specific. A swapped-looking
        # footprint on another class must be imported as-is.
        bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0, 0, 1.5))
        obj = bpy.context.active_object
        obj.dimensions = (0.3, 3.0, 3.0)
        bpy.context.view_layer.update()
        bpy.ops.bim.assign_class(ifc_class="IfcSlab", predefined_type="", userdefined_type="")

        x_extent, y_extent = _local_xy_extents(obj)
        assert x_extent == pytest.approx(0.3, abs=1e-3)
        assert y_extent == pytest.approx(3.0, abs=1e-3)
