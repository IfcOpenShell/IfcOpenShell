# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import bpy

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestCurveRaycastDatablockLeak(NewFile):
    def test_object_is_visible_in_clipping_plane_does_not_leak_datablocks(self):
        curve_data = bpy.data.curves.new("TestCurve", type="CURVE")
        curve_data.dimensions = "3D"
        spline = curve_data.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (0.0, 0.0, 0.0, 1.0)
        spline.points[1].co = (1.0, 1.0, 1.0, 1.0)
        obj = bpy.data.objects.new("TestCurveObj", curve_data)
        bpy.context.scene.collection.objects.link(obj)

        n_obj_before = len(bpy.data.objects)
        n_mesh_before = len(bpy.data.meshes)

        for _ in range(10):
            is_vis = tool.Raycast.object_is_visible_in_clipping_plane(obj)
            assert is_vis is True

        assert len(bpy.data.objects) == n_obj_before
        assert len(bpy.data.meshes) == n_mesh_before
        assert not any(o.name.startswith("new_object") for o in bpy.data.objects)
