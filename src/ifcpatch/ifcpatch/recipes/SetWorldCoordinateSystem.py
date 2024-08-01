# IfcPatch - IFC patching utiliy
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

import math
import numpy as np
import typing


class Patcher:
    def __init__(
        self,
        src,
        file,
        logger,
        x: typing.Union[str, float] = "0",
        y: typing.Union[str, float] = "0",
        z: typing.Union[str, float] = "0",
        ax: typing.Union[str, float] = "0",
        ay: typing.Union[str, float] = "0",
        az: typing.Union[str, float] = "0",
    ):
        """Sets the world coordinate system of the geometric representation context

        Sets the world coordinate system to whatever you want.

        :param x: The X coordinate.
        :type x: typing.Union[str, float]
        :param y: The Y coordinate.
        :type y: typing.Union[str, float]
        :param z: The Z coordinate.
        :type z: typing.Union[str, float]
        :param ax: An angle to rotate by for 3D rotations along the X axis.
            Angles are in decimal degrees and positive is anticlockwise.
        :type ax: typing.Union[str, float]
        :param ay: An angle to rotate by for 3D rotations along the Y axis.
            Angles are in decimal degrees and positive is anticlockwise.
        :type ay: typing.Union[str, float]
        :param az: An angle to rotate by for 3D rotations along the Z axis.
            Angles are in decimal degrees and positive is anticlockwise.
        :type az: typing.Union[str, float]

        Example:

        .. code:: python

            # Set the world coordinate system back to 0, 0, 0
            ifcpatch.execute({"input": "input.ifc", "file": model, "recipe": "SetWorldCoordinateSystem", "arguments": [0,0,0,0,0,0]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self.ax = float(ax)
        self.ay = float(ay)
        self.az = float(az)

    def patch(self):
        rotate = self.identity_matrix()

        for arg in (("x", self.ax), ("y", self.ay), ("z", self.az)):
            if arg[1]:
                rotate = getattr(self, f"{arg[0]}_rotation_matrix")(math.radians(arg[1]), rotate)

        m = rotate

        x = np.array((m[0][0], m[1][0], m[2][0]))
        z = np.array((m[0][2], m[1][2], m[2][2]))

        for context in self.file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if context.ContextType == "Model":
                context.WorldCoordinateSystem = self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint((self.x, self.y, self.z)),
                    self.file.createIfcDirection(z.tolist()),
                    self.file.createIfcDirection(x.tolist()),
                )
            elif context.ContextType == "Plan":
                context.WorldCoordinateSystem = self.file.createIfcAxis2Placement2D(
                    self.file.createIfcCartesianPoint((self.x, self.y, self.z)),
                    self.file.createIfcDirection(x.tolist()),
                )

    def identity_matrix(self):
        return np.eye(4)

    def x_rotation_matrix(self, angle, transformation):
        transformation[1][1] = math.cos(angle)
        transformation[1][2] = -math.sin(angle)
        transformation[2][1] = math.sin(angle)
        transformation[2][2] = math.cos(angle)
        return transformation

    def y_rotation_matrix(self, angle, transformation):
        transformation[0][0] = math.cos(angle)
        transformation[0][2] = math.sin(angle)
        transformation[2][0] = -math.sin(angle)
        transformation[2][2] = math.cos(angle)
        return transformation

    def z_rotation_matrix(self, angle, transformation):
        transformation[0][0] = math.cos(angle)
        transformation[0][1] = -math.sin(angle)
        transformation[1][0] = math.sin(angle)
        transformation[1][1] = math.cos(angle)
        return transformation
