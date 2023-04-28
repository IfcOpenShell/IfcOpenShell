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
    def __init__(self, src, file, logger, a=None, b=None, c=None, d=None):
        """Reset any large coordinates to smaller coordinates based on a threshold

        If you find large coordinates in your model, the large coordinates may
        either by due to large coordinates in the object placement matrix of
        each object, or large coordinates in the geometry of each object.

        If it is the former (preferred), consult the OffsetObjectPlacements
        recipe. If it is the latter, this indicates seriously incorrect
        coordinates in your IFC model.

        This recipe finds any large coordinates (if either the X, Y, or Z
        ordinate is larger than a threshold) and offsets it back down to a small
        number.

        You may either manually specify the offset to apply to any large
        coordinate, or an offset will be automatically determined arbitrarily
        based on the first large number we encounter.

        Note that if your model inconsistently mixes coordinates between large
        and small (such as if your model mixes both local and map coordinates)
        then the results of this function may be poor. Provide a bug report back
        to your BIM application to get it fixed.

        You may specify up to 4 arguments, a, b, c, and d.

        If you specify no arguments, then the threshold is set to 1000000. The
        offset is auto detected.

        If you only specify 1 parameter (i.e. a), then this is treated as the
        threshold beyond which an ordinate is considered to be large. The offset
        is auto detected.

        If you specify 3 parameters, (i.e. a, b, c) then your three numbers are
        treated as the X, Y, Z offset to apply. Typically your numbers will be
        negative to bring the numbers smaller. The threshold is set to 1000000.

        If you specify 4 parameters (i.e. a, b, c, d), then the first three
        numbers are treated as the X, Y, Z offset to apply (a, b, c). The fourth
        (d) will be treated as the threshold.

        :param a: The first parameter
        :type a: float,optional
        :param b: The second parameter
        :type b: float,optional
        :param c: The third parameter
        :type c: float,optional
        :param d: The fourth parameter
        :type d: float,optional

        Example:

        .. code:: python

            # Reset all coordinates with an ordinate larger than 1000000 arbitrarily
            ifcpatch.execute({"input": model, "recipe": "ResetAbsoluteCoordinates", "arguments": []})

            # Reset all coordinates with an ordinate larger than 1000 arbitrarily
            ifcpatch.execute({"input": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [1000]})

            # Reset all coordinates with an ordinate larger than 1000000 by -50000,-20000,0
            ifcpatch.execute({"input": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [-50000,-20000,0]})

            # Reset all coordinates with an ordinate larger than 1000 by -500,-200,0
            ifcpatch.execute({"input": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [-500,-200,0,1000]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.args = [x for x in [a, b, c, d] if x is not None]

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
