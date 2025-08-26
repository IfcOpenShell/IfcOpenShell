# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape_builder
from typing import Optional


def connect_wall(
    file: ifcopenshell.file,
    wall1: ifcopenshell.entity_instance,
    wall2: ifcopenshell.entity_instance,
    is_atpath: bool = False,
) -> Optional[ifcopenshell.entity_instance]:
    matrix1i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(wall1.ObjectPlacement))
    matrix2 = ifcopenshell.util.placement.get_local_placement(wall2.ObjectPlacement)
    axis1 = ifcopenshell.util.representation.get_reference_line(wall1)
    axis2 = ifcopenshell.util.representation.get_reference_line(wall2)
    axis2[0] = (matrix1i @ matrix2 @ np.concatenate((axis2[0], (0, 1))))[:2]
    axis2[1] = (matrix1i @ matrix2 @ np.concatenate((axis2[1], (0, 1))))[:2]
    midx = (axis1[0][0] + axis1[1][0]) / 2
    starty = axis2[0][1]
    endy = axis2[1][1]
    y = axis1[0][1]

    if (x := ifcopenshell.util.shape_builder.intersect_x_axis_2d(*axis2, y=y)) is None:
        return

    wall1_end = "ATEND" if x > midx else "ATSTART"
    if is_atpath:
        wall2_end = "ATPATH"
    elif abs(y - starty) < abs(y - endy):
        wall2_end = "ATSTART"
    else:
        wall2_end = "ATEND"

    return ifcopenshell.api.geometry.connect_path(
        file,
        relating_element=wall1,
        related_element=wall2,
        relating_connection=wall1_end,
        related_connection=wall2_end,
    )
