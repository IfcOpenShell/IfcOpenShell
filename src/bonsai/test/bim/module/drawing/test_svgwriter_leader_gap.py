# This file was generated with the assistance of an AI coding tool.

import bpy
import pytest

from bonsai.bim.module.drawing.svgwriter import SvgWriter
from test.bim.bootstrap import NewFile


class TestLeaderTextGap(NewFile):
    def make_leader(self, end):
        curve = bpy.data.curves.new("Leader", "CURVE")
        spline = curve.splines.new("POLY")
        spline.points.add(1)
        spline.points[0].co = (0, 0, 0, 1)
        spline.points[1].co = (*end, 1)
        return bpy.data.objects.new("Leader", curve), spline

    def test_gap_points_away_from_the_line(self):
        writer = SvgWriter.__new__(SvgWriter)
        writer.scale = 1 / 100
        obj, spline = self.make_leader((1, 0, 0))
        offset = writer.get_leader_text_gap_offset(obj, spline.points)
        assert tuple(offset) == pytest.approx((-0.15, 0, 0))

    def test_degenerate_leader_has_no_gap(self):
        writer = SvgWriter.__new__(SvgWriter)
        writer.scale = 1 / 100
        obj, spline = self.make_leader((0, 0, 0))
        assert tuple(writer.get_leader_text_gap_offset(obj, spline.points)) == (0, 0, 0)
