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

"""How a schedule cell is drawn from the borders its spreadsheet declares.

A cell that declares none keeps the `.border` class the stylesheet controls, so
a document that never set borders draws as it always did. A cell that declares
them gets one line per side, which is the only way an outline and the inner
rules can differ. A spreadsheet says so in ODF style attributes and a workbook
in openpyxl Sides; both arrive at draw_cell in the same shape.
"""

import pytest
from openpyxl.styles import Border, Side
from openpyxl.styles.colors import Color

from bonsai.bim.module.drawing.scheduler import Scheduler

PT = 25.4 / 72


class FakeSvg:
    """Collects what the scheduler draws, in order."""

    def __init__(self):
        self.items = []

    def rect(self, **kwargs):
        return ("rect", kwargs)

    def line(self, **kwargs):
        return ("line", kwargs)

    def add(self, item):
        self.items.append(item)


@pytest.fixture
def scheduler():
    scheduler = Scheduler()
    scheduler.svg = FakeSvg()
    return scheduler


def draw(scheduler, style):
    background_color = style.get("background-color", "#ffffff")
    scheduler.draw_cell(0, 0, 40, 6, background_color, scheduler.get_cell_borders(style))
    return scheduler.svg.items


def widths(items):
    return [float(line["style"].split("stroke-width: ")[1].split(";")[0]) for _, line in items[1:]]


def test_cell_without_borders_is_left_to_the_stylesheet(scheduler):
    ((kind, cell),) = draw(scheduler, {"background-color": "#eeeeee"})
    assert kind == "rect"
    assert cell["class_"] == "border"
    assert cell["style"] == "fill: #eeeeee;"


def test_cell_that_declares_no_border_gets_no_line(scheduler):
    assert [kind for kind, _ in draw(scheduler, {"border": "none"})] == ["rect"]


def test_border_is_drawn_on_every_side(scheduler):
    items = draw(scheduler, {"border": "0.5pt solid #ff0000"})
    assert [kind for kind, _ in items] == ["rect", "line", "line", "line", "line"]
    assert "stroke: none" in items[0][1]["style"]
    assert [line["start"] for _, line in items[1:]] == [(0, 0), (40, 0), (0, 0), (0, 6)]
    assert [line["end"] for _, line in items[1:]] == [(0, 6), (40, 6), (40, 0), (40, 6)]
    for _, line in items[1:]:
        assert "stroke: #ff0000;" in line["style"]
    assert widths(items) == [pytest.approx(0.5 * PT)] * 4


def test_a_side_of_its_own_departs_from_the_shorthand(scheduler):
    items = draw(scheduler, {"border": "0.25pt solid #000000", "border-left": "1pt solid #000000"})
    assert widths(items)[0] == pytest.approx(1 * PT)
    assert widths(items)[1:] == [pytest.approx(0.25 * PT)] * 3


@pytest.mark.parametrize(
    "border,dashes",
    [
        ("0.5pt dashed #000000", (3, 2)),
        ("0.5pt dotted #000000", (1, 1)),
        ("0.5pt solid #000000", None),
        ("0.5pt double #000000", None),
    ],
)
def test_border_style_becomes_a_dash_pattern(scheduler, border, dashes):
    _, line = draw(scheduler, {"border": border})[1]
    if dashes is None:
        assert "stroke-dasharray" not in line["style"]
    else:
        expected = ",".join(str(dash * 0.5 * PT) for dash in dashes)
        assert f"stroke-dasharray: {expected};" in line["style"]


@pytest.mark.parametrize("border", ["0.5pt solid #ff0000", "solid 0.5pt #ff0000", "#ff0000 0.5pt solid"])
def test_the_three_parts_may_come_in_any_order(scheduler, border):
    assert scheduler.parse_border(border) == (pytest.approx(0.5 * PT), "#ff0000", None)


def test_a_border_without_a_width_is_no_line(scheduler):
    assert scheduler.parse_border("solid #ff0000") is None


def test_the_shorthand_stands_in_for_the_sides_left_silent(scheduler):
    borders = scheduler.get_cell_borders({"border": "0.25pt solid #000000", "border-top": "none"})
    assert borders["top"] is None
    assert borders["left"] == borders["right"] == borders["bottom"]


def test_workbook_cell_without_borders_is_left_to_the_stylesheet(scheduler):
    assert scheduler.get_xlsx_cell_borders(Border()) is None


def test_workbook_cell_rules_only_the_sides_it_names(scheduler):
    border = Border(left=Side(style="thick", color="FFFF0000"), bottom=Side(style="thin"))
    borders = scheduler.get_xlsx_cell_borders(border)
    assert borders["left"] == (pytest.approx(1.5 * PT), "#ff0000", None)
    assert borders["bottom"] == (pytest.approx(0.5 * PT), "#000000", None)
    assert borders["right"] is borders["top"] is None


@pytest.mark.parametrize(
    "style,dashes",
    [("dashed", (3, 2)), ("dotted", (1, 1)), ("mediumDashDot", (3, 2, 1, 2)), ("double", None)],
)
def test_a_workbook_border_style_becomes_a_dash_pattern(scheduler, style, dashes):
    assert scheduler.get_xlsx_cell_borders(Border(top=Side(style=style)))["top"][2] == dashes


def test_a_workbook_colour_that_needs_the_theme_draws_black(scheduler):
    # openpyxl answers .rgb on a theme colour with its complaint as a string
    # rather than raising, so the length is what tells a real ARGB from it.
    borders = scheduler.get_xlsx_cell_borders(Border(top=Side(style="thin", color=Color(theme=1))))
    assert borders["top"][1] == "#000000"
