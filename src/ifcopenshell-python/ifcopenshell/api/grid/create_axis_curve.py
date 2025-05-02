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
from ifcopenshell.util.shape_builder import VectorType, V, ifc_safe_vector_type, np_apply_matrix


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

    Points are provided as 3D coordinates in world space.
    During axis creation, the coordinates will be localized relative to IfcGrid
    and saved as 2D.

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
    points = V([p1, p2])
    if is_si:
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
        points /= unit_scale

    grid = next(i for i in file.get_inverse(grid_axis) if i.is_a("IfcGrid"))
    grid_matrix_i = np.linalg.inv(ifcopenshell.util.placement.get_local_placement(grid.ObjectPlacement))
    p1, p2 = ifc_safe_vector_type(np_apply_matrix(points, grid_matrix_i))
    grid_axis.AxisCurve = file.create_entity(
        "IfcPolyline",
        (
            file.create_entity("IfcCartesianPoint", p1[:2]),
            file.create_entity("IfcCartesianPoint", p2[:2]),
        ),
    )

    if existing_curve:
        ifcopenshell.util.element.remove_deep2(file, existing_curve)
