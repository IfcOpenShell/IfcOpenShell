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

from test.bim.bootstrap import NewFile
from bonsai.tool.cad import Cad as subject
from mathutils import Vector

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
