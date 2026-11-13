# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from unittest import mock

import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing.decoration import BaseDecorator


class TestDrawLabelFontSize:
    @pytest.mark.parametrize("region_width", [1001, 1234, 2731])
    def test_font_size_is_not_truncated_to_a_whole_number_of_pixels_per_mm(self, region_width):
        decorator = BaseDecorator.__new__(BaseDecorator)
        decorator.font_id = 0
        context = mock.Mock()
        context.space_data.region_3d.view_camera_zoom = 0
        context.region.width = region_width
        camera_width_mm = 0.297
        preferences = mock.Mock()
        preferences.doc.magic_font_scale = 0.004118616
        preferences.decorations_colour = (1, 1, 1, 1)
        mm_to_px = decorator.camera_zoom_to_factor(0) * region_width / camera_width_mm
        with (
            mock.patch("bonsai.bim.module.drawing.decoration.blf") as blf,
            mock.patch.object(BaseDecorator, "get_camera_width_mm", return_value=camera_width_mm),
            mock.patch.object(tool.Blender, "get_addon_preferences", return_value=preferences),
        ):
            decorator.draw_label(context, "text", Vector((0, 0)), Vector((1, 0)), center=False, gap=0)
        assert blf.size.call_args.args[1] == pytest.approx(0.004118616 * mm_to_px, rel=1e-12)
