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

"""Sizing-math test for viewport annotation text (issues #3353 and #3683).

The viewport (``blf``) text path and the SVG/print path historically diverged:
the SVG sizes text through CSS with a fixed millimetre-to-pixel ratio (resolution
independent), while ``BaseDecorator.draw_label`` sized text from the IFC font size
through ``int(magic_font_scale * mm_to_px)``. Because ``mm_to_px`` changes with
viewport zoom, screen DPI and the drawing's Raster X resolution, the ``int()``
truncation quantised the paper-to-pixel conversion, so viewport text size relative
to the drawing jumped in steps and drifted away from the print size.

These tests exercise the pure sizing expression (no Blender/``blf`` needed) and
assert: before the fix the effective mm->px factor varies with ``mm_to_px`` and
disagrees with the SVG; after the fix it is constant (DPI/raster independent) and
matches the SVG's CSS ratio.

The formula and constants are read from the real source so the test stays tied to
the code rather than a private copy.
"""

import re
from pathlib import Path

import pytest

# Locate the bonsai package source relative to this test file.
BONSAI_ROOT = Path(__file__).resolve().parents[4] / "bonsai"
UI_PY = BONSAI_ROOT / "bim" / "ui.py"
DECORATION_PY = BONSAI_ROOT / "bim" / "module" / "drawing" / "decoration.py"
DEFAULT_CSS = BONSAI_ROOT / "bim" / "data" / "assets" / "default.css"


def _read_magic_font_scale_default() -> float:
    text = UI_PY.read_text(encoding="utf-8")
    m = re.search(r"magic_font_scale:\s*bpy\.props\.FloatProperty\(\s*default=([0-9.]+)", text)
    assert m, "Could not find magic_font_scale default in ui.py"
    return float(m.group(1))


def _read_svg_regular_mm_and_px() -> tuple[float, float]:
    """Return (mm, px) the SVG CSS uses for regular annotation text.

    e.g. ``text.regular ... /* 2.5mm */ font-size: 4.13px;`` -> (2.5, 4.13).
    """
    text = DEFAULT_CSS.read_text(encoding="utf-8")
    m = re.search(r"text\.regular[^{]*\{\s*/\*\s*([0-9.]+)mm\s*\*/\s*font-size:\s*([0-9.]+)px", text)
    assert m, "Could not find regular text font-size in default.css"
    return float(m.group(1)), float(m.group(2))


MAGIC_FONT_SCALE = _read_magic_font_scale_default()
SVG_REGULAR_MM, SVG_REGULAR_PX = _read_svg_regular_mm_and_px()
# The SVG maps a nominal text height in mm to a font-size in SVG user units (which
# equal mm, because the drawing viewBox is 1:1 with its mm page size). This ratio is
# fixed for every class, so it is the resolution-independent ground truth for print.
SVG_MM_TO_UNIT = SVG_REGULAR_PX / SVG_REGULAR_MM  # 4.13 / 2.5 = 1.652


def viewport_font_size_px_current(font_size_mm: float, mm_to_px: float) -> float:
    """draw_label sizing BEFORE the fix (with the int() truncation)."""
    return int(MAGIC_FONT_SCALE * mm_to_px) * font_size_mm / 2.5


def viewport_font_size_px_fixed(font_size_mm: float, mm_to_px: float) -> float:
    """draw_label sizing AFTER the fix (float, no truncation)."""
    return MAGIC_FONT_SCALE * mm_to_px * font_size_mm / 2.5


def effective_paper_unit_factor(font_size_px: float, font_size_mm: float, mm_to_px: float) -> float:
    """Convert a viewport pixel size back into the drawing's paper units per nominal mm.

    ``mm_to_px`` is screen pixels per paper *metre* (get_camera_width_mm returns the
    page width in metres), so ``font_size_px * 1000 / mm_to_px`` is the on-screen text
    size expressed in paper mm. Divided by the nominal mm it gives the same quantity the
    SVG fixes at ``SVG_MM_TO_UNIT``. If this factor is constant across ``mm_to_px`` the
    viewport is resolution independent; if it equals ``SVG_MM_TO_UNIT`` it matches print.
    """
    paper_mm = font_size_px * 1000.0 / mm_to_px
    return paper_mm / font_size_mm


# A sweep of mm_to_px values standing in for different viewport zoom levels, screen DPI
# and drawing Raster X resolutions (mm_to_px = zoom_factor * region_width_px / page_metres).
MM_TO_PX_SWEEP = [700.0, 800.0, 1000.0, 1200.0, 1220.0, 1500.0, 2000.0, 2731.0, 3000.0, 4096.0]
FONT_SIZES_MM = [1.0, 1.8, 2.5, 3.5, 5.0, 7.0]  # incl. the #3683 custom "little" = 1mm


def test_current_viewport_factor_varies_with_resolution():
    """BEFORE: the effective mm->px factor swings with mm_to_px (DPI/zoom/raster)."""
    factors = [effective_paper_unit_factor(viewport_font_size_px_current(2.5, x), 2.5, x) for x in MM_TO_PX_SWEEP]
    spread = max(factors) - min(factors)
    assert spread > 0.3, f"Expected the buggy factor to vary widely, got spread {spread:.4f}: {factors}"
    # And it disagrees with the SVG by more than 10% at some resolutions.
    worst = max(abs(f - SVG_MM_TO_UNIT) / SVG_MM_TO_UNIT for f in factors)
    assert worst > 0.10, f"Expected >10% disagreement with SVG somewhere, worst was {worst:.3%}"


def test_fixed_viewport_factor_is_resolution_independent():
    """AFTER: the effective mm->px factor is constant across all resolutions."""
    for font_mm in FONT_SIZES_MM:
        factors = [effective_paper_unit_factor(viewport_font_size_px_fixed(font_mm, x), font_mm, x) for x in MM_TO_PX_SWEEP]
        spread = max(factors) - min(factors)
        assert spread < 1e-9, f"font {font_mm}mm not resolution independent, spread {spread}: {factors}"


def test_fixed_viewport_matches_svg_ratio():
    """AFTER: the constant factor equals the SVG's CSS mm->unit ratio (within the pre-existing magic-constant tolerance)."""
    factor = effective_paper_unit_factor(viewport_font_size_px_fixed(1.0, 1234.0), 1.0, 1234.0)
    rel_error = abs(factor - SVG_MM_TO_UNIT) / SVG_MM_TO_UNIT
    # magic_font_scale (0.004118616) is a hand-tuned proxy for the SVG's 4.13/1000; it is 0.28% low.
    assert rel_error < 0.005, f"viewport factor {factor:.5f} vs SVG {SVG_MM_TO_UNIT:.5f}, rel error {rel_error:.3%}"


def test_3683_custom_little_size_is_consistent_after_fix():
    """#3683: a 1mm custom size keeps a fixed relationship to regular 2.5mm text after the fix.

    Before the fix the ratio between the 1mm size and the 2.5mm size measured back in paper mm
    can be distorted by the truncation at some resolutions; after the fix it is exactly 1/2.5.
    """
    for x in MM_TO_PX_SWEEP:
        little = effective_paper_unit_factor(viewport_font_size_px_fixed(1.0, x), 1.0, x)
        regular = effective_paper_unit_factor(viewport_font_size_px_fixed(2.5, x), 2.5, x)
        assert little == pytest.approx(regular, rel=1e-12)
        # Both equal the SVG ground-truth factor (print consistency).
        assert little == pytest.approx(SVG_MM_TO_UNIT, rel=0.005)


def test_source_no_longer_truncates_font_size():
    """Guard against the int() truncation returning to draw_label."""
    text = DECORATION_PY.read_text(encoding="utf-8")
    assert "int(magic_font_scale * mm_to_px)" not in text, "The int() truncation regressed in draw_label"
    assert "font_size_px = magic_font_scale * mm_to_px * font_size_mm / 2.5" in text


if __name__ == "__main__":
    mfs = MAGIC_FONT_SCALE
    print(f"magic_font_scale (ui.py default) = {mfs}")
    print(f"SVG regular: {SVG_REGULAR_MM}mm -> {SVG_REGULAR_PX}px  =>  SVG_MM_TO_UNIT = {SVG_MM_TO_UNIT:.5f}")
    print()
    print("Effective paper-unit factor per nominal mm (want constant == SVG 1.65200):")
    print(f"{'mm_to_px':>10} | {'BEFORE int()':>14} | {'AFTER (float)':>14}")
    for x in MM_TO_PX_SWEEP:
        before = effective_paper_unit_factor(viewport_font_size_px_current(2.5, x), 2.5, x)
        after = effective_paper_unit_factor(viewport_font_size_px_fixed(2.5, x), 2.5, x)
        print(f"{x:>10.0f} | {before:>14.4f} | {after:>14.4f}")
    print()
    print("#3683 -- 1mm 'little' text, paper-mm-per-nominal-mm factor:")
    print(f"{'mm_to_px':>10} | {'BEFORE':>10} | {'AFTER':>10} | SVG=1.652")
    for x in MM_TO_PX_SWEEP:
        before = effective_paper_unit_factor(viewport_font_size_px_current(1.0, x), 1.0, x)
        after = effective_paper_unit_factor(viewport_font_size_px_fixed(1.0, x), 1.0, x)
        print(f"{x:>10.0f} | {before:>10.4f} | {after:>10.4f}")
