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

import math
import numpy as np
import ifcopenshell
import ifcopenshell.util.placement


class Patcher:
    def __init__(self, src, file, logger, x=None, y=None, z=None, should_rotate_first=True, ax=None, ay=None, az=None):
        """Offset and rotate all object placements in a model

        Every physical object in an IFC model has an object placement, a
        matrix dictating where it is in XYZ space and its rotation.

        Sometimes, models will have their models offset incorrectly into map
        coordinates (i.e. very large coordinates) when they should be using
        local coordinates, or vice versa, or simply be using wrong coordinates.

        In some cases, models will even be rotated, especially with mixups where
        Y is up instead of Z, coming from low quality BIM software.

        This patch lets you translate, and optionally rotate (either rotate 2D
        in plan view along the Z axis, or rotate in 3D across any axis) the
        entire IFC model.

        :param x: The X coordinate to offset by in project length units.
        :type x: float
        :param y: The Y coordinate to offset by in project length units.
        :type y: float
        :param z: The Z coordinate to offset by in project length units.
        :type z: float
        :param should_rotate_first: Whether or not to rotate first and then
            translate, or to first translate and rotate afterwards. Defaults to
            rotate first then translate.
        :type should_rotate_first: bool
        :param ax: An optional angle to rotate by. If only this angle is
            specified, it is treated as the angle to rotate in plan view (i.e.
            around the Z axis). If all angle parameters are specified, then it
            is treated as the angle to rotate around the X axis. Angles are in
            decimal degrees and positive is anticlockwise.
        :type ax: float,optional
        :param ay: An optional angle to rotate by for 3D rotations along the Y
            axis. Angles are in decimal degrees and positive is anticlockwise.
        :type ay: float,optional
        :param az: An optional angle to rotate by for 3D rotations along the Z
            axis. Angles are in decimal degrees and positive is anticlockwise.
        :type az: float,optional

        Example:

        .. code:: python

            # Offset a model by 100 units in both the X and Y axis.
            ifcpatch.execute({"input": model, "recipe": "OffsetObjectPlacements", "arguments": [100,100,0]})

            # Rotate by 90 degrees, but don't do any offset
            ifcpatch.execute({"input": model, "recipe": "OffsetObjectPlacements", "arguments": [0,0,0,True,90]})

            # Some crazy 3D rotation and offset
            ifcpatch.execute({"input": model, "recipe": "OffsetObjectPlacements", "arguments": [12.5,5,2,False,90,90,45]})
        """
        self.src = src
        self.file = file
        self.logger = logger
        self.x = x
        self.y = y
        self.z = z
        self.should_rotate_first = should_rotate_first
        self.ax = ax
        self.ay = ay
        self.az = az
        if self.ay is not None:
            self.angle_type = "3D"
        elif self.ay is not None:
            self.angle_type = "2D"
        else:
            self.angle_type = None

    def patch(self):
        absolute_placements = []

        for product in self.file.by_type("IfcProduct"):
            if not product.ObjectPlacement:
                continue
            absolute_placement = self.get_absolute_placement(product.ObjectPlacement)
            if absolute_placement.is_a("IfcLocalPlacement"):
                absolute_placements.append(absolute_placement)
        absolute_placements = set(absolute_placements)

        translate = self.identity_matrix()
        rotate = self.identity_matrix()

        if self.angle_type == "2D":
            angle = float(self.ax)
            if angle:
                rotate = self.z_rotation_matrix(math.radians(angle), rotate)
        elif self.angle_type == "3D":
            for arg in (("x", float(self.ax)), ("y", float(self.ay)), ("z", float(self.az))):
                if arg[1]:
                    rotate = getattr(self, f"{arg[0]}_rotation_matrix")(math.radians(arg[1]), rotate)

        translate[0][3] += float(self.x)
        translate[1][3] += float(self.y)
        translate[2][3] += float(self.z)

        if self.should_rotate_first:
            transformation = translate @ rotate
        else:
            transformation = rotate @ translate

        for placement in absolute_placements:
            placement.RelativePlacement = self.get_relative_placement(
                transformation @ ifcopenshell.util.placement.get_local_placement(placement)
            )

    def get_absolute_placement(self, object_placement):
        if object_placement.PlacementRelTo:
            return self.get_absolute_placement(object_placement.PlacementRelTo)
        return object_placement

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

    def get_relative_placement(self, m):
        x = np.array((m[0][0], m[1][0], m[2][0]))
        z = np.array((m[0][2], m[1][2], m[2][2]))
        o = np.array((m[0][3], m[1][3], m[2][3]))
        object_matrix = ifcopenshell.util.placement.a2p(o, z, x)
        return self.create_ifc_axis_2_placement_3d(
            object_matrix[:, 3][0:3],
            object_matrix[:, 2][0:3],
            object_matrix[:, 0][0:3],
        )

    def create_ifc_axis_2_placement_3d(self, point, up, forward):
        return self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint(point.tolist()),
            self.file.createIfcDirection(up.tolist()),
            self.file.createIfcDirection(forward.tolist()),
        )
