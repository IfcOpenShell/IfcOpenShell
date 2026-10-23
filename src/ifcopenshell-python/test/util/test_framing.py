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


def solve(members, segments=(3.0,), height=1.1, extents=None):
    return subject.solve(subject.parse_system({"members": members}), list(segments), height, extents=extents)


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
