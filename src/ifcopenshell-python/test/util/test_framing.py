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

import math

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
                    {"name": "Rail", "kind": "H", "v": {"member": "Cables"}},
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

    @pytest.mark.parametrize(
        "align, expected",
        [
            ("START", [1.0, 2.0, 3.0]),
            ("CENTER", [0.25, 1.25, 2.25, 3.25]),
            ("END", [0.5, 1.5, 2.5]),
        ],
    )
    def test_fixed_spacing_alignment(self, align, expected):
        layout = self.solve_one({"spacing": {"mode": "FIXED", "value": 1.0, "align": align}}, segments=(3.5,))
        assert us(layout, "M") == approx_list(expected)

    @pytest.mark.parametrize(
        "align, offset, expected",
        [
            ("START", 0.3, [0.3, 1.3, 2.3, 3.3]),
            ("END", 0.3, [0.2, 1.2, 2.2, 3.2]),
            # Centred remainder of 0.25 each side, slid 0.5 along u, refilled at the start.
            ("CENTER", 0.5, [0.75, 1.75, 2.75]),
            ("CENTER", -0.5, [0.75, 1.75, 2.75]),
            # The first member is the offset in from that end, with nothing before it.
            ("START", 1.3, [1.3, 2.3, 3.3]),
        ],
    )
    def test_fixed_spacing_offset(self, align, offset, expected):
        spacing = {"mode": "FIXED", "value": 1.0, "align": align, "offset": offset}
        layout = self.solve_one({"spacing": spacing}, segments=(3.5,))
        assert us(layout, "M") == approx_list(expected)

    @pytest.mark.parametrize(
        "align, offset, expected",
        [
            (None, 0.0, [1.25, 2.5, 3.75]),
            ("START", 0.0, [1.25, 2.5, 3.75]),
            ("END", 0.0, [1.25, 2.5, 3.75]),
            # A member 0.4 in, then 4.6 split into bays no wider than 1.5.
            ("START", 0.4, [0.4, 1.55, 2.7, 3.85]),
            ("END", 0.4, [1.15, 2.3, 3.45, 4.6]),
            # A member on the centre line, then 2.5 either side in bays of 1.25.
            ("CENTER", 0.0, [1.25, 2.5, 3.75]),
            ("CENTER", 0.5, [1.5, 3.0, 4.0]),
            # An anchor past the end leaves the range evenly split.
            ("START", 6.0, [1.25, 2.5, 3.75]),
        ],
    )
    def test_max_spacing_anchor(self, align, offset, expected):
        spacing = {"mode": "MAX", "value": 1.5, "offset": offset}
        if align:
            spacing["align"] = align
        layout = self.solve_one({"spacing": spacing}, segments=(5.0,))
        assert us(layout, "M") == approx_list(expected)

    def test_max_centre_anchor_differs_from_even(self):
        # Three bays of 1.0 have no member on the centre line; anchoring there gives two each side.
        even = self.solve_one({"spacing": {"mode": "MAX", "value": 1.0}})
        centred = self.solve_one({"spacing": {"mode": "MAX", "value": 1.0, "align": "CENTER"}})
        assert us(even, "M") == approx_list([1.0, 2.0])
        assert us(centred, "M") == approx_list([0.75, 1.5, 2.25])

    def test_horizontal_max_anchor_from_the_top(self):
        rail = {"name": "R", "kind": "H", "spacing": {"mode": "MAX", "value": 0.5, "align": "END", "offset": 0.1}}
        layout = solve([rail], height=1.0)
        # A rail 0.1 below the top, then 0.9 down to the base in two bays of 0.45.
        assert [m.v for m in layout.by_entry("R")] == approx_list([0.45, 0.9])

    @pytest.mark.parametrize(
        "spacing",
        [{"mode": "MAX", "value": 1.0, "offset": 0.2}, {"mode": "COUNT", "value": 2, "offset": 0.2}],
    )
    def test_rejects_offset_without_alignment(self, spacing):
        with pytest.raises(FramingError, match="nothing to offset from"):
            self.solve_one({"spacing": spacing})

    def test_fixed_alignment_counts_per_bay(self):
        layout = solve(
            [
                POSTS,
                {
                    "name": "B",
                    "kind": "V",
                    "spacing": {"mode": "FIXED", "value": 0.4, "align": "START"},
                    "within": "Post",
                },
            ]
        )
        # Each 1.5 bay starts again from its own start: 0.4, 0.8, 1.2, then 1.9, 2.3, 2.7.
        assert us(layout, "B") == approx_list([0.4, 0.8, 1.2, 1.9, 2.3, 2.7])

    def test_horizontal_fixed_spacing_from_the_top(self):
        rail = {"name": "R", "kind": "H", "spacing": {"mode": "FIXED", "value": 0.3, "align": "END"}}
        layout = solve([rail], height=1.0)
        assert [m.v for m in layout.by_entry("R")] == approx_list([0.1, 0.4, 0.7])

    def test_rejects_unknown_alignment(self):
        with pytest.raises(FramingError, match="alignment"):
            self.solve_one({"spacing": {"mode": "FIXED", "value": 1.0, "align": "MIDDLE"}})

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
        # Not broken at the posts, so it covers the end posts out to their outer faces.
        assert [(r.u_start, r.u_end) for r in rails] == [pytest.approx((-0.025, 3.025))]

    def test_rail_reaches_the_faces_of_posts_at_its_bay_ends(self):
        members = [
            {"name": "Post", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True},
            {"name": "Rail", "kind": "H", "v": 0.5, "between": "Post", "bays": [2]},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}), [3.0], 1.1, extents={"Post": (-0.025, 0.025)}
        )
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [pytest.approx((1.475, 3.025))]

    def test_offset_rail_is_not_stretched_over_posts_it_misses(self):
        members = [
            {"name": "Post", "kind": "V", "at_ends": True},
            {"name": "Handrail", "kind": "H", "v": 0.9},
        ]
        extents = {"Post": (-0.025, 0.025), "Handrail": (-0.025, 0.025)}
        entries = subject.parse_system({"members": members})
        beside = subject.solve(
            entries, [3.0], 1.1, extents=extents, lateral={"Post": (-0.025, 0.025), "Handrail": (-0.02, 0.03)}
        )
        apart = subject.solve(
            entries, [3.0], 1.1, extents=extents, lateral={"Post": (-0.025, 0.025), "Handrail": (-0.125, -0.075)}
        )
        assert [(r.u_start, r.u_end) for r in beside.by_entry("Handrail")] == [pytest.approx((-0.025, 3.025))]
        assert [(r.u_start, r.u_end) for r in apart.by_entry("Handrail")] == [(0.0, 3.0)]

    def test_rail_extends_past_its_ends_by_a_distance(self):
        members = [
            {"name": "Post", "kind": "V", "at_ends": True},
            {"name": "Rail", "kind": "H", "v": 1.0, "extend_start": 0.3, "extend_end": -0.1},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}), [3.0], 1.1, extents={"Post": (-0.025, 0.025)}
        )
        # Past the outer post faces at the start; pulled back from them at the end.
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [pytest.approx((-0.325, 2.925))]

    def test_extension_leaves_breaks_alone(self):
        members = [
            {"name": "Post", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True},
            {"name": "Rail", "kind": "H", "v": 0.5, "breaks_at": ["Post"], "extend_start": 0.2, "extend_end": 0.2},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}), [3.0], 1.1, extents={"Post": (-0.025, 0.025)}
        )
        # The run ends are past the end posts, but the posts still cut it back to their faces.
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [
            pytest.approx((-0.225, -0.025)),
            pytest.approx((0.025, 1.475)),
            pytest.approx((1.525, 2.975)),
            pytest.approx((3.025, 3.225)),
        ]

    def test_rejects_non_numeric_extension(self):
        with pytest.raises(FramingError, match="to be a number"):
            subject.parse_system({"members": [{"name": "R", "kind": "H", "v": 1.0, "extend_end": "far"}]})

    def test_rail_ignores_verticals_that_do_not_reach_it(self):
        members = [
            {"name": "Stub", "kind": "V", "at_ends": True, "top": 0.2},
            {"name": "Rail", "kind": "H", "v": 1.0},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}), [3.0], 1.1, extents={"Stub": (-0.025, 0.025)}
        )
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [(0.0, 3.0)]

    def test_rail_round_a_loop_has_no_ends_to_extend(self):
        members = [
            {"name": "Post", "kind": "V", "at_corners": True},
            {"name": "Rail", "kind": "H", "v": 1.0},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}), [2.0] * 4, 1.1, closed=True, extents={"Post": (-0.025, 0.025)}
        )
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [(0.0, 8.0)]

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
        assert [p.address for p in panels] == [(0, 0, 0, 0), (0, 1, 0, 0)]
        first = panels[0]
        assert (first.u_start, first.u_end) == pytest.approx((0.0285, 1.4715))
        assert (first.v_start, first.v_end) == pytest.approx((0.0285, 2.3715))

    def test_negative_gap_runs_the_panel_into_its_members(self):
        members = [
            {"name": "Post", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True},
            {"name": "Rail", "kind": "H", "v": 1.0},
            {"name": "Glass", "kind": "INFILL", "between": "Post", "top": {"member": "Rail"}, "gap": -0.01},
        ]
        layout = subject.solve(
            subject.parse_system({"members": members}),
            [3.0],
            1.1,
            extents={"Post": (-0.025, 0.025), "Rail": (-0.02, 0.02)},
        )
        glass = layout.by_entry("Glass")[0]
        # 10 mm into the post faces at either side and into the rail above.
        assert (glass.u_start, glass.u_end) == pytest.approx((0.015, 1.485))
        assert glass.v_end == pytest.approx(0.99)

    def test_frameless_panels_split_by_max_width(self):
        entries = subject.parse_system(
            {"members": [{"name": "Glass", "kind": "INFILL", "max_width": 1.2, "joint": 0.01}]}
        )
        panels = subject.solve(entries, [5.0], 1.0).infills
        assert len(panels) == 5
        assert all(p.u_end - p.u_start == pytest.approx(0.992) for p in panels)
        assert panels[1].u_start - panels[0].u_end == pytest.approx(0.01)
        assert panels[-1].u_end == pytest.approx(5.0)

    def test_infill_breaks_at_members_it_is_not_between(self):
        # Pickets fill the post bays but never stand at a post, so glass between pickets
        # would run straight past the middle post unless it breaks there.
        members = [
            {"name": "Post", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True},
            {
                "name": "Picket",
                "kind": "V",
                "spacing": {"mode": "MAX", "value": 0.28},
                "at_ends": True,
                "within": "Post",
            },
            {"name": "Glass", "kind": "INFILL", "between": "Picket", "gap": 0.02},
        ]
        extents = {"Post": (-0.025, 0.025), "Picket": (-0.03, 0.03)}

        def crossing(layout):
            return [p for p in layout.by_entry("Glass") if p.u_start < 1.525 and p.u_end > 1.475]

        assert crossing(subject.solve(subject.parse_system({"members": members}), [3.0], 1.1, extents=extents))
        members[2]["breaks_at"] = ["Post"]
        layout = subject.solve(subject.parse_system({"members": members}), [3.0], 1.1, extents=extents)
        assert not crossing(layout)
        ends = sorted(round(p.u_end, 6) for p in layout.by_entry("Glass"))
        starts = sorted(round(p.u_start, 6) for p in layout.by_entry("Glass"))
        assert 1.455 in ends and 1.545 in starts

    def test_infill_breaks_only_at_members_through_its_height(self):
        members = [
            {"name": "Stub", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "top": 0.2},
            {"name": "Glass", "kind": "INFILL", "bottom": 0.5, "breaks_at": ["Stub"]},
        ]
        layout = subject.solve(subject.parse_system({"members": members}), [3.0], 1.1)
        assert len(layout.by_entry("Glass")) == 1

    def test_infill_splits_at_path_vertices(self):
        entries = subject.parse_system({"members": [{"name": "Glass", "kind": "INFILL"}]})
        panels = subject.solve(entries, [1.0, 2.0], 1.0).infills
        assert [(p.u_start, p.u_end, p.address) for p in panels] == [(0.0, 1.0, (0, 0, 0, 0)), (1.0, 3.0, (1, 0, 0, 0))]


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


def solve(members, segments=(3.0,), height=1.1, extents=None, voids=()):
    return subject.solve(
        subject.parse_system({"members": members}), list(segments), height, extents=extents, voids=tuple(voids)
    )


POSTS = {
    "name": "Post",
    "kind": "V",
    "spacing": {"mode": "MAX", "value": 1.5},
    "at_ends": True,
    "at_corners": True,
}


class TestBaySelection:
    def test_select_counts_from_one_and_from_the_end(self):
        assert subject._select(list("abcd"), ()) == list("abcd")
        assert subject._select(list("abcd"), (1, -1)) == ["a", "d"]
        assert subject._select(list("abcd"), (2, 3)) == ["b", "c"]
        assert subject._select(list("abcd"), (9,)) == []

    def test_rejects_zero_or_non_integers(self):
        with pytest.raises(FramingError, match="non-zero whole numbers"):
            subject.parse_system({"members": [dict(POSTS, bays=[0])]})
        with pytest.raises(FramingError, match="non-zero whole numbers"):
            subject.parse_system({"members": [dict(POSTS, bays="1")]})

    def test_verticals_fill_only_the_picked_bays(self):
        # Posts at 0, 1.5 and 3 give two bays; one baluster in the middle of the second only.
        baluster = {"name": "Baluster", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "within": "Post"}
        layout = solve([POSTS, dict(baluster, bays=[2])])
        assert us(layout, "Baluster") == approx_list([2.25])
        assert us(solve([POSTS, dict(baluster, bays=[-1])]), "Baluster") == approx_list([2.25])
        assert us(solve([POSTS, baluster]), "Baluster") == approx_list([0.75, 2.25])

    def test_horizontal_runs_only_in_the_picked_bays(self):
        rail = {"name": "Rail", "kind": "H", "v": 0.5, "between": "Post", "bays": [2], "breaks_at": ["Post"]}
        layout = solve([POSTS, rail], extents={"Post": (-0.025, 0.025)})
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [pytest.approx((1.525, 2.975))]

    def test_verticals_follow_the_rail_they_are_bounded_by(self):
        rail = {"name": "Rail", "kind": "H", "v": 0.5, "between": "Post", "bays": [2]}
        baluster = {
            "name": "Baluster",
            "kind": "V",
            "spacing": {"mode": "COUNT", "value": 3},
            "within": "Post",
            "bottom": {"member": "Rail"},
        }
        layout = solve([POSTS, rail, baluster], extents={"Baluster": (-0.01, 0.01)})
        # Balusters stand on the rail, and only in the second bay, where the rail runs.
        assert us(layout, "Baluster") == approx_list([1.875, 2.25, 2.625])
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [(1.5, 3.0)]

    def test_adjacent_bays_merge_into_one_rail(self):
        rail = {"name": "Rail", "kind": "H", "v": 0.5, "between": "Post", "bays": [1, 2]}
        layout = solve([POSTS, rail])
        assert [(r.u_start, r.u_end) for r in layout.by_entry("Rail")] == [(0.0, 3.0)]


class TestVerticalBreaks:
    def test_picket_breaks_at_a_mid_rail(self):
        members = [
            {"name": "Mid", "kind": "H", "v": 0.5},
            {"name": "Picket", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "breaks_at": ["Mid"]},
        ]
        layout = solve(members, extents={"Mid": (-0.02, 0.02)})
        assert [(m.v_start, m.v_end, m.piece) for m in layout.by_entry("Picket")] == [
            pytest.approx((0.0, 0.48, 0)),
            pytest.approx((0.52, 1.1, 1)),
        ]
        # The rail itself stays continuous.
        assert len(layout.by_entry("Mid")) == 1

    def test_mullion_breaks_at_every_row_of_a_repeating_transom(self):
        members = [
            {"name": "Transom", "kind": "H", "spacing": {"mode": "COUNT", "value": 2}},
            {"name": "Mullion", "kind": "V", "at_ends": True, "breaks_at": ["Transom"]},
        ]
        layout = solve(members, height=3.0)
        assert [(m.u, m.v_start, m.v_end) for m in layout.by_entry("Mullion")] == [
            (0.0, 0.0, 1.0),
            (0.0, 1.0, 2.0),
            (0.0, 2.0, 3.0),
            (3.0, 0.0, 1.0),
            (3.0, 1.0, 2.0),
            (3.0, 2.0, 3.0),
        ]

    def test_only_breaks_where_the_rail_runs(self):
        members = [
            dict(POSTS),
            {"name": "Mid", "kind": "H", "v": 0.5, "between": "Post", "bays": [1]},
            {
                "name": "Picket",
                "kind": "V",
                "spacing": {"mode": "COUNT", "value": 1},
                "within": "Post",
                "breaks_at": ["Mid"],
            },
        ]
        layout = solve(members, extents={"Mid": (-0.02, 0.02)})
        pieces = layout.by_entry("Picket")
        # Broken in the first bay, where the mid rail runs; whole in the second.
        assert [round(m.u, 6) for m in pieces] == [0.75, 0.75, 2.25]

    def test_entries_cannot_break_at_each_other(self):
        members = [
            {"name": "Post", "kind": "V", "at_ends": True, "breaks_at": ["Rail"]},
            {"name": "Rail", "kind": "H", "v": 0.5, "breaks_at": ["Post"]},
        ]
        with pytest.raises(FramingError, match="break at each other"):
            subject.parse_system({"members": members})

    def test_breaks_at_must_be_horizontal(self):
        members = [dict(POSTS), {"name": "Picket", "kind": "V", "at_ends": True, "breaks_at": ["Post"]}]
        with pytest.raises(FramingError, match="to be a horizontal"):
            subject.parse_system({"members": members})


class TestRepeatingBounds:
    STOREFRONT = [
        {"name": "Mullion", "kind": "V", "at_ends": True},
        {"name": "Sill", "kind": "H", "v": "BASE", "breaks_at": ["Mullion"]},
        {"name": "Transom", "kind": "H", "spacing": {"mode": "COUNT", "value": 2}, "breaks_at": ["Mullion"]},
        {"name": "Head", "kind": "H", "v": "TOP", "breaks_at": ["Mullion"]},
        {
            "name": "Vision",
            "kind": "INFILL",
            "between": "Mullion",
            "bottom": {"member": "Sill"},
            "top": {"member": "Transom"},
        },
        {
            "name": "Clerestory",
            "kind": "INFILL",
            "between": "Mullion",
            "bottom": {"member": "Transom"},
            "top": {"member": "Head"},
        },
        {"name": "Middle", "kind": "INFILL", "between": "Mullion", "within": "Transom", "rows": [2]},
    ]

    def test_infill_uses_the_nearest_rows(self):
        # Transoms at 1 and 2 on a 3 high storefront.
        layout = solve(self.STOREFRONT, height=3.0, extents={"Transom": (-0.02, 0.02)})
        (vision,) = layout.by_entry("Vision")
        (clerestory,) = layout.by_entry("Clerestory")
        (middle,) = layout.by_entry("Middle")
        assert (vision.v_start, vision.v_end) == pytest.approx((0.0, 0.98))
        assert (clerestory.v_start, clerestory.v_end) == pytest.approx((2.02, 3.0))
        assert (middle.v_start, middle.v_end) == pytest.approx((1.02, 1.98))

    def test_vertical_between_two_repeating_bounds_takes_the_first_gap(self):
        members = [
            {"name": "Rail", "kind": "H", "spacing": {"mode": "COUNT", "value": 3}},
            {
                "name": "Picket",
                "kind": "V",
                "at_ends": True,
                "bottom": {"member": "Rail"},
                "top": {"member": "Rail"},
            },
        ]
        layout = solve(members, height=4.0)
        assert {(m.v_start, m.v_end) for m in layout.by_entry("Picket")} == {(1.0, 2.0)}


class TestHorizontalWithin:
    RAILS = {"name": "Rail", "kind": "H", "spacing": {"mode": "COUNT", "value": 2}}

    def test_repeats_in_each_gap_between_rows(self):
        cable = {"name": "Cable", "kind": "H", "spacing": {"mode": "COUNT", "value": 1}, "within": "Rail"}
        layout = solve([self.RAILS, cable], height=3.0, extents={"Rail": (-0.02, 0.02)})
        assert [r.v for r in layout.by_entry("Rail")] == approx_list([1.0, 2.0])
        # Gaps are (0, 0.98), (1.02, 1.98), (2.02, 3).
        assert [c.v for c in layout.by_entry("Cable")] == approx_list([0.49, 1.5, 2.51])
        assert [c.address[0] for c in layout.by_entry("Cable")] == [0, 1, 2]

    def test_rows_pick_gaps(self):
        cable = {
            "name": "Cable",
            "kind": "H",
            "spacing": {"mode": "COUNT", "value": 1},
            "within": "Rail",
            "rows": [1, -1],
        }
        layout = solve([self.RAILS, cable], height=3.0, extents={"Rail": (-0.02, 0.02)})
        assert [c.v for c in layout.by_entry("Cable")] == approx_list([0.49, 2.51])

    def test_needs_spacing(self):
        with pytest.raises(FramingError, match="needs spacing"):
            subject.parse_system({"members": [self.RAILS, {"name": "C", "kind": "H", "v": 1.0, "within": "Rail"}]})

    def test_within_must_be_horizontal(self):
        with pytest.raises(FramingError, match="to be a horizontal"):
            subject.parse_system(
                {
                    "members": [
                        POSTS,
                        {"name": "C", "kind": "H", "spacing": {"mode": "COUNT", "value": 1}, "within": "Post"},
                    ]
                }
            )


class TestInfillGrid:
    GLASS = {"name": "Glass", "kind": "INFILL", "between": "Post"}
    RAIL = {"name": "Rail", "kind": "H", "spacing": {"mode": "COUNT", "value": 1}}

    def test_stacks_panels_between_rows(self):
        layout = solve([POSTS, self.RAIL, dict(self.GLASS, within="Rail")], extents={"Rail": (-0.02, 0.02)})
        panels = layout.by_entry("Glass")
        assert [(p.address[1], p.address[2]) for p in panels] == [(0, 0), (0, 1), (1, 0), (1, 1)]
        assert (panels[0].v_start, panels[0].v_end) == pytest.approx((0.0, 0.53))
        assert (panels[1].v_start, panels[1].v_end) == pytest.approx((0.57, 1.1))

    def test_bays_and_rows_pick_cells(self):
        layout = solve([POSTS, self.RAIL, dict(self.GLASS, within="Rail", bays=[-1], rows=[2])])
        panels = layout.by_entry("Glass")
        assert [(p.address[1], p.address[2]) for p in panels] == [(1, 1)]

    def test_panels_follow_the_rail_they_are_bounded_by(self):
        # The mid rail only runs in the second bay, so the panel under it is only there too.
        mid = {"name": "Mid", "kind": "H", "v": 0.6, "between": "Post", "bays": [2], "breaks_at": ["Post"]}
        glass = dict(self.GLASS, top={"member": "Mid"})
        layout = solve([POSTS, mid, glass], extents={"Post": (-0.025, 0.025), "Mid": (-0.02, 0.02)})
        panels = layout.by_entry("Glass")
        assert [p.address[1] for p in panels] == [1]
        assert panels[0].v_end == pytest.approx(0.58)

    def test_stacked_panels_follow_a_partial_rail(self):
        # Within a rail that only runs in the first bay: that bay stacks, the other does not.
        rail = {"name": "Rail", "kind": "H", "v": 0.5, "between": "Post", "bays": [1]}
        layout = solve([POSTS, rail, dict(self.GLASS, within="Rail")])
        assert [(p.address[1], p.address[2]) for p in layout.by_entry("Glass")] == [(0, 0), (0, 1), (1, 0)]


class TestSolveInput:
    def test_rejects_zero_length_segment(self):
        entries = subject.parse_system({"members": [{"name": "A", "kind": "V", "at_ends": True}]})
        with pytest.raises(FramingError, match="non-zero"):
            subject.solve(entries, [1.0, 0.0], 1.0)

    def test_rejects_zero_height(self):
        entries = subject.parse_system({"members": [{"name": "A", "kind": "V", "at_ends": True}]})
        with pytest.raises(FramingError, match="height"):
            subject.solve(entries, [1.0], 0.0)


class TestFlush:
    def test_end_verticals_stop_at_the_path_ends(self):
        post = {"name": "P", "kind": "V", "at_ends": True, "at_corners": True}
        extents = {"P": (-0.05, 0.05)}
        assert us(solve([post], segments=(2.0, 2.0), extents=extents), "P") == approx_list([0.0, 2.0, 4.0])
        # Flush, the outer faces sit on the ends; a corner is not a boundary, so it stays centred.
        flush = solve([{**post, "flush": True}], segments=(2.0, 2.0), extents=extents)
        assert us(flush, "P") == approx_list([0.05, 2.0, 3.95])

    def test_max_spacing_between_flush_end_verticals(self):
        post = {"name": "P", "kind": "V", "at_ends": True, "flush": True, "spacing": {"mode": "MAX", "value": 1.4}}
        layout = solve([post], extents={"P": (-0.05, 0.05)})
        # 0.05 to 2.95 in three equal bays.
        assert us(layout, "P") == approx_list([0.05, 0.05 + 2.9 / 3, 0.05 + 5.8 / 3, 2.95])

    def test_fixed_start_puts_the_first_face_on_the_start(self):
        member = {"name": "P", "kind": "V", "flush": True, "spacing": {"mode": "FIXED", "value": 1.0, "align": "START"}}
        layout = solve([member], segments=(3.5,), extents={"P": (-0.05, 0.05)})
        assert us(layout, "P") == approx_list([0.05, 1.05, 2.05, 3.05])

    def test_max_anchor_on_the_end(self):
        spacing = {"mode": "MAX", "value": 1.5, "align": "END"}
        member = {"name": "P", "kind": "V", "flush": True, "spacing": spacing}
        layout = solve([member], segments=(3.0,), extents={"P": (-0.05, 0.05)})
        # A member with its face on the end, then 0.05 to 2.95 in two equal bays.
        assert us(layout, "P") == approx_list([1.5, 2.95])

    def test_balusters_start_against_the_post_face(self):
        baluster = {
            "name": "B",
            "kind": "V",
            "flush": True,
            "within": "Post",
            "spacing": {"mode": "FIXED", "value": 0.1, "align": "START"},
        }
        layout = solve([POSTS, baluster], extents={"Post": (-0.025, 0.025), "B": (-0.008, 0.008)})
        bays = {}
        for m in layout.by_entry("B"):
            bays.setdefault(m.address[1], []).append(m.u)
        assert [min(u) for u in bays.values()] == approx_list([0.033, 1.533])

    def test_horizontals_at_base_and_top(self):
        members = [
            {"name": "Head", "kind": "H", "v": "TOP", "flush": True},
            {"name": "Sill", "kind": "H", "v": "BASE", "flush": True},
            {"name": "Mid", "kind": "H", "v": 0.5, "flush": True},
            {"name": "Post", "kind": "V", "at_ends": True, "top": {"member": "Head"}},
        ]
        extents = {"Head": (-0.02, 0.02), "Sill": (-0.03, 0.03), "Mid": (-0.01, 0.01)}
        layout = solve(members, height=1.0, extents=extents)
        levels = {name: [m.v for m in layout.by_entry(name)] for name in ("Head", "Sill", "Mid")}
        # An absolute level is not a boundary, so it stays centred.
        assert levels == {"Head": approx_list([0.98]), "Sill": approx_list([0.03]), "Mid": approx_list([0.5])}
        # A vertical bounded by the flush head still stops under its bottom face.
        assert [m.v_end for m in layout.by_entry("Post")] == approx_list([0.96, 0.96])

    def test_repeating_horizontal(self):
        rail = {"name": "R", "kind": "H", "flush": True, "spacing": {"mode": "FIXED", "value": 0.3, "align": "START"}}
        layout = solve([rail], height=1.0, extents={"R": (-0.01, 0.01)})
        assert [m.v for m in layout.by_entry("R")] == approx_list([0.01, 0.31, 0.61, 0.91])

    def test_off_by_default(self):
        entries = subject.parse_system({"members": [{"name": "P", "kind": "V", "at_ends": True}]})
        assert entries[0].flush is False


class TestWithinSeveralEntries:
    MEMBERS = [
        {"name": "Ends", "kind": "V", "at_ends": True},
        {"name": "Mid", "kind": "V", "spacing": {"mode": "COUNT", "value": 2}},
    ]
    EXTENTS = {"Ends": (-0.2, 0.2), "Mid": (-0.1, 0.1)}

    def jambs(self, within):
        jamb = {
            "name": "Jamb",
            "kind": "V",
            "within": within,
            "spacing": {"mode": "MAX", "value": 10.0, "align": "END", "offset": 0.05},
        }
        return solve(self.MEMBERS + [jamb], segments=(6.0,), extents=self.EXTENTS).by_entry("Jamb")

    def test_end_bays_stop_at_the_other_entry_faces(self):
        # Within Mid alone, the end bays run to the path ends, inside the Ends posts.
        assert [m.u for m in self.jambs("Mid")] == approx_list([1.85, 3.85, 5.95])
        # Within both, every bay runs face to face, so the last jamb clears the Ends post.
        assert [m.u for m in self.jambs(["Mid", "Ends"])] == approx_list([1.85, 3.85, 5.75])

    def test_bays_are_counted_the_same(self):
        assert [m.address[1] for m in self.jambs(["Mid", "Ends"])] == [0, 1, 2]

    def test_one_name_or_a_list_of_one(self):
        assert [m.u for m in self.jambs(["Mid"])] == [m.u for m in self.jambs("Mid")]

    def test_widest_parent_bounds_a_shared_position(self):
        members = [
            {"name": "Ends", "kind": "V", "at_ends": True},
            {"name": "Corner", "kind": "V", "at_ends": True},
            {"name": "B", "kind": "V", "within": ["Ends", "Corner"], "spacing": {"mode": "COUNT", "value": 1}},
        ]
        layout = solve(members, segments=(2.0,), extents={"Ends": (-0.1, 0.1), "Corner": (-0.3, 0.3)})
        # Both sit at 0 and 2; the wider Corner bounds the bay, 0.3 to 1.7.
        assert us(layout, "B") == approx_list([1.0])
        assert solve(
            members[:2] + [{**members[2], "spacing": {"mode": "FIXED", "value": 0.5, "align": "START"}}],
            segments=(2.0,),
            extents={"Ends": (-0.1, 0.1), "Corner": (-0.3, 0.3)},
        ).by_entry("B")[0].u == pytest.approx(0.8)

    @pytest.mark.parametrize(
        "within, message",
        [(["Nope"], "unknown entry"), ([1], "entry name"), ({"name": "Ends"}, "entry name")],
    )
    def test_rejects_invalid_parents(self, within, message):
        members = [
            {"name": "Ends", "kind": "V", "at_ends": True},
            {"name": "B", "kind": "V", "within": within, "at_ends": True},
        ]
        with pytest.raises(FramingError, match=message):
            subject.parse_system({"members": members})

    def test_rejects_a_loop_through_a_list(self):
        members = [
            {"name": "A", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "within": ["C", "B"]},
            {"name": "B", "kind": "V", "spacing": {"mode": "COUNT", "value": 1}, "within": "A"},
            {"name": "C", "kind": "V", "at_ends": True},
        ]
        with pytest.raises(FramingError, match="loop"):
            subject.parse_system({"members": members})


class TestEqualOpenings:
    EXTENTS = {"Ends": (-0.2, 0.2), "Mid": (-0.1, 0.1)}

    def mids(self, spacing, extents=EXTENTS):
        members = [
            {"name": "Ends", "kind": "V", "at_ends": True},
            {"name": "Mid", "kind": "V", "within": "Ends", "spacing": spacing},
        ]
        return us(solve(members, segments=(6.0,), extents=extents), "Mid")

    def openings(self, mids):
        faces = [0.2] + [f for u in mids for f in (u - 0.1, u + 0.1)] + [5.8]
        return [b - a for a, b in zip(faces[::2], faces[1::2])]

    def test_count_leaves_equal_openings(self):
        mids = self.mids({"mode": "COUNT", "value": 2, "openings": True})
        # 5.6 between the end faces, less two 0.2 posts, in three openings of 5.2 / 3.
        assert self.openings(mids) == approx_list([5.2 / 3] * 3)
        # Centre to centre between the end faces, the end openings are wider by half a post.
        centred = self.openings(self.mids({"mode": "COUNT", "value": 2}))
        assert centred[0] - centred[1] == pytest.approx(0.1)

    @pytest.mark.parametrize("value, n_openings", [(1.8, 3), (1.7, 4)])
    def test_max_limits_the_clear_opening(self, value, n_openings):
        mids = self.mids({"mode": "MAX", "value": value, "openings": True})
        openings = self.openings(mids)
        assert len(openings) == n_openings
        assert openings == approx_list([openings[0]] * n_openings)
        assert openings[0] <= value

    def test_lines_match_equal_bays(self):
        spacing = {"mode": "COUNT", "value": 2}
        assert self.mids({**spacing, "openings": True}, extents={}) == approx_list(self.mids(spacing, extents={}))

    def test_horizontal_rows_between_member_faces(self):
        members = [
            {"name": "Bottom", "kind": "H", "v": "BASE", "flush": True},
            {"name": "Top", "kind": "H", "v": "TOP", "flush": True},
            {
                "name": "Rail",
                "kind": "H",
                "bottom": {"member": "Bottom"},
                "top": {"member": "Top"},
                "spacing": {"mode": "COUNT", "value": 1, "openings": True},
            },
        ]
        extents = {"Bottom": (-0.1, 0.1), "Top": (-0.05, 0.05), "Rail": (-0.02, 0.02)}
        layout = solve(members, height=1.0, extents=extents)
        # Faces at 0.2 and 0.9: a 0.04 rail leaves two openings of 0.33.
        assert [m.v for m in layout.by_entry("Rail")] == approx_list([0.2 + 0.33 + 0.02])

    def test_too_many_members(self):
        with pytest.raises(FramingError, match="too wide"):
            self.mids({"mode": "COUNT", "value": 40, "openings": True})

    @pytest.mark.parametrize(
        "member, message",
        [
            ({"spacing": {"mode": "FIXED", "value": 1.0, "openings": True}}, "FIXED"),
            ({"spacing": {"mode": "MAX", "value": 1.0, "align": "START", "openings": True}}, "alignment"),
        ],
    )
    def test_rejects_combinations(self, member, message):
        with pytest.raises(FramingError, match=message):
            subject.parse_system({"members": [{"name": "M", "kind": "V", **member}]})

    @pytest.mark.parametrize("flush, openings", [(False, 1.6), (True, (5.2 - 0.8) / 3)])
    def test_own_end_members_bound_the_openings(self, flush, openings):
        post = {
            "name": "Post",
            "kind": "V",
            "at_ends": True,
            "flush": flush,
            "spacing": {"mode": "COUNT", "value": 2, "openings": True},
        }
        layout = solve([post], segments=(6.0,), extents={"Post": (-0.2, 0.2)})
        posts = us(layout, "Post")
        # Centred end posts leave 0.2 to 5.8 between their faces, flush ones 0.4 to 5.6.
        faces = [f for u in posts for f in (u - 0.2, u + 0.2)]
        gaps = [b - a for a, b in zip(faces[1::2], faces[2::2])]
        assert gaps == approx_list([openings] * 3)
        assert posts[0] == pytest.approx(0.2 if flush else 0.0)

    def test_flush_horizontal_repeat_measures_from_the_bound_faces(self):
        rail = {
            "name": "Rail",
            "kind": "H",
            "flush": True,
            "bottom": {"member": "Bottom"},
            "top": {"member": "Top"},
            "spacing": {"mode": "COUNT", "value": 1, "openings": True},
        }
        members = [
            {"name": "Bottom", "kind": "H", "v": "BASE", "flush": True},
            {"name": "Top", "kind": "H", "v": "TOP", "flush": True},
        ]
        extents = {"Bottom": (-0.1, 0.1), "Top": (-0.05, 0.05), "Rail": (-0.02, 0.02)}
        layout = solve(members + [rail], height=1.0, extents=extents)
        assert [m.v for m in layout.by_entry("Rail")] == approx_list([0.2 + 0.33 + 0.02])


def storefront(**mullion):
    return [
        {"name": "Mullion", "kind": "V", "spacing": {"mode": "MAX", "value": 1.5}, "at_ends": True, **mullion},
        {"name": "Sill", "kind": "H", "v": "BASE", "breaks_at": ["Mullion"]},
        {"name": "Head", "kind": "H", "v": "TOP", "breaks_at": ["Mullion"]},
        {
            "name": "Glass",
            "kind": "INFILL",
            "between": "Mullion",
            "bottom": {"member": "Sill"},
            "top": {"member": "Head"},
            "gap": 0.01,
        },
    ]


STOREFRONT_EXTENTS = {"Mullion": (-0.025, 0.025), "Sill": (0.0, 0.1), "Head": (-0.1, 0.0)}
DOOR = subject.Void(2.0, 3.0, 0.0, 2.1, "IfcDoor")


def solve_storefront(members, voids, segments=(6.0,), extents=STOREFRONT_EXTENTS):
    return solve(members, segments=segments, height=3.0, extents=extents, voids=voids)


def jambs(layout, name):
    return [m for m in layout.by_entry(name) if isinstance(m, subject.VerticalMember) and m.address[1] < 0]


def boxes(layout, name):
    return sorted((p.u_start, p.u_end, p.v_start, p.v_end) for p in layout.by_entry(name))


class TestVoids:
    def test_door_in_the_middle(self):
        layout = solve_storefront(storefront(), [DOOR])
        # The end mullion's profile frames the door, flush outside it. The spaced mullion
        # at 3.0 is in the way of the right jamb, so it makes way.
        assert [m.u for m in jambs(layout, "Mullion")] == approx_list([1.975, 3.025])
        assert all((m.v_start, m.v_end) == (0.0, 3.0) for m in jambs(layout, "Mullion"))
        assert sorted(us(layout, "Mullion")) == approx_list([0.0, 1.5, 1.975, 3.025, 4.5, 6.0])
        # The head defaults to the top horizontal's profile, its underside on the opening.
        head = [m for m in layout.by_entry("Head") if m.address[0] < 0]
        assert [(m.v, m.u_start, m.u_end) for m in head] == [pytest.approx((2.2, 2.0, 3.0))]
        # The sill does not cross the door or the jambs.
        assert all(m.u_end <= 1.95 + 1e-9 or m.u_start >= 3.05 - 1e-9 for m in layout.by_entry("Sill"))

    def test_glass_is_cut_around_the_door_with_its_gap(self):
        layout = solve_storefront(storefront(), [DOOR])
        middle_bay = [b for b in boxes(layout, "Glass") if 1.5 < b[0] < 4.5]
        assert middle_bay == [
            pytest.approx((1.535, 1.94, 0.11, 2.89)),
            pytest.approx((2.01, 2.99, 2.21, 2.89)),  # the transom over the door
            pytest.approx((3.06, 4.465, 0.11, 2.89)),
        ]

    def test_mullions_over_a_door_are_cut_above_the_head(self):
        door = subject.Void(1.0, 2.0, 0.0, 2.1)
        layout = solve_storefront(storefront(), [door], extents={**STOREFRONT_EXTENTS, "Mullion": (-0.01, 0.01)})
        over = [(m.v_start, m.v_end) for m in layout.by_entry("Mullion") if abs(m.u - 1.5) < 1e-9]
        assert over == [pytest.approx((2.2, 3.0))]

    def test_members_can_run_through(self):
        door = subject.Void(2.5, 3.5, 0.0, 2.1)
        members = storefront(cut_by_voids=False)
        members[3]["cut_by_voids"] = False
        layout = solve_storefront(members, [door])
        assert [(m.v_start, m.v_end) for m in layout.by_entry("Mullion") if abs(m.u - 3.0) < 1e-9] == [(0.0, 3.0)]
        # The glass is left whole too.
        assert boxes(layout, "Glass") == boxes(solve_storefront(members, []), "Glass")

    def test_a_running_through_horizontal_serves_as_the_head(self):
        transom = {"name": "Transom", "kind": "H", "v": 2.15, "cut_by_voids": False}
        layout = solve_storefront(
            storefront() + [transom], [DOOR], extents={**STOREFRONT_EXTENTS, "Transom": (-0.025, 0.025)}
        )
        assert not [m for m in layout.by_entry("Head") if m.address[0] < 0]
        assert [(m.u_start, m.u_end) for m in layout.by_entry("Transom")] == [(-0.025, 6.025)]

    def test_door_at_the_end_uses_the_end_mullion_as_its_jamb(self):
        door = subject.Void(5.0, 5.975, 0.0, 2.1)
        layout = solve_storefront(storefront(), [door])
        assert [m.u for m in jambs(layout, "Mullion")] == approx_list([4.975])
        head = [m for m in layout.by_entry("Head") if m.address[0] < 0]
        assert [(m.u_start, m.u_end) for m in head] == [pytest.approx((5.0, 5.975))]

    def test_opening_to_the_path_end_cuts_the_end_member(self):
        door = subject.Void(5.5, 6.0, 0.0, 2.1)
        layout = solve_storefront(storefront(), [door])
        assert [m.u for m in jambs(layout, "Mullion")] == approx_list([5.475])
        end = [(m.v_start, m.v_end) for m in layout.by_entry("Mullion") if abs(m.u - 6.0) < 1e-9]
        assert end == [pytest.approx((2.2, 3.0))]

    def test_full_height_opening_has_no_head(self):
        gate = subject.Void(2.0, 3.0, 0.0, 3.0)
        layout = solve_storefront(storefront(), [gate])
        assert not [m for m in layout.by_entry("Head") if m.address[0] < 0]
        assert all(m.u_end <= 2.0 or m.u_start >= 3.0 for m in layout.by_entry("Head"))


WOOD = [
    {"name": "Plate", "kind": "H", "v": "BASE"},
    {"name": "TopPlate", "kind": "H", "v": "TOP"},
    {
        "name": "Stud",
        "kind": "V",
        "spacing": {"mode": "MAX", "value": 0.4},
        "at_ends": True,
        "bottom": {"member": "Plate"},
        "top": {"member": "TopPlate"},
    },
    {
        "name": "King",
        "kind": "V",
        "void_role": "JAMB",
        "void_layer": 2,
        "bottom": {"member": "Plate"},
        "top": {"member": "TopPlate"},
    },
    {"name": "Jack", "kind": "V", "void_role": "JAMB", "jamb_height": "HEAD", "bottom": {"member": "Plate"}},
    {"name": "Header", "kind": "H", "void_role": "HEAD"},
    {"name": "RoughSill", "kind": "H", "void_role": "SILL"},
]
WOOD_EXTENTS = {
    "Plate": (0.0, 0.04),
    "TopPlate": (-0.04, 0.0),
    "Stud": (-0.02, 0.02),
    "King": (-0.02, 0.02),
    "Jack": (-0.02, 0.02),
    "Header": (-0.1, 0.1),
    "RoughSill": (-0.02, 0.02),
}
WINDOW = subject.Void(1.0, 2.0, 0.9, 2.0, "IfcWindow")


class TestLayeredJambs:
    def layout(self, members=WOOD, voids=(WINDOW,)):
        return solve(members, segments=(3.2,), height=2.4, extents=WOOD_EXTENTS, voids=voids)

    def test_jacks_carry_the_header_between_full_height_kings(self):
        layout = self.layout()
        assert [(m.u, m.v_start, m.v_end) for m in layout.by_entry("Jack")] == [
            pytest.approx((0.98, 0.04, 2.0)),
            pytest.approx((2.02, 0.04, 2.0)),
        ]
        assert [(m.u, m.v_start, m.v_end) for m in layout.by_entry("King")] == [
            pytest.approx((0.94, 0.04, 2.36)),
            pytest.approx((2.06, 0.04, 2.36)),
        ]
        assert [(m.v, m.u_start, m.u_end) for m in layout.by_entry("Header")] == [pytest.approx((2.1, 0.96, 2.04))]
        assert [(m.v, m.u_start, m.u_end) for m in layout.by_entry("RoughSill")] == [pytest.approx((0.88, 1.0, 2.0))]

    def test_studs_become_cripples_or_make_way(self):
        layout = self.layout()
        cripples = [(m.v_start, m.v_end) for m in layout.by_entry("Stud") if abs(m.u - 1.2) < 1e-9]
        assert cripples == [pytest.approx((0.04, 0.86)), pytest.approx((2.2, 2.36))]
        # The stud at 2.0 is where the right jack goes.
        assert not [m for m in layout.by_entry("Stud") if abs(m.u - 2.0) < 1e-9]
        assert [(m.u_start, m.u_end) for m in layout.by_entry("Plate")] == [pytest.approx((-0.02, 3.22))]

    def test_framing_entries_can_be_for_one_filling(self):
        members = [dict(m, void_for=["IfcDoor"]) if m.get("void_role") else m for m in WOOD]
        layout = self.layout(members, voids=(subject.Void(1.0, 2.0, 0.9, 2.0),))
        assert not layout.by_entry("Jack") and not layout.by_entry("King")
        # Without its own jambs, the bare opening falls back to the end stud's profile.
        assert [m.u for m in jambs(layout, "Stud")] == approx_list([0.98, 2.02])

    @pytest.mark.parametrize(
        "member, message",
        [
            ({"name": "J", "kind": "V", "void_role": "JAMB", "at_ends": True}, "cannot have 'at_ends'"),
            ({"name": "J", "kind": "V", "void_role": "JAMB", "jamb_height": "HALF"}, "jamb height"),
            ({"name": "J", "kind": "V", "void_role": "HEAD"}, "unknown void role"),
            ({"name": "J", "kind": "H", "void_role": "HEAD", "v": 1.0}, "cannot have 'v'"),
            ({"name": "J", "kind": "INFILL", "void_role": "HEAD"}, "cannot have a void role"),
            ({"name": "J", "kind": "V", "at_ends": True, "top": {"member": "Header"}}, "only frames openings"),
        ],
    )
    def test_rejects(self, member, message):
        with pytest.raises(FramingError, match=message):
            subject.parse_system({"members": [{"name": "Header", "kind": "H", "void_role": "HEAD"}, member]})

    @pytest.mark.parametrize(
        "void, message",
        [
            (subject.Void(2.5, 3.5, 0.0, 2.0), "crosses a corner"),
            (subject.Void(1.0, 1.0, 0.0, 2.0), "no size"),
        ],
    )
    def test_rejects_openings(self, void, message):
        with pytest.raises(FramingError, match=message):
            solve(WOOD, segments=(3.0, 3.0), height=2.4, extents=WOOD_EXTENTS, voids=(void,))


def frame(jamb_height=None):
    members = [
        {
            "name": "Ends",
            "kind": "V",
            "at_ends": True,
            "flush": True,
            "bottom": {"member": "Bottom"},
            "top": {"member": "Top"},
        },
        {
            "name": "Stud",
            "kind": "V",
            "spacing": {"mode": "MAX", "value": 1.0},
            "within": "Ends",
            "bottom": {"member": "Bottom"},
            "top": {"member": "Top"},
        },
        {"name": "Bottom", "kind": "H", "v": "BASE", "flush": True},
        {"name": "Top", "kind": "H", "v": "TOP", "flush": True},
        {"name": "Rail", "kind": "H", "v": 1.5, "breaks_at": ["Ends", "Stud"]},
        {
            "name": "Glass",
            "kind": "INFILL",
            "between": "Stud",
            "bottom": {"member": "Bottom"},
            "top": {"member": "Rail"},
            "gap": 0.01,
        },
    ]
    if jamb_height:
        jamb = {"name": "Jamb", "kind": "V", "void_role": "JAMB", "jamb_height": jamb_height}
        members.append({**jamb, "bottom": {"member": "Bottom"}, "top": {"member": "Top"}})
    return members


FRAME_EXTENTS = {
    "Ends": (-0.05, 0.05),
    "Stud": (-0.025, 0.025),
    "Bottom": (-0.05, 0.05),
    "Top": (-0.05, 0.05),
    "Rail": (-0.02, 0.02),
    "Jamb": (-0.05, 0.05),
}
# Everything left of the line from (2/3, -1) to (7/3, 4), so u = 2/3 + (v + 1) / 3.
ANGLED_END = subject.Void(-1, 2.4, -1, 4, outline=((-1, -1), (2 / 3, -1), (7 / 3, 4), (-1, 4)))
# Everything above the line v = 2.9 - 0.1 (u + 1).
RAKED_TOP = subject.Void(-1, 7, 2.1, 4, outline=((-1, 2.9), (7, 2.1), (7, 4), (-1, 4)))


def end_line(v):
    return 2 / 3 + (v + 1) / 3


def rake_line(u):
    return 2.9 - 0.1 * (u + 1)


def solve_frame(voids, jamb_height=None):
    return solve(frame(jamb_height), segments=(6.0,), height=3.0, extents=FRAME_EXTENTS, voids=voids)


def parallel(cut, direction):
    return abs(cut[0] * direction[1] - cut[1] * direction[0]) < 1e-6


class TestSlopedVoids:
    def test_raked_top(self):
        layout = solve_frame([RAKED_TOP])
        (rake,) = layout.inclined
        # The rake is framed under the opening, so as a sill: the lowest horizontal's profile.
        assert (rake.entry, rake.kind) == ("Bottom", "H")
        # Its top face lies on the rake, and it runs to the path end, cut plumb there.
        assert rake.end[0] == pytest.approx(6.0)
        assert rake.start[1] + 0.05 * math.hypot(1, 0.1) == pytest.approx(rake_line(rake.start[0]))
        assert parallel(rake.end_cut, (0, 1))
        # Studs stop on the rake's underside, cut along it.
        for stud in layout.by_entry("Stud"):
            assert stud.v_end == pytest.approx(rake_line(stud.u) - 0.1 * math.hypot(1, 0.1))
            assert parallel(stud.top_cut, (1, -0.1))
        # The end posts are cut too, and the top rail is gone.
        assert all(m.top_cut for m in layout.by_entry("Ends"))
        assert not layout.by_entry("Top")

    def test_angled_end(self):
        layout = solve_frame([ANGLED_END])
        (jamb,) = layout.inclined
        assert (jamb.entry, jamb.kind) == ("Ends", "V")
        # It stands on the bottom rail and leans with the edge, its face on it.
        assert jamb.start[1] == pytest.approx(0.1)
        assert parallel(jamb.start_cut, (1, 0))
        assert jamb.start[0] - 0.05 * math.hypot(1, 1 / 3) == pytest.approx(end_line(0.1))
        # The end post inside the opening is gone; the other one stays.
        assert [m.u for m in layout.by_entry("Ends") if isinstance(m, subject.VerticalMember)] == [5.95]
        # The bottom rail runs to the edge, and the rail to the jamb's far face, both cut along it.
        (bottom, *_) = layout.by_entry("Bottom")
        assert bottom.u_start == pytest.approx(end_line(0.05))
        rail = min(layout.by_entry("Rail"), key=lambda m: m.u_start)
        assert rail.u_start == pytest.approx(end_line(1.5) + 0.1 * math.hypot(1, 1 / 3))
        assert parallel(bottom.start_cut, (1, 3)) and parallel(rail.start_cut, (1, 3))

    def test_panels_take_the_shape_left_by_the_opening(self):
        layout = solve_frame([ANGLED_END])
        first = min(layout.by_entry("Glass"), key=lambda p: p.u_start)
        assert len(first.outline) == 4
        # Its sloped side keeps the glass gap from the jamb's far face.
        u, v = min(first.outline, key=lambda p: (p[1], p[0]))
        assert v == pytest.approx(0.11)
        assert u > end_line(0.11) + 0.1 * math.hypot(1, 1 / 3)

    @pytest.mark.parametrize("jamb_height", [None, "FULL", "HEAD", "MITRE"])
    def test_corner_joints(self, jamb_height):
        layout = solve_frame([ANGLED_END, RAKED_TOP], jamb_height)
        jamb = next(m for m in layout.inclined if m.kind == "V")
        rake = next(m for m in layout.inclined if m.kind == "H")
        if jamb_height in (None, "FULL"):
            # The jamb runs through to the rake, which butts into it.
            assert jamb.end[1] == pytest.approx(rake_line(jamb.end[0]))
            assert parallel(rake.start_cut, (1, 3))
            assert rake.start[0] > jamb.end[0]
        elif jamb_height == "HEAD":
            # The rake runs through to the edge, and the jamb stops under it.
            assert rake.start[0] == pytest.approx(end_line(rake.start[1]))
            assert jamb.end[1] < rake_line(jamb.end[0]) - 0.1
        else:
            assert jamb.end == pytest.approx(rake.start)
            assert parallel(jamb.end_cut, rake.start_cut)
            assert not parallel(jamb.end_cut, (1, 3)) and not parallel(jamb.end_cut, (1, -0.1))

    def test_mitred_jambs_frame_a_rectangle_edge_by_edge(self):
        window = subject.Void(2.0, 3.0, 1.0, 2.0)
        layout = solve_frame([window], "MITRE")
        assert sorted((m.entry, m.kind) for m in layout.inclined) == [
            ("Bottom", "H"),
            ("Jamb", "V"),
            ("Jamb", "V"),
            ("Top", "H"),
        ]
        jamb = next(m for m in layout.inclined if m.entry == "Jamb")
        head = next(m for m in layout.inclined if m.entry == "Top")
        assert parallel(jamb.end_cut, (1, 1)) or parallel(jamb.end_cut, (1, -1))
        assert parallel(head.start_cut, jamb.end_cut) or parallel(head.end_cut, jamb.end_cut)

    def test_cuts_the_framing_of_rectangular_openings(self):
        window = subject.Void(3.2, 3.8, 1.0, 1.4)
        layout = solve_frame([window, RAKED_TOP])
        jambs = [m for m in layout.by_entry("Ends") if isinstance(m, subject.VerticalMember) and m.address[1] < 0]
        assert len(jambs) == 2
        for m in jambs:
            assert m.v_end < rake_line(m.u)
            assert m.top_cut is not None

    def test_stays_on_its_leg(self):
        # Mostly on the second leg, reaching back round the corner: kept to the second leg.
        void = subject.Void(2.5, 5.0, 1.0, 2.0, outline=((2.5, 1.0), (5.0, 1.0), (5.0, 2.0), (2.5, 2.0)))
        layout = solve(frame(), segments=(3.0, 3.0), height=3.0, extents=FRAME_EXTENTS, voids=[void])
        assert all(m.start[0] >= 3.0 - 1e-9 for m in layout.inclined)
        # The first leg's studs are not cut.
        assert all(m.top_cut is None and m.bottom_cut is None for m in layout.by_entry("Stud") if m.u < 3.0)


class TestEdgeAndHoleOpenings:
    # A door standing on the base reaches a side of the framing, so it is an edge opening;
    # a window inside it is a hole.
    DOOR = subject.Void(2.0, 3.0, 0.0, 2.6, "IfcDoor")
    WINDOW = subject.Void(4.0, 5.0, 1.0, 2.6, "IfcWindow")

    def transom(self, **cuts):
        transom = {"name": "Transom", "kind": "H", "v": 2.4, **cuts}
        extents = {**STOREFRONT_EXTENTS, "Transom": (-0.025, 0.025)}
        layout = solve_storefront(storefront() + [transom], [self.DOOR, self.WINDOW], extents=extents)
        return [(round(m.u_start, 3), round(m.u_end, 3)) for m in layout.by_entry("Transom") if m.address[0] >= 0]

    def test_cut_by_both(self):
        runs = self.transom()
        assert not any(a < 2.5 < b for a, b in runs) and not any(a < 4.5 < b for a, b in runs)

    def test_runs_through_holes(self):
        runs = self.transom(cut_by_hole_voids=False)
        assert not any(a < 2.5 < b for a, b in runs)
        assert any(a < 4.0 and b > 5.0 for a, b in runs)

    def test_runs_through_edge_openings(self):
        runs = self.transom(cut_by_edge_voids=False)
        assert any(a < 2.0 and b > 3.0 for a, b in runs)
        assert not any(a < 4.5 < b for a, b in runs)

    def test_the_older_key_sets_both(self):
        (entry,) = subject.parse_system({"members": [{"name": "R", "kind": "H", "v": 1.0, "cut_by_voids": False}]})
        assert not entry.cut_by_edge_voids and not entry.cut_by_hole_voids
        (entry,) = subject.parse_system(
            {"members": [{"name": "R", "kind": "H", "v": 1.0, "cut_by_voids": False, "cut_by_hole_voids": True}]}
        )
        assert not entry.cut_by_edge_voids and entry.cut_by_hole_voids

    def test_sloped_openings_are_sorted_too(self):
        # The rake reaches the top, so it is an edge opening; a diamond in the middle is a hole.
        diamond = subject.Void(2.7, 3.3, 0.7, 1.3, outline=((3.0, 0.7), (3.3, 1.0), (3.0, 1.3), (2.7, 1.0)))
        members = frame()
        rail = next(m for m in members if m["name"] == "Rail")
        rail.update(v=1.0, cut_by_edge_voids=False)
        stud = next(m for m in members if m["name"] == "Stud")
        stud["cut_by_hole_voids"] = False
        layout = solve(members, segments=(6.0,), height=3.0, extents=FRAME_EXTENTS, voids=[RAKED_TOP, diamond])
        # The rail is cut by the diamond, but the stud at 3.0 runs through it, and stops at the rake.
        assert not any(m.u_start < 2.85 < m.u_end for m in layout.by_entry("Rail"))
        (stud,) = [m for m in layout.by_entry("Stud") if abs(m.u - 3.0) < 1e-9]
        assert stud.v_start == pytest.approx(0.1) and stud.top_cut is not None


class TestHeadAndSillLayers:
    def test_layers_stack_away_from_the_opening(self):
        members = WOOD[:-2] + [
            {"name": "Header Bottom", "kind": "H", "void_role": "HEAD"},
            {"name": "Header A", "kind": "H", "void_role": "HEAD", "void_layer": 2, "offset": -0.02},
            {"name": "Header B", "kind": "H", "void_role": "HEAD", "void_layer": 2, "offset": 0.02},
            {"name": "Header Top", "kind": "H", "void_role": "HEAD", "void_layer": 3},
            {"name": "Sill Top", "kind": "H", "void_role": "SILL"},
            {"name": "Sill Bottom", "kind": "H", "void_role": "SILL", "void_layer": 2},
        ]
        extents = {
            **WOOD_EXTENTS,
            "Header Bottom": (-0.02, 0.02),
            "Header A": (-0.1, 0.1),
            "Header B": (-0.1, 0.1),
            "Header Top": (-0.02, 0.02),
            "Sill Top": (-0.02, 0.02),
            "Sill Bottom": (-0.02, 0.02),
        }
        layout = solve(members, segments=(3.2,), height=2.4, extents=extents, voids=[WINDOW])
        levels = {m.entry: m.v for m in layout.horizontals if m.address[0] < 0}
        # Upwards from the opening's head at 2.0: 0.04, then the sistered pair 0.2 side by side, then 0.04.
        assert levels == pytest.approx(
            {
                "Header Bottom": 2.02,
                "Header A": 2.14,
                "Header B": 2.14,
                "Header Top": 2.26,
                "Sill Top": 0.88,
                "Sill Bottom": 0.84,
            }
        )
        # Studs over the opening stop on the top layer, and under it at the bottom one.
        pieces = [(m.v_start, m.v_end) for m in layout.by_entry("Stud") if abs(m.u - 1.2) < 1e-9]
        assert pieces == [pytest.approx((0.04, 0.82)), pytest.approx((2.28, 2.36))]

    def test_the_layer_must_be_positive(self):
        with pytest.raises(FramingError, match="void layer"):
            subject.parse_system({"members": [{"name": "H", "kind": "H", "void_role": "HEAD", "void_layer": 0}]})


# Over the second leg of an L (u 3 to 6), everything above a line falling from 3.0 at the corner.
RAKE_ON_LEG = subject.Void(3.0, 7.0, 2.0, 5.0, outline=((3.0, 3.0), (7.0, 1.8), (7.0, 5.0), (3.0, 5.0)))
RAKE_PLATES = [
    {"name": "Rake Plate", "kind": "H", "void_role": "SILL", "void_layer": 1},
    {"name": "Rake Plate 2", "kind": "H", "void_role": "SILL", "void_layer": 2},
]


class TestSlopedLayers:
    def test_layers_stack_parallel_to_the_slope_and_stop_at_the_corner(self):
        extents = {**FRAME_EXTENTS, "Rake Plate": (-0.05, 0.05), "Rake Plate 2": (-0.05, 0.05)}
        layout = solve(frame() + RAKE_PLATES, segments=(3.0, 3.0), height=3.0, extents=extents, voids=[RAKE_ON_LEG])
        first, second = sorted(layout.inclined, key=lambda m: m.entry)
        slope = math.hypot(1, 0.3)
        for member, depth in ((first, 0.05), (second, 0.15)):
            # Parallel to the rake, each a plate's depth further from it, square to the slope.
            u, v = member.start
            assert v == pytest.approx(3.0 - 0.3 * (u - 3.0) - depth * slope)
            assert (member.end[1] - member.start[1]) / (member.end[0] - member.start[0]) == pytest.approx(-0.3)
            # They start on the corner, cut plumb there, and run to the path end.
            assert u == pytest.approx(3.0) and parallel(member.start_cut, (0, 1))
            assert member.end[0] == pytest.approx(6.0)
        # The first leg's top rail stops at the corner, cut plumb there too.
        (top,) = [m for m in layout.by_entry("Top") if m.u_start < 3.0]
        assert top.u_end == pytest.approx(3.0) and parallel(top.end_cut, (0, 1))


class TestLevelOffset:
    def test_a_plate_follows_the_top_a_set_distance_under_it(self):
        members = [
            {"name": "Upper", "kind": "H", "v": "TOP", "flush": True},
            {"name": "Lower", "kind": "H", "v": "TOP", "flush": True, "level_offset": -0.125},
        ]
        extents = {"Upper": (-0.0625, 0.0625), "Lower": (-0.0625, 0.0625)}
        for height in (8.0, 9.0):
            layout = solve(members, height=height, extents=extents)
            (upper,), (lower,) = layout.by_entry("Upper"), layout.by_entry("Lower")
            # Flush under the top, then down by its own depth: right under the upper plate.
            assert lower.v == pytest.approx(upper.v - 0.125) == pytest.approx(height - 0.1875)

    def test_offsets_any_level(self):
        members = [
            {"name": "Rail", "kind": "H", "v": 1.0},
            {"name": "Above", "kind": "H", "v": {"member": "Rail"}, "level_offset": 0.25},
        ]
        assert solve(members).by_entry("Above")[0].v == pytest.approx(1.25)


class TestCornerMembers:
    def test_keep_both_legs_clear(self):
        members = [
            {"name": "Post", "kind": "V", "at_ends": True, "at_corners": True},
            {
                "name": "Next",
                "kind": "V",
                "within": "Post",
                "spacing": {"mode": "MAX", "value": 100.0, "align": "START", "offset": 0.02},
            },
        ]
        entries = subject.parse_system({"members": members})
        # Facing along one leg, the corner post reaches its depth out of plane across the other.
        extents, lateral = {"Post": (-0.02, 0.02), "Next": (-0.02, 0.02)}, {"Post": (-0.07, 0.07)}
        layout = subject.solve(entries, [3.0, 3.0], 1.0, extents=extents, lateral=lateral)
        assert us(layout, "Next") == approx_list([0.02 + 0.02, 3.0 + 0.07 + 0.02])


class TestButtCorners:
    def layout(self, turn=math.pi / 2):
        members = [
            {"name": "Post", "kind": "V", "at_corners": True, "butt_corners": True},
            {"name": "Stud", "kind": "V", "within": "Post", "spacing": {"mode": "FIXED", "value": 0.5}},
        ]
        entries = subject.parse_system({"members": members})
        # 0.04 along the path, 0.14 through the wall.
        extents, lateral = {"Post": (-0.02, 0.02), "Stud": (-0.02, 0.02)}, {"Post": (-0.07, 0.07)}
        return subject.solve(entries, [3.0, 3.0], 1.0, extents=extents, lateral=lateral, turns=[turn])

    def test_the_first_leg_runs_through_and_the_second_butts_into_it(self):
        posts = sorted((m.u, m.address[0]) for m in self.layout().by_entry("Post"))
        # The first leg's post is flush with the second leg's outer face, 0.07 past the
        # corner; the second leg's stands against the first leg's inner face, 0.07 along.
        assert posts == [(pytest.approx(3.05), 0), (pytest.approx(3.09), 1)]

    def test_the_legs_space_from_their_own_posts(self):
        layout = self.layout()
        first = [m.u for m in layout.by_entry("Stud") if m.address[0] == 0]
        second = [m.u for m in layout.by_entry("Stud") if m.address[0] == 1]
        # The first leg's bay runs to its post's inner face at 3.03, past the corner, and the
        # second's from its post's outer face at 3.11.
        assert 3.0 < max(first) < 3.03
        assert min(second) > 3.11

    def test_an_open_corner_reaches_further(self):
        posts = sorted(m.u for m in self.layout(math.pi / 4).by_entry("Post"))
        assert posts[0] == pytest.approx(3.0 + 0.07 / math.sin(math.pi / 4) - 0.02)


class TestCornerMembersAndOpenings:
    def test_corner_members_run_through_and_serve_as_jambs(self):
        members = frame() + RAKE_PLATES
        ends = next(m for m in members if m["name"] == "Ends")
        ends.update(at_corners=True, butt_corners=True)
        extents = {**FRAME_EXTENTS, "Rake Plate": (-0.05, 0.05), "Rake Plate 2": (-0.05, 0.05)}
        # A rake starting at the first leg's inner face, well under the top, so its first edge
        # is steep, as a rake butting into the corner.
        rake = subject.Void(3.07, 7.0, 1.0, 5.0, outline=((3.07, 2.0), (7.0, 1.0), (7.0, 5.0), (3.07, 5.0)))
        entries = subject.parse_system({"members": members})
        # 0.14 through the wall, so the corner members stand at 3.02 and 3.12, either side of the
        # first leg's inner face at 3.07.
        layout = subject.solve(
            entries, [3.0, 3.0], 3.0, extents=extents, lateral={"Ends": (-0.07, 0.07)}, voids=(rake,)
        )
        corner = sorted(
            (m for m in layout.by_entry("Ends") if isinstance(m, subject.VerticalMember) and 3.0 < m.u < 3.2),
            key=lambda m: m.u,
        )
        # The first leg's member runs through, whole from the bottom rail to the top rail. The
        # second leg's is an end member like any other, so it stops under the rake plates.
        through, butting = corner
        assert (through.v_start, through.v_end) == pytest.approx((0.1, 2.9))
        assert butting.v_end < 2.0 and butting.top_cut is not None
        # The steep edge beside them gets no jamb of its own; only the rake plates frame the rake.
        assert sorted(m.entry for m in layout.inclined) == ["Rake Plate", "Rake Plate 2"]


class TestSlopedMembersAtButtCorners:
    def test_run_over_the_member_that_runs_through(self):
        members = frame() + RAKE_PLATES
        ends = next(m for m in members if m["name"] == "Ends")
        ends.update(at_corners=True, butt_corners=True)
        extents = {**FRAME_EXTENTS, "Rake Plate": (-0.05, 0.05), "Rake Plate 2": (-0.05, 0.05)}
        # Over the middle leg, reaching past its end at the second corner, u = 6.
        rake = subject.Void(3.07, 6.5, 1.0, 5.0, outline=((3.07, 2.0), (6.5, 1.415), (6.5, 5.0), (3.07, 5.0)))
        entries = subject.parse_system({"members": members})
        layout = subject.solve(
            entries, [3.0, 3.0, 3.0], 3.0, extents=extents, lateral={"Ends": (-0.07, 0.07)}, voids=(rake,)
        )
        # At the second corner the middle leg runs through, so the rake plates run square over
        # its member at 6.02, to the last leg's outer face at 6.07, and it is cut under them.
        for member in layout.inclined:
            assert member.end[0] == pytest.approx(6.07)
            assert parallel(member.end_cut, (0, 1))
        ends = layout.by_entry("Ends")
        (through,) = [m for m in ends if isinstance(m, subject.VerticalMember) and abs(m.u - 6.02) < 1e-9]
        assert through.v_end < 2.0 and through.top_cut is not None
        # The last leg's member, standing against the middle leg, runs whole.
        (last,) = [m for m in ends if isinstance(m, subject.VerticalMember) and abs(m.u - 6.12) < 1e-9]
        assert (last.v_start, last.v_end) == pytest.approx((0.1, 2.9))
