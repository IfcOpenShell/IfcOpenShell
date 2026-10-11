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

from bonsai.bim.module.drawing.operator import CreateDrawing
from test.bim.bootstrap import NewFile

CUBE_FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def add_cube(name, x):
    verts = [(x + i, j, k) for i in (0, 2) for j in (0, 2) for k in (0, 2)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], CUBE_FACES)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


class TestSolidsOverlap(NewFile):
    def test_overlapping_solids_are_detected(self):
        assert CreateDrawing.solids_overlap(None, bpy.context, add_cube("A", 0), add_cube("B", 1))

    def test_touching_solids_are_not_overlapping(self):
        assert not CreateDrawing.solids_overlap(None, bpy.context, add_cube("A", 0), add_cube("B", 2))
