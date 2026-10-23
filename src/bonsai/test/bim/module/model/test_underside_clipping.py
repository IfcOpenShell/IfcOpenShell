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

``get_slab_clipping_bmesh`` must keep every downward face however steep."""

from math import cos, radians, sin
from unittest.mock import Mock, patch

import bpy
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
