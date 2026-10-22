# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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

import svgwrite
from odf.text import LineBreak, P, S

from bonsai.bim.module.drawing.scheduler import Scheduler


class TestAddText:
    def test_keep_repeated_spaces_and_line_breaks(self):
        scheduler = Scheduler()
        scheduler.svg = svgwrite.Drawing()
        paragraph = P()
        paragraph.addText("a")
        paragraph.addElement(S(c=3))
        paragraph.addText("b")
        paragraph.addElement(LineBreak())
        paragraph.addText("c")
        scheduler.add_text([paragraph], 0, 0, 2.5, box_alignment="top-left")
        lines = [tspan.text for tspan in scheduler.svg.elements[-1].elements]
        assert lines == ["a   b", "c"]
