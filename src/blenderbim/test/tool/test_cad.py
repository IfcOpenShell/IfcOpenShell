# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from test.bim.bootstrap import NewFile
from blenderbim.tool.cad import Cad as subject
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
