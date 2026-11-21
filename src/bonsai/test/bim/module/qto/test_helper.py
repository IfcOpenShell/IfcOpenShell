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

from bonsai.bim.module.qto.helper import calculate_volumes
from test.bim.bootstrap import NewFile

CUBE_VERTS = [(x, y, z) for x in (0, 2) for y in (0, 2) for z in (0, 2)]
CUBE_FACES = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]


def add_mesh_object(name, faces):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(CUBE_VERTS, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


class TestCalculateVolumes(NewFile):
    def test_skips_a_non_manifold_mesh_and_reports_its_name(self):
        closed = add_mesh_object("Closed", CUBE_FACES)
        open_box = add_mesh_object("Open", CUBE_FACES[:5])
        bpy.context.view_layer.objects.active = closed

        volume, skipped = calculate_volumes([closed, open_box], bpy.context)

        assert round(volume, 5) == 8.0
        assert skipped == ["Open"]
