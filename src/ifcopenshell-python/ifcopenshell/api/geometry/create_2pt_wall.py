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
import ifcopenshell.api
import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, element=None, context=None, p1=None, p2=None, elevation=None, height=None, thickness=None):
        self.file = file
        self.settings = {
            "element": element,
            "context": context,
            "p1": p1,
            "p2": p2,
            "elevation": elevation,
            "height": height,
            "thickness": thickness,
        }

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)

        self.settings["p1"] = np.array(self.settings["p1"])
        self.settings["p2"] = np.array(self.settings["p2"])

        length = float(np.linalg.norm(self.settings["p2"] - self.settings["p1"])) * self.settings["unit_scale"]
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
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
                [v[0], -v[1], 0, self.settings["p1"][0]] * self.settings["unit_scale"],
                [v[1], v[0], 0, self.settings["p1"][1]] * self.settings["unit_scale"],
                [0, 0, 1, self.convert_si_to_unit(self.settings["elevation"])],
                [0, 0, 0, 1],
            ]
        )
        ifcopenshell.api.run(
            "geometry.edit_object_placement", self.file, product=self.settings["element"], matrix=matrix
        )
        return representation

    def convert_si_to_unit(self, co):
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        return co / self.settings["unit_scale"]
