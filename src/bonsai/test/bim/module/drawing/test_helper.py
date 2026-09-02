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

import ifcopenshell
import mathutils
import pytest

import bonsai.bim.module.drawing.helper as helper
import bonsai.tool as tool
from bonsai.tool.drawing import Drawing as subject
from test.bim.bootstrap import NewFile


class TestOrthoViewFrame(NewFile):
    def make_camera(self, ortho_scale: float, diagram_scale: str = "1:100|1/100"):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        camera = subject.create_camera("Camera", mathutils.Matrix(), 0, "PLAN_VIEW")
        camera.data.ortho_scale = ortho_scale
        tool.Drawing.get_camera_props(camera.data).diagram_scale = diagram_scale
        return camera

    def test_it_reserves_a_fixed_paper_space_margin_regardless_of_drawing_scale(self):
        camera = self.make_camera(ortho_scale=50.0, diagram_scale="1:100|1/100")

        xmin, xmax, ymin, ymax = helper.ortho_view_frame(camera.data)[:4]

        scale = helper.parse_diagram_scale(camera.data)
        half_width = camera.data.ortho_scale / 2
        margin_mm_on_paper = (half_width - xmax) * scale * 1000
        assert margin_mm_on_paper == pytest.approx(20.0)
        assert xmin == pytest.approx(-xmax)
        assert ymin == pytest.approx(-ymax)

    def test_the_paper_space_margin_is_the_same_at_a_smaller_drawing_scale(self):
        # A fixed physical symbol size on paper needs more world space to be
        # left clear the smaller the drawing scale is (e.g. 1:200 vs 1:100).
        camera = self.make_camera(ortho_scale=100.0, diagram_scale="1:200|1/200")

        xmin, xmax, ymin, ymax = helper.ortho_view_frame(camera.data)[:4]

        scale = helper.parse_diagram_scale(camera.data)
        half_width = camera.data.ortho_scale / 2
        margin_mm_on_paper = (half_width - xmax) * scale * 1000
        assert margin_mm_on_paper == pytest.approx(20.0)

    def test_it_does_not_invert_the_bounds_for_a_camera_smaller_than_the_margin(self):
        camera = self.make_camera(ortho_scale=0.001, diagram_scale="1:100|1/100")

        xmin, xmax, ymin, ymax = helper.ortho_view_frame(camera.data)[:4]

        assert xmin < xmax
        assert ymin < ymax
