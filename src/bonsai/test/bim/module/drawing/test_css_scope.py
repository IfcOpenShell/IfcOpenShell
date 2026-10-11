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

from bonsai.bim.module.drawing import css_scope
from bonsai.bim.module.drawing.sheeter import SVG, SheetBuilder


class TestScopeCssRules:
    def test_brace_in_comment_does_not_stop_scoping(self):
        assert css_scope.scope_css_rules("a { x: 1 } /* { */ b { y: 2 }", "d7").endswith("b.d7 { y: 2 }")

    def test_brace_in_string_does_not_stop_scoping(self):
        assert css_scope.scope_css_rules('a { content: "{"; } b { y: 2 }', "d7").endswith("b.d7 { y: 2 }")

    def test_at_rule_prelude_is_left_alone(self):
        assert css_scope.scope_css_rules("@font-face { x: 1 } a { y: 2 }", "d7").startswith("@font-face {")

    def test_comma_inside_pseudo_class_is_not_a_separator(self):
        assert css_scope.scope_css_rules(":is(.a, .b) { x: 1 }", "d7") == ":is(.a, .b).d7 { x: 1 }"

    def test_urls_are_prefixed(self):
        assert css_scope.scope_css_rules("a { fill: url(#m); }", "d7") == "a.d7 { fill: url(#d7-m); }"


class TestEnsureDrawingUniqueStyles:
    def test_brace_in_comment_does_not_stop_scoping(self):
        svg = ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg"><defs><style>a { x: 1 } /* { */ b { y: 2 }</style></defs></svg>'
        )

        SheetBuilder().ensure_drawing_unique_styles(svg, 7)

        assert svg.find(f"{SVG}defs/{SVG}style").text.endswith("b.d7 { y: 2 }")

    def test_use_references_follow_the_prefixed_ids(self):
        svg = ET.fromstring(
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">'
            '<defs><g id="glyph-0-0"/></defs><use xlink:href="#glyph-0-0"/></svg>'
        )

        SheetBuilder().ensure_drawing_unique_styles(svg, 3)

        assert svg.find(f"{SVG}defs/{SVG}g").attrib["id"] == "d3-glyph-0-0"
        assert svg.find(f"{SVG}use").attrib["{http://www.w3.org/1999/xlink}href"] == "#d3-glyph-0-0"
