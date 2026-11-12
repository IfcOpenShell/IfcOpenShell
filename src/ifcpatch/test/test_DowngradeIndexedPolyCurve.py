# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bonsai Contributors
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

import ifcpatch
import test.bootstrap


class TestDowngradeIndexedPolyCurve(test.bootstrap.IFC4):
    def _make_curve(self, segments=None):
        point_list = self.file.create_entity(
            "IfcCartesianPointList2D",
            CoordList=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)],
        )
        curve = self.file.create_entity(
            "IfcIndexedPolyCurve",
            Points=point_list,
            Segments=segments,
        )
        self.file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=curve)
        return curve

    def test_run_without_segments(self):
        """An IfcIndexedPolyCurve with no Segments must downgrade to an
        IfcPolyline through every CoordList point in order — IFC4 defines
        the implicit-polyline meaning of an absent Segments list, and the
        ifcopenshell shape builder emits this form for simple open curves."""
        self._make_curve(segments=None)
        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "DowngradeIndexedPolyCurve", "arguments": []}
        )
        polylines = self.file.by_type("IfcPolyline")
        assert len(polylines) == 1
        assert len(polylines[0].Points) == 3

    def test_run_with_line_segments(self):
        """Line-segmented IfcIndexedPolyCurves downgrade to an equivalent IfcPolyline."""
        segments = [
            self.file.createIfcLineIndex((1, 2)),
            self.file.createIfcLineIndex((2, 3)),
        ]
        self._make_curve(segments=segments)
        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "DowngradeIndexedPolyCurve", "arguments": []}
        )
        polylines = self.file.by_type("IfcPolyline")
        assert len(polylines) == 1
        assert len(polylines[0].Points) == 3

    def test_run_with_multi_index_line_segment(self):
        """An IfcLineIndex with >2 indices encodes a polyline through every
        index — the downgraded IfcPolyline must include every one of them.
        This is the canonical form Bonsai's shape builder emits for closed
        rectangle profiles (e.g. parametric wall body outlines), serialised
        as ``IfcIndexedPolyCurve(Points, (IfcLineIndex((1,2,3,4,1))))``."""
        point_list = self.file.create_entity(
            "IfcCartesianPointList2D",
            CoordList=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
        )
        curve = self.file.create_entity(
            "IfcIndexedPolyCurve",
            Points=point_list,
            Segments=[self.file.createIfcLineIndex((1, 2, 3, 4, 1))],
        )
        self.file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=curve)
        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "DowngradeIndexedPolyCurve", "arguments": []}
        )
        polylines = self.file.by_type("IfcPolyline")
        assert len(polylines) == 1
        assert len(polylines[0].Points) == 5
        coords = [p.Coordinates for p in polylines[0].Points]
        assert coords[0] == coords[-1] == (0.0, 0.0)
        assert coords[1] == (1.0, 0.0)
        assert coords[2] == (1.0, 1.0)
        assert coords[3] == (0.0, 1.0)

    def test_run_with_chained_multi_index_segments(self):
        """When two IfcLineIndex segments are chained, the shared endpoint
        between them must appear once, not twice."""
        point_list = self.file.create_entity(
            "IfcCartesianPointList2D",
            CoordList=[(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)],
        )
        curve = self.file.create_entity(
            "IfcIndexedPolyCurve",
            Points=point_list,
            Segments=[
                self.file.createIfcLineIndex((1, 2, 3)),
                self.file.createIfcLineIndex((3, 4)),
            ],
        )
        self.file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA", OuterCurve=curve)
        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "DowngradeIndexedPolyCurve", "arguments": []}
        )
        polylines = self.file.by_type("IfcPolyline")
        assert len(polylines) == 1
        coords = [p.Coordinates for p in polylines[0].Points]
        assert coords == [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

    def test_run_facets_arc_segments(self):
        """Arc-segmented IfcIndexedPolyCurves are downgraded by sampling the
        circular arc into a chord polyline. The chord count is fixed by
        the recipe's subdivision parameter."""
        from ifcpatch.recipes.DowngradeIndexedPolyCurve import ARC_SUBDIVISION

        segments = [self.file.createIfcArcIndex((1, 2, 3))]
        self._make_curve(segments=segments)
        ifcpatch.execute(
            {"input": "input.ifc", "file": self.file, "recipe": "DowngradeIndexedPolyCurve", "arguments": []}
        )
        polylines = self.file.by_type("IfcPolyline")
        assert len(polylines) == 1
        assert len(polylines[0].Points) == ARC_SUBDIVISION + 1
