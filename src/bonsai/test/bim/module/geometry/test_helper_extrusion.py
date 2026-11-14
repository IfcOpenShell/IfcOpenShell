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

import bmesh
import bpy
import ifcopenshell
import pytest

from bonsai.bim.module.geometry.helper import Helper

pytestmark = pytest.mark.geometry


def make_prism_with_duplicated_bottom(offset):
    bm = bmesh.new()
    bottom = [bm.verts.new(co) for co in ((0, 0, 0), (2, 0, 0), (0, 1, 0))]
    top = [bm.verts.new((v.co.x, v.co.y, 1)) for v in bottom]
    bottom_copy = [bm.verts.new((v.co.x + offset, v.co.y, 0)) for v in bottom]
    bm.faces.new(reversed(bottom_copy))
    bm.faces.new(top)
    for i in range(3):
        j = (i + 1) % 3
        bm.faces.new((bottom[i], bottom[j], top[j], top[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new("prism")
    bm.to_mesh(mesh)
    bm.free()
    return mesh


def test_extrusion_is_recovered_from_near_coincident_duplicate_vertices():
    mesh = make_prism_with_duplicated_bottom(1e-3)
    result = Helper(ifcopenshell.file()).auto_detect_arbitrary_closed_profile_extruded_area_solid(mesh)
    assert result["extrusion"] is not None
    assert len(result["profile"]) == 3
