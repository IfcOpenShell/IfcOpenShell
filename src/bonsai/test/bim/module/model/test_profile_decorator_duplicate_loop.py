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

"""Regression tests for ``ProfileDecorator``'s ``_connected_components`` helper.

Duplicating a circle/arc void's loop in Edit Mode (Tab, Tab, select the
loop, Shift+D) copies the ``IFCARCINDEX``/``IFCCIRCLE`` vertex-group
weights onto the new geometry, since Blender's mesh duplicate never
allocates a new vertex group. Before this fix, ``ProfileDecorator``
grouped arc/circle vertices by group index alone, so the duplicate's
vertices piled into the same entry as the source loop's, failing the
"exactly 2/3 verts" check and silently dropping *both* loops from the
decorator until the mesh was re-imported (e.g. by leaving and re-entering
Edit Mode). ``_connected_components`` splits each group's vertices back
into their connected loops so a duplicate is drawn immediately, see #6944."""

import bmesh
import bpy
import pytest

from bonsai.bim.module.model.decorator import _connected_components

pytestmark = pytest.mark.model


def _bm_with_groups(verts, edges, groups):
    """Build a standalone bmesh with a deform layer, and populate ``groups``:
    a list of (group_index, [vert_indices]) pairs, mirroring how
    ``tool.Model.import_profile``/``convert_curve_to_mesh`` assign one
    vertex group per circle/arc loop."""
    bm = bmesh.new()
    deform_layer = bm.verts.layers.deform.new()
    bm_verts = [bm.verts.new(v) for v in verts]
    bm.verts.ensure_lookup_table()
    for a, b in edges:
        bm.edges.new((bm_verts[a], bm_verts[b]))
    bm.verts.ensure_lookup_table()
    bm_verts = list(bm.verts)
    for group_index, vert_indices in groups:
        for vi in vert_indices:
            bm_verts[vi][deform_layer][group_index] = 1.0
    return bm, bm_verts, deform_layer


def _group_dict(bm_verts, deform_layer, group_index, vert_indices):
    return {group_index: [bm_verts[i] for i in vert_indices]}


def test_single_circle_loop_is_one_component():
    # A circle is exactly 2 verts joined by 1 edge (tool.Model.convert_curve_to_mesh).
    bm, bm_verts, deform_layer = _bm_with_groups(
        verts=[(0, -1, 0), (0, 1, 0)],
        edges=[(0, 1)],
        groups=[(0, [0, 1])],
    )
    circles = _group_dict(bm_verts, deform_layer, 0, [0, 1])
    components = _connected_components(circles)
    assert len(components) == 1
    assert len(components[0]) == 2
    bm.free()


def test_single_arc_loop_is_one_component():
    # An arc is exactly 3 verts: endpoint-midpoint-endpoint (2 edges).
    bm, bm_verts, deform_layer = _bm_with_groups(
        verts=[(0, -1, 0), (0, 0, 0.3), (0, 1, 0)],
        edges=[(0, 1), (1, 2)],
        groups=[(0, [0, 1, 2])],
    )
    arcs = _group_dict(bm_verts, deform_layer, 0, [0, 1, 2])
    components = _connected_components(arcs)
    assert len(components) == 1
    assert len(components[0]) == 3
    bm.free()


def test_duplicated_circle_loop_splits_into_two_components():
    # Duplicating verts 0-1 (Shift+D) yields verts 2-3, connected to each
    # other but NOT to the source loop, while keeping the same group index
    # (0) -- exactly what bmesh.ops.duplicate produces mid Edit-Mode.
    bm, bm_verts, deform_layer = _bm_with_groups(
        verts=[(0, -1, 0), (0, 1, 0), (5, -1, 0), (5, 1, 0)],
        edges=[(0, 1), (2, 3)],
        groups=[(0, [0, 1, 2, 3])],
    )
    circles = _group_dict(bm_verts, deform_layer, 0, [0, 1, 2, 3])
    components = _connected_components(circles)
    assert len(components) == 2
    assert sorted(len(c) for c in components) == [2, 2]
    bm.free()


def test_duplicated_arc_loop_splits_into_two_components():
    bm, bm_verts, deform_layer = _bm_with_groups(
        verts=[(0, -1, 0), (0, 0, 0.3), (0, 1, 0), (5, -1, 0), (5, 0, 0.3), (5, 1, 0)],
        edges=[(0, 1), (1, 2), (3, 4), (4, 5)],
        groups=[(0, [0, 1, 2, 3, 4, 5])],
    )
    arcs = _group_dict(bm_verts, deform_layer, 0, [0, 1, 2, 3, 4, 5])
    components = _connected_components(arcs)
    assert len(components) == 2
    assert sorted(len(c) for c in components) == [3, 3]
    bm.free()


def test_distinct_circle_groups_stay_separate_and_correctly_sized():
    # Multiple genuinely different circles (distinct group indices) must
    # each still resolve to their own single 2-vert component.
    verts = []
    edges = []
    groups = []
    for i in range(5):
        base = len(verts)
        verts += [(i * 3, -1, 0), (i * 3, 1, 0)]
        edges.append((base, base + 1))
        groups.append((i, [base, base + 1]))
    bm, bm_verts, deform_layer = _bm_with_groups(verts, edges, groups)
    circles = {}
    for group_index, vert_indices in groups:
        circles[group_index] = [bm_verts[i] for i in vert_indices]
    components = _connected_components(circles)
    assert len(components) == 5
    assert all(len(c) == 2 for c in components)
    bm.free()
