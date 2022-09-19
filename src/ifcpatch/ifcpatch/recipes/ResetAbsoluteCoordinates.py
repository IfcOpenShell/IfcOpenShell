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


class Patcher:
    def __init__(self, src, file, logger, args=None):
        self.src = src
        self.file = file
        self.logger = logger
        self.args = args

    def patch(self):
        placement_coord_ids = set()
        for placement in self.file.by_type("IfcObjectPlacement"):
            [placement_coord_ids.add(e.id()) for e in self.file.traverse(placement) if e.is_a("IfcCartesianPoint")]

        # Arbitrary threshold based on experience
        self.threshold = 1000000
        if self.args and len(self.args) == 1:
            self.threshold = float(self.args[0])
        elif self.args and len(self.args) == 4:
            self.threshold = float(self.args[3])

        # This method will not work all the time, but will catch most issues. It
        # assumes that absolute coordinates are easily recognisable based on
        # having a large absolute value above a threshold. This is not always
        # the case, but is very fast to run, and works for most cases.
        offset_point = None
        if self.args and len(self.args) >= 3:
            offset_point = (float(self.args[0]), float(self.args[1]), float(self.args[2]))
        try:
            point_lists = self.file.by_type("IfcCartesianPointList3D")
        except:
            # IFC2X3 does not have IfcCartesianPointList3D
            point_lists = []
        for point_list in point_lists:
            coord_list = [None] * len(point_list.CoordList)
            for i, point in enumerate(point_list.CoordList):
                if len(point) == 2 or not self.is_point_far_away(point):
                    coord_list[i] = point
                    continue
                if not offset_point:
                    offset_point = (-point[0], -point[1], -point[2])
                    self.logger.info(f"Resetting absolute coordinates by {point}")
                point = (point[0] + offset_point[0], point[1] + offset_point[1], point[2] + offset_point[2])
                coord_list[i] = point
            point_list.CoordList = coord_list
        for point in self.file.by_type("IfcCartesianPoint"):
            if len(point.Coordinates) == 2 or not self.is_point_far_away(point):
                continue
            if point.id() in placement_coord_ids:
                continue
            if not offset_point:
                offset_point = (-point.Coordinates[0], -point.Coordinates[1], -point.Coordinates[2])
                self.logger.info(f"Resetting absolute coordinates by {point}")
            point.Coordinates = (
                point.Coordinates[0] + offset_point[0],
                point.Coordinates[1] + offset_point[1],
                point.Coordinates[2] + offset_point[2],
            )

    def is_point_far_away(self, point):
        if hasattr(point, "Coordinates"):
            return (
                abs(point.Coordinates[0]) > self.threshold
                or abs(point.Coordinates[1]) > self.threshold
                or abs(point.Coordinates[2]) > self.threshold
            )
        return abs(point[0]) > self.threshold or abs(point[1]) > self.threshold or abs(point[2]) > self.threshold
