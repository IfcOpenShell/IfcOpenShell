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
    x = x / np.linalg.norm(x)
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    y = y / np.linalg.norm(y)
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


def get_cartesiantransformationoperator3d(inst):
    origin = np.array(inst.LocalOrigin.Coordinates)
    axis1 = np.array((1., 0., 0.))
    axis2 = np.array((0., 1., 0.))
    axis3 = np.array((0., 0., 1.))

    if inst.Axis1:
        axis1[0:3] = inst.Axis1.DirectionRatios
    if inst.Axis2:
        axis2[0:3] = inst.Axis2.DirectionRatios
    if inst.Axis3:
        axis3[0:3] = inst.Axis3.DirectionRatios

    m4 = ifcopenshell.util.placement.a2p(origin, axis3, axis1)
    # Negate axis2 (introduce mirroring) when supplied axis2
    # is opposite of constructed axis2, but remains orthogonal
    if m4.T[1][0:3].dot(axis2) < 0.:
        m4.T[1] *= -1.

    scale1 = scale2 = scale3 = 1.

    if inst.Scale:
        scale1 = inst.Scale

    if inst.is_a('IfcCartesianTransformationOperator3DnonUniform'):
        scale2 = inst.Scale2 if inst.Scale2 is not None else scale1
        scale3 = inst.Scale3 if inst.Scale3 is not None else scale1

    m4.T[0] *= scale1
    m4.T[1] *= scale2
    m4.T[2] *= scale3

    return m4


def get_mappeditem_transformation(item):
    m4 = ifcopenshell.util.placement.get_axis2placement(item.MappingSource.MappingOrigin)
    return get_cartesiantransformationoperator(item.MappingTarget) @ m4


def get_storey_elevation(storey):
    if storey.ObjectPlacement:
        matrix = get_local_placement(storey.ObjectPlacement)
        return matrix[2][3]
    return getattr(storey, "Elevation", 0.0) or 0.0


def rotation(angle, axis, is_degrees=True):
    theta = np.radians(angle) if is_degrees else angle
    cos, sin = np.cos(theta), np.sin(theta)

    if axis == "X":
        return np.array([
            [1, 0, 0, 0],
            [0, cos, -sin, 0],
            [0, sin, cos, 0],
            [0, 0, 0, 1]
        ])
    elif axis == "Y":
        return np.array([
            [cos, 0, sin, 0],
            [0, 1, 0, 0],
            [-sin, 0, cos, 0],
            [0, 0, 0, 1]
        ])
    elif axis == "Z":
        return np.array([
            [cos, -sin, 0, 0],
            [sin, cos, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ])
