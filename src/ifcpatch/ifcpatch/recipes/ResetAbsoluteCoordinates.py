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

import logging
import numpy as np
import numpy.typing as npt
import ifcopenshell
from typing import Literal, Optional, Union


class Patcher:
    def __init__(
        self,
        src: str,
        file: ifcopenshell.file,
        logger: logging.Logger,
        mode: Literal[
            "Geometry",
            "Placement",
            "Both",
        ] = "Geometry",
        automatic_offset_point: bool = True,
        threshold: float = 1000000,  # Arbitrary default threshold based on experience
        x: Union[str, float] = "0",
        y: Union[str, float] = "0",
        z: Union[str, float] = "0",
    ):
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

        You may either let Blender BIM determine the offset to apply to any large
        coordinate automatically, arbitrarily based on the first large number we
        encounter, or manually specify this offset.

        Note that if your model inconsistently mixes coordinates between large
        and small (such as if your model mixes both local and map coordinates)
        then the results of this function may be poor. Provide a bug report back
        to your BIM application to get it fixed.

        :param mode: Choose from "Geometry", "Placement", or "Both". Choosing
            "Geometry" will only replace cartesian points used in shape
            representations. Choosing "Placement" will only replace cartesian
            points used in object placements. Choosing "Both" will replace all
            cartesian points regardless of use (useful if the model has both
            large placement offsets and large geometry offsets).
        :type mode: str
        :param automatic_offset_point: Choose, whether the offset should be
            determined automatically or specified manually.
        :type automatic_offset_point: bool
        :param threshold: The threshold for deciding, whether a coordinate is
            treated as a large coordinate.
        :type threshold: float
        :param x: The x-ordinate of the manually specified offset point.
        :type x: Union[str, float]
        :param y: The y-ordinate of the manually specified offset point.
        :type y: Union[str, float]
        :param z: The z-ordinate of the manually specified offset point.
        :type z: Union[str, float]

        Example:

        .. code:: python

            # Reset all coordinates with an ordinate larger than 1000000 arbitrarily
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ResetAbsoluteCoordinates", "arguments": []})

            # Reset all coordinates with an ordinate larger than 1000 arbitrarily
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [True, 1000]})

            # Reset all coordinates with an ordinate larger than 1000000 by -50000,-20000,0
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [False, 1000000, -50000,-20000,0]})

            # Reset all coordinates with an ordinate larger than 1000 by -500,-200,0
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "ResetAbsoluteCoordinates", "arguments": [False, 1000, -500,-200,0]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.mode = mode.lower()
        self.threshold = threshold
        if automatic_offset_point:
            self.offset_point = None
        else:
            self.offset_point = (float(x), float(y), float(z))

    def patch(self):
        placement_coord_ids = set()
        for placement in self.file.by_type("IfcObjectPlacement"):
            [placement_coord_ids.add(e.id()) for e in self.file.traverse(placement) if e.is_a("IfcCartesianPoint")]

        # This method will not work all the time, but will catch most issues. It
        # assumes that absolute coordinates are easily recognisable based on
        # having a large absolute value above a threshold. This is not always
        # the case, but is very fast to run, and works for most cases.
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
                if not self.offset_point:
                    self.offset_point = (-point[0], -point[1], -point[2])
                    self.logger.info(f"Resetting absolute coordinates by {point}")
                point = (
                    point[0] + self.offset_point[0],
                    point[1] + self.offset_point[1],
                    point[2] + self.offset_point[2],
                )
                coord_list[i] = point
            point_list.CoordList = coord_list
        for point in self.file.by_type("IfcCartesianPoint"):
            if len(point.Coordinates) == 2 or not self.is_point_far_away(point):
                continue
            if self.mode == "geometry":
                if point.id() in placement_coord_ids:
                    continue
            elif self.mode == "placement":
                if point.id() not in placement_coord_ids:
                    continue
            if not self.offset_point:
                self.offset_point = (-point.Coordinates[0], -point.Coordinates[1], -point.Coordinates[2])
                self.logger.info(f"Resetting absolute coordinates by {point}")
            point.Coordinates = (
                point.Coordinates[0] + self.offset_point[0],
                point.Coordinates[1] + self.offset_point[1],
                point.Coordinates[2] + self.offset_point[2],
            )

    def is_point_far_away(self, point: Union[ifcopenshell.entity_instance, npt.NDArray[np.float64]]) -> bool:
        if hasattr(point, "Coordinates"):
            return (
                abs(point.Coordinates[0]) > self.threshold
                or abs(point.Coordinates[1]) > self.threshold
                or abs(point.Coordinates[2]) > self.threshold
            )
        return abs(point[0]) > self.threshold or abs(point[1]) > self.threshold or abs(point[2]) > self.threshold
