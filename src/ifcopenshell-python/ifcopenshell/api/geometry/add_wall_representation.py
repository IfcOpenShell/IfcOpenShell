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

from dataclasses import dataclass, field
from typing import Optional
import warnings
import ifcopenshell
import ifcopenshell.util.unit
from ifcopenshell.util.unit import convert_si_to_unit
from ifcopenshell.util.representation import ClippingInfo
from math import sin, cos
from ifcopenshell.util.data import Clipping


@dataclass(slots=True)
class Usecase:
    file: ifcopenshell.file
    context: Optional[ifcopenshell.entity_instance] = None  # IfcGeometricRepresentationContext
    length: float = 1.
    height: float = 3.
    offset: float = 0.
    thickness: float = .2
    x_angle: float = 0.  # Sloped walls along the wall's X axis, provided in radians
    clippings: list[
        ClippingInfo | ClippingInfo.typed_dict() | ifcopenshell.entity_instance
    ] = field(default_factory=list)  # A list of planes that define clipping half space solids
    booleans: list[ifcopenshell.entity_instance] = field(default_factory=list)  # Any existing IfcBooleanResults
    unit_scale: float = field(init=False)

    def execute(self) -> ifcopenshell.entity_instance:
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        if self.file.strict_validation:
            self.validate_attrs()
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
            # Planes are defined either by Clipping objects
            # or by dictionaries of arguments for `Clipping.parse`
            "clippings": [],  # A list of planes that define clipping half space solids
            "booleans": [],  # Any existing IfcBooleanResults
        }
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        self.settings["clippings"] = [Clipping.parse(c) for c in self.settings["clippings"]]
        return self.file.createIfcShapeRepresentation(
            self.context,
            self.context.ContextIdentifier,
            "Clipping" if self.clippings or self.booleans else "SweptSolid",
            [self.create_item()],
        )

    def validate_attrs(self) -> None:
        self.validate_context()
        self.validate_clippings()
        self.validate_booleans()

    def validate_context(self) -> None:
        if (not isinstance(self.context, ifcopenshell.entity_instance)
                or not self.context.is_a("IfcGeometricRepresentationContext")):
            raise ValueError(f"Context must be an IfcGeometricRepresentationContext, not '{self.context}'")

    def validate_clippings(self) -> None:
        clippings = [ClippingInfo.parse(clipping, self.unit_scale) for clipping in self.clippings]
        self.clippings = [clipping for clipping in clippings if clipping]

    def validate_booleans(self) -> None:
        booleans: list[ifcopenshell.entity_instance] = []
        for boolean in self.booleans:
            if not isinstance(boolean, ifcopenshell.entity_instance):
                warnings.warn(f'Ignoring boolean of unexpected type: {boolean}')
            elif not boolean.is_a("IfcBooleanResult"):
                warnings.warn(f'Ignoring boolean of unexpected IFC class: {boolean}')
            else:
                booleans.append(boolean)
        self.booleans = booleans

    def create_item(self):
        length = convert_si_to_unit(self, self.length)
        thickness = convert_si_to_unit(self, self.thickness)
        thickness *= 1 / cos(self.x_angle)
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
        if self.x_angle:
            extrusion_direction = self.file.createIfcDirection(
                (0.0, sin(self.x_angle), cos(self.x_angle))
            )
        else:
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
            self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, convert_si_to_unit(self, self.offset), 0.0)),
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            ),
            extrusion_direction,
            convert_si_to_unit(self, self.height) * (1 / cos(self.x_angle)),
        )
        extrusion = self.apply_booleans(extrusion)
        extrusion = self.apply_clippings(extrusion)
        return extrusion

    def apply_booleans(self, first_operand):
        while self.booleans:
            boolean = self.booleans.pop()
            boolean.FirstOperand = first_operand
            first_operand = boolean
        return first_operand

    def apply_clippings(self, first_operand):
        while self.clippings:
            clipping = self.clippings.pop()
            if isinstance(clipping, ifcopenshell.entity_instance):
                new = ifcopenshell.util.element.copy(self.file, clipping)
                new.FirstOperand = first_operand
                first_operand = new
            else:
                first_operand = clipping.apply(self.file, first_operand)
            else:  # Clipping
                first_operand = clipping.apply(self.file, first_operand, self.settings["unit_scale"])
        return first_operand
