# This file was generated with the assistance of an AI coding tool.
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

import svgwrite

from bonsai.bim.module.drawing.svgwriter import SvgWriter


class TestDrawSymbol:
    def test_adds_the_symbol_name_as_a_css_class(self):
        writer = SvgWriter.__new__(SvgWriter)
        writer.svg = svgwrite.Drawing()

        writer.draw_symbol("space-tag", "translate(1, 2)")

        use = writer.svg.elements[-1]
        assert use.attribs["class"] == "space-tag"

    def test_replaces_whitespace_in_the_symbol_name(self):
        assert SvgWriter.get_symbol_class(" my tag ") == "my-tag"
