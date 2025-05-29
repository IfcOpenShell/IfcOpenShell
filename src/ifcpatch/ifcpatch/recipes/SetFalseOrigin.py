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
import ifcopenshell.api.georeference
import ifcopenshell.util.geolocation
from ifcpatch.recipes import OffsetObjectPlacements, SetWorldCoordinateSystem
import typing


class Patcher:
    def __init__(
        self,
        file,
        logger,
        name: str = "EPSG:1234",
        x: typing.Union[str, float] = "0",
        y: typing.Union[str, float] = "0",
        z: typing.Union[str, float] = "0",
        e: typing.Union[str, float] = "0",
        n: typing.Union[str, float] = "0",
        h: typing.Union[str, float] = "0",
        gn_angle: typing.Union[str, float] = "0",
        rotate_angle: typing.Union[str, float] = "0",
    ):
        """Sets local coordinates XYZ as a (false) origin that correlates to map coordinates ENH

        The recommended workflow is to specify a projected CRS name (e.g.
        EPSG:1234). The local XYZ coordinate will become the new local origin
        in IFC (we call this the false origin). A map conversion will be added
        that correlates that origin to eastings, northings, and orthogonal
        height.

        On IFC2X3 models, a EPset_MapConversion is used.

        If the map projected CRS name is left blank, it merely transforms the
        model such that the current point XYZ now becomes the point ENH (still
        in local coordinates). The Grid North angle is ignored. Any existing
        georeferencing is purged. This workflow not recommended, but may be is
        relevant for BIM software that does not properly support map
        coordinates.

        :param x: The local X coordinate in project units which will become the new false origin.
        :param y: The local Y coordinate in project units which will become the new false origin.
        :param z: The local Z coordinate in project units which will become the new false origin.
        :param e: The easting in project units which the false origin correlates to.
        :param n: The northing in project units which the false origin correlates to.
        :param h: The height in project units which the false origin correlates to.
        :param gn_angle: The anticlockwise angle to grid north.
        :param rotate_angle: An anticlockwise angle to rotate the model by if
            necessary (pivoted by the false origin).

        Example:

        .. code:: python

            # Set the current origin 0,0,0 to correlate to map coordinates 1000,1000,0 and a grid north of 15.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "SetFalseOrigin", "arguments": ["EPSG:1234", 0, 0, 0, 1000, 1000, 0, 15, 0]})
        """
        self.file = file
        self.logger = logger
        self.name = name
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.e = float(e)
        self.n = float(n)
        self.h = float(h)
        self.gn_angle = float(gn_angle)
        self.rotate_angle = float(rotate_angle)

    def patch(self):
        SetWorldCoordinateSystem.Patcher(self.file, self.logger, x=0, y=0, z=0, ax=0, ay=0, az=0).patch()
        if self.name:
            coordinate_operation = {
                "Eastings": self.e,
                "Northings": self.n,
                "OrthogonalHeight": self.h,
            }
            if self.gn_angle:
                a, o = ifcopenshell.util.geolocation.angle2xaxis(self.gn_angle)
                coordinate_operation.update({"XAxisAbscissa": a, "XAxisOrdinate": o})
            ifc_class = "IfcMapConversionScaled"
            if self.file.schema in ("IFC4", "IFC2X3"):
                ifc_class = "IfcMapConversion"
            ifcopenshell.api.georeference.add_georeferencing(self.file, ifc_class=ifc_class)
            ifcopenshell.api.georeference.edit_georeferencing(
                self.file, projected_crs={"Name": self.name, "MapUnit": None}, coordinate_operation=coordinate_operation
            )
            OffsetObjectPlacements.Patcher(
                self.file,
                self.logger,
                x=-self.x,
                y=-self.y,
                z=-self.z,
                should_rotate_first=False,
                ax=self.rotate_angle or None,
            ).patch()
        else:
            ifcopenshell.api.georeference.remove_georeferencing(self.file)
            OffsetObjectPlacements.Patcher(
                self.file,
                self.logger,
                x=-self.x,
                y=-self.y,
                z=-self.z,
                should_rotate_first=False,
                ax=self.rotate_angle or None,
            ).patch()
            OffsetObjectPlacements.Patcher(
                self.file,
                self.logger,
                x=self.e,
                y=self.n,
                z=self.h,
                should_rotate_first=False,
            ).patch()
