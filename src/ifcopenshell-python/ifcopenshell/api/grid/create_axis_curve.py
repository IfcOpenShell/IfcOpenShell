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
from mathutils import Matrix  # For now, we depend on Blender
import bpy.types


def create_axis_curve(
    file: ifcopenshell.file, axis_curve: bpy.types.Object, grid_axis: ifcopenshell.entity_instance
) -> None:
    """Adds curve geometry to a grid axis to represent the axis extents

    This currently depends on the Blender geometry kernel to function.

    An IFC grid will have a minimum of two axes (typically perpendicular). Each
    axis will then have a line which represents the extents of the axis.

    :param axis_curve: The Blender object that contains a mesh data block with a
        single edge.
    :type axis_curve: bpy.types.Object
    :param grid_axis: The IfcGridAxis element to add geometry to.
    :type grid_axis: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # A pretty standard rectangular grid, with only two axes.
        grid = ifcopenshell.api.root.create_entity(model, ifc_class="IfcGrid")
        axis_a = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="A", uvw_axes="UAxes", grid=grid)
        axis_1 = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="1", uvw_axes="VAxes", grid=grid)

        # Assume you have these Blender objects in your active Blender session
        obj1 = bpy.data.objects.get("AxisA")
        obj2 = bpy.data.objects.get("Axis1")
        ifcopenshell.api.grid.create_axis_curve(model, axis_curve=obj1, grid_axis=axis_a)
        ifcopenshell.api.grid.create_axis_curve(model, axis_curve=obj2, grid_axis=axis_1)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "axis_curve": axis_curve,  # A Blender object
        "grid_axis": grid_axis,
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        existing_curve = self.settings["grid_axis"].AxisCurve
        if existing_curve and len(self.file.get_inverse(existing_curve)) == 1:
            ifcopenshell.util.element.remove_deep(self.file, existing_curve)
            self.file.remove(existing_curve)

        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        grid = [i for i in self.file.get_inverse(self.settings["grid_axis"]) if i.is_a("IfcGrid")][0]
        points = [
            Matrix(ifcopenshell.util.placement.get_local_placement(grid.ObjectPlacement)).inverted()
            @ (self.settings["axis_curve"].matrix_world @ v.co)
            for v in self.settings["axis_curve"].data.vertices[0:2]
        ]
        self.settings["grid_axis"].AxisCurve = self.file.createIfcPolyline(
            [
                self.create_cartesian_point(points[0][0], points[0][1]),
                self.create_cartesian_point(points[1][0], points[1][1]),
            ]
        )

    def create_cartesian_point(self, x, y, z=None):
        x = self.convert_si_to_unit(x)
        y = self.convert_si_to_unit(y)
        if z is None:
            return self.file.createIfcCartesianPoint((x, y))
        z = self.convert_si_to_unit(z)
        return self.file.createIfcCartesianPoint((x, y, z))

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
