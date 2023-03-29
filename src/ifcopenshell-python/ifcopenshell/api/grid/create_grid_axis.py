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


class Usecase:
    def __init__(self, file, axis_tag=None, same_sense=None, uvw_axes=None, grid=None):
        """Adds a new grid axis to a grid

        An IFC grid will typically have a minimum of two axes which will be
        perpendicular to one another. Grids may be rectangular (typically
        perpendicular lines), radial (where one set of axes is a circle and the
        other is a line), or triangular (three sets of axes, each at a different
        angle to one another).

        For a simple rectangular grid, the "UAxes" are a set of one or more
        horizontal axes, which are typically labeled with the convention of A,
        B, C, etc. The "VAxes" is another set of one or more vertical axes,
        typically labeled with the convention of 1, 2, 3, etc. These axes are
        horizontal or vertical relative to project north.

        For a radial grid, the "UAxes" are straight lines, typically radiating
        from a central point. The "VAxes" are circular perimeters, with the
        center of these circles being the same central point.

        For a triangular grid, the UAxes, VAxes, and WAxes are all sets of one
        or more straight lines.

        :param axis_tag: The name of the axis, that would typically be labeled
            on drawings or described on site during coordination, such as A, B,
            C, 1, 2, 3, etc. Defaults to "A".
        :type axis_tag: str, optional
        :param same_sense: Determines whether the direction of the axis's line
            is reversed. True means the direction the geometry is defined in
            represents the direction of the axis. False means the direction is
            reversed. Leave as True if unsure. Defaults to "True".
        :type same_sense: bool, optional
        :param uvw_axes: Choose from "UAxes", "VAxes" or "WAxes" depending on
            which set of axes the new axis you are adding should belong to.
            Defaults to "UAxes".
        :type uvw_axes: str, optional
        :param grid: The IfcGrid you are adding the axis to.
        :type grid: ifcopenshell.entity_instance.entity_instance
        :return: The newly created IfcGridAxis
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

            # A pretty standard rectangular grid, with only two axes.
            grid = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcGrid")
            axis_a = ifcopenshell.api.run("grid.create_grid_axis", model,
                axis_tag="A", uvw_axes="UAxes", grid=grid)
            axis_1 = ifcopenshell.api.run("grid.create_grid_axis", model,
                axis_tag="1", uvw_axes="VAxes", grid=grid)
        """
        self.file = file
        self.settings = {
            "axis_tag": axis_tag or "A",
            "same_sense": same_sense or True,
            "uvw_axes": uvw_axes or "UAxes",  # Choose which axes
            "grid": grid,
        }

    def execute(self):
        element = self.file.create_entity(
            "IfcGridAxis", **{"AxisTag": self.settings["axis_tag"], "SameSense": self.settings["same_sense"]}
        )
        axes = list(getattr(self.settings["grid"], self.settings["uvw_axes"]) or [])
        axes.append(element)
        setattr(self.settings["grid"], self.settings["uvw_axes"], axes)
        return element
