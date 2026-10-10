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

from collections.abc import Iterable
from typing import Literal, Optional

import numpy as np
import numpy.typing as npt

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.unit

MatrixType = npt.NDArray[np.float64]
"""`npt.NDArray[np.float64]`"""


def a2p(o: Iterable[float], z: Iterable[float], x: Iterable[float]) -> MatrixType:
    """Converts a location, X, and Z axis vector to a 4x4 transformation matrix

    IFC uses a right-handed coordinate system, so it is not necessary to
    provide the Y axis.

    :param o: The origin (i.e. location) of the matrix
    :param z: The +Z vector / axis of the matrix
    :param x: The +X vector / axis of the matrix
    :return: A 4x4 numpy matrix
    """
    x = x / np.linalg.norm(x)
    z = z / np.linalg.norm(z)
    y = np.cross(z, x)
    y = y / np.linalg.norm(y)
    r = np.eye(4)
    r[:-1, :-1] = x, y, z
    r[-1, :-1] = o
    return r.T


_settings: dict[bool, ifcopenshell.geom.settings] = {}


def get_placement(
    placement: Optional[ifcopenshell.entity_instance] = None, should_return_si: bool = False
) -> MatrixType:
    """Parse an object or coordinate placement into a 4x4 transformation matrix

    If an IfcObjectPlacement is provided, this is the fully composed matrix
    with all of its parents.

    .. code::

        [ [ x_x, y_x, z_x, x   ]
          [ x_y, y_y, z_y, y   ]
          [ x_z, y_z, z_z, z   ]
          [ 0.0, 0.0, 0.0, 1.0 ] ]

    Example:

    .. code:: python

        placement = file.by_type("IfcBeam")[0].ObjectPlacement
        matrix = ifcopenshell.util.placement.get_placement(placement)

    :param placement: The IfcObjectPlacement, IfcPlacement or
        IfcCartesianTransformationOperator entity. None gives the identity
        matrix.
    :param should_return_si: Return the translation in metres instead of the
        file's length unit.
    :return: A 4x4 numpy matrix
    """
    if placement is None:
        return np.eye(4)
    # TODO: delete this branch and _operator_placement once BUILD_COMMIT in
    # src/ifcopenshell-python/Makefile includes 870f06412, which teaches
    # create_shape to map operators itself. Packaged builds pair this module
    # with an older wrapper that raises "Failed to process shape" on them.
    if placement.is_a("IfcCartesianTransformationOperator"):
        return _operator_placement(placement, should_return_si)
    if (settings := _settings.get(should_return_si)) is None:
        settings = _settings[should_return_si] = ifcopenshell.geom.settings()
        settings.set("convert-back-units", not should_return_si)
    return np.array(ifcopenshell.geom.create_shape(settings, placement).matrix).reshape((4, 4), order="F")


def _operator_placement(inst: ifcopenshell.entity_instance, should_return_si: bool) -> MatrixType:
    origin = np.zeros(3)
    origin[: len(inst.LocalOrigin.Coordinates)] = inst.LocalOrigin.Coordinates
    if should_return_si:
        origin *= ifcopenshell.util.unit.calculate_unit_scale(inst.file)
    axes = np.eye(3)
    for axis, direction in zip(axes, (inst.Axis1, inst.Axis2, getattr(inst, "Axis3", None))):
        if direction:
            axis[: len(direction.DirectionRatios)] = direction.DirectionRatios
    matrix = a2p(origin, axes[2], axes[0])
    # Mirror when the supplied Axis2 opposes the right-handed Y axis
    if matrix[:3, 1].dot(axes[1]) < 0.0:
        matrix[:3, 1] *= -1.0
    scale = inst.Scale or 1.0
    scales = [scale, scale, scale if inst.is_a("IfcCartesianTransformationOperator3D") else 1.0]
    if inst.is_a("IfcCartesianTransformationOperator3DnonUniform"):
        scales[1] = inst.Scale2 if inst.Scale2 is not None else scale
        scales[2] = inst.Scale3 if inst.Scale3 is not None else scale
    elif inst.is_a("IfcCartesianTransformationOperator2DnonUniform"):
        scales[1] = inst.Scale2 if inst.Scale2 is not None else scale
    matrix[:3, :3] *= scales
    return matrix


def get_mappeditem_transformation(item: ifcopenshell.entity_instance) -> MatrixType:
    """Parse an IfcMappedItem into a 4x4 transformation matrix

    Mapped items take a representation with an origin and transform them with a
    cartesian transformation operation. This function returns the final
    transformation matrix.

    :param item: The IfcMappedItem entity
    :return: A 4x4 numpy transformation matrix
    """
    return get_placement(item.MappingTarget) @ get_placement(item.MappingSource.MappingOrigin)


def get_storey_elevation(storey: ifcopenshell.entity_instance) -> float:
    """Get the Z elevation in project units of a buildling storey

    Building storeys store elevation in two possible locations: the Z value of
    its placement, or as a fallback the ``Elevation`` attribute.

    :param storey: The IfcBuildingStorey entity
    :return: The elevation in project units
    """
    if storey.ObjectPlacement:
        matrix = get_placement(storey.ObjectPlacement)
        return matrix[2][3]
    return getattr(storey, "Elevation", 0.0) or 0.0


def rotation(angle: float, axis: Literal["X", "Y", "Z"], is_degrees=True) -> MatrixType:
    """Create a 4x4 numpy matrix representing an euler rotation

    :param angle: The angle of rotation
    :param axis: The axis to rotate around, either X, Y, or Z.
    :param is_degrees: Whether or not the angle is specified in degrees or
        radians. Defaults to true (i.e. degrees).
    :return: A 4x4 numpy rotation matrix
    """
    theta = np.radians(angle) if is_degrees else angle
    cos, sin = np.cos(theta), np.sin(theta)

    # fmt: off
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
    # fmt: on
