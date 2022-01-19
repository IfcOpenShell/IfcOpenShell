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
import ifcopenshell.util.unit
import ifcopenshell.util.placement
from mathutils import Matrix  # For now, we depend on Blender


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "axis_curve": None,  # A Blender object
            "grid_axis": None,
        }
        for key, value in settings.items():
            self.settings[key] = value

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
                self.create_cartesian_point(points[0][0], points[0][1], points[0][2]),
                self.create_cartesian_point(points[1][0], points[1][1], points[1][2]),
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
