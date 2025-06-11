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
import numpy.typing as npt
from ifcopenshell.util.shape_builder import SequenceOfVectors, ifc_safe_vector_type, V
from typing import Optional, Union


def add_arbitrary_profile_with_voids(
    file: ifcopenshell.file,
    outer_profile: SequenceOfVectors,
    inner_profiles: list[SequenceOfVectors],
    name: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    """Adds a new arbitrary polyline-based profile with voids

    The outer profile is represented as a polyline defined by a list of
    coordinates. Only straight segments are allowed. Coordinates must be
    provided in SI meters.

    To represent a closed curve, the first and last coordinate must be
    identical.

    The inner profiles are represented as a list of polylines.
    Every polyline in defined by a list of coordinates.
    Only straight segments are allowed. Coordinates must be
    provided in SI meters.

    :param outer_profile: A list of coordinates
    :param inner_profiles: A list of polylines
    :param name: If the profile is semantically significant (i.e. to be
        managed and reused by the user) then it must be named. Otherwise,
        this may be left as none.
    :return: The newly created IfcArbitraryProfileDefWithVoids

    Example:

    .. code:: python

        # A 400mm by 400mm square with a 200mm by 200mm hole in it.
        square_with_hole = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(model,
            outer_profile=[(0., 0.), (.4, 0.), (.4, .4), (0., .4), (0., 0.)],
            inner_profiles=[[(0.1, 0.1), (0.3, 0.1), (0.3, 0.3), (0.1, 0.3), (0.1, 0.1)]],
            name="SK01 Hole Profile")
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(V(outer_profile), [V(p) for p in inner_profiles], name)


class Usecase:
    file: ifcopenshell.file

    def execute(
        self,
        outer_profile: npt.NDArray,
        inner_profiles: list[npt.NDArray],
        name: Union[str, None],
    ):
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        outer_points = self.convert_si_to_unit(outer_profile)
        inner_points: list[npt.NDArray] = []
        for inner_profile in inner_profiles:
            inner_points.append(self.convert_si_to_unit(inner_profile))

        inner_curves: list[ifcopenshell.entity_instance] = []
        if self.file.schema == "IFC2X3":
            outer_curve = self.file.create_entity(
                "IfcPolyline",
                [self.file.create_entity("IfcCartesianPoint", ifc_safe_vector_type(p)) for p in outer_points],
            )
            for inner_point in inner_points:
                inner_curves.append(
                    self.file.create_entity(
                        "IfcPolyline",
                        [self.file.create_entity("IfcCartesianPoint", ifc_safe_vector_type(p)) for p in inner_point],
                    )
                )
        else:
            outer_curve = self.file.create_entity(
                "IfcIndexedPolyCurve",
                (self.file.create_entity("IfcCartesianPointList3D", ifc_safe_vector_type(outer_points))),
            )
            for inner_point in inner_points:
                dimensions = inner_point.shape[1]
                if dimensions == 2:
                    ifc_points = self.file.create_entity("IfcCartesianPointList2D", ifc_safe_vector_type(inner_point))
                elif dimensions == 3:
                    ifc_points = self.file.create_entity("IfcCartesianPointList3D", ifc_safe_vector_type(inner_point))
                else:
                    assert False, f"Invalid dimensions: {dimensions}."
                inner_curves.append(self.file.create_entity("IfcIndexedPolyCurve", ifc_points))
        return self.file.create_entity("IfcArbitraryProfileDefWithVoids", "AREA", name, outer_curve, inner_curves)

    def convert_si_to_unit(self, co: npt.NDArray) -> npt.NDArray:
        return co / self.unit_scale
