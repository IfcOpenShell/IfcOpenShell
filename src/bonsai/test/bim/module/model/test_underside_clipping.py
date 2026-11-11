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

"""Steep undersides for Extend Walls To Underside (#10038).

``get_slab_clipping_bmesh`` must keep every downward face however steep, and
``clip_wall_to_slabs`` must not push a clip solid below its own face, or a
roof's eave cut reaches back under the steep underside and notches the wall."""

from math import cos, radians, sin
from unittest.mock import Mock, patch

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import numpy as np
import pytest
from mathutils import Vector

import bonsai.tool as tool

pytestmark = pytest.mark.model


def _down_quad(origin, slope_deg, length=10.0, width=2.0):
    """Corners of a downward-facing quad rising from ``origin`` toward -X at ``slope_deg``."""
    a = radians(slope_deg)
    up = Vector((-cos(a), 0, sin(a))) * length
    across = Vector((0, width, 0))
    o = Vector(origin)
    # up x across points down.
    return [o, o + up, o + up + across, o + across]


def test_slab_clipping_keeps_steep_undersides_but_not_vertical_faces():
    quads = [
        _down_quad((0, 0, 0), 80),
        _down_quad((20, 0, 0), 61),
        _down_quad((40, 0, 0), 30),
        _down_quad((60, 0, 0), 90),  # vertical
    ]
    verts = [tuple(v) for q in quads for v in q]
    faces = [tuple(range(i * 4, i * 4 + 4)) for i in range(len(quads))]
    mesh = bpy.data.meshes.new("underside")
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new("underside", mesh)
    try:
        with (
            patch("bonsai.tool.model.tool.Ifc.get", return_value=Mock()),
            patch("bonsai.tool.model.ifcopenshell.util.unit.calculate_unit_scale", return_value=1.0),
        ):
            clip = tool.Model.get_slab_clipping_bmesh(obj)
        assert clip is not None
        assert len(clip.faces) == 3
        clip.free()
    finally:
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)


def _wall_file():
    ifc = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc)
    model = ifcopenshell.api.context.add_context(ifc, context_type="Model")
    body = ifcopenshell.api.context.add_context(
        ifc, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
    )
    wall = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcWall")
    ifcopenshell.api.geometry.edit_object_placement(ifc, product=wall)
    rep = ifcopenshell.api.geometry.add_wall_representation(ifc, context=body, length=10, height=3, thickness=0.2)
    ifcopenshell.api.geometry.assign_representation(ifc, product=wall, representation=rep)
    return ifc, wall


def test_clip_solids_do_not_extend_below_their_faces():
    """A steep underside and the shallow eave cut below it, sharing the eave edge at z=4."""
    eave_z = 4.0
    bm = bmesh.new()
    a, b = bm.verts.new((8, -1, eave_z)), bm.verts.new((8, 1.2, eave_z))
    steep = radians(80)
    c = bm.verts.new((8 - 10 * cos(steep), 1.2, eave_z + 10 * sin(steep)))
    d = bm.verts.new((8 - 10 * cos(steep), -1, eave_z + 10 * sin(steep)))
    eave = radians(10)
    e = bm.verts.new((9, 1.2, eave_z + sin(eave) / cos(eave)))
    f = bm.verts.new((9, -1, eave_z + sin(eave) / cos(eave)))
    bm.faces.new([a, b, c, d])
    bm.faces.new([b, a, f, e])
    ridge_z = d.co.z

    ifc, wall = _wall_file()
    with (
        patch("bonsai.tool.model.tool.Ifc.get", return_value=ifc),
        patch.object(tool.Model, "mark_manual_booleans"),
    ):
        tool.Model.clip_wall_to_slabs(wall, [bm])
    bm.free()

    leaves = ifc.by_type("IfcPolygonalFaceSet")
    assert len(leaves) == 2
    bottom_zs = []
    for leaf in leaves:
        zs = np.array(leaf.Coordinates.CoordList)[:, 2]
        bottom_zs.extend(zs[zs < zs.max() - 1e-6])
    # Nothing below the eave edge: no downslope margin.
    assert min(bottom_zs) >= eave_z - 1e-6
    # Still reaching past the top of the steep face: the upslope (ridge) margin stays.
    assert max(bottom_zs) > ridge_z + 0.5
