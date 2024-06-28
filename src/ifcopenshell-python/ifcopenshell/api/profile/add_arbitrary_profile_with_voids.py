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
from typing import Optional


def add_arbitrary_profile_with_voids(
    file: ifcopenshell.file,
    outer_profile: list[tuple[float, float]],
    inner_profiles: list[list[tuple[float, float]]],
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
    :type profile: list[tuple[float, float]]
    :param inner_profiles: A list of polylines
    :type profile: list[list[tuple[float, float]]]
    :param name: If the profile is semantically significant (i.e. to be
        managed and reused by the user) then it must be named. Otherwise,
        this may be left as none.
    :type name: str, optional
    :return: The newly created IfcArbitraryProfileDefWithVoids
    :rtype: ifcopenshell.entity_instance

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
    usecase.settings = {"outer_profile": outer_profile, "inner_profiles": inner_profiles, "name": name}
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        outer_points = [self.convert_si_to_unit(p) for p in self.settings["outer_profile"]]
        inner_points = []
        for inner_profile in self.settings["inner_profiles"]:
            inner_points.append([self.convert_si_to_unit(p) for p in inner_profile])
        if self.file.schema == "IFC2X3":
            outer_curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in outer_points])
            inner_curves = []
            for inner_point in inner_points:
                inner_curves.append(
                    self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in inner_point])
                )
        else:
            outer_curve = self.file.createIfcIndexedPolyCurve(self.file.createIfcCartesianPointList3D(outer_points))
            inner_curves = []
            for inner_point in inner_points:
                dimensions = len(inner_point[0])
                if dimensions == 2:
                    ifc_points = self.file.createIfcCartesianPointList2D(inner_point)
                elif dimensions == 3:
                    ifc_points = self.file.createIfcCartesianPointList3D(inner_point)
                inner_curves.append(self.file.createIfcIndexedPolyCurve(ifc_points))
        return self.file.createIfcArbitraryProfileDefWithVoids("AREA", self.settings["name"], outer_curve, inner_curves)

    def convert_si_to_unit(self, co):
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        return co / self.settings["unit_scale"]
