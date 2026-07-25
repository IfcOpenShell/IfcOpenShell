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

import math

import bpy

from bonsai.tool.raycast import SnapObj
from test.bim.bootstrap import NewFile


def make_disk_object(name: str, n: int, radius: float, center=(0.0, 0.0, 0.0)) -> bpy.types.Object:
    """Build a mesh with a single n-gon face, like a tessellated circular end cap."""
    cx, cy, cz = center
    verts = [
        (cx + radius * math.cos(2 * math.pi * i / n), cy + radius * math.sin(2 * math.pi * i / n), cz) for i in range(n)
    ]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], [tuple(range(n))])
    mesh.update()
    return bpy.data.objects.new(name, mesh)


class TestFindCircleCenters(NewFile):
    def test_finds_the_centre_of_a_round_ngon_cap(self):
        obj = make_disk_object("Cap", n=16, radius=0.5, center=(1.0, 2.0, 3.0))
        snap_obj = SnapObj(obj)
        assert len(snap_obj.circle_centers) == 1
        center = snap_obj.circle_centers[0]
        assert abs(center.x - 1.0) < 1e-6
        assert abs(center.y - 2.0) < 1e-6
        assert abs(center.z - 3.0) < 1e-6

    def test_ignores_triangles_and_quads(self):
        # Small n-gons (n < 8) are never round profile caps in practice, so they
        # should not be treated as circle centres, avoiding false positives on
        # every ordinary triangle/quad face in a mesh.
        obj = make_disk_object("Quad", n=4, radius=0.5)
        snap_obj = SnapObj(obj)
        assert snap_obj.circle_centers == []

    def test_ignores_irregular_non_round_ngon(self):
        mesh = bpy.data.meshes.new("Irregular")
        verts = [
            (0.0, 0.0, 0.0),
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (0.6, 3.0, 0.0),
            (0.0, 1.0, 0.0),
            (-2.0, 0.5, 0.0),
            (-0.5, -1.0, 0.0),
            (0.2, -0.3, 0.0),
        ]
        mesh.from_pydata(verts, [], [tuple(range(len(verts)))])
        mesh.update()
        obj = bpy.data.objects.new("Irregular", mesh)
        snap_obj = SnapObj(obj)
        assert snap_obj.circle_centers == []

    def test_finds_the_centre_of_a_regular_polygon_cap(self):
        # A regular polygon (e.g. an IfcRegularPolygonProfileDef end cap) is also
        # equidistant from its centroid, so it is expected to qualify too.
        obj = make_disk_object("Octagon", n=8, radius=1.0)
        snap_obj = SnapObj(obj)
        assert len(snap_obj.circle_centers) == 1
        center = snap_obj.circle_centers[0]
        assert abs(center.x) < 1e-6
        assert abs(center.y) < 1e-6
