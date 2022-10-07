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
            "context": None,  # IfcGeometricRepresentationContext
            "depth": 0.2,
            # Planes are defined as a matrix. The XY plane is the clipping boundary and +Z is removed.
            "clippings": [],  # A list of planes that define clipping half space solids
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Clipping" if self.settings["clippings"] else "SweptSolid",
            [self.create_item()],
        )

    def create_item(self):
        size = self.convert_si_to_unit(1)
        points = ((0.0, 0.0), (size, 0.0), (size, size), (0.0, size), (0.0, 0.0))
        if self.file.schema == "IFC2X3":
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
        else:
            curve = self.file.createIfcIndexedPolyCurve(self.file.createIfcCartesianPointList3D(points))
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
            None,
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.convert_si_to_unit(self.settings["depth"]),
        )
        if self.settings["clippings"]:
            return self.apply_clippings(extrusion)
        return extrusion

    def apply_clippings(self, first_operand):
        while self.settings["clippings"]:
            clipping = self.settings["clippings"].pop()
            second_operand = self.file.createIfcHalfSpaceSolid(
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
            first_operand = self.file.createIfcBooleanClippingResult("DIFFERENCE", first_operand, second_operand)
        return first_operand

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
