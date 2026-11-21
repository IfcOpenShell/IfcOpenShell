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

import xml.etree.ElementTree as ET

from bonsai.bim.module.drawing.sheeter import SVG, SheetBuilder


def parse(body: str) -> ET.Element:
    return ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{body}</svg>')


class TestEnsureDrawingUniqueStyles:
    def test_scopes_selectors_and_classes_with_the_drawing_prefix(self):
        svg = parse('<defs><style>text, tspan { font-family: Arial; }</style></defs><text class="a"/>')

        SheetBuilder().ensure_drawing_unique_styles(svg, 7)

        assert svg.find(f"{SVG}defs/{SVG}style").text.startswith("text.d7, tspan.d7")
        assert svg.find(f"{SVG}text").attrib["class"] == "a d7"

    def test_still_prefixes_ids_when_the_document_has_no_stylesheet(self):
        svg = parse('<g id="x"/>')

        SheetBuilder().ensure_drawing_unique_styles(svg, 7)

        assert svg.find(f"{SVG}g").attrib["id"] == "d7-x"
