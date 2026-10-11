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

import svgwrite

from bonsai.bim.module.drawing.svgwriter import SvgWriter


def test_bundled_fonts_are_embedded_in_the_svg():
    fake_self = SimpleNamespace(svg=svgwrite.Drawing())

    SvgWriter.embed_fonts(fake_self)

    svg = fake_self.svg.tostring()
    assert "@font-face" in svg
    assert "font-family: 'OpenGost Type B TT'" in svg
