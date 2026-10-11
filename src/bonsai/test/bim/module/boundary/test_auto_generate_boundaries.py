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

from functools import partial

import bpy

import bonsai.tool as tool
from bonsai.bim.module.boundary.operator import AddBoundary
from test.bim.bootstrap import NewFile


class OperatorSelf:
    def __getattr__(self, name):
        return partial(getattr(AddBoundary, name), self)


class TestAutoGenerateBoundaries(NewFile):
    def add_box(self, ifc_class, location, dimensions):
        bpy.ops.mesh.primitive_cube_add(size=1, location=location)
        obj = bpy.context.active_object
        obj.dimensions = dimensions
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        bpy.ops.bim.assign_class(ifc_class=ifc_class)
        return obj

    def test_a_curtain_wall_next_to_a_space_gets_a_boundary(self):
        bpy.ops.bim.create_project()
        space_obj = self.add_box("IfcSpace", (2, 2, 1.5), (4, 4, 3))
        self.add_box("IfcCurtainWall", (4.05, 2, 1.5), (0.1, 4, 3))
        space = tool.Ifc.get_entity(space_obj)
        operator = OperatorSelf()
        boundaries = AddBoundary.auto_generate_boundaries(operator, space, space_obj)
        assert [b.RelatedBuildingElement.is_a() for b in boundaries] == ["IfcCurtainWall"]
