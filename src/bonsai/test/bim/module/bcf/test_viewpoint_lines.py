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

# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace

import bpy

from bonsai.bim.module.bcf.operator import ActivateBcfViewpoint
from test.bim.bootstrap import NewFile


def _viewpoint(*lines):
    def point(x, y, z):
        return SimpleNamespace(x=x, y=y, z=z)

    line = [SimpleNamespace(start_point=point(*a), end_point=point(*b)) for a, b in lines]
    return SimpleNamespace(visualization_info=SimpleNamespace(lines=SimpleNamespace(line=line)))


class TestViewpointLines(NewFile):
    def test_lines_are_drawn_as_an_object(self):
        viewpoint = _viewpoint(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)), ((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)))
        ActivateBcfViewpoint.draw_lines(None, viewpoint, bpy.context)
        obj = bpy.data.objects["BCF"]
        drawing = obj.data.layers[0].frames[0].drawing
        assert len(drawing.attributes["position"].data) == 4

    def test_lines_are_removed_before_redrawing(self):
        viewpoint = _viewpoint(((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)))
        ActivateBcfViewpoint.draw_lines(None, viewpoint, bpy.context)
        ActivateBcfViewpoint.delete_lines(None)
        assert "BCF" not in bpy.data.objects
        assert "BCF" not in bpy.data.grease_pencils
