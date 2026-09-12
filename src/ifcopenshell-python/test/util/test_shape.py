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

import numpy as np

import ifcopenshell.util.shape as subject


def _cube_verts_faces(size=2.0, z_offset=0.0):
    """Build a triangulated cube as (verts, faces) numpy arrays."""
    s = size / 2
    verts = np.array(
        [
            [-s, -s, -s + z_offset],
            [s, -s, -s + z_offset],
            [s, s, -s + z_offset],
            [-s, s, -s + z_offset],
            [-s, -s, s + z_offset],
            [s, -s, s + z_offset],
            [s, s, s + z_offset],
            [-s, s, s + z_offset],
        ],
        dtype=np.float64,
    )
    faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
            [4, 6, 5],
            [4, 7, 6],
            [0, 4, 5],
            [0, 5, 1],
            [1, 5, 6],
            [1, 6, 2],
            [2, 6, 7],
            [2, 7, 3],
            [3, 7, 4],
            [3, 4, 0],
        ],
        dtype=np.int32,
    )
    return verts, faces


class TestBisectMeshPlaneVf:
    def test_bisect_at_mid_height(self):
        verts, faces = _cube_verts_faces(size=2.0)
        segments = subject.bisect_mesh_plane_vf(verts, faces, plane_z=0.0)
        assert len(segments) >= 4
        for start, end in segments:
            assert len(start) == 2
            assert len(end) == 2

    def test_bisect_above_mesh_returns_empty(self):
        verts, faces = _cube_verts_faces(size=2.0)
        segments = subject.bisect_mesh_plane_vf(verts, faces, plane_z=10.0)
        assert segments == []

    def test_bisect_below_mesh_returns_empty(self):
        verts, faces = _cube_verts_faces(size=2.0)
        segments = subject.bisect_mesh_plane_vf(verts, faces, plane_z=-10.0)
        assert segments == []

    def test_bisect_with_extend(self):
        verts, faces = _cube_verts_faces(size=2.0)
        segments_no_extend = subject.bisect_mesh_plane_vf(verts, faces, plane_z=0.0, extend=0.0)
        segments_extend = subject.bisect_mesh_plane_vf(verts, faces, plane_z=0.0, extend=0.05)
        assert len(segments_extend) == len(segments_no_extend)
        for (s_ext, e_ext), (s_no, e_no) in zip(segments_extend, segments_no_extend):
            assert abs(s_ext[0] - s_no[0]) >= 0.04 or abs(s_ext[1] - s_no[1]) >= 0.04

    def test_bisect_empty_faces(self):
        verts = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
        faces = np.array([], dtype=np.int32).reshape(0, 3)
        assert subject.bisect_mesh_plane_vf(verts, faces, plane_z=0.0) == []

    def test_bisect_precision(self):
        verts, faces = _cube_verts_faces(size=2.0)
        segments = subject.bisect_mesh_plane_vf(verts, faces, plane_z=0.0, precision=6)
        for start, end in segments:
            for coord in start + end:
                assert round(coord, 6) == coord
