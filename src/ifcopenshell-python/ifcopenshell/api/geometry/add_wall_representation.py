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
from math import sin, cos


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            "length": 1.0,
            "height": 3.0,
            "offset": 0.0,
            "thickness": 0.2,
            # Sloped walls along the wall's X axis, provided in radians
            "x_angle": 0,
            # Planes are defined as a matrix. The XY plane is the clipping boundary and +Z is removed.
            # [{"type": "IfcBooleanClippingResult", "operand_type": "IfcHalfSpaceSolid", "matrix": [...]}, {...}]
            "clippings": [],  # A list of planes that define clipping half space solids
            "booleans": [],  # Any existing IfcBooleanResults
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Clipping" if self.settings["clippings"] or self.settings["booleans"] else "SweptSolid",
            [self.create_item()],
        )

    def create_item(self):
        length = self.convert_si_to_unit(self.settings["length"])
        thickness = self.convert_si_to_unit(self.settings["thickness"])
        thickness *= 1 / cos(self.settings["x_angle"])
        points = (
            (0.0, 0.0),
            (0.0, thickness),
            (length, thickness),
            (length, 0.0),
            (0.0, 0.0),
        )
        if self.file.schema == "IFC2X3":
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
        else:
            curve = self.file.createIfcIndexedPolyCurve(self.file.createIfcCartesianPointList2D(points), None, False)
        if self.settings["x_angle"]:
            extrusion_direction = self.file.createIfcDirection(
                (0.0, sin(self.settings["x_angle"]), cos(self.settings["x_angle"]))
            )
        else:
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
            self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, self.convert_si_to_unit(self.settings["offset"]), 0.0)),
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            ),
            extrusion_direction,
            self.convert_si_to_unit(self.settings["height"]) * (1 / cos(self.settings["x_angle"])),
        )
        if self.settings["booleans"]:
            extrusion = self.apply_booleans(extrusion)
        if self.settings["clippings"]:
            extrusion = self.apply_clippings(extrusion)
        return extrusion

    def apply_booleans(self, first_operand):
        while self.settings["booleans"]:
            boolean = self.settings["booleans"].pop()
            boolean.FirstOperand = first_operand
            first_operand = boolean
        return first_operand

    def apply_clippings(self, first_operand):
        while self.settings["clippings"]:
            clipping = self.settings["clippings"].pop()
            if isinstance(clipping, ifcopenshell.entity_instance):
                new = ifcopenshell.util.element.copy(self.file, clipping)
                new.FirstOperand = first_operand
                first_operand = new
            elif clipping["operand_type"] == "IfcHalfSpaceSolid":
                matrix = clipping["matrix"]
                second_operand = self.file.createIfcHalfSpaceSolid(
                    self.file.createIfcPlane(
                        self.file.createIfcAxis2Placement3D(
                            self.file.createIfcCartesianPoint(
                                (
                                    self.convert_si_to_unit(matrix[0][3]),
                                    self.convert_si_to_unit(matrix[1][3]),
                                    self.convert_si_to_unit(matrix[2][3]),
                                )
                            ),
                            self.file.createIfcDirection((matrix[0][2], matrix[1][2], matrix[2][2])),
                            self.file.createIfcDirection((matrix[0][0], matrix[1][0], matrix[2][0])),
                        )
                    ),
                    False,
                )
                first_operand = self.file.create_entity(clipping["type"], "DIFFERENCE", first_operand, second_operand)
        return first_operand

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
