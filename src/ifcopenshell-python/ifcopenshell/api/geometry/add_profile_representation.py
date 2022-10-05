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

import ifcopenshell.geom
import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            "profile": None,
            "depth": 1.0,
            "cardinal_point": 5,
            # Planes are defined as a matrix. The XY plane is the clipping boundary and +Z is removed.
            # [{"type": "IfcBooleanClippingResult", "operand_type": "IfcHalfSpaceSolid", "matrix": [...]}, {...}]
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
        point = self.get_point()
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.settings["profile"],
            self.file.createIfcAxis2Placement3D(
                point,
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            ),
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.convert_si_to_unit(self.settings["depth"]),
        )
        if self.settings["clippings"]:
            return self.apply_clippings(extrusion)
        return extrusion

    def apply_clippings(self, first_operand):
        while self.settings["clippings"]:
            clipping = self.settings["clippings"].pop()
            if clipping["operand_type"] == "IfcHalfSpaceSolid":
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

    def get_point(self):
        if not self.settings["cardinal_point"]:
            return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        elif self.settings["cardinal_point"] == 1:
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, self.get_y() / 2, 0.0))
        elif self.settings["cardinal_point"] == 2:
            return self.file.createIfcCartesianPoint((0.0, self.get_y() / 2, 0.0))
        elif self.settings["cardinal_point"] == 3:
            return self.file.createIfcCartesianPoint((self.get_x() / 2, self.get_y() / 2, 0.0))
        elif self.settings["cardinal_point"] == 4:
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, 0.0, 0.0))
        elif self.settings["cardinal_point"] == 5:
            return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        elif self.settings["cardinal_point"] == 6:
            return self.file.createIfcCartesianPoint((self.get_x() / 2, 0.0, 0.0))
        elif self.settings["cardinal_point"] == 7:
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, -self.get_y() / 2, 0.0))
        elif self.settings["cardinal_point"] == 8:
            return self.file.createIfcCartesianPoint((0.0, -self.get_y() / 2, 0.0))
        elif self.settings["cardinal_point"] == 9:
            return self.file.createIfcCartesianPoint((self.get_x() / 2, -self.get_y() / 2, 0.0))
        # TODO other cardinal points
        return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))

    def get_x(self):
        if self.settings["profile"].is_a("IfcAsymmetricIShapeProfileDef"):
            return self.settings["profile"].OverallWidth
        elif self.settings["profile"].is_a("IfcCShapeProfileDef"):
            return self.settings["profile"].Width
        elif self.settings["profile"].is_a("IfcCircleProfileDef"):
            return self.settings["profile"].Radius * 2
        elif self.settings["profile"].is_a("IfcEllipseProfileDef"):
            return self.settings["profile"].SemiAxis1 * 2
        elif self.settings["profile"].is_a("IfcIShapeProfileDef"):
            return self.settings["profile"].OverallWidth
        elif self.settings["profile"].is_a("IfcLShapeProfileDef"):
            return self.settings["profile"].Width
        elif self.settings["profile"].is_a("IfcRectangleProfileDef"):
            return self.settings["profile"].XDim
        elif self.settings["profile"].is_a("IfcTShapeProfileDef"):
            return self.settings["profile"].FlangeWidth
        elif self.settings["profile"].is_a("IfcUShapeProfileDef"):
            return self.settings["profile"].FlangeWidth
        elif self.settings["profile"].is_a("IfcZShapeProfileDef"):
            return (self.settings["profile"].FlangeWidth * 2) - self.settings["profile"].WebThickness
        else:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.INCLUDE_CURVES, True)
            shape = ifcopenshell.geom.create_shape(settings, self.settings["profile"])
            x = [verts[i] for i in range(0, len(shape.verts), 3)]
            return self.convert_si_to_unit(max(x) - min(x))
        return 0.0

    def get_y(self):
        if self.settings["profile"].is_a("IfcAsymmetricIShapeProfileDef"):
            return self.settings["profile"].OverallDepth
        elif self.settings["profile"].is_a("IfcCShapeProfileDef"):
            return self.settings["profile"].Depth
        elif self.settings["profile"].is_a("IfcCircleProfileDef"):
            return self.settings["profile"].Radius * 2
        elif self.settings["profile"].is_a("IfcEllipseProfileDef"):
            return self.settings["profile"].SemiAxis2 * 2
        elif self.settings["profile"].is_a("IfcIShapeProfileDef"):
            return self.settings["profile"].OverallDepth
        elif self.settings["profile"].is_a("IfcLShapeProfileDef"):
            return self.settings["profile"].Depth
        elif self.settings["profile"].is_a("IfcRectangleProfileDef"):
            return self.settings["profile"].YDim
        elif self.settings["profile"].is_a("IfcTShapeProfileDef"):
            return self.settings["profile"].Depth
        elif self.settings["profile"].is_a("IfcUShapeProfileDef"):
            return self.settings["profile"].Depth
        elif self.settings["profile"].is_a("IfcZShapeProfileDef"):
            return self.settings["profile"].Depth
        else:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.INCLUDE_CURVES, True)
            shape = ifcopenshell.geom.create_shape(settings, self.settings["profile"])
            y = [verts[i + 1] for i in range(0, len(shape.verts), 3)]
            return self.convert_si_to_unit(max(y) - min(y))
        return 0.0
