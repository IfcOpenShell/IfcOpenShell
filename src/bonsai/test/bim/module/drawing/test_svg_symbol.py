# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Bonsai Contributors
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

import os

import pytest

import bonsai.bim.module.drawing.svg_symbol as svg_symbol

SYMBOLS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "bonsai",
    "bim",
    "data",
    "assets",
    "symbols.svg",
)

DEFAULT_SYMBOL_IDS = (
    "rectangle-tag",
    "triangle-tag",
    "hexagon-tag",
    "capsule-tag",
    "circle-tag",
    "door-tag",
    "window-tag",
    "space-tag",
    "elevation-arrow",
    "elevation-tag",
    "section-arrow",
    "section-tag",
    "dot",
    "setout-tag",
    "setout-point",
    "control-point",
    "traverse-point",
    "spot-elevation",
)


def test_symbols_svg_exists():
    assert os.path.exists(SYMBOLS_PATH)


@pytest.mark.parametrize("symbol_id", DEFAULT_SYMBOL_IDS)
def test_default_symbols_are_parsed(symbol_id):
    polylines = svg_symbol.get_symbol_polylines(SYMBOLS_PATH, symbol_id)
    assert polylines, f"expected {symbol_id} to resolve to real geometry, not fall back to a placeholder"
    assert all(len(polyline) >= 2 for polyline in polylines)


def test_unknown_symbol_id_returns_none():
    assert svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "not-a-real-symbol") is None


def test_missing_file_returns_none_instead_of_raising():
    assert svg_symbol.get_symbol_polylines("/no/such/file.svg", "dot") is None


def test_empty_arguments_return_none():
    assert svg_symbol.get_symbol_polylines("", "dot") is None
    assert svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "") is None


def test_rect_symbol_bbox():
    (polyline,) = svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "rectangle-tag")
    xs = [p.x for p in polyline]
    ys = [p.y for p in polyline]
    assert min(xs) == pytest.approx(-6)
    assert max(xs) == pytest.approx(6)
    assert min(ys) == pytest.approx(-2.5)
    assert max(ys) == pytest.approx(2.5)


def test_circle_symbol_bbox():
    (polyline,) = svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "circle-tag")
    xs = [p.x for p in polyline]
    ys = [p.y for p in polyline]
    assert min(xs) == pytest.approx(-5, abs=1e-3)
    assert max(xs) == pytest.approx(5, abs=1e-3)
    assert min(ys) == pytest.approx(-5, abs=1e-3)
    assert max(ys) == pytest.approx(5, abs=1e-3)


def test_rounded_rect_capsule_bbox_matches_flat_rect():
    """`capsule-tag` is a rounded rect (rx=ry=2.5) with the same outer width/height
    as `rectangle-tag`, so its bounding box should match even though its corners
    are tessellated arcs rather than sharp corners."""
    (polyline,) = svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "capsule-tag")
    xs = [p.x for p in polyline]
    ys = [p.y for p in polyline]
    assert min(xs) == pytest.approx(-6, abs=1e-2)
    assert max(xs) == pytest.approx(6, abs=1e-2)
    assert min(ys) == pytest.approx(-2.5, abs=1e-2)
    assert max(ys) == pytest.approx(2.5, abs=1e-2)


def test_setout_tag_arc_quarter_circles_stay_within_radius():
    """`setout-tag`/`setout-point` use elliptical arc (`A`) path commands for two
    quarter-circle wedges of radius 2.5; every tessellated point must stay on
    (within floating point tolerance) or inside that radius."""
    polylines = svg_symbol.get_symbol_polylines(SYMBOLS_PATH, "setout-point")
    assert polylines
    for polyline in polylines:
        for p in polyline:
            assert (p.x**2 + p.y**2) ** 0.5 <= 2.5 + 1e-6
