# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
#
# This file was generated with the assistance of an AI coding tool.

import os

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.util.representation

FIXTURE = os.path.join(os.path.dirname(__file__), "..", "..", "fixtures", "bug_4790_styled_wall.ifc")


def get_walls(file):
    styled = unstyled = None
    for wall in file.by_type("IfcWall"):
        body = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
        if body and any(item.StyledByItem for item in body.Items):
            styled = wall
        else:
            unstyled = wall
    return styled, unstyled


def wall_has_body_style(file, wall):
    body = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
    return any(item.StyledByItem for item in body.Items)


class TestRegenerateWallRepresentation:
    def test_regen_preserves_the_body_surface_style(self):
        file = ifcopenshell.open(FIXTURE)
        wall, _ = get_walls(file)
        style_count = len(file.by_type("IfcSurfaceStyle"))

        ifcopenshell.api.geometry.regenerate_wall_representation(file, wall)

        assert wall_has_body_style(file, wall)
        assert len(file.by_type("IfcSurfaceStyle")) == style_count

    def test_regen_leaves_no_orphan_styled_items(self):
        file = ifcopenshell.open(FIXTURE)
        wall, _ = get_walls(file)

        ifcopenshell.api.geometry.regenerate_wall_representation(file, wall)

        body = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
        live_items = set(body.Items)
        for styled_item in file.by_type("IfcStyledItem"):
            assert styled_item.Item in live_items

    def test_regen_does_not_style_an_unstyled_wall(self):
        file = ifcopenshell.open(FIXTURE)
        _, wall = get_walls(file)

        ifcopenshell.api.geometry.regenerate_wall_representation(file, wall)

        assert not wall_has_body_style(file, wall)

    def test_repeated_regen_does_not_duplicate_styles(self):
        file = ifcopenshell.open(FIXTURE)
        wall, _ = get_walls(file)
        style_count = len(file.by_type("IfcSurfaceStyle"))
        styled_item_count = len(file.by_type("IfcStyledItem"))

        for _ in range(3):
            ifcopenshell.api.geometry.regenerate_wall_representation(file, wall)

        assert wall_has_body_style(file, wall)
        assert len(file.by_type("IfcSurfaceStyle")) == style_count
        assert len(file.by_type("IfcStyledItem")) == styled_item_count
