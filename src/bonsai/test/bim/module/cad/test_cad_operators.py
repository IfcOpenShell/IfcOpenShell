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

"""Behaviour tests for CadArcFrom3Points (issue #7234): the middle vertex of
the 3-point selection is removed to build the arc, silently deleting any
faces attached to it. These tests pin the warning added for that case and
confirm the original edge-only (no faces) behaviour is unaffected."""

from unittest.mock import Mock

import bmesh
import bpy
import pytest

from bonsai.bim.module.cad.operator import CadArcFrom3Points
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.cad


def _select_verts(bm, indices):
    for v in bm.verts:
        v.select = False
    bm.verts.ensure_lookup_table()
    for i in indices:
        bm.verts[i].select = True
    bm.select_flush(True)


def _run(resolution=1):
    reports = []
    op = Mock()
    op.resolution = resolution
    op.report = lambda level, message: reports.append((set(level), message))
    result = CadArcFrom3Points.execute(op, bpy.context)
    return result, reports


class TestCadArcFrom3PointsWithFace(NewFile):
    def test_warns_and_removes_face_when_middle_vertex_has_faces(self):
        bpy.ops.mesh.primitive_plane_add(size=2)
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        assert len(bm.faces) == 1
        _select_verts(bm, [0, 1, 2])
        bmesh.update_edit_mesh(obj.data)

        result, reports = _run()

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        num_faces = len(bm.faces)
        bpy.ops.object.mode_set(mode="OBJECT")

        assert result == {"FINISHED"}
        assert num_faces == 0
        assert any("WARNING" in level for level, _ in reports)


class TestCadArcFrom3PointsWireOnly(NewFile):
    def test_no_warning_and_arc_built_for_wire_only_selection(self):
        mesh = bpy.data.meshes.new("WireArc")
        obj = bpy.data.objects.new("WireArc", mesh)
        bpy.context.collection.objects.link(obj)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        bm = bmesh.new()
        v0 = bm.verts.new((0, 0, 0))
        v1 = bm.verts.new((1, 1, 0))
        v2 = bm.verts.new((2, 0, 0))
        bm.edges.new((v0, v1))
        bm.edges.new((v1, v2))
        bm.to_mesh(mesh)
        bm.free()

        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        assert len(bm.faces) == 0
        _select_verts(bm, [0, 1, 2])
        bmesh.update_edit_mesh(obj.data)

        result, reports = _run()

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        num_verts = len(bm.verts)
        num_faces = len(bm.faces)
        bpy.ops.object.mode_set(mode="OBJECT")

        assert result == {"FINISHED"}
        assert reports == []
        assert num_verts == 5
        assert num_faces == 0
