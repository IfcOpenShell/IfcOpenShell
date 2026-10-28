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

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.feature
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.geom
import ifcopenshell.util.framing
import ifcopenshell.util.shape
from ifcopenshell.api.geometry.add_framing_representation import (
    FramingExtrusion,
    FramingPanel,
    FramingRail,
    _GuideMap,
    _rail_pieces,
    compute_framing_geometry,
    compute_framing_mesh,
    get_framing_voids,
    get_profile_mesh,
    project_void,
)
from ifcopenshell.util.framing import FramingError, Void
from ifcopenshell.util.shape_builder import ShapeBuilder


def rectangle_points(x: float, y: float) -> np.ndarray:
    return np.array(((-x / 2, -y / 2), (x / 2, -y / 2), (x / 2, y / 2), (-x / 2, y / 2)))


def railing_system(profile_ids=None) -> dict:
    ids = profile_ids or {}
    return {
        "members": [
            {
                "name": "Post",
                "kind": "V",
                "spacing": {"mode": "MAX", "value": 1.5},
                "at_ends": True,
                "at_corners": True,
                "top": {"member": "TopRail"},
                "profile": {"id": ids.get("Post", 0), "name": "Post 50"},
            },
            {
                "name": "TopRail",
                "kind": "H",
                "v": 1.07,
                "profile": {"id": ids.get("TopRail", 0), "name": "Cap 60x20"},
            },
            {
                "name": "BotRail",
                "kind": "H",
                "v": 0.1,
                "breaks_at": ["Post"],
                "profile": {"id": ids.get("BotRail", 0), "name": "Rail 40"},
            },
            {
                "name": "Glass",
                "kind": "INFILL",
                "between": "Post",
                "bottom": {"member": "BotRail"},
                "top": {"member": "TopRail"},
                "thickness": 0.012,
                "gap": 0.02,
            },
        ]
    }


RAILING_POINTS = {
    "Post": rectangle_points(0.05, 0.05),
    "TopRail": rectangle_points(0.06, 0.02),
    "BotRail": rectangle_points(0.04, 0.04),
}


class TestComputeFramingGeometry:
    def compute(self, guide=((0.0, 0.0, 0.0), (3.0, 0.0, 0.0)), **kwargs):
        return compute_framing_geometry(
            system=kwargs.pop("system", railing_system()),
            guide=guide,
            height=1.1,
            profile_points=kwargs.pop("profile_points", RAILING_POINTS),
            **kwargs,
        )

    def test_items_follow_entry_order(self):
        items = self.compute()
        assert [i.entry for i in items] == ["Post"] * 3 + ["TopRail"] + ["BotRail"] * 2 + ["Glass"] * 2

    def test_posts_stand_on_the_path_and_stop_under_the_top_rail(self):
        posts = [i for i in self.compute() if isinstance(i, FramingExtrusion)]
        assert [p.origin.tolist() for p in posts] == [[0, 0, 0], [1.5, 0, 0], [3, 0, 0]]
        assert all(p.depth == pytest.approx(1.06) for p in posts)
        assert all(np.allclose(p.ref_direction, (1, 0, 0)) for p in posts)

    def test_rails_run_along_the_path_at_their_level(self):
        rails = [i for i in self.compute() if isinstance(i, FramingRail)]
        # The top rail covers the end posts out to their outer faces.
        assert np.allclose(rails[0].origin, (-0.025, 0, 1.07))
        assert rails[0].length == pytest.approx(3.05)
        assert np.allclose(rails[1].origin, (0.025, 0, 0.1))
        assert rails[1].length == pytest.approx(1.45)
        assert all(r.start_mitre is None and r.end_mitre is None for r in rails)
        assert all(np.allclose(r.x_axis, (0, 1, 0)) for r in rails)

    def test_continuous_rail_is_mitred_at_corners(self):
        guide = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0))
        first, second = [i for i in self.compute(guide=guide) if i.entry == "TopRail"]
        bisector = np.array((1.0, 1.0, 0.0)) / np.sqrt(2)
        assert first.start_mitre is None and np.allclose(first.end_mitre, bisector)
        assert np.allclose(second.start_mitre, -bisector) and second.end_mitre is None
        assert np.allclose(first.end_corner, (2, 0, 1.07))
        # The outer edge of a 0.06 wide rail is 0.03 past the corner.
        assert first.end_extension == pytest.approx(0.03 * 1.05, abs=1e-5)

    def test_closed_loop_mitres_every_corner(self):
        guide = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0), (0.0, 2.0, 0.0))
        system = railing_system()
        del system["members"][2:]
        rails = [i for i in self.compute(guide=guide, system=system, closed=True) if i.entry == "TopRail"]
        assert len(rails) == 4
        assert all(r.start_mitre is not None and r.end_mitre is not None for r in rails)

    def test_corner_post_faces_its_own_segment(self):
        guide = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0))
        posts = [i for i in self.compute(guide=guide) if isinstance(i, FramingExtrusion)]
        corner = next(p for p in posts if np.allclose(p.origin, (2, 0, 0)))
        assert np.allclose(corner.ref_direction, (0, 1, 0))

    def test_panels_fill_the_bays(self):
        panels = [i for i in self.compute() if isinstance(i, FramingPanel)]
        assert len(panels) == 2
        first = panels[0]
        assert np.allclose(first.origin, (0.045, 0, 0.14))
        assert first.width == pytest.approx(1.41)
        assert first.height == pytest.approx(0.9)
        assert np.allclose(first.normal, (0, 1, 0))

    def test_offset_moves_out_of_the_guide_plane(self):
        system = railing_system()
        system["members"][3]["offset"] = 0.1
        panel = next(i for i in self.compute(system=system) if isinstance(i, FramingPanel))
        assert np.allclose(panel.origin, (0.045, 0.1, 0.14))

    def test_rotation_changes_the_extent_along_the_path(self):
        system = railing_system()
        system["members"][0]["rotation"] = 90
        points = dict(RAILING_POINTS, Post=rectangle_points(0.1, 0.02))
        rail = next(i for i in self.compute(system=system, profile_points=points) if i.entry == "BotRail")
        # Rotated 90 degrees, the post is 0.02 along the path, so the rail stops 0.01 from it.
        assert rail.origin[0] == pytest.approx(0.01)

    def test_member_without_profile_is_rejected(self):
        with pytest.raises(FramingError, match="needs a profile"):
            self.compute(profile_points={"Post": RAILING_POINTS["Post"]})

    def test_infill_without_thickness_is_rejected(self):
        system = railing_system()
        del system["members"][3]["thickness"]
        with pytest.raises(FramingError, match="thickness"):
            self.compute(system=system)


RECTANGLE_TRIANGLES = np.array(((0, 1, 2), (0, 2, 3)))
RAILING_MESHES = {name: (points, RECTANGLE_TRIANGLES) for name, points in RAILING_POINTS.items()}


class TestComputeFramingMesh:
    def mesh(self, guide=((0.0, 0.0, 0.0), (3.0, 0.0, 0.0)), system=None):
        items = compute_framing_geometry(
            system=system or railing_system(), guide=guide, height=1.1, profile_points=RAILING_POINTS
        )
        return compute_framing_mesh(items, RAILING_MESHES)

    def entry_vertices(self, mesh, name):
        indices = {i for face, entry in zip(mesh.faces, mesh.face_entries) if entry == name for i in face}
        return mesh.vertices[sorted(indices)]

    def test_matches_the_ifc_solids(self):
        mesh = self.mesh()
        posts = self.entry_vertices(mesh, "Post")
        assert np.allclose(posts.min(axis=0), (-0.025, -0.025, 0)) and np.allclose(
            posts.max(axis=0), (3.025, 0.025, 1.06)
        )
        top = self.entry_vertices(mesh, "TopRail")
        assert np.allclose(top.min(axis=0), (-0.025, -0.03, 1.06))
        assert np.allclose(top.max(axis=0), (3.025, 0.03, 1.08))
        glass = self.entry_vertices(mesh, "Glass")
        assert np.allclose(glass.min(axis=0), (0.045, -0.006, 0.14))
        assert np.allclose(glass.max(axis=0), (2.955, 0.006, 1.04))

    def test_every_prism_is_closed(self):
        mesh = self.mesh()
        edge_uses = {}
        for face in mesh.faces:
            for a, b in zip(face, face[1:] + face[:1]):
                key = (min(a, b), max(a, b))
                edge_uses[key] = edge_uses.get(key, 0) + 1
        assert set(edge_uses.values()) == {2}

    def test_corner_is_mitred_exactly(self):
        system = railing_system()
        del system["members"][2:]
        mesh = self.mesh(guide=((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0)), system=system)
        top = self.entry_vertices(mesh, "TopRail")
        # The two pieces share the outer and inner corner of the mitre.
        assert np.allclose(top.max(axis=0), (2.03, 2.025, 1.08))
        assert any(np.allclose(v, (2.03, -0.03, 1.08)) for v in top)
        assert any(np.allclose(v, (1.97, 0.03, 1.08)) for v in top)
        assert not any(v[0] > 2.03 + 1e-9 or v[1] < -0.03 - 1e-9 for v in top)


SLOPE = ((0.0, 0.0, 0.0), (3.0, 0.0, 1.5))  # rises 0.5 per unit of plan length
KINK = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (4.0, 0.0, 1.0))  # level, then sloped, straight in plan


def closed_mesh(mesh) -> bool:
    edge_uses = {}
    for face in mesh.faces:
        for a, b in zip(face, face[1:] + face[:1]):
            key = (min(a, b), max(a, b))
            edge_uses[key] = edge_uses.get(key, 0) + 1
    return set(edge_uses.values()) == {2}


class TestSlopedGuide:
    def compute(self, guide, system=None):
        return compute_framing_geometry(
            system=system or railing_system(), guide=guide, height=1.1, profile_points=RAILING_POINTS
        )

    def test_spacing_is_measured_in_plan(self):
        posts = [i for i in self.compute(SLOPE) if isinstance(i, FramingExtrusion)]
        assert [p.origin.tolist() for p in posts] == [[0, 0, 0], [1.5, 0, 0.75], [3, 0, 1.5]]

    def test_sloped_rail_is_oblique_with_a_plumb_section(self):
        top = next(i for i in self.compute(SLOPE) if i.entry == "TopRail")
        assert np.allclose(top.direction, np.array((1, 0, 0.5)) / np.hypot(1, 0.5))
        assert top.length == pytest.approx(3.05 * np.hypot(1, 0.5))
        assert np.allclose(top.plane_normal, (1, 0, 0))
        assert np.allclose(top.x_axis, (0, 1, 0))

    def test_rail_breaks_at_post_faces_in_plan(self):
        bottom = [i for i in self.compute(SLOPE) if i.entry == "BotRail"]
        assert bottom[0].origin == pytest.approx((0.025, 0, 0.0125 + 0.1))
        assert bottom[0].length == pytest.approx(1.45 * np.hypot(1, 0.5))

    def test_post_tops_are_raked(self):
        post = [i for i in self.compute(SLOPE) if isinstance(i, FramingExtrusion)][1]
        ((point, normal),) = post.top_planes
        assert np.allclose(point, (1.5, 0, 0.75 + 1.06))
        assert np.allclose(normal, np.array((-0.5, 0, 1)) / np.hypot(1, 0.5))
        assert post.top_extension > 0.025 * 0.5

    def test_level_guide_keeps_square_ends(self):
        post = next(i for i in self.compute(((0.0, 0.0, 0.0), (3.0, 0.0, 0.0))) if isinstance(i, FramingExtrusion))
        assert post.top_planes == () and post.top_extension == 0.0

    def test_square_cut_opt_out(self):
        system = railing_system()
        system["members"][0]["square_cut"] = True
        post = next(i for i in self.compute(SLOPE, system) if isinstance(i, FramingExtrusion))
        assert post.top_planes == ()

    def test_change_of_slope_needs_no_mitre(self):
        first, second = [i for i in self.compute(KINK) if i.entry == "TopRail"]
        assert first.end_mitre is None and second.start_mitre is None
        assert np.allclose(first.origin + first.direction * first.length, second.origin)

    def test_post_at_a_change_of_slope_is_cut_under_both(self):
        posts = [i for i in self.compute(KINK) if isinstance(i, FramingExtrusion)]
        kink_post = next(p for p in posts if np.allclose(p.origin[:2], (2, 0)))
        assert len(kink_post.top_planes) == 2

    def test_sloped_panel_is_a_parallelogram(self):
        glass = next(i for i in self.compute(SLOPE) if isinstance(i, FramingPanel))
        assert glass.slope == pytest.approx(0.5)
        outline = glass.outline()
        assert outline[1][1] == pytest.approx(glass.width * 0.5)
        assert outline[3][0] == 0.0  # plumb sides

    def test_preview_mesh_is_closed_and_raked(self):
        items = self.compute(SLOPE)
        mesh = compute_framing_mesh(items, RAILING_MESHES)
        assert closed_mesh(mesh)
        post = [i for i, e in zip(mesh.faces, mesh.face_entries) if e == "Post"]
        indices = sorted({i for face in post for i in face})
        middle = [v for v in mesh.vertices[indices] if 1.4 < v[0] < 1.6 and v[2] > 1.5]
        # The raked top lies on the rail underside: 0.75 + 1.06 at the post's axis, rising 0.5 per unit.
        assert all(v[2] == pytest.approx(0.75 + 1.06 + (v[0] - 1.5) * 0.5) for v in middle)


TURN_AND_CLIMB = ((0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 2.0, 1.0))  # level, then a left turn rising 0.5


def handrail_system(offset: float) -> dict:
    return {
        "members": [
            {
                "name": "Handrail",
                "kind": "H",
                "v": 0.9,
                "offset": offset,
                "profile": {"id": 0, "name": "Post 50"},
            }
        ]
    }


class TestOffsetRailAroundAClimbingCorner:
    def rails(self, offset):
        items = compute_framing_geometry(
            system=handrail_system(offset),
            guide=TURN_AND_CLIMB,
            height=1.1,
            profile_points={"Handrail": RAILING_POINTS["Post"]},
        )
        return [i for i in items if isinstance(i, FramingRail)]

    def end(self, rail):
        return rail.origin + rail.direction * rail.length

    def test_outside_runs_level_around_the_corner_before_climbing(self):
        # Offset to the right, the rail is on the outside of the left turn.
        level, ret, climb = self.rails(-0.1)
        assert np.allclose(ret.direction, (0, 1, 0))  # level, along the outgoing leg
        assert np.allclose(ret.origin, (3.1, -0.1, 0.9))
        assert np.allclose(self.end(ret), (3.1, 0.0, 0.9))
        assert np.allclose(climb.origin, self.end(ret))  # plumb joint where the climb starts
        assert level.end_mitre is not None and ret.start_mitre is not None
        assert ret.end_mitre is None and climb.start_mitre is None

    def test_inside_starts_the_climb_before_the_corner(self):
        level, ramp, climb = self.rails(0.1)
        assert np.allclose(ramp.direction, np.array((1, 0, 0.5)) / np.hypot(1, 0.5))  # rising, along the incoming leg
        assert np.allclose(ramp.origin, (2.8, 0.1, 0.9))
        assert np.allclose(self.end(level), ramp.origin)
        assert np.allclose(self.end(ramp), (2.9, 0.1, 0.95))
        assert np.isclose(climb.origin[2] + 0.5 * (0.1 - climb.origin[1]), 0.95)  # the climb passes the corner at 0.95
        assert ramp.end_mitre is not None and climb.start_mitre is not None

    def test_centred_rail_needs_no_easing(self):
        assert len(self.rails(0.0)) == 2

    def test_eased_rails_build(self):
        f = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        profile = f.createIfcRectangleProfileDef("AREA", "Post 50", None, 0.05, 0.05)
        system = handrail_system(-0.1)
        system["members"][0]["profile"]["id"] = profile.id()
        representation = ifcopenshell.api.geometry.add_framing_representation(
            f, context=body, system=system, guide=TURN_AND_CLIMB, height=1.1, unit_scale=1.0
        )
        settings = ifcopenshell.geom.settings()
        for item in representation.Items:
            assert len(ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(settings, item)))
        assert closed_mesh(
            compute_framing_mesh(self.rails(-0.1), {"Handrail": (RAILING_POINTS["Post"], RECTANGLE_TRIANGLES)})
        )


class TestAddFramingRepresentation:
    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        self.profiles = {
            "Post": self.rectangle("Post 50", 0.05, 0.05),
            "TopRail": self.rectangle("Cap 60x20", 0.06, 0.02),
            "BotRail": self.rectangle("Rail 40", 0.04, 0.04),
        }

    def rectangle(self, name, x, y):
        return self.file.createIfcRectangleProfileDef("AREA", name, None, x, y)

    def system(self):
        return railing_system({k: p.id() for k, p in self.profiles.items()})

    def add(self, system=None, guide=((0.0, 0.0, 0.0), (3.0, 0.0, 0.0)), **kwargs):
        return ifcopenshell.api.geometry.add_framing_representation(
            self.file,
            context=self.body,
            system=system or self.system(),
            guide=guide,
            height=1.1,
            unit_scale=1.0,
            **kwargs,
        )

    def bounds(self, items):
        settings = ifcopenshell.geom.settings()
        vertices = np.vstack(
            [ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(settings, i)) for i in items]
        )
        return vertices.min(axis=0), vertices.max(axis=0)

    def test_creates_one_solid_per_member_and_panel(self):
        representation = self.add()
        assert representation.RepresentationIdentifier == "Body"
        assert representation.RepresentationType == "SweptSolid"
        assert [i.is_a() for i in representation.Items] == ["IfcExtrudedAreaSolid"] * 8

    def test_posts_extrude_their_profile(self):
        posts = self.add().Items[:3]
        assert all(p.SweptArea == self.profiles["Post"] for p in posts)
        low, high = self.bounds(posts)
        assert np.allclose(low, (-0.025, -0.025, 0))
        assert np.allclose(high, (3.025, 0.025, 1.06))

    def test_rail_profile_is_upright(self):
        top = self.add().Items[3]
        assert top.SweptArea == self.profiles["TopRail"]
        low, high = self.bounds([top])
        # Profile X (0.06) is out of plane and profile Y (0.02) is up.
        assert np.allclose(low, (-0.025, -0.03, 1.06))
        assert np.allclose(high, (3.025, 0.03, 1.08))

    def test_rail_offset_moves_to_the_left_of_the_path(self):
        system = self.system()
        system["members"][1]["offset"] = 0.1
        low, high = self.bounds([self.add(system).Items[3]])
        assert np.allclose((low[1], high[1]), (0.07, 0.13))

    def test_corner_rails_meet_on_a_mitre(self):
        system = self.system()
        del system["members"][2:]
        guide = ((0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (2.0, 2.0, 0.0))
        representation = self.add(system, guide=guide)
        assert representation.RepresentationType == "SolidModel"
        first, second = representation.Items[-2:]
        assert first.is_a("IfcCsgSolid") and second.is_a("IfcCsgSolid")
        low, high = self.bounds([first])
        assert np.allclose(low, (-0.025, -0.03, 1.06)) and np.allclose(high, (2.03, 0.03, 1.08))
        low, high = self.bounds([second])
        assert np.allclose(low, (1.97, -0.03, 1.06)) and np.allclose(high, (2.03, 2.025, 1.08))

    def test_sloped_rail_solid_has_plumb_ends_and_thickness(self):
        system = self.system()
        del system["members"][2:]
        representation = self.add(system, guide=SLOPE)
        top = representation.Items[-1]
        settings = ifcopenshell.geom.settings()
        v = ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(settings, top))
        assert sorted({round(x, 6) for x in v[:, 0]}) == [-0.025, 3.025]
        at_start = v[np.isclose(v[:, 0], -0.025)]
        # Past the path's start the rail carries on down the slope: 0.025 * 0.5 lower.
        assert (at_start[:, 2].min(), at_start[:, 2].max()) == pytest.approx((1.0475, 1.0675))

    def test_raked_post_and_sloped_panel_solids(self):
        representation = self.add(guide=SLOPE)
        assert representation.RepresentationType == "SolidModel"
        middle_post = representation.Items[1]
        assert middle_post.is_a("IfcCsgSolid")
        low, high = self.bounds([middle_post])
        assert high[2] == pytest.approx(0.75 + 1.06 + 0.025 * 0.5)
        glass = representation.Items[-2]
        assert glass.SweptArea.is_a("IfcArbitraryClosedProfileDef")

    def test_post_at_a_change_of_slope_builds(self):
        # The level side gives a straight-down bottom plane, which must still build.
        representation = self.add(guide=KINK)
        settings = ifcopenshell.geom.settings()
        for item in representation.Items:
            assert len(ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(settings, item)))

    def test_panels_are_centred_on_the_guide_plane(self):
        glass = self.add().Items[6]
        low, high = self.bounds([glass])
        assert np.allclose(low, (0.045, -0.006, 0.14))
        assert np.allclose(high, (1.455, 0.006, 1.04))

    def test_groups_items_by_entry_in_shape_aspects(self):
        product_shape = self.file.createIfcProductDefinitionShape(None, None, ())
        representation = self.add(part_of_product=product_shape)
        aspects = {a.Name: a for a in product_shape.HasShapeAspects}
        assert set(aspects) == {"Post", "TopRail", "BotRail", "Glass"}
        assert len(aspects["Post"].ShapeRepresentations[0].Items) == 3
        assert set(aspects["Glass"].ShapeRepresentations[0].Items) == set(representation.Items[6:])

    def test_regenerating_replaces_aspect_items(self):
        product_shape = self.file.createIfcProductDefinitionShape(None, None, ())
        self.add(part_of_product=product_shape)
        representation = self.add(part_of_product=product_shape)
        aspects = {a.Name: a for a in product_shape.HasShapeAspects}
        assert len(product_shape.HasShapeAspects) == 4
        assert set(aspects["Post"].ShapeRepresentations[0].Items) == set(representation.Items[:3])

    def test_styles_items_from_constituent_materials(self):
        constituent_set = ifcopenshell.api.material.add_material_set(
            self.file, name="Framing", set_type="IfcMaterialConstituentSet"
        )
        styles = {}
        for entry in ("Post", "TopRail"):
            material = ifcopenshell.api.material.add_material(self.file, name=f"{entry} material")
            styles[entry] = ifcopenshell.api.style.add_style(self.file, name=entry)
            ifcopenshell.api.style.assign_material_style(
                self.file, material=material, style=styles[entry], context=self.body
            )
            constituent = ifcopenshell.api.material.add_constituent(
                self.file, constituent_set=constituent_set, material=material
            )
            constituent.Name = entry
        representation = self.add(constituent_set=constituent_set)
        assert all(i.StyledByItem[0].Styles == (styles["Post"],) for i in representation.Items[:3])
        assert representation.Items[3].StyledByItem[0].Styles == (styles["TopRail"],)
        # Entries without a constituent are left unstyled.
        assert not any(i.StyledByItem for i in representation.Items[4:])

    @pytest.mark.parametrize(
        "make, expected_area",
        [
            # The kernel returns only the outline for rectangles and I-shapes, but faces
            # for hollow sections and circles; both must give the right area.
            (lambda f: f.createIfcRectangleProfileDef("AREA", "R", None, 0.05, 0.02), 0.05 * 0.02),
            (
                lambda f: f.createIfcIShapeProfileDef("AREA", "I", None, 0.1, 0.2, 0.006, 0.01, None, None, None),
                2 * 0.1 * 0.01 + 0.006 * (0.2 - 2 * 0.01),
            ),
            (
                lambda f: f.createIfcRectangleHollowProfileDef("AREA", "Tube", None, 0.1, 0.1, 0.01, None, None),
                0.1 * 0.1 - 0.08 * 0.08,
            ),
        ],
    )
    def test_profile_mesh_area(self, make, expected_area):
        points, triangles = get_profile_mesh(make(self.file), 1.0)
        a, b, c = points[triangles[:, 0]], points[triangles[:, 1]], points[triangles[:, 2]]
        area = ((b - a)[:, 0] * (c - a)[:, 1] - (b - a)[:, 1] * (c - a)[:, 0]) / 2
        assert (area > 0).all()
        assert area.sum() == pytest.approx(expected_area)

    def test_profile_mesh_builds_a_closed_prism(self):
        profile = self.file.createIfcRectangleHollowProfileDef("AREA", "Tube", None, 0.1, 0.1, 0.01, None, None)
        items = [FramingExtrusion("Post", np.zeros(3), np.array((1.0, 0.0, 0.0)), 1.0)]
        mesh = compute_framing_mesh(items, {"Post": get_profile_mesh(profile, 1.0)})
        edge_uses = {}
        for face in mesh.faces:
            for a, b in zip(face, face[1:] + face[:1]):
                key = (min(a, b), max(a, b))
                edge_uses[key] = edge_uses.get(key, 0) + 1
        assert set(edge_uses.values()) == {2}

    def test_unresolved_profile_is_reported(self):
        system = self.system()
        system["members"][0]["profile"] = {"id": 0, "name": "Missing"}
        with pytest.raises(FramingError, match="No profile found for: Post"):
            self.add(system)


class TestProjectVoid:
    def test_box_on_a_straight_guide(self):
        box = [(x, y, z) for x in (2.0, 3.0) for y in (-0.1, 0.1) for z in (0.0, 2.1)]
        void = project_void([(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)], box, "IfcDoor")
        assert (void.u_start, void.u_end, void.v_start, void.v_end) == pytest.approx((2.0, 3.0, 0.0, 2.1))
        assert void.filling == "IfcDoor"

    def test_picks_the_nearest_segment(self):
        box = [(x, y, z) for x in (3.9, 4.1) for y in (1.0, 2.0) for z in (0.5, 1.5)]
        void = project_void([(0.0, 0.0, 0.0), (4.0, 0.0, 0.0), (4.0, 3.0, 0.0)], box)
        assert (void.u_start, void.u_end, void.v_start, void.v_end) == pytest.approx((5.0, 6.0, 0.5, 1.5))

    def test_height_is_measured_plumb_above_a_sloped_guide(self):
        box = [(1.0, 0.0, 0.5), (2.0, 0.0, 1.0), (1.0, 0.0, 2.5), (2.0, 0.0, 3.0)]
        void = project_void([(0.0, 0.0, 0.0), (4.0, 0.0, 2.0)], box)
        assert (void.u_start, void.u_end, void.v_start, void.v_end) == pytest.approx((1.0, 2.0, 0.0, 2.0))

    def test_off_the_guide(self):
        box = [(x, 0.0, z) for x in (7.0, 8.0) for z in (0.0, 1.0)]
        assert project_void([(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)], box) is None


class TestGetFramingVoids:
    def setup_method(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        self.host = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcCurtainWall")
        # Turned a quarter and moved, so the opening has to come back into the host's coordinates.
        self.host_matrix = np.array(((0.0, -1.0, 0.0, 10.0), (1.0, 0.0, 0.0, 5.0), (0.0, 0.0, 1.0, 1.0), (0, 0, 0, 1)))
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=self.host, matrix=self.host_matrix)

    def add_opening(self, u, width, height, filling=None):
        opening = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcOpeningElement")
        local = np.eye(4)
        local[:3, 3] = (u, -0.15, 0.0)
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=opening, matrix=self.host_matrix @ local)
        builder = ShapeBuilder(self.file)
        solid = builder.extrude(builder.rectangle(size=(width, 0.3)), height)
        ifcopenshell.api.geometry.assign_representation(
            self.file, product=opening, representation=builder.get_representation(self.body, [solid])
        )
        ifcopenshell.api.feature.add_feature(self.file, feature=opening, element=self.host)
        if filling:
            element = ifcopenshell.api.root.create_entity(self.file, ifc_class=filling)
            ifcopenshell.api.feature.add_filling(self.file, opening=opening, element=element)

    def voids(self):
        return get_framing_voids(self.host, [(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)], unit_scale=1.0)

    def test_reads_each_opening_in_the_hosts_coordinates(self):
        self.add_opening(2.0, 1.0, 2.1, "IfcDoor")
        self.add_opening(4.0, 1.2, 1.0)
        door, bare = self.voids()
        assert (door.u_start, door.u_end, door.v_start, door.v_end) == pytest.approx((2.0, 3.0, 0.0, 2.1))
        assert door.filling == "IfcDoor"
        assert (bare.u_start, bare.u_end, bare.v_end) == pytest.approx((4.0, 5.2, 1.0))
        assert bare.filling is None

    def test_no_openings(self):
        assert self.voids() == ()


def sloped_system(profile_ids=None) -> dict:
    ids = profile_ids or {}
    bounds = {"bottom": {"member": "Bottom"}, "top": {"member": "Top"}}
    return {
        "members": [
            {"name": "Ends", "kind": "V", "at_ends": True, "flush": True, **bounds},
            {"name": "Stud", "kind": "V", "spacing": {"mode": "MAX", "value": 1.0}, "within": "Ends", **bounds},
            {"name": "Bottom", "kind": "H", "v": "BASE", "flush": True},
            {"name": "Top", "kind": "H", "v": "TOP", "flush": True},
            {
                "name": "Glass",
                "kind": "INFILL",
                "between": "Stud",
                "bottom": {"member": "Bottom"},
                "top": {"member": "Top"},
                "thickness": 0.01,
                "gap": 0.01,
            },
        ]
        if not ids
        else [
            {**m, "profile": {"id": ids[m["name"]], "name": m["name"]}} if m["name"] in ids else m
            for m in sloped_system()["members"]
        ]
    }


SLOPED_PROFILES = {"Ends": (0.1, 0.1), "Stud": (0.05, 0.1), "Bottom": (0.1, 0.1), "Top": (0.1, 0.1)}
SLOPED_VOIDS = (
    # An angled end, u = 2/3 + (v + 1) / 3, and a raked top, v = 2.9 - 0.1 (u + 1).
    Void(-1, 2.4, -1, 4, outline=((-1, -1), (2 / 3, -1), (7 / 3, 4), (-1, 4))),
    Void(-1, 7, 2.1, 4, outline=((-1, 2.9), (7, 2.1), (7, 4), (-1, 4))),
)


class TestSlopedOpenings:
    def items(self):
        return compute_framing_geometry(
            system=sloped_system(),
            guide=[(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)],
            height=3.0,
            profile_points={name: rectangle_points(*size) for name, size in SLOPED_PROFILES.items()},
            voids=SLOPED_VOIDS,
        )

    def test_a_sloped_outline_is_kept(self):
        box = [(x, y, z) for x, z in ((1.0, 0.0), (2.0, 0.0), (3.0, 3.0), (0.0, 3.0)) for y in (-0.1, 0.1)]
        void = project_void([(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)], box)
        assert sorted(void.outline) == pytest.approx([(0.0, 3.0), (1.0, 0.0), (2.0, 0.0), (3.0, 3.0)])
        rectangle = [(x, y, z) for x in (1.0, 2.0) for y in (-0.1, 0.1) for z in (0.0, 2.0)]
        assert project_void([(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)], rectangle).outline == ()

    def test_members_along_sloped_edges_have_a_true_section(self):
        items = self.items()
        jamb = next(i for i in items if i.entry == "Ends" and not np.allclose(i.axis, (0, 0, 1)))
        rake = next(i for i in items if i.entry == "Bottom" and isinstance(i, FramingExtrusion))
        assert jamb.axis == pytest.approx(np.array((1, 0, 3)) / np.sqrt(10))
        assert rake.axis == pytest.approx(np.array((1, 0, -0.1)) / np.sqrt(1.01))
        for item in (jamb, rake):
            # The section is square to the axis, and its Y axis out of plane for a jamb, up for a head.
            assert abs(item.ref_direction @ item.axis) < 1e-9
        assert np.cross(jamb.axis, jamb.ref_direction) == pytest.approx((0, 1, 0))
        assert np.cross(rake.axis, rake.ref_direction)[2] > 0.99

    def test_studs_are_cut_along_the_rake(self):
        studs = [i for i in self.items() if i.entry == "Stud"]
        assert studs
        for stud in studs:
            ((_, normal),) = stud.top_planes
            # The plane holds the rake's direction and faces up out of the stud.
            assert normal @ np.array((1, 0, -0.1)) == pytest.approx(0.0, abs=1e-9)
            assert normal[2] > 0.9
            assert stud.top_extension > 0 and stud.bottom_extension == 0

    def test_mesh_is_closed(self):
        items = self.items()
        meshes = {name: get_profile_mesh(self.rectangle_profile(*size), 1.0) for name, size in SLOPED_PROFILES.items()}
        assert closed_mesh(compute_framing_mesh(items, meshes))
        # Glass trimmed by the openings keeps its shape.
        assert any(isinstance(i, FramingPanel) and i.points is not None for i in items)

    def rectangle_profile(self, x, y):
        # The file must outlive the profile, so it is kept on the test.
        self.file = getattr(self, "file", None) or ifcopenshell.file(schema="IFC4")
        return self.file.createIfcRectangleProfileDef("AREA", None, None, x, y)

    def test_ifc_body_tessellates(self):
        file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
        model = ifcopenshell.api.context.add_context(file, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        ids = {
            name: file.createIfcRectangleProfileDef("AREA", name, None, *size).id()
            for name, size in SLOPED_PROFILES.items()
        }
        representation = ifcopenshell.api.geometry.add_framing_representation(
            file,
            context=body,
            system=sloped_system(ids),
            guide=[(0.0, 0.0, 0.0), (6.0, 0.0, 0.0)],
            height=3.0,
            unit_scale=1.0,
            voids=SLOPED_VOIDS,
        )
        settings = ifcopenshell.geom.settings()
        vertices = ifcopenshell.util.shape.get_vertices(ifcopenshell.geom.create_shape(settings, representation))
        # Nothing reaches into the angled end or above the rake.
        assert all(u >= 2 / 3 + (v + 1) / 3 - 1e-6 for u, _, v in vertices)
        assert all(v <= 2.9 - 0.1 * (u + 1) + 1e-6 for u, _, v in vertices)


class TestRakeOverACorner:
    def test_members_mitre_on_the_corner(self):
        system = sloped_system()
        system["members"] += [
            {"name": "Rake", "kind": "H", "void_role": "SILL"},
        ]
        profiles = {**SLOPED_PROFILES, "Rake": (0.1, 0.1)}
        rake = Void(3.0, 7.0, 2.0, 5.0, outline=((3.0, 3.0), (7.0, 1.8), (7.0, 5.0), (3.0, 5.0)))
        items = compute_framing_geometry(
            system=system,
            guide=[(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 3.0, 0.0)],
            height=3.0,
            profile_points={name: rectangle_points(*size) for name, size in profiles.items()},
            voids=(rake,),
        )
        bisector = np.array((1.0, 1.0, 0.0)) / np.sqrt(2)
        (rake_member,) = [i for i in items if i.entry == "Rake"]
        ((_, normal),) = rake_member.bottom_planes
        assert abs(normal @ bisector) == pytest.approx(1.0)
        top = [i for i in items if i.entry == "Top" and isinstance(i, FramingRail)]
        assert any(i.end_mitre is not None and abs(i.end_mitre @ bisector) == pytest.approx(1.0) for i in top)


class TestRailCornerJoints:
    def pieces(self, joint):
        rail = {"name": "Rail", "kind": "H", "v": 1.0, "corner_joint": joint}
        items = compute_framing_geometry(
            system={"members": [rail]},
            guide=[(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 3.0, 0.0)],
            height=1.1,
            # 0.1 out of the guide plane, 0.05 tall.
            profile_points={"Rail": rectangle_points(0.1, 0.05)},
        )
        first, second = (i for i in items if isinstance(i, FramingRail))
        ends = []
        for rail in (first, second):
            start = rail.origin - rail.direction * rail.start_extension
            end = rail.origin + rail.direction * (rail.length + rail.end_extension)
            ends.append((start, end, rail.start_mitre, rail.end_mitre))
        return ends

    def test_mitre(self):
        (_, _, _, end_mitre), (_, _, start_mitre, _) = self.pieces("MITRE")
        assert end_mitre is not None and start_mitre is not None

    @pytest.mark.parametrize(
        "joint, first_end, second_start", [("BUTT_FIRST", 3.05, 0.05), ("BUTT_SECOND", 2.95, -0.05)]
    )
    def test_butt(self, joint, first_end, second_start):
        (_, end, _, end_mitre), (start, _, start_mitre, _) = self.pieces(joint)
        # Square ends: the leg running through reaches the other's outer face, the other
        # stops at its inner face.
        assert end_mitre is None and start_mitre is None
        assert end[0] == pytest.approx(first_end)
        assert start[1] == pytest.approx(second_start)

    def test_rejects_unknown(self):
        with pytest.raises(FramingError, match="corner joint"):
            ifcopenshell.util.framing.parse_system(
                {"members": [{"name": "R", "kind": "H", "v": 1.0, "corner_joint": "LAP"}]}
            )


class TestRailPiecesWithNoLength:
    def test_a_butted_second_leg_ending_within_the_first_legs_depth_is_left_out(self):
        # The run ends 0.05 past the corner, as deep as the first leg's rail reaches across it.
        rail = {"name": "Rail", "kind": "H", "v": 1.0, "corner_joint": "BUTT_FIRST", "extend_end": -2.95}
        items = compute_framing_geometry(
            system={"members": [rail]},
            guide=[(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 3.0, 0.0)],
            height=1.1,
            profile_points={"Rail": rectangle_points(0.1, 0.05)},
        )
        (only,) = [i for i in items if isinstance(i, FramingRail)]
        assert (only.origin + only.direction * (only.length + only.end_extension))[0] == pytest.approx(3.05)


class TestSlopedOpeningOnALeg:
    def test_is_measured_along_its_segment(self):
        # Sloped and reaching 0.5 past the end of the middle leg, round the next corner.
        box = [(x, y, z) for x in (-0.1, 0.1) for y, z in ((1.0, 2.0), (3.5, 1.0), (3.5, 3.0), (1.0, 3.0))]
        void = project_void([(0.0, 0.0, 0.0), (0.0, 3.0, 0.0), (2.0, 3.0, 0.0)], box)
        # Measured along the second leg, even past its end; the solver keeps it to that leg.
        assert max(u for u, _ in void.outline) == pytest.approx(3.5)
        assert void.u_end == pytest.approx(3.0)

    def test_may_reach_past_the_path_end(self):
        box = [(x, y, z) for x in (-0.1, 0.1) for y, z in ((1.0, 2.0), (3.5, 1.0), (3.5, 3.0), (1.0, 3.0))]
        void = project_void([(0.0, 0.0, 0.0), (0.0, 3.0, 0.0)], box)
        assert max(u for u, _ in void.outline) == pytest.approx(3.5)


class TestRailCutOnACorner:
    def test_a_butted_run_cut_on_a_corner_ends_as_its_corners_do(self):
        # The run starts on the corner, cut plumb there, with nothing on the first leg to meet.
        guide_map = _GuideMap([(0.0, 0.0, 0.0), (3.0, 0.0, 0.0), (3.0, 3.0, 0.0)], False)
        (piece,) = _rail_pieces(
            "Rail", 3.0, 6.0, 1.0, guide_map, 0.0, 0.0, rectangle_points(0.1, 0.05), (0.0, 1.0), None, "BUTT_FIRST"
        )
        # The second leg butts: square, starting at the first leg's inner face.
        assert piece.start_mitre is None
        assert (piece.origin - piece.direction * piece.start_extension)[1] == pytest.approx(0.05)
        profile = rectangle_points(0.1, 0.05)
        (through,) = _rail_pieces("Rail", 3.0, 6.0, 1.0, guide_map, 0.0, 0.0, profile, (0.0, 1.0), None, "BUTT_SECOND")
        # The second leg runs through: back to the first leg's outer face.
        assert (through.origin - through.direction * through.start_extension)[1] == pytest.approx(-0.05)
        (mitred,) = _rail_pieces(
            "Rail", 3.0, 6.0, 1.0, guide_map, 0.0, 0.0, rectangle_points(0.1, 0.05), (0.0, 1.0), None, "MITRE"
        )
        assert mitred.start_mitre is not None
