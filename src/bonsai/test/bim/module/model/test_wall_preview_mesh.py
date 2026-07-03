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

"""Pins the outward-normals invariant of the parametric-wall draft preview mesh.

``regenerate_wall_mesh_from_props`` rebuilds ``obj.data`` as a fresh bmesh
box from ``BIMWallProperties`` every time a gizmo handle moves. The hand
authored face windings carry no guarantee of outward orientation, so the
function must normalise face windings before writing the mesh back —
otherwise the viewport renders the draft with inverted shading and
back-face culling hides faces the user expects to see."""

import types
from unittest.mock import patch

import bpy
import pytest
from mathutils import Vector

pytestmark = pytest.mark.wall


def test_regenerate_wall_mesh_from_props_outward_normals():
    """Every face of the preview box must have its normal pointing away
    from the box centroid — the contract every other preview-mesh builder
    in ``bim/module/model`` (door / window / roof / railing) holds."""
    from bonsai.bim.module.model.wall import regenerate_wall_mesh_from_props

    mesh = bpy.data.meshes.new("preview_mesh")
    obj = bpy.data.objects.new("preview_wall", mesh)
    fake_props = types.SimpleNamespace(
        length=2.0,
        height=3.0,
        thickness=0.2,
        offset=0.0,
        x_angle=0.0,
        anchor_x=0.0,
        mesh_dirty=False,
    )

    try:
        with patch("bonsai.tool.Model.get_wall_props", return_value=fake_props):
            regenerate_wall_mesh_from_props(obj)

        assert len(mesh.polygons) == 6, f"expected 6 faces, got {len(mesh.polygons)}"
        centroid = sum((v.co for v in mesh.vertices), Vector()) / len(mesh.vertices)
        for face in mesh.polygons:
            outward = (face.center - centroid).normalized()
            dot = face.normal.dot(outward)
            assert dot > 0.5, (
                f"face {face.index} normal {tuple(face.normal)} points inward "
                f"(outward direction {tuple(outward)}, dot={dot:.3f})"
            )
    finally:
        bpy.data.objects.remove(obj)
        bpy.data.meshes.remove(mesh)
