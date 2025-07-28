# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import ifcopenshell
import ifcopenshell.util.placement
from ifcopenshell import entity_instance
import numpy as np


def update_fallback_position(file: ifcopenshell.file, lp: entity_instance):
    """
    Updates the IfcLinearPlacement.CartesianPoint fallback position.

    If the CartesianPosition is not assigned to the IfcLinearPlacement, one will be created

    :param lp: The linear placement
    :return: None
    """

    if not lp.CartesianPosition:
        lp.CartesianPosition = file.createIfcAxis2Placement3D(Location=file.createIfcCartesianPoint((0.0, 0.0)))

    p = np.array(ifcopenshell.util.placement.get_axis2placement(lp.RelativePlacement))

    x = float(p[0, 3])
    y = float(p[1, 3])
    z = float(p[2, 3])

    rx = float(p[0, 0])
    ry = float(p[1, 0])
    rz = float(p[2, 0])

    ax = float(p[0, 2])
    ay = float(p[1, 2])
    az = float(p[2, 2])

    lp.CartesianPosition.Location.Coordinates = (x, y, z)

    if not lp.CartesianPosition.RefDirection:
        lp.CartesianPosition.RefDirection = file.createIfcDirection((1.0, 0.0, 0.0))

    if not lp.CartesianPosition.Axis:
        lp.CartesianPosition.Axis = file.createIfcDirection((0.0, 0.0, 1.0))

    lp.CartesianPosition.RefDirection.DirectionRatios = (rx, ry, rz)
    lp.CartesianPosition.Axis.DirectionRatios = (ax, ay, az)
