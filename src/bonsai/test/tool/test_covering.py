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

from bonsai.tool.covering import Covering as subject
from test.bim.bootstrap import NewFile

# A box standing in for a LAYER2 wall mesh: X is length (0..2), Y thickness (0..0.1), Z height (0..3).
LENGTH, THICKNESS, HEIGHT = 2.0, 0.1, 3.0


def _make_wall_obj():
    verts = [
        (0, 0, 0),
        (LENGTH, 0, 0),
        (LENGTH, 0, HEIGHT),
        (0, 0, HEIGHT),  # -Y face (side=-1.0)
        (0, THICKNESS, 0),
        (LENGTH, THICKNESS, 0),
        (LENGTH, THICKNESS, HEIGHT),
        (0, THICKNESS, HEIGHT),  # +Y face (side=1.0)
    ]
    faces = [
        (0, 1, 2, 3),  # -Y
        (7, 6, 5, 4),  # +Y (reversed winding so the normal points the other way)
        (0, 1, 5, 4),  # bottom
        (3, 2, 6, 7),  # top
        (0, 3, 7, 4),  # left end
        (1, 2, 6, 5),  # right end
    ]
    mesh = bpy.data.meshes.new("WallMesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new("Wall", mesh)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.update()
    return obj


class TestGetWallSideFacingCursor(NewFile):
    def test_cursor_on_the_positive_y_side_returns_positive_side(self):
        obj = _make_wall_obj()
        bpy.context.scene.cursor.location = (1.0, THICKNESS + 1.0, 1.0)
        assert subject.get_wall_side_facing_cursor(obj) == 1.0

    def test_cursor_on_the_negative_y_side_returns_negative_side(self):
        obj = _make_wall_obj()
        bpy.context.scene.cursor.location = (1.0, -1.0, 1.0)
        assert subject.get_wall_side_facing_cursor(obj) == -1.0

    def test_cursor_exactly_on_the_wall_centerline_defaults_to_positive_side(self):
        obj = _make_wall_obj()
        center_y = THICKNESS / 2
        bpy.context.scene.cursor.location = (1.0, center_y, 1.0)
        assert subject.get_wall_side_facing_cursor(obj) == 1.0

    def test_respects_the_wall_objects_world_transform(self):
        obj = _make_wall_obj()
        obj.location = (10.0, 10.0, 0.0)
        bpy.context.view_layer.update()
        bpy.context.scene.cursor.location = (11.0, 10.0 + THICKNESS + 1.0, 1.0)
        assert subject.get_wall_side_facing_cursor(obj) == 1.0


class TestGetWallSideFace(NewFile):
    def test_positive_side_returns_only_the_positive_face_polygons(self):
        obj = _make_wall_obj()
        result = subject.get_wall_side_face(obj, 1.0)
        assert result is not None
        face_polys, face_y = result
        assert abs(face_y - THICKNESS) < 1e-5
        assert len(face_polys) == 1
        assert abs(face_polys[0].area - LENGTH * HEIGHT) < 1e-6

    def test_negative_side_returns_only_the_negative_face_polygons(self):
        obj = _make_wall_obj()
        result = subject.get_wall_side_face(obj, -1.0)
        assert result is not None
        face_polys, face_y = result
        assert abs(face_y - 0.0) < 1e-5
        assert len(face_polys) == 1
        assert abs(face_polys[0].area - LENGTH * HEIGHT) < 1e-6

    def test_no_matching_face_returns_none(self):
        mesh = bpy.data.meshes.new("FlatMesh")
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)], [], [(0, 1, 2, 3)])
        mesh.update()
        obj = bpy.data.objects.new("Flat", mesh)
        bpy.context.scene.collection.objects.link(obj)
        bpy.context.view_layer.update()

        assert subject.get_wall_side_face(obj, 1.0) is None
