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
from ifcopenshell.util.data import Clipping
from typing import Any, Union, Optional, Literal

VECTOR_3D = tuple[float, float, float]


def add_profile_representation(
    file: ifcopenshell.file,
    # IfcGeometricRepresentationContext
    context: ifcopenshell.entity_instance,
    profile: ifcopenshell.entity_instance,
    # in meters
    depth: float = 1.0,
    cardinal_point: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] = 5,
    # A list of planes that define clipping half space solids
    # Planes are defined either by Clipping objects
    # or by dictionaries of arguments for `Clipping.parse`
    clippings: Optional[list[Union[Clipping, dict[str, Any]]]] = None,
    placement_zx_axes: tuple[Union[VECTOR_3D, None], Union[VECTOR_3D, None]] = (None, None),
) -> ifcopenshell.entity_instance:
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "context": context,
        "profile": profile,
        "depth": depth,
        "cardinal_point": cardinal_point,
        "clippings": clippings if clippings is not None else [],
        "placement_zx_axes": placement_zx_axes,
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        self.settings["clippings"] = [Clipping.parse(c) for c in self.settings["clippings"]]
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Clipping" if self.settings["clippings"] else "SweptSolid",
            [self.create_item()],
        )

    def create_item(self):
        point = self.get_point()
        placement = self.file.createIfcAxis2Placement3D(
            point,
            self.file.createIfcDirection(self.settings["placement_zx_axes"][0] or (0.0, 0.0, 1.0)),
            self.file.createIfcDirection(self.settings["placement_zx_axes"][1] or (1.0, 0.0, 0.0)),
        )
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.settings["profile"],
            placement,
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.convert_si_to_unit(self.settings["depth"]),
        )
        if self.settings["clippings"]:
            return self.apply_clippings(extrusion)
        return extrusion

    def apply_clippings(self, first_operand):
        while self.settings["clippings"]:
            clipping = self.settings["clippings"].pop()
            if isinstance(clipping, ifcopenshell.entity_instance):
                new = ifcopenshell.util.element.copy(self.file, clipping)
                new.FirstOperand = first_operand
                first_operand = new
            else:  # Clipping
                first_operand = clipping.apply(self.file, first_operand, self.settings["unit_scale"])
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
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            shape = ifcopenshell.geom.create_shape(settings, self.settings["profile"])
            x = [shape.verts[i] for i in range(0, len(shape.verts), 3)]
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
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            shape = ifcopenshell.geom.create_shape(settings, self.settings["profile"])
            y = [shape.verts[i + 1] for i in range(0, len(shape.verts), 3)]
            return self.convert_si_to_unit(max(y) - min(y))
        return 0.0
