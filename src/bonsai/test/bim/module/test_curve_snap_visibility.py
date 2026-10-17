# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestCurveSnapVisibility(NewFile):
    def make_curve(self, xs):
        curve = bpy.data.curves.new("Curve", "CURVE")
        spline = curve.splines.new("POLY")
        spline.points.add(len(xs) - 1)
        for point, x in zip(spline.points, xs):
            point.co = (x, 0, 0, 1)
        return bpy.data.objects.new("Curve", curve)

    @pytest.mark.parametrize("xs, expected", [((0, 10), True), ((0, 1), False)])
    def test_visibility_uses_control_points_without_new_datablocks(self, monkeypatch, xs, expected):
        monkeypatch.setattr(tool.Raycast, "point_is_visible_in_clipping_plane", lambda vertex: vertex.x > 5)
        obj = self.make_curve(xs)
        objects, meshes = len(bpy.data.objects), len(bpy.data.meshes)
        assert tool.Raycast.object_is_visible_in_clipping_plane(obj) is expected
        assert (len(bpy.data.objects), len(bpy.data.meshes)) == (objects, meshes)
