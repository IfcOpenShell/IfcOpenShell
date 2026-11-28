# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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

import bmesh
import ifcopenshell

from bonsai.bim.module.geometry.helper import Helper


class TestDetectExtrusionEdge:
    def test_pick_the_edge_most_aligned_with_the_profile_normal(self):
        bm = bmesh.new()
        square = [bm.verts.new(co) for co in ((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0))]
        face = bm.faces.new(square)
        shallow = bm.verts.new((-1, 0, 0.01))
        sweep = bm.verts.new((0, 0, 1))
        bm.edges.new((square[0], shallow))
        bm.edges.new((square[0], sweep))
        bm.verts.index_update()
        bm.normal_update()

        edge = Helper(ifcopenshell.file()).detect_extrusion_edge(bm, face)

        assert edge == [square[0].index, sweep.index]
        bm.free()
