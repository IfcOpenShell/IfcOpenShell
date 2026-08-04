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

"""Regression tests for #9230 and #8983: two symptoms of the same missing
guard in ``auto_detect_profiles()`` -- a curve whose loop doesn't resolve to
exactly one simple polygon must not be silently promoted, dropped, or
arbitrarily resolved.

#9230: editing a void crashed with ``AttributeError: 'LineString' object
has no attribute 'geoms'``. ``shapely.union_all()`` returns a scalar
``LineString``, not a ``MultiLineString``, whenever the dissolved boundary
collapses to a single connected piece -- only multi-part geometries expose
``.geoms``. A curve with no enclosed area (the simplest case: one still-open
edge, which slips past the ``UNCLOSED_LOOP`` sanity check whenever the mesh
has no IFCARCINDEX/IFCCIRCLE vertex groups at all, since that check is
gated behind ``if deform_layer:``) unions to exactly that scalar LineString.

A prior fix attempt that only guarded the ``.geoms`` access without also
excluding the curve from the odd/even nesting loop further down would have
traded the crash for a worse bug: the loop unconditionally wraps every
curve at nesting level 0 in ``IfcArbitraryClosedProfileDef``, so an open,
never-polygonised curve would silently become a bogus "closed" profile
instead of being dropped.

#8983: a curve that IS authored as a closed loop (e.g. a void boundary),
but is degenerate (collinear points, encloses zero area), also fails to
polygonise -- but unlike a stray open edge, it was clearly meant to enclose
an area. Silently dropping it (matching the #9230 fix's tolerance for
open, never-closed stray geometry) would quietly turn a boundary-with-void
into a boundary-without-void, with nothing shown to the user. `curves` that
were authored closed (or a circle, always closed) must resolve to exactly
one polygon or surface ``(False, "INVALID_LOOP")``; only curves that were
never closed to begin with are tolerated and skipped."""

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


def test_degenerate_closed_void_loop_surfaces_a_failure(ifc_file):
    # #8983: a genuine 10x10 outer square, plus a "void" that IS a closed
    # loop (3 collinear points along y=4, closing back on itself) but
    # encloses zero area. Unlike the stray open edge above, this loop was
    # authored closed, so it must not be silently dropped.
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
