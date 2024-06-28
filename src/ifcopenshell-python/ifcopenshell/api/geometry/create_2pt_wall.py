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
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "element": element,
        "context": context,
        "p1": p1,
        "p2": p2,
        "elevation": elevation,
        "height": height,
        "thickness": thickness,
        "is_si": is_si,
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        self.settings["p1"] = np.array(self.settings["p1"]).astype(float)
        self.settings["p2"] = np.array(self.settings["p2"]).astype(float)

        length = float(np.linalg.norm(self.settings["p2"] - self.settings["p1"]))

        if not self.settings["is_si"]:
            length = self.convert_unit_to_si(length)
            self.settings["height"] = self.convert_unit_to_si(self.settings["height"])
            self.settings["thickness"] = self.convert_unit_to_si(self.settings["thickness"])
            self.settings["p1"][0] = self.convert_unit_to_si(self.settings["p1"][0])
            self.settings["p1"][1] = self.convert_unit_to_si(self.settings["p1"][1])
            self.settings["elevation"] = self.convert_unit_to_si(self.settings["elevation"])

        representation = ifcopenshell.api.geometry.add_wall_representation(
            self.file,
            context=self.settings["context"],
            length=length,
            height=self.settings["height"],
            thickness=self.settings["thickness"],
        )
        v = self.settings["p2"] - self.settings["p1"]
        v /= float(np.linalg.norm(v))
        matrix = np.array(
            [
                [v[0], -v[1], 0, self.settings["p1"][0]],
                [v[1], v[0], 0, self.settings["p1"][1]],
                [0, 0, 1, self.settings["elevation"]],
                [0, 0, 0, 1],
            ]
        )
        ifcopenshell.api.geometry.edit_object_placement(self.file, product=self.settings["element"], matrix=matrix)
        return representation

    def convert_unit_to_si(self, co):
        return co * self.settings["unit_scale"]
