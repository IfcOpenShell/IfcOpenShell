# This file was generated with the assistance of an AI coding tool.
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

import bpy
from mathutils import Vector

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAlignLocalXToLength(NewFile):
    def create_wall_long_on_local_y(self) -> bpy.types.Object:
        bpy.ops.bim.create_project()
        bpy.ops.mesh.primitive_cube_add()
        obj = bpy.context.active_object
        obj.dimensions = (0.2, 4.0, 3.0)
        bpy.ops.object.transform_apply(scale=True)
        obj.location = (1.0, 2.0, 0.0)
        bpy.ops.bim.assign_class(obj=obj.name, ifc_class="IfcWall")
        return obj

    def test_long_side_moves_to_local_x_without_moving_the_wall(self):
        obj = self.create_wall_long_on_local_y()
        corners_before = sorted(tuple(round(c, 4) for c in obj.matrix_world @ Vector(v)) for v in obj.bound_box)

        bpy.ops.bim.align_local_x_to_length()

        x_extent, y_extent = tool.Model.get_local_horizontal_extents(obj)
        assert x_extent > y_extent
        corners_after = sorted(tuple(round(c, 4) for c in obj.matrix_world @ Vector(v)) for v in obj.bound_box)
        assert corners_after == corners_before
