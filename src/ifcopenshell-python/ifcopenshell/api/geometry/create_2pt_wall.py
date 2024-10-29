# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api.geometry
import ifcopenshell.util.unit
from typing import Any


def create_2pt_wall(
    file: ifcopenshell.file,
    element: ifcopenshell.entity_instance,
    context: ifcopenshell.entity_instance,
    p1: tuple[float, float],
    p2: tuple[float, float],
    elevation: float,
    height: float,
    thickness: float,
    is_si: bool = True,
) -> ifcopenshell.entity_instance:
    """
    Create a wall between two points (p1 and p2).
    A shortcut for geometry.add_wall_representation.

    :param element: Wall IFC element.
    :param context: IfcGeometricRepresentationContext for the representation.
        only Model/Body/MODEL_VIEW type of representations are currently supported.
    :param p1: The starting point (x, y) of the wall.
    :param p2: The ending point (x, y) of the wall.
    :param elevation: The base elevation (z-coordinate) for the wall.
    :param height: The height of the wall.
    :param thickness: The thickness of the wall.
    :param is_si: If True, provided arguments units are treated as SI (meters).
        If False, values are converted from project units to SI.
    :return: IfcShapeRepresentation.
    """
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(file)

    p1_ = np.array(p1).astype(float)
    p2_ = np.array(p2).astype(float)

    length = float(np.linalg.norm(p2_ - p1_))

    if not is_si:
        length = convert_unit_to_si(length, si_conversion)
        height = convert_unit_to_si(height, si_conversion)
        thickness = convert_unit_to_si(thickness, si_conversion)
        # No need to convert p2 as length is already calculated.
        p1_ = convert_unit_to_si(p1_, si_conversion)
        elevation = convert_unit_to_si(elevation, si_conversion)

    representation = ifcopenshell.api.geometry.add_wall_representation(
        file,
        context=context,
        length=length,
        height=height,
        thickness=thickness,
    )

    v = p2_ - p1_
    v /= float(np.linalg.norm(v))
    matrix = np.array(
        [
            [v[0], -v[1], 0, p1_[0]],
            [v[1], v[0], 0, p1_[1]],
            [0, 0, 1, elevation],
            [0, 0, 0, 1],
        ]
    )
    ifcopenshell.api.geometry.edit_object_placement(file, product=element, matrix=matrix)
    return representation


def convert_unit_to_si(co: Any, si_conversion: float) -> Any:
    return co * si_conversion
