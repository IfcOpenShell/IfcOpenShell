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

import ifcopenshell.util.element


def remove_grid_axis(file: ifcopenshell.file, axis: ifcopenshell.entity_instance) -> None:
    """Removes a grid axis from a grid

    :param axis: The IfcGridAxis you want to remove.
    :type axis: ifcopenshell.entity_instance
    :return: None
    :rtype: None

    Example:

        # A pretty standard rectangular grid, with only two axes.
        grid = ifcopenshell.api.root.create_entity(model, ifc_class="IfcGrid")
        axis_a = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="A", uvw_axes="UAxes", grid=grid)
        axis_1 = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="1", uvw_axes="VAxes", grid=grid)

        # Let's create a third so we can remove it later
        axis_2 = ifcopenshell.api.grid.create_grid_axis(model,
            axis_tag="2", uvw_axes="VAxes", grid=grid)

        # Let's remove it!
        ifcopenshell.api.grid.remove_grid_axis(model, axis=axis_2)
    """
    axis_curve = axis.AxisCurve
    if len(file.get_inverse(axis_curve)) == 1:
        ifcopenshell.util.element.remove_deep(file, axis_curve)
        file.remove(axis_curve)
    file.remove(axis)
