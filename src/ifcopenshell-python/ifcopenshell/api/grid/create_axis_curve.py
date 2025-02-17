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

from __future__ import annotations
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.unit
import ifcopenshell.util.placement
import numpy as np
from ifcopenshell.util.shape_builder import VectorType, V, ifc_safe_vector_type


def create_axis_curve(
    file: ifcopenshell.file,
    *,
    p1: VectorType,
    p2: VectorType,
    grid_axis: ifcopenshell.entity_instance,
    is_si: bool = True,
) -> None:
    """Adds curve geometry to a grid axis to represent the axis extents

    An IFC grid will have a minimum of two axes (typically perpendicular). Each
    axis will then have a line which represents the extents of the axis.

    :param p1: The first point of the grid axis
    :param p2: The second point of the grid axis
    :param grid_axis: The IfcGridAxis element to add geometry to.
    :param is_si: If true, the points are in meters, not project units

    Example:

    .. code:: python

        # A pretty standard rectangular grid, with only two axes.
        grid = ifcopenshell.api.root.create_entity(model, ifc_class="IfcGrid")
        axis_a = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="A", uvw_axes="UAxes", grid=grid)
        axis_1 = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="1", uvw_axes="VAxes", grid=grid)

        # By convention, alphabetic grids are horizontal, and numeric are vertical
        ifcopenshell.api.grid.create_axis_curve(
            model, p1=np.array((0., 0., 0.)), p2=np.array((10., 0., 0.)), grid_axis=axis_a)
        ifcopenshell.api.grid.create_axis_curve(
            model, p1=np.array((0., 0., 0.)), p2=np.array((0., 10., 0.)), grid_axis=axis_1)
    """
    existing_curve = grid_axis.AxisCurve
    p1, p2 = V(p1), V(p2)
    if is_si:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
        p1 /= unit_scale
        p2 /= unit_scale

    grid = [i for i in file.get_inverse(grid_axis) if i.is_a("IfcGrid")][0]
    grid_matrix_i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(grid.ObjectPlacement))
    grid_axis.AxisCurve = file.createIfcPolyline(
        (
            file.createIfcCartesianPoint(ifc_safe_vector_type(grid_matrix_i @ p1)),
            file.createIfcCartesianPoint(ifc_safe_vector_type(grid_matrix_i @ p2)),
        )
    )

    if existing_curve:
        ifcopenshell.util.element.remove_deep2(file, existing_curve)
