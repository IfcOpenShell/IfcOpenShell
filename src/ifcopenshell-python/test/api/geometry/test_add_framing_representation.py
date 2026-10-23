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
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.shape
from ifcopenshell.api.geometry.add_framing_representation import (
    FramingExtrusion,
    FramingPanel,
    FramingRail,
    compute_framing_geometry,
)
from ifcopenshell.util.framing import FramingError


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
        assert np.allclose(rails[0].origin, (0, 0, 1.07))
        assert rails[0].length == pytest.approx(3.0)
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
        assert np.allclose(low, (0, -0.03, 1.06))
        assert np.allclose(high, (3, 0.03, 1.08))

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
        assert np.allclose(low, (0, -0.03, 1.06)) and np.allclose(high, (2.03, 0.03, 1.08))
        low, high = self.bounds([second])
        assert np.allclose(low, (1.97, -0.03, 1.06)) and np.allclose(high, (2.03, 2, 1.08))

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

    def test_unresolved_profile_is_reported(self):
        system = self.system()
        system["members"][0]["profile"] = {"id": 0, "name": "Missing"}
        with pytest.raises(FramingError, match="No profile found for: Post"):
            self.add(system)
