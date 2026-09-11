# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY, without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import re
from pathlib import Path

# Resolved relative to this test file rather than importing `bonsai.bim`, since this test
# only checks a static shipped asset and shouldn't need bpy to run.
CSS_PATH = Path(__file__).resolve().parents[4] / "bonsai" / "bim" / "data" / "assets" / "default.css"

# .PredefinedType-LINEWORK.fine is the codebase's existing "fine" weight (see issue #5428).
FINE_STROKE_WIDTH = "0.18"


class TestDefaultCss:
    def css_text(self) -> str:
        return CSS_PATH.read_text()

    def rule_for(self, css_text: str, selector: str) -> str:
        """Return the declaration block of the rule whose comma-separated selector list
        contains `selector` exactly, ignoring commented-out rules."""
        # Strip CSS comments first so a disabled example rule can't be picked up.
        without_comments = re.sub(r"/\*.*?\*/", "", css_text, flags=re.S)
        matches = []
        for selector_list, declaration in re.findall(r"([^{}]+)\{([^{}]*)\}", without_comments):
            if selector in [s.strip() for s in selector_list.split(",")]:
                matches.append(declaration)
        assert matches, f"No active CSS rule selects {selector} in {CSS_PATH}"
        assert len(matches) == 1, f"Expected exactly one rule selecting {selector}, found {len(matches)}"
        return matches[0]

    def test_furniture_and_geographic_elements_print_at_fine_weight(self):
        css_text = self.css_text()

        for class_name in (".IfcFurniture", ".IfcGeographicElement"):
            declaration = self.rule_for(css_text, class_name)
            match = re.search(r"stroke-width\s*:\s*([0-9.]+)", declaration)
            assert match, f"{class_name} rule has no stroke-width declaration: {declaration!r}"
            assert match.group(1) == FINE_STROKE_WIDTH, (
                f"{class_name} stroke-width is {match.group(1)}, expected the 'fine' weight "
                f"({FINE_STROKE_WIDTH}) per issue #5428, not the thicker .cut/.projection default"
            )

    def test_furniture_and_geographic_rule_wins_the_cascade_over_cut(self):
        # A cut/projection SVG element carries BOTH the base class (e.g. "cut") and the IFC
        # class (e.g. "IfcFurniture") on the same element (see SvgSerializer.cpp's
        # `class="cut IfcFurniture ..."` prefixing). Since `.IfcFurniture` and `.cut` are both
        # single-class selectors, they have equal specificity, so whichever is declared LATER
        # in the stylesheet wins for the properties it sets. The fine-weight rule must therefore
        # appear after both `.cut` and `.projection` or it will be silently overridden.
        css_text = self.css_text()
        cut_pos = css_text.index(".cut {")
        projection_pos = css_text.index(".projection {")
        furniture_pos = css_text.index(".IfcFurniture")

        assert (
            furniture_pos > cut_pos
        ), ".IfcFurniture/.IfcGeographicElement rule must come after .cut to win the cascade"
        assert (
            furniture_pos > projection_pos
        ), ".IfcFurniture/.IfcGeographicElement rule must come after .projection to win the cascade"
