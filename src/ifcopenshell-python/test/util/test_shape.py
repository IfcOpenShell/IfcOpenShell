# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.
# This file was generated with the assistance of an AI coding tool.

import math

import ifcopenshell.util.shape as subject


class FakeTriangulation:
    """A minimal stand-in for W.triangulation, exposing only what get_volume/is_manifold use."""

    def __init__(self, verts: list[tuple[float, float, float]], faces: list[tuple[int, int, int]]):
        self.verts = [c for v in verts for c in v]
        self.faces = [i for tri in faces for i in tri]


def cube(size: float = 1.0) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]:
    s = size
    verts = [
        (0, 0, 0),
        (s, 0, 0),
        (s, s, 0),
        (0, s, 0),
        (0, 0, s),
        (s, 0, s),
        (s, s, s),
        (0, s, s),
    ]
    faces = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (3, 7, 6),
        (3, 6, 2),
        (0, 4, 7),
        (0, 7, 3),
        (1, 2, 6),
        (1, 6, 5),
    ]
    return verts, faces


class TestIsManifold:
    def test_closed_consistently_wound_mesh_is_manifold(self):
        verts, faces = cube()
        assert subject.is_manifold(FakeTriangulation(verts, faces)) is True

    def test_closed_mesh_with_duplicated_vertex_positions_is_manifold(self):
        verts, faces = cube()
        unwelded_verts = [verts[i] for tri in faces for i in tri]
        unwelded_faces = [(i, i + 1, i + 2) for i in range(0, len(unwelded_verts), 3)]
        assert subject.is_manifold(FakeTriangulation(unwelded_verts, unwelded_faces)) is True

    def test_solids_touching_along_an_edge_are_manifold(self):
        verts, faces = cube()
        neighbour = [(x + 1, y + 1, z) for x, y, z in verts]
        faces = faces + [(a + 8, b + 8, c + 8) for a, b, c in faces]
        assert subject.is_manifold(FakeTriangulation(verts + neighbour, faces)) is True

    def test_open_mesh_is_not_manifold(self):
        verts, faces = cube()
        geometry = FakeTriangulation(verts, faces[:-1])
        assert subject.is_manifold(geometry) is False

    def test_inconsistent_winding_is_not_manifold(self):
        verts, faces = cube()
        faces = list(faces)
        i = faces.index((1, 2, 6))
        faces[i] = (1, 6, 2)
        geometry = FakeTriangulation(verts, faces)
        assert subject.is_manifold(geometry) is False


class TestGetVolume:
    def test_manifold_cube_volume(self):
        verts, faces = cube(size=2)
        geometry = FakeTriangulation(verts, faces)
        assert math.isclose(subject.get_volume(geometry), 8.0, rel_tol=1e-9)

    def test_open_mesh_returns_nan(self):
        verts, faces = cube()
        geometry = FakeTriangulation(verts, faces[:-1])
        assert math.isnan(subject.get_volume(geometry))

    def test_inconsistent_winding_returns_nan_instead_of_wrong_value(self):
        verts, faces = cube()
        faces = list(faces)
        i = faces.index((1, 2, 6))
        faces[i] = (1, 6, 2)
        geometry = FakeTriangulation(verts, faces)
        assert math.isnan(subject.get_volume(geometry))
