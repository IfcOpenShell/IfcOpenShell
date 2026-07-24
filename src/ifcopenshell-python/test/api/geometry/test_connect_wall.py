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
# This file was generated with the assistance of an AI coding tool.

import numpy as np

import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import test.bootstrap


class TestConnectWall(test.bootstrap.IFC4):
    def setup_axis_context(self):
        model = ifcopenshell.api.context.add_context(self.file, context_type="Plan")
        return ifcopenshell.api.context.add_context(
            self.file,
            context_type="Plan",
            context_identifier="Axis",
            target_view="GRAPH_VIEW",
            parent=model,
        )

    def make_wall(self, axis_context, matrix, p1, p2):
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=wall, matrix=matrix)
        poly = self.file.create_entity(
            "IfcPolyline",
            Points=[
                self.file.create_entity("IfcCartesianPoint", Coordinates=p1),
                self.file.create_entity("IfcCartesianPoint", Coordinates=p2),
            ],
        )
        rep = self.file.create_entity(
            "IfcShapeRepresentation",
            ContextOfItems=axis_context,
            RepresentationIdentifier="Axis",
            RepresentationType="Curve2D",
            Items=[poly],
        )
        wall.Representation = self.file.create_entity("IfcProductDefinitionShape", Representations=[rep])
        return wall

    def make_crossing_walls(self, axis_context):
        # wall1's own axis runs (0, 0) to (10, 0). wall2 crosses it near
        # wall1's far end (world x=8, past wall1's own midpoint of 5), so the
        # default heuristic keeps wall1's longer (start-side) portion.
        wall1 = self.make_wall(axis_context, np.eye(4), (0.0, 0.0), (10.0, 0.0))
        theta = np.pi / 2
        rotation = np.array(
            [
                [np.cos(theta), -np.sin(theta), 0, 0],
                [np.sin(theta), np.cos(theta), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1],
            ]
        )
        translation = np.eye(4)
        translation[0, 3] = 8.0
        translation[1, 3] = -5.0
        wall2 = self.make_wall(axis_context, translation @ rotation, (-5.0, 0.0), (5.0, 0.0))
        return wall1, wall2

    def test_default_keeps_the_longer_portion_of_wall1(self):
        axis_context = self.setup_axis_context()
        wall1, wall2 = self.make_crossing_walls(axis_context)
        rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2)
        assert rel.RelatingConnectionType == "ATEND"

    def test_invert_swaps_which_portion_of_wall1_is_kept(self):
        axis_context = self.setup_axis_context()
        wall1, wall2 = self.make_crossing_walls(axis_context)
        rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2, invert=True)
        assert rel.RelatingConnectionType == "ATSTART"

    def test_invert_does_not_affect_wall2s_own_connection_end(self):
        axis_context = self.setup_axis_context()
        wall1, wall2 = self.make_crossing_walls(axis_context)
        default_rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2)
        default_related = default_rel.RelatedConnectionType
        self.file.remove(default_rel)
        inverted_rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2, invert=True)
        assert inverted_rel.RelatedConnectionType == default_related

    def test_is_atpath_takes_precedence_over_wall2_end_regardless_of_invert(self):
        axis_context = self.setup_axis_context()
        wall1, wall2 = self.make_crossing_walls(axis_context)
        rel = ifcopenshell.api.geometry.connect_wall(self.file, wall1=wall1, wall2=wall2, is_atpath=True, invert=True)
        assert rel.RelatedConnectionType == "ATPATH"
        assert rel.RelatingConnectionType == "ATSTART"


class TestConnectWallIFC2X3(test.bootstrap.IFC2X3, TestConnectWall):
    pass
