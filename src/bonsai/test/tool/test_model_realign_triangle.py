# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import pytest
from mathutils import Matrix, Vector

from bonsai.tool.model import Model as subject
from test.bim.bootstrap import NewFile


def add_object(vertices, edges):
    mesh = bpy.data.meshes.new("Profile")
    mesh.from_pydata(vertices, edges, [])
    obj = bpy.data.objects.new("Profile", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


class TestRealignToTriangleProfile(NewFile):
    def test_an_edited_out_of_plane_triangle_rotates_the_object_onto_its_plane(self):
        edited = [Vector((0, 0, 0)), Vector((1, 0, 0)), Vector((0, 1, 1))]
        obj = add_object(edited, [(0, 1), (1, 2), (2, 0)])
        assert subject.realign_to_triangle_profile(obj, Matrix())
        assert all(vertex.co.z == pytest.approx(0, abs=1e-6) for vertex in obj.data.vertices)
        for vertex, expected in zip(obj.data.vertices, edited):
            assert (obj.matrix_world @ vertex.co - expected).length == pytest.approx(0, abs=1e-6)

    def test_a_flat_triangle_is_left_alone(self):
        obj = add_object([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1), (1, 2), (2, 0)])
        assert not subject.realign_to_triangle_profile(obj, Matrix())

    def test_a_profile_with_more_than_three_vertices_is_left_alone(self):
        obj = add_object([(0, 0, 0), (1, 0, 0), (1, 1, 1), (0, 1, 0)], [(0, 1), (1, 2), (2, 3), (3, 0)])
        assert not subject.realign_to_triangle_profile(obj, Matrix())
