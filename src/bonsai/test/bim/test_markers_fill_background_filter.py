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

import xml.etree.ElementTree as ET

import pytest

import bonsai.tool as tool

pytestmark = pytest.mark.drawing


class TestFillBackgroundFilter:
    def test_filter_does_not_copy_the_text_it_sits_behind(self):
        path = tool.Blender.get_internal_data_dir() / "assets" / "markers.svg"
        root = ET.parse(path).getroot()
        svg_filter = next(el for el in root.iter() if el.get("id") == "fill-background")

        inputs = {el.get(name) for el in svg_filter.iter() for name in ("in", "in2")}
        tags = {el.tag.split("}")[-1] for el in svg_filter.iter()}

        assert "SourceGraphic" not in inputs
        assert "feMerge" not in tags
