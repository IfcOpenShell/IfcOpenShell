# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "representation": None,
            "operator": "DIFFERENCE",
            # The XY plane is the clipping boundary and +Z is removed.
            "matrix": None,  # A matrix to define a clipping half space solid.
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        self.settings["representation"].RepresentationType = "Clipping"
        result = self.create_half_space_solid()
        items = []
        for item in self.settings["representation"].Items:
            items.append(self.file.createIfcBooleanResult(self.settings["operator"], item, result))
        self.settings["representation"].Items = items

    def create_half_space_solid(self):
        clipping = self.settings["matrix"]
        return self.file.createIfcHalfSpaceSolid(
            self.file.createIfcPlane(
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint(
                        (
                            self.convert_si_to_unit(clipping[0][3]),
                            self.convert_si_to_unit(clipping[1][3]),
                            self.convert_si_to_unit(clipping[2][3]),
                        )
                    ),
                    self.file.createIfcDirection((clipping[0][2], clipping[1][2], clipping[2][2])),
                    self.file.createIfcDirection((clipping[0][0], clipping[1][0], clipping[2][0])),
                )
            ),
            False,
        )

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
