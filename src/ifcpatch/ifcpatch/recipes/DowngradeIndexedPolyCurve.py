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

import ifcopenshell
import ifcopenshell.util.element


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        if self.file.schema == "IFC2X3":
            return
        curve_map = {}

        for curve in self.file.by_type("IfcIndexedPolyCurve"):
            if "IfcArcIndex" in [s.is_a() for s in curve.Segments]:
                print("Could not convert curve due to arcs", curve)
                continue
            coordinates = curve.Points.CoordList
            points = []
            for i, segment in enumerate(curve.Segments):
                segment = segment.wrappedValue
                if i == 0:
                    points.append(self.file.createIfcCartesianPoint(coordinates[segment[0] - 1]))
                points.append(self.file.createIfcCartesianPoint(coordinates[segment[1] - 1]))
            polyline = self.file.create_entity("IfcPolyline", points)
            curve_map[curve] = polyline

        for curve, polyline in curve_map.items():
            for inverse in self.file.get_inverse(curve):
                ifcopenshell.util.element.replace_attribute(inverse, curve, polyline)
