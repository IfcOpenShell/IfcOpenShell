# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import numpy as np


def a2p(o, z, x):
    y = np.cross(z, x)
    r = np.eye(4)
    r[:-1, :-1] = x, y, z
    r[-1, :-1] = o
    return r.T


def get_axis2placement(plc):
    if plc.is_a("IfcAxis2Placement3D"):
        z = np.array(plc.Axis.DirectionRatios if plc.Axis else (0, 0, 1))
        x = np.array(plc.RefDirection.DirectionRatios if plc.RefDirection else (1, 0, 0))
        o = plc.Location.Coordinates
    elif plc.is_a("IfcAxis2Placement2D"):
        z = np.array((0, 0, 1))
        if plc.RefDirection:
            x = np.array(plc.RefDirection.DirectionRatios)
            x.resize(3)
        else:
            x = np.array((1, 0, 0))
        o = (*plc.Location.Coordinates, 0.0)
    return a2p(o, z, x)


def get_local_placement(plc):
    if plc is None:
        return np.eye(4)
    if plc.PlacementRelTo is None:
        parent = np.eye(4)
    else:
        parent = get_local_placement(plc.PlacementRelTo)
    return np.dot(parent, get_axis2placement(plc.RelativePlacement))


def get_storey_elevation(storey):
    if storey.ObjectPlacement:
        matrix = get_local_placement(storey.ObjectPlacement)
        return matrix[2][3]
    return getattr(storey, "Elevation", 0.0) or 0.0
