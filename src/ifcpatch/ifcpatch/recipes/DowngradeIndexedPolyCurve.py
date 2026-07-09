# IfcPatch - IFC patching utiliy
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcPatch.
#
# IfcPatch is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcPatch is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcPatch.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell.util.element
import ifcopenshell.util.shape_builder

# Number of straight chords used to approximate one IfcArcIndex when flattening
# an IfcIndexedPolyCurve to an IfcPolyline. Higher values track the true arc
# more closely at the cost of file weight.
ARC_SUBDIVISION = 16


class Patcher:
    def __init__(self, file, logger):
        """Downgrade indexed polycurves to simple polylines

        Low quality IFC viewers like Navisworks do not support various IFC4
        geometry, such as indexed polycurves. These can result in missing
        geometry or geometric glitches (such as arcs being displayed as full
        circles). This is pretty common when viewing IFCs from ArchiCAD that
        include site boundaries (incorrectly drawn using the ArchiCAD grid tool,
        as ArchiCAD has no site boundary tool).

        This will downgrade specifically the indexed polycurve geometry types in
        an IFC4 model (IFC2X3 does not have this geometry type) to help
        compatibility in viewers like Navisworks.

        Arc segments (``IfcArcIndex``) are approximated by a chord polyline
        through ``ARC_SUBDIVISION`` evenly-spaced points along the arc.

        Example:

            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "DowngradeIndexedPolyCurve", "arguments": []})
        """
        self.file = file
        self.logger = logger

    def patch(self):
        if self.file.schema == "IFC2X3":
            return
        curve_map = {}

        for curve in self.file.by_type("IfcIndexedPolyCurve"):
            coordinates = curve.Points.CoordList
            segments = curve.Segments
            if segments is None:
                # IFC4: an absent Segments list means the curve is a polyline
                # through every CoordList point in declared order.
                points = [tuple(c) for c in coordinates]
            else:
                points = self._segments_to_points(segments, coordinates)
                if points is None:
                    continue
            ifc_points = [self.file.createIfcCartesianPoint(p) for p in points]
            polyline = self.file.create_entity("IfcPolyline", ifc_points)
            curve_map[curve] = polyline

        for curve, polyline in curve_map.items():
            ifcopenshell.util.element.replace_element(curve, polyline)

    def _segments_to_points(self, segments, coordinates):
        points: list[tuple[float, ...]] = []
        for i, segment in enumerate(segments):
            indices = segment.wrappedValue
            if segment.is_a("IfcArcIndex"):
                if len(indices) != 3:
                    return None
                arc_points = ifcopenshell.util.shape_builder.arc_to_polyline_points(
                    coordinates[indices[0] - 1],
                    coordinates[indices[1] - 1],
                    coordinates[indices[2] - 1],
                    ARC_SUBDIVISION,
                )
                if i == 0:
                    points.append(tuple(arc_points[0]))
                points.extend(tuple(p) for p in arc_points[1:])
            else:
                # IfcLineIndex is LIST [2:?] OF IfcPositiveInteger — a polyline
                # through every listed index. Skip the first index on non-leading
                # segments since it duplicates the previous segment's endpoint.
                seg_points = [tuple(coordinates[idx - 1]) for idx in indices]
                if i == 0:
                    points.extend(seg_points)
                else:
                    points.extend(seg_points[1:])
        return points
