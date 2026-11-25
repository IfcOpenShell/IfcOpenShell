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

"""Regression tests for #9230 and #8983.

A curve authored as a closed loop (or a circle) must export as exactly one
polygon or surface ``(False, "INVALID_LOOP")`` -- including on GEOS >= 3.14,
where ``union_all()`` returns a scalar ``LineString`` for a single closed
ring. Stray open geometry is still tolerated and skipped."""

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore

pytestmark = pytest.mark.model


@pytest.fixture
def ifc_file():
    ifc = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject", name="P")
    ifcopenshell.api.unit.assign_unit(ifc)
    previous = IfcStore.file
    IfcStore.file = ifc
    try:
        yield ifc
    finally:
        IfcStore.file = previous


@pytest.fixture(autouse=True)
def _cleanup_bpy_data():
    before_objects = set(bpy.data.objects)
    before_meshes = set(bpy.data.meshes)
    yield
    for obj in set(bpy.data.objects) - before_objects:
        bpy.data.objects.remove(obj)
    for mesh in set(bpy.data.meshes) - before_meshes:
        bpy.data.meshes.remove(mesh)


def _mesh_obj(name, verts, edges):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bm_verts = [bm.verts.new(v) for v in verts]
    bm.verts.ensure_lookup_table()
    for a, b in edges:
        bm.edges.new((bm_verts[a], bm_verts[b]))
    bm.to_mesh(mesh)
    bm.free()
    return obj, mesh


def test_open_edge_without_groups_does_not_crash(ifc_file):
    obj, mesh = _mesh_obj("open_edge", [(0, 0, 0), (1, 0.2, 0)], [(0, 1)])
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert result is None


def test_closed_triangle_still_detected(ifc_file):
    obj, mesh = _mesh_obj(
        "closed_triangle",
        [(0, -1, 0), (1, 0, 0), (0, 1, 0)],
        [(0, 1), (1, 2), (2, 0)],
    )
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    assert result["profile_def"].is_a("IfcArbitraryClosedProfileDef")


def test_closed_quad_still_detected(ifc_file):
    obj, mesh = _mesh_obj(
        "closed_quad",
        [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)],
        [(0, 1), (1, 2), (2, 3), (3, 0)],
    )
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    assert result["profile_def"].is_a("IfcArbitraryClosedProfileDef")


def test_circle_profile_still_detected(ifc_file):
    obj, mesh = _mesh_obj("circle_profile", [(0, 0, 0), (1, 1, 0)], [(0, 1)])
    group = obj.vertex_groups.new(name="IFCCIRCLE")
    group.add([0, 1], 1.0, "REPLACE")
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    assert result["profile_def"].is_a("IfcArbitraryClosedProfileDef")
    assert result["profile_def"].OuterCurve.is_a("IfcCircle")


def test_valid_boundary_survives_stray_unclosed_edge(ifc_file):
    obj, mesh = _mesh_obj(
        "square_plus_stray_edge",
        [
            (-1, -1, 0),
            (1, -1, 0),
            (1, 1, 0),
            (-1, 1, 0),
            (5, 5, 0),
            (6, 5.2, 0),
        ],
        [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5)],
    )
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    assert result["profile_def"].is_a("IfcArbitraryClosedProfileDef")


def test_void_with_hole_still_detected(ifc_file):
    outer = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
    inner = [(-0.25, -0.25, 0), (0.25, -0.25, 0), (0.25, 0.25, 0), (-0.25, 0.25, 0)]
    verts = outer + inner
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)]
    obj, mesh = _mesh_obj("void_with_hole", verts, edges)
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    assert result["profile_def"].is_a("IfcArbitraryProfileDefWithVoids")


def test_nested_voids_still_detected(ifc_file):
    outer = [(-3, -3, 0), (3, -3, 0), (3, 3, 0), (-3, 3, 0)]
    void = [(-2, -2, 0), (2, -2, 0), (2, 2, 0), (-2, 2, 0)]
    island = [(-1, -1, 0), (1, -1, 0), (1, 1, 0), (-1, 1, 0)]
    verts = outer + void + island
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 7),
        (7, 4),
        (8, 9),
        (9, 10),
        (10, 11),
        (11, 8),
    ]
    obj, mesh = _mesh_obj("nested_voids", verts, edges)
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert isinstance(result, dict)
    profile = result["profile_def"]
    assert profile.is_a("IfcCompositeProfileDef")
    assert [p.is_a() for p in profile.Profiles] == [
        "IfcArbitraryProfileDefWithVoids",
        "IfcArbitraryClosedProfileDef",
    ]


def test_degenerate_closed_void_loop_surfaces_a_failure(ifc_file):
    verts = [
        (0, 0, 0),
        (10, 0, 0),
        (10, 10, 0),
        (0, 10, 0),
        (4, 4, 0),
        (5, 4, 0),
        (6, 4, 0),
    ]
    edges = [
        (0, 1),
        (1, 2),
        (2, 3),
        (3, 0),
        (4, 5),
        (5, 6),
        (6, 4),
    ]
    obj, mesh = _mesh_obj("degenerate_closed_void", verts, edges)
    result = tool.Model.auto_detect_profiles(obj, mesh)
    assert result == (False, "INVALID_LOOP"), result
