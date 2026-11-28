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

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.geometry


def add_profile_from_mesh(vertices, faces):
    mesh = bpy.data.meshes.new("Profile")
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new("Profile", mesh)
    bpy.context.scene.collection.objects.link(obj)
    props = tool.Profile.get_profile_props()
    props.profile_classes = "IfcArbitraryClosedProfileDef"
    props.object_to_profile = obj
    bpy.ops.bim.add_profile_def()
    return tool.Ifc.get().by_type("IfcArbitraryClosedProfileDef")[0]


class TestAddProfileDefFromMesh(NewIfc):
    @pytest.mark.parametrize(
        "vertices, faces",
        [
            ([(0, 0, 0), (2, 0, 0), (2, 1, 0), (0, 1, 0)], [(0, 1, 2, 3)]),
            ([(0, 0, 0), (0, 1, 0), (2, 1, 0), (2, 0, 0)], [(0, 1, 2, 3)]),
            ([(0, 0, 0), (2, 0, 0), (2, 1, 0)], [(0, 1, 2)]),
        ],
    )
    def test_a_flat_mesh_without_an_ngon_becomes_the_profile(self, vertices, faces):
        profile = add_profile_from_mesh(vertices, faces)
        points = {tuple(p) for p in profile.OuterCurve.Points.CoordList}
        assert points == {v[:2] for v in vertices}
