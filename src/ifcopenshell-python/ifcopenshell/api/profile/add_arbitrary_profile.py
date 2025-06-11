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

import numpy.typing as npt
import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import V, SequenceOfVectors, ifc_safe_vector_type
from typing import Optional, Union


def add_arbitrary_profile(
    file: ifcopenshell.file, profile: SequenceOfVectors, name: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Adds a new arbitrary polyline-based profile

    The profile is represented as a polyline defined by a list of
    coordinates. Only straight segments are allowed. Coordinates must be
    provided in SI meters.

    To represent a closed curve, the first and last coordinate must be
    identical.

    :param profile: A list of coordinates
    :param name: If the profile is semantically significant (i.e. to be
        managed and reused by the user) then it must be named. Otherwise,
        this may be left as none.
    :return: The newly created IfcArbitraryClosedProfileDef

    Example:

    .. code:: python

        # A 10mm by 100mm rectangle, such that might be used as a wooden
        # skirting board or kick plate.
        square = ifcopenshell.api.profile.add_arbitrary_profile(model,
            profile=[(0., 0.), (.01, 0.), (.01, .1), (0., .1), (0., 0.)],
            name="SK01 Profile")
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(V(profile), name)


class Usecase:
    file: ifcopenshell.file

    def execute(self, profile: npt.NDArray, name: Union[str, None]):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        points = self.convert_si_to_unit(profile)
        if self.file.schema == "IFC2X3":
            curve = self.file.create_entity(
                "IfcPolyline",
                [self.file.create_entity("IfcCartesianPoint", ifc_safe_vector_type(p)) for p in points],
            )
        else:
            dimensions = points.shape[1]
            if dimensions == 2:
                ifc_points = self.file.create_entity("IfcCartesianPointList2D", ifc_safe_vector_type(points))
            elif dimensions == 3:
                ifc_points = self.file.create_entity("IfcCartesianPointList3D", ifc_safe_vector_type(points))
            else:
                assert False, f"Invalid dimensions: {dimensions}."
            curve = self.file.create_entity("IfcIndexedPolyCurve", ifc_points)
        return self.file.create_entity("IfcArbitraryClosedProfileDef", "AREA", name, curve)

    def convert_si_to_unit(self, co: npt.NDArray) -> npt.NDArray:
        return co / self.unit_scale
