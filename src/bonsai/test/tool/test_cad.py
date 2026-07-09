# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import math

from mathutils import Matrix, Vector

from bonsai.tool.cad import Cad as subject
from test.bim.bootstrap import NewFile

V = lambda *x: Vector([float(i) for i in x])


class TestAreEdgesCollinear(NewFile):
    def test_run(self):
        # fmt: off
        # Parallel edges but not collinear (different z-coordinates)
        assert not subject.are_edges_collinear(
            (V(-1,0,-1), V(1,0,-1)), 
            (V(-1,0,1), V(1,0,1))
        )
        
        # One edge is just a point and the other is a line segment.
        assert not subject.are_edges_collinear(
            (V(1,-1,0), V(1,-1,0)), 
            (V(-1,1,0), V(1,1,0))
        )
        
        # Both edges are collinear and overlap.
        assert subject.are_edges_collinear(
            (V(0,0,0), V(2,2,2)),
            (V(1,1,1), V(3,3,3))
        )

        # Both edges are collinear but don't overlap.
        assert subject.are_edges_collinear(
            (V(0,0,0), V(1,1,1)),
            (V(2,2,2), V(3,3,3))
        )
        
        # Edges are not parallel and not collinear.
        assert not subject.are_edges_collinear(
            (V(0,0,0), V(1,1,1)),
            (V(0,1,0), V(1,0,1))
        )
        # fmt: on


class TestClosestPoints(NewFile):
    def test_run(self):
        # non collinear
        edge1 = (V(0, 0, 0), V(1, 0, 0))
        edge2 = (V(2, 0, 1), V(2, 0, 2))
        assert subject.closest_points(edge1, edge2)[0] == (edge1[1], edge2[0])

        # check other points
        assert subject.closest_points(edge1, edge2)[1] == (edge1[0], edge2[1])

        # collinear
        edge1 = (V(0, 0, 0), V(1, 0, 0))
        edge2 = (V(3, 0, 0), V(2, 0, 0))
        assert subject.closest_points(edge1, edge2)[0] == (edge1[1], edge2[1])

        # parallel
        edge1 = (V(0, 0, 0), V(1, 0, 0))
        edge2 = (V(-5, 0, 0), V(-1, 0, 0))
        assert subject.closest_points(edge1, edge2)[0] == (edge1[0], edge2[1])

        # overlapping
        edge1 = (V(0, 0, 0), V(3, 0, 0))
        edge2 = (V(2, 0, 0), V(5, 0, 0))
        assert subject.closest_points(edge1, edge2)[0] == (edge1[1], edge2[0])

        # edge as a point
        edge1 = (V(0, 0, 0), V(0, 0, 0))
        edge2 = (V(1, 0, 1), V(2, 0, 2))
        assert subject.closest_points(edge1, edge2)[0] == (edge1[0], edge2[0])


class TestObbWorldClipPlanes(NewFile):
    def test_unit_box_at_origin_returns_axis_aligned_planes(self):
        planes = subject.obb_world_clip_planes(
            V(0, 0, 0),
            (V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)),
            V(1, 1, 1),
        )
        assert planes[0] == (-1.0, 0.0, 0.0, 1.0)
        assert planes[1] == (1.0, 0.0, 0.0, 1.0)
        assert planes[2] == (0.0, -1.0, 0.0, 1.0)
        assert planes[3] == (0.0, 1.0, 0.0, 1.0)
        assert planes[4] == (0.0, 0.0, -1.0, 1.0)
        assert planes[5] == (0.0, 0.0, 1.0, 1.0)

    def test_center_is_inside_all_planes(self):
        center = V(5, -3, 2)
        planes = subject.obb_world_clip_planes(
            center,
            (V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)),
            V(2, 1, 0.5),
        )
        assert subject.point_is_inside_clip_planes(planes, center)

    def test_point_just_outside_positive_x_face_rejected(self):
        planes = subject.obb_world_clip_planes(
            V(0, 0, 0),
            (V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)),
            V(1, 1, 1),
        )
        assert subject.point_is_inside_clip_planes(planes, V(0.5, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(1.5, 0, 0))

    def test_rotated_obb_clips_along_rotated_axes(self):
        s = math.sin(math.radians(45))
        planes = subject.obb_world_clip_planes(
            V(0, 0, 0),
            (V(s, s, 0), V(-s, s, 0), V(0, 0, 1)),
            V(1, 1, 1),
        )
        assert subject.point_is_inside_clip_planes(planes, V(1.2, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(1.42, 0, 0))

    def test_zero_extent_axis_does_not_raise(self):
        planes = subject.obb_world_clip_planes(
            V(0, 0, 0),
            (V(1, 0, 0), V(0, 1, 0), V(0, 0, 1)),
            V(1, 1, 0),
        )
        assert subject.point_is_inside_clip_planes(planes, V(0, 0, 0))


class TestObbClipPlanesFromMatrix(NewFile):
    def test_identity_matches_unit_box(self):
        planes = subject.obb_clip_planes_from_matrix(Matrix.Identity(4))
        assert subject.point_is_inside_clip_planes(planes, V(0, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(2, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(0, -2, 0))

    def test_translated_host_shifts_clip_region(self):
        translated = Matrix.Translation(V(10, 0, 0))
        planes = subject.obb_clip_planes_from_matrix(translated)
        assert not subject.point_is_inside_clip_planes(planes, V(0, 0, 0))
        assert subject.point_is_inside_clip_planes(planes, V(10, 0, 0))

    def test_z_rotation_rotates_box(self):
        rot = Matrix.Rotation(math.radians(45), 4, "Z")
        planes = subject.obb_clip_planes_from_matrix(rot)
        assert subject.point_is_inside_clip_planes(planes, V(1.2, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(1.42, 0, 0))

    def test_host_scale_scales_box_extents(self):
        scaled = Matrix.Diagonal((2.0, 2.0, 2.0, 1.0))
        planes = subject.obb_clip_planes_from_matrix(scaled)
        assert subject.point_is_inside_clip_planes(planes, V(1.9, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(2.1, 0, 0))

    def test_non_uniform_scale_axis_independent(self):
        scaled = Matrix.Diagonal((3.0, 1.0, 1.0, 1.0))
        planes = subject.obb_clip_planes_from_matrix(scaled)
        assert subject.point_is_inside_clip_planes(planes, V(2.9, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(3.1, 0, 0))
        assert not subject.point_is_inside_clip_planes(planes, V(0, 1.1, 0))
