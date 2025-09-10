# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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
import numpy as np
import ifcopenshell
from typing import Any, Union
from dataclasses import dataclass
from ifcopenshell.util.shape_builder import ShapeBuilder


@dataclass
class Clipping:
    location: tuple[float, float, float]
    normal: tuple[float, float, float]
    type: str = "IfcBooleanClippingResult"
    operand_type: str = "IfcHalfSpaceSolid"

    @classmethod
    def parse(
        cls, raw_data: Union[ifcopenshell.entity_instance, Clipping, dict[str, Any]]
    ) -> Union[ifcopenshell.entity_instance, Clipping]:
        """Parse various formats into a clipping object

        `raw_data` can be either:

        - IfcBooleanResult IFC entity
        - `Clipping` instance
        - dictionary to define `Clipping` - either `location` and `normal`
            or a `matrix` where XY plane is the clipping boundary and +Z is removed.
            `matrix` method will be soon to be deprecated completely.
        """
        if isinstance(raw_data, ifcopenshell.entity_instance):
            if not raw_data.is_a("IfcBooleanResult"):
                raise Exception(f"Provided clipping of unexpected IFC class: {raw_data}")
            return raw_data
        elif isinstance(raw_data, Clipping):
            return raw_data
        elif isinstance(raw_data, dict):
            if "matrix" in raw_data:
                raw_data = raw_data.copy()
                matrix = np.array(raw_data["matrix"])[:3]
                raw_data["normal"] = matrix[:, 2].tolist()
                raw_data["location"] = matrix[:, 3].tolist()
                del raw_data["matrix"]
            clipping_data = cls(**raw_data)
            if clipping_data.type != "IfcBooleanClippingResult":
                raise Exception(f'Provided clipping with unexpected result type "{clipping_data.type}"')
            if clipping_data.operand_type != "IfcHalfSpaceSolid":
                raise Exception(f'Provided clipping with unexpected operand type "{clipping_data.operand_type}"')
            return clipping_data
        raise Exception(f"Unexpected clipping type provided: {raw_data}")

    def apply(
        self, ifc_file: Union[ifcopenshell.file, None], first_operand: ifcopenshell.entity_instance, unit_scale: float
    ) -> ifcopenshell.entity_instance:
        """Applies the clipping data as an IfcBooleanClippingResult to an operand

        :param ifc_file: The model to create the entities in
        :param first_operand: The representation item to apply the boolean clipping to.
        :param unit_scale: The unit scale value to convert from the Clipping's SI units to project units
        :return: An IfcBooleanClippingResult which uses an IfcHalfSpaceSolid to clip the first operand
        """

        if not ifc_file:
            ifc_file = first_operand.file
        builder = ShapeBuilder(ifc_file)

        normal = np.array(self.normal)
        if np.allclose(normal, np.array([0.0, 0.0, 1.0]), atol=1e-2) or np.allclose(
            normal, np.array([0.0, 0.0, -1.0]), atol=1e-2
        ):
            arbitrary_vector = np.array([0.0, 1.0, 0.0])
        else:
            arbitrary_vector = np.array([0.0, 0.0, 1.0])

        x_axis = np.cross(normal, arbitrary_vector)
        x_axis /= np.linalg.norm(x_axis)

        placement = builder.create_axis2_placement_3d([i / unit_scale for i in self.location], self.normal, x_axis)
        plane = ifc_file.create_entity("IfcPlane", placement)

        second_operand = ifc_file.createIfcHalfSpaceSolid(plane, False)
        return ifc_file.createIfcBooleanClippingResult("DIFFERENCE", first_operand, second_operand)
