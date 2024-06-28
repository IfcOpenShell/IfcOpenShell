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


def add_arbitrary_profile(
    file: ifcopenshell.file, profile: list[tuple[float, float]], name: Optional[str] = None
) -> ifcopenshell.entity_instance:
    """Adds a new arbitrary polyline-based profile

    The profile is represented as a polyline defined by a list of
    coordinates. Only straight segments are allowed. Coordinates must be
    provided in SI meters.

    To represent a closed curve, the first and last coordinate must be
    identical.

    :param profile: A list of coordinates
    :type profile: list[tuple[float, float]]
    :param name: If the profile is semantically significant (i.e. to be
        managed and reused by the user) then it must be named. Otherwise,
        this may be left as none.
    :type name: str, optional
    :return: The newly created IfcArbitraryClosedProfileDef
    :rtype: ifcopenshell.entity_instance

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
    usecase.settings = {"profile": profile, "name": name}
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        points = [self.convert_si_to_unit(p) for p in self.settings["profile"]]
        if self.file.schema == "IFC2X3":
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
        else:
            dimensions = len(points[0])
            if dimensions == 2:
                ifc_points = self.file.createIfcCartesianPointList2D(points)
            elif dimensions == 3:
                ifc_points = self.file.createIfcCartesianPointList3D(points)
            curve = self.file.createIfcIndexedPolyCurve(ifc_points)
        return self.file.createIfcArbitraryClosedProfileDef("AREA", self.settings["name"], curve)

    def convert_si_to_unit(self, co):
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        return co / self.settings["unit_scale"]
