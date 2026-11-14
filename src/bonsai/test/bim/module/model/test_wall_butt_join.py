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

"""Alt+T joins two walls like Shift+T, but as a butt: the first wall runs through, the active one stops."""

from unittest.mock import Mock, patch

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.util.placement
import numpy as np
import pytest

from bonsai.bim.module.model.wall import DumbWallJoiner

pytestmark = pytest.mark.model


def _joiner():
    joiner = DumbWallJoiner.__new__(DumbWallJoiner)  # Skip __init__, which needs a loaded IFC.
    joiner.keep_clicked_side = False
    return joiner


class TestButtJoin:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(self.file, length={"is_metric": True, "raw": "METERS"})
        model = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        self.body = ifcopenshell.api.context.add_context(
            self.file, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        plan = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        ifcopenshell.api.context.add_context(
            self.file, context_type="Plan", context_identifier="Axis", target_view="GRAPH_VIEW", parent=plan
        )
        self.layer_set = ifcopenshell.api.material.add_material_set(
            self.file, name="Wall", set_type="IfcMaterialLayerSet"
        )
        material = ifcopenshell.api.material.add_material(self.file, name="Material")
        for thickness in (0.05, 0.2, 0.05):
            layer = ifcopenshell.api.material.add_layer(self.file, layer_set=self.layer_set, material=material)
            layer.LayerThickness = thickness

    def wall(self, p1, p2):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.material.assign_material(
            self.file, products=[wall], type="IfcMaterialLayerSetUsage", material=self.layer_set
        )
        representation = ifcopenshell.api.geometry.create_2pt_wall(
            self.file, element=wall, context=self.body, p1=p1, p2=p2, elevation=0, height=3, thickness=1
        )
        ifcopenshell.api.geometry.assign_representation(self.file, product=wall, representation=representation)
        return wall

    def extents(self, wall):
        """The wall's regenerated footprint as world (min x, min y, max x, max y)."""
        representation = ifcopenshell.api.geometry.regenerate_wall_representation(self.file, wall)
        item = representation.Items[0]
        while not item.is_a("IfcExtrudedAreaSolid"):
            item = item.FirstOperand
        matrix = ifcopenshell.util.placement.get_placement(wall.ObjectPlacement)
        points = np.array([(matrix @ (*p, 0, 1))[:2] for p in item.SweptArea.OuterCurve.Points.CoordList])
        return tuple(np.round([*points.min(axis=0), *points.max(axis=0)], 3))

    def join(self, wall1, wall2, is_butt):
        rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2)
        if is_butt:
            _joiner().set_butt_priorities(rel)
        return rel

    def test_priorities_favour_the_relating_wall(self):
        rel = self.join(self.wall((0, 0), (5, 0)), self.wall((5, 0), (5, 5)), is_butt=True)
        assert list(rel.RelatingPriorities) == [100, 100, 100]
        assert list(rel.RelatedPriorities) == [0, 0, 0]

    def test_without_butt_the_corner_is_a_mitre(self):
        wall1, wall2 = self.wall((0, 0), (5, 0)), self.wall((5, 0), (5, 5))
        self.join(wall1, wall2, is_butt=False)
        # Wall 2 spans x 4.7-5.0 and wall 1 spans y 0.0-0.3; a mitre meets on the diagonal.
        assert self.extents(wall1) == (0.0, 0.0, 5.0, 0.3)
        assert self.extents(wall2) == (4.7, 0.0, 5.0, 5.0)

    @pytest.mark.parametrize(
        "p1, p2, wall1_extents, wall2_extents",
        [
            # Left turn: wall 1 runs to wall 2's outer face, wall 2 stops at wall 1's inner face.
            (((0, 0), (5, 0)), ((5, 0), (5, 5)), (0.0, 0.0, 5.0, 0.3), (4.7, 0.3, 5.0, 5.0)),
            # Wall 2 drawn the other way.
            (((0, 0), (5, 0)), ((5, 5), (5, 0)), (0.0, 0.0, 5.3, 0.3), (5.0, 0.3, 5.3, 5.0)),
            # Right turn.
            (((0, 0), (5, 0)), ((5, 0), (5, -5)), (0.0, 0.0, 5.3, 0.3), (5.0, -5.0, 5.3, 0.0)),
            # Both walls drawn towards the corner.
            (((5, 0), (0, 0)), ((5, -5), (5, 0)), (0.0, -0.3, 5.0, 0.0), (4.7, -5.0, 5.0, -0.3)),
        ],
    )
    def test_butt_runs_the_first_wall_through(self, p1, p2, wall1_extents, wall2_extents):
        wall1, wall2 = self.wall(*p1), self.wall(*p2)
        self.join(wall1, wall2, is_butt=True)
        assert self.extents(wall1) == wall1_extents
        assert self.extents(wall2) == wall2_extents


class TestConnect:
    def connect(self, is_butt):
        joiner = _joiner()
        rel = Mock()
        joiner.connect_path = Mock(return_value=rel)
        joiner.set_butt_priorities = Mock()
        with (
            patch("bonsai.tool.Ifc.get_entity"),
            patch("bonsai.tool.Ifc.is_moved", return_value=False),
            patch("bonsai.tool.Model.recreate_wall"),
        ):
            joiner.connect(Mock(), Mock(), is_butt=is_butt)
        return joiner, rel

    def test_butt_sets_priorities_on_the_new_joint(self):
        joiner, rel = self.connect(is_butt=True)
        joiner.set_butt_priorities.assert_called_once_with(rel)

    def test_a_plain_join_leaves_priorities_alone(self):
        joiner, _ = self.connect(is_butt=False)
        joiner.set_butt_priorities.assert_not_called()
