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

from types import SimpleNamespace

import bpy
import svgwrite

from bonsai.bim.module.drawing.svgwriter import SvgWriter


def test_stair_label_carries_the_annotation_classes():
    curve = bpy.data.curves.new("Stair", "CURVE")
    spline = curve.splines.new("POLY")
    spline.points.add(1)
    spline.points[0].co = (0, 0, 0, 1)
    spline.points[1].co = (1, 0, 0, 1)
    obj = bpy.data.objects.new("Stair", curve)
    fake_self = SimpleNamespace(
        raw_width=1,
        raw_height=1,
        svg_scale=1,
        svg=svgwrite.Drawing(),
        get_attribute_classes=lambda obj: ["GlobalId-abc", "EPsetStatusStatus-NEW"],
        get_spline_points=lambda spline: spline.points,
        project_point_onto_camera=lambda point: point,
    )

    SvgWriter.draw_stair_annotation(fake_self, obj)

    assert 'class="GlobalId-abc EPsetStatusStatus-NEW STAIR"' in fake_self.svg.tostring()
