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
from ifcpatch.recipes import OffsetObjectPlacements, SetWorldCoordinateSystem
import typing


class Patcher:
    def __init__(
        self,
        src,
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
        """Sets a false origin with a map conversion in a model

        On IFC2X3 models, a EPset_MapConversion is used.

        :param x: The local X coordinate which will become the new false origin.
        :param y: The local Y coordinate which will become the new false origin.
        :param z: The local Z coordinate which will become the new false origin.
        :param e: The easting which the false origin correlates to.
        :param n: The northing which the false origin correlates to.
        :param h: The height which the false origin correlates to.
        :param gn_angle: The anticlockwise angle to grid north.
        :param rotate_angle: An anticlockwise angle to rotate the model by if
            necessary (pivoted by the false origin).

        Example:

        .. code:: python

            # Set the current origin 0,0,0 to correlate to map coordinates 1000,1000,0 and a grid north of 15.
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "SetFalseOrigin", "arguments": ["EPSG:1234", 0, 0, 0, 1000, 1000, 0, 15, 0]})
        """
        self.src = src
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
        SetWorldCoordinateSystem.Patcher(self.src, self.file, self.logger, x=0, y=0, z=0, ax=0, ay=0, az=0).patch()
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
            self.file, projected_crs={"Name": self.name}, coordinate_operation=coordinate_operation
        )
        OffsetObjectPlacements.Patcher(
            self.src,
            self.file,
            self.logger,
            x=-self.x,
            y=-self.y,
            z=self.z,
            should_rotate_first=False,
            ax=self.rotate_angle or None,
        ).patch()
