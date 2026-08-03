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

"""Regression tests for #9230: editing a void crashed with
``AttributeError: 'LineString' object has no attribute 'geoms'``.

``shapely.union_all()`` returns a scalar ``LineString``, not a
``MultiLineString``, whenever the dissolved boundary collapses to a single
connected piece -- only multi-part geometries expose ``.geoms``. A curve
with no enclosed area (the simplest case: one still-open edge, which slips
past the ``UNCLOSED_LOOP`` sanity check whenever the mesh has no
IFCARCINDEX/IFCCIRCLE vertex groups at all, since that check is gated
behind ``if deform_layer:``) unions to exactly that scalar LineString.

A prior fix attempt that only guarded the ``.geoms`` access without also
excluding the curve from the odd/even nesting loop further down would have
traded the crash for a worse bug: the loop unconditionally wraps every
curve at nesting level 0 in ``IfcArbitraryClosedProfileDef``, so an open,
never-polygonised curve would silently become a bogus "closed" profile
instead of being dropped."""

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
    # One unclosed edge, no vertex groups: the UNCLOSED_LOOP sanity check
    # is skipped (it is gated behind `if deform_layer:`), so this reaches
    # the shapely union as the crash-triggering single LineString.
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


def test_valid_boundary_survives_stray_unclosed_edge(ifc_file):
    # A real closed square plus an unrelated stray open edge in the same
    # mesh (e.g. leftover geometry from an aborted arc edit). The square
    # must still be detected; the stray edge must not corrupt or block it.
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
