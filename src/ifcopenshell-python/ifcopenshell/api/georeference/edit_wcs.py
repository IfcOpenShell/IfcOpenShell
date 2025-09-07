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

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder
from math import sin, cos, radians


def edit_wcs(
    file: ifcopenshell.file,
    x: float = 0.0,
    y: float = 0.0,
    z: float = 0.0,
    rotation: float = 0.0,
    is_si: bool = True,
) -> None:
    """Edits the WCS for all geometric contexts to a translation and rotation

    Typically, a project's local engineering origin (0, 0, 0) has a coordinate
    operation (e.g. map conversion) to a projected CRS. If a WCS is provided,
    the coordinate operation is relative to the WCS, not the local engineering
    origin.

    For example, if I have an IfcSite with a placement at (10, 0, 0) and a map
    conversion of (50, 0, 0), my IfcSite's local XYZ is at (10, 0, 0) with an
    ENH (Easting, Northing, Height) of (60, 0, 0).

    If I then define by WCS at (15, 0, 0), my IfcSite's local XYZ is still at
    (10, 0, 0) but its ENH is now at (45, 0, 0).

    It's recommended to leave the WCS at 0,0,0. Please :)

    :param x: The X translation of the WCS
    :param y: The Y translation of the WCS
    :param z: The Z translation of the WCS
    :param rotation: The rotation around the Z axis (i.e. top down plan view)
        in decimal degrees of the WCS. Anticlockwise is positive.

    Example:

    .. code:: python

        # This is the simplest scenario, resetting the WCS to 0,0,0 with no rotation (recommended)
        ifcopenshell.api.georeference.edit_wcs(model)
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    builder = ShapeBuilder(file)
    if np.isclose(rotation, 0):
        xaxis_x = 1.0
        xaxis_y = 0.0
    else:
        xaxis_x = cos(radians(rotation))
        xaxis_y = sin(radians(rotation))
    if np.allclose((x, y, z), (0, 0, 0)):
        x = y = z = 0.0
    for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
        old_wcs = context.WorldCoordinateSystem
        if context.CoordinateSpaceDimension == 3:
            if is_si:
                xyz = (x / unit_scale, y / unit_scale, z / unit_scale)
            else:
                xyz = (x, y, z)
            placement = builder.create_axis2_placement_3d(xyz, (0.0, 0.0, 1.0), (xaxis_x, xaxis_y, 0.0))
        elif context.CoordinateSpaceDimension == 2:
            if is_si:
                point = file.createIfcCartesianPoint((x / unit_scale, y / unit_scale))
            else:
                point = file.createIfcCartesianPoint((x, y))
            placement = file.createIfcAxis2Placement2D(
                point,
                file.createIfcDirection((xaxis_x, xaxis_y)),
            )
        context.WorldCoordinateSystem = placement
        if file.get_total_inverses(old_wcs) == 0:
            ifcopenshell.util.element.remove_deep2(file, old_wcs)
