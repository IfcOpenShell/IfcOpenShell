# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import pytest

import ifcopenshell
import ifcopenshell.util.framing as subject
from ifcopenshell.util.framing import FramingError


def approx_list(values):
    return pytest.approx(values, abs=1e-9)


def us(layout, name):
    return [m.u for m in layout.by_entry(name)]


RAILING = {
    "members": [
        {
            "name": "Post",
            "kind": "V",
            "spacing": {"mode": "MAX", "value": 1.5},
            "at_ends": True,
            "at_corners": True,
            "bottom": "BASE",
            "top": {"member": "TopRail"},
        },
        {"name": "TopRail", "kind": "H", "v": 1.07, "breaks_at": ["Post"]},
        {"name": "BotRail", "kind": "H", "v": 0.10, "breaks_at": ["Post"]},
        {
            "name": "Baluster",
            "kind": "V",
            "spacing": {"mode": "MAX", "value": 0.1},
            "within": "Post",
            "bottom": {"member": "BotRail"},
            "top": {"member": "TopRail"},
        },
    ]
}
RAILING_EXTENTS = {
    "Post": (-0.025, 0.025),
    "TopRail": (-0.01, 0.01),
    "BotRail": (-0.02, 0.02),
    "Baluster": (-0.008, 0.008),
}


class TestParseSystem:
    def test_parses_each_kind(self):
        entries = subject.parse_system(
            {
                "members": [
                    {"name": "A", "kind": "V", "at_ends": True},
                    {"name": "B", "kind": "H", "v": "TOP"},
                    {"name": "C", "kind": "INFILL", "between": "A", "gap": {"left": 0.1}},
                ]
            }
        )
        assert [type(e) for e in entries] == [subject.VerticalEntry, subject.HorizontalEntry, subject.InfillEntry]
        assert entries[1].v == "TOP"
        assert entries[2].gap == (0.1, 0.0, 0.0, 0.0)

    @pytest.mark.parametrize(
        "members, message",
        [
            (
                [{"name": "A", "kind": "V", "at_ends": True}, {"name": "A", "kind": "V", "at_ends": True}],
                "more than once",
            ),
            ([{"name": "A", "kind": "X"}], "unknown kind"),
            ([{"name": "A", "kind": "V"}], "needs spacing"),
            ([{"name": "A", "kind": "V", "spacing": {"mode": "MAX", "value": 0}}], "positive spacing"),
            ([{"name": "A", "kind": "V", "spacing": {"mode": "COUNT", "value": 1.5}}], "whole number"),
            ([{"name": "A", "kind": "V", "at_ends": True, "within": "Nope"}], "unknown entry"),
            ([{"name": "A", "kind": "H", "v": 1, "breaks_at": ["A"]}], "to be a vertical"),
            ([{"name": "A", "kind": "H", "v": 1, "spacing": {"mode": "COUNT", "value": 2}}], "both"),
            ([{"name": "A", "kind": "H"}], "either 'v' or 'spacing'"),
            ([{"name": "A", "kind": "V", "at_ends": True, "top": "ROOF"}], "invalid bound"),
            (
                [
                    {"name": "Cables", "kind": "H", "spacing": {"mode": "COUNT", "value": 3}},
                    {"name": "Post", "kind": "V", "at_ends": True, "top": {"member": "Cables"}},
                ],
                "repeating horizontal",
            ),
        ],
    )
    def test_rejects_invalid_data(self, members, message):
        with pytest.raises(FramingError, match=message):
            subject.parse_system({"members": members})

    def test_rejects_within_loop(self):
        members = [
            {"name": "A", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "within": "B"},
            {"name": "B", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "within": "A"},
        ]
        with pytest.raises(FramingError, match="loop"):
            subject.parse_system({"members": members})

    def test_rejects_horizontal_bound_loop(self):
        members = [
            {"name": "A", "kind": "H", "v": {"member": "B"}},
            {"name": "B", "kind": "H", "v": {"member": "A"}},
        ]
        with pytest.raises(FramingError, match="loop"):
            subject.parse_system({"members": members})


class TestVerticalSpacing:
    def solve_one(self, member, segments=(3.0,), **kwargs):
        entries = subject.parse_system({"members": [{"name": "M", "kind": "V", **member}]})
        return subject.solve(entries, list(segments), 1.0, **kwargs)

    def test_max_spacing_makes_equal_bays(self):
        layout = self.solve_one({"spacing": {"mode": "MAX", "value": 1.4}, "at_ends": True})
        assert us(layout, "M") == approx_list([0.0, 1.0, 2.0, 3.0])

    def test_count_spacing(self):
        layout = self.solve_one({"spacing": {"mode": "COUNT", "value": 2}})
        assert us(layout, "M") == approx_list([1.0, 2.0])

    def test_fixed_spacing_centres_the_remainder(self):
        layout = self.solve_one({"spacing": {"mode": "FIXED", "value": 1.0}}, segments=(3.5,))
        assert us(layout, "M") == approx_list([0.25, 1.25, 2.25, 3.25])

    def test_fixed_spacing_does_not_duplicate_ends(self):
        layout = self.solve_one({"spacing": {"mode": "FIXED", "value": 1.0}, "at_ends": True})
        assert us(layout, "M") == approx_list([0.0, 1.0, 2.0, 3.0])

    def test_spacing_restarts_per_segment(self):
        layout = self.solve_one(
            {"spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True, "at_corners": True}, segments=(2.0, 2.0)
        )
        assert us(layout, "M") == approx_list([0.0, 1.0, 2.0, 3.0, 4.0])
        assert [m.address for m in layout.verticals] == [
            (0, 0, 0),
            (0, 0, 1),
            (1, 0, 0),
            (1, 0, 1),
            (1, 0, 2),
        ]

    def test_path_scope_spaces_across_vertices(self):
        layout = self.solve_one({"spacing": {"mode": "COUNT", "value": 2}}, segments=(1.0, 2.0), scope="PATH")
        assert us(layout, "M") == approx_list([1.0, 2.0])

    def test_closed_path_has_corners_but_no_ends(self):
        layout = self.solve_one({"at_ends": True, "at_corners": True}, segments=(2.0, 2.0, 2.0, 2.0), closed=True)
        assert us(layout, "M") == approx_list([0.0, 2.0, 4.0, 6.0])

    def test_vertical_without_height_is_rejected(self):
        with pytest.raises(FramingError, match="no height"):
            self.solve_one({"at_ends": True, "bottom": "TOP", "top": "BASE"})


class TestRailing:
    def solve(self, segments=(3.0,)):
        return subject.solve(subject.parse_system(RAILING), list(segments), 1.1, extents=RAILING_EXTENTS)

    def test_posts_stop_under_the_top_rail(self):
        posts = self.solve().by_entry("Post")
        assert [p.u for p in posts] == approx_list([0.0, 1.5, 3.0])
        assert all(p.v_start == 0.0 and p.v_end == pytest.approx(1.06) for p in posts)

    def test_top_rail_runs_over_the_posts(self):
        rails = self.solve().by_entry("TopRail")
        assert [(r.u_start, r.u_end) for r in rails] == [(0.0, 3.0)]

    def test_bottom_rail_breaks_at_post_faces(self):
        rails = self.solve().by_entry("BotRail")
        assert [(r.u_start, r.u_end) for r in rails] == [
            pytest.approx((0.025, 1.475)),
            pytest.approx((1.525, 2.975)),
        ]
        assert [r.address for r in rails] == [(0, 0), (0, 1)]

    def test_balusters_are_symmetric_in_each_bay(self):
        balusters = self.solve().by_entry("Baluster")
        # Bay between post faces is 1.45 long; MAX 0.1 gives 15 bays, so 14 balusters each.
        assert len(balusters) == 28
        first_bay = [b.u for b in balusters if b.address[1] == 0]
        assert first_bay[0] - 0.025 == pytest.approx(1.475 - first_bay[-1])
        assert all(b.v_start == pytest.approx(0.12) and b.v_end == pytest.approx(1.06) for b in balusters)

    def test_bays_do_not_cross_corners(self):
        balusters = self.solve(segments=(3.0, 3.0)).by_entry("Baluster")
        assert not any(2.975 < b.u < 3.025 for b in balusters)
        assert {b.address[0] for b in balusters} == {0, 1}


class TestHorizontalRepeat:
    def test_count_between_two_rails(self):
        entries = subject.parse_system(
            {
                "members": [
                    {"name": "Top", "kind": "H", "v": 1.0},
                    {"name": "Bottom", "kind": "H", "v": 0.2},
                    {
                        "name": "Cable",
                        "kind": "H",
                        "spacing": {"mode": "COUNT", "value": 3},
                        "bottom": {"member": "Bottom"},
                        "top": {"member": "Top"},
                    },
                ]
            }
        )
        layout = subject.solve(entries, [2.0], 1.1)
        cables = layout.by_entry("Cable")
        assert [c.v for c in cables] == approx_list([0.4, 0.6, 0.8])
        assert [c.address for c in cables] == [(0, 0), (1, 0), (2, 0)]


class TestInfill:
    def test_storefront_cells_sit_between_mullions_and_rails(self):
        entries = subject.parse_system(
            {
                "members": [
                    {
                        "name": "Mullion",
                        "kind": "V",
                        "spacing": {"mode": "MAX", "value": 1.5},
                        "at_ends": True,
                        "at_corners": True,
                    },
                    {"name": "Sill", "kind": "H", "v": "BASE", "breaks_at": ["Mullion"]},
                    {"name": "Transom", "kind": "H", "v": 2.4, "breaks_at": ["Mullion"]},
                    {"name": "Head", "kind": "H", "v": "TOP", "breaks_at": ["Mullion"]},
                    {
                        "name": "Vision",
                        "kind": "INFILL",
                        "between": "Mullion",
                        "bottom": {"member": "Sill"},
                        "top": {"member": "Transom"},
                        "gap": 0.006,
                    },
                ]
            }
        )
        half = (-0.0225, 0.0225)
        extents = {"Mullion": half, "Sill": half, "Transom": half, "Head": half}
        layout = subject.solve(entries, [3.0], 3.0, extents=extents)

        assert len(layout.by_entry("Sill")) == 2
        assert len(layout.by_entry("Head")) == 2
        panels = layout.by_entry("Vision")
        assert [p.address for p in panels] == [(0, 0, 0), (0, 1, 0)]
        first = panels[0]
        assert (first.u_start, first.u_end) == pytest.approx((0.0285, 1.4715))
        assert (first.v_start, first.v_end) == pytest.approx((0.0285, 2.3715))

    def test_frameless_panels_split_by_max_width(self):
        entries = subject.parse_system(
            {"members": [{"name": "Glass", "kind": "INFILL", "max_width": 1.2, "joint": 0.01}]}
        )
        panels = subject.solve(entries, [5.0], 1.0).infills
        assert len(panels) == 5
        assert all(p.u_end - p.u_start == pytest.approx(0.992) for p in panels)
        assert panels[1].u_start - panels[0].u_end == pytest.approx(0.01)
        assert panels[-1].u_end == pytest.approx(5.0)

    def test_infill_splits_at_path_vertices(self):
        entries = subject.parse_system({"members": [{"name": "Glass", "kind": "INFILL"}]})
        panels = subject.solve(entries, [1.0, 2.0], 1.0).infills
        assert [(p.u_start, p.u_end, p.address) for p in panels] == [(0.0, 1.0, (0, 0, 0)), (1.0, 3.0, (1, 0, 0))]


class TestResolveProfile:
    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        self.a = self.file.createIfcRectangleProfileDef("AREA", "A", None, 1.0, 1.0)
        self.b = self.file.createIfcRectangleProfileDef("AREA", "B", None, 1.0, 1.0)

    def test_by_id(self):
        assert subject.resolve_profile(self.file, {"id": self.a.id(), "name": "A"}) == self.a

    def test_falls_back_to_name_when_id_is_gone(self):
        assert subject.resolve_profile(self.file, {"id": 999, "name": "B"}) == self.b

    def test_name_wins_when_id_points_to_another_profile(self):
        # As after appending into another file, where the old id now belongs to a different profile.
        assert subject.resolve_profile(self.file, {"id": self.a.id(), "name": "B"}) == self.b

    def test_id_wins_after_a_rename(self):
        assert subject.resolve_profile(self.file, {"id": self.a.id(), "name": "Old name"}) == self.a

    def test_ignores_ids_of_non_profiles(self):
        point = self.file.createIfcCartesianPoint((0.0, 0.0))
        assert subject.resolve_profile(self.file, {"id": point.id(), "name": "Missing"}) is None

    def test_none_when_nothing_resolves(self):
        assert subject.resolve_profile(self.file, {"id": 0, "name": "Missing"}) is None
        assert subject.resolve_profile(self.file, None) is None


class TestSolveInput:
    def test_rejects_zero_length_segment(self):
        entries = subject.parse_system({"members": [{"name": "A", "kind": "V", "at_ends": True}]})
        with pytest.raises(FramingError, match="non-zero"):
            subject.solve(entries, [1.0, 0.0], 1.0)

    def test_rejects_zero_height(self):
        entries = subject.parse_system({"members": [{"name": "A", "kind": "V", "at_ends": True}]})
        with pytest.raises(FramingError, match="height"):
            subject.solve(entries, [1.0], 0.0)
