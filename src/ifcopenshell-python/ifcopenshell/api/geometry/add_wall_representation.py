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

from math import cos, sin
from typing import Any

import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell.util.data import Clipping


def add_wall_representation(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    length: float = 1.0,
    height: float = 3.0,
    direction_sense: str = "POSITIVE",
    offset: float = 0.0,
    thickness: float = 0.2,
    x_angle: float = 0.0,
    clippings: list[Clipping | dict[str, Any]] | None = None,
    booleans: list[ifcopenshell.entity_instance] | None = None,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for a wall.

    :param context: The IfcGeometricRepresentationContext for the representation,
        only Model/Body/MODEL_VIEW type of representations are currently supported.
    :param length: The length of the wall in meters.
    :param height: The height of the wall in meters.
    :param offset: The base offset distance of the wall from the origin.
    :param thickness: The thickness of the wall in meters.
    :param x_angle: The slope angle along the wall's X-axis, in radians.
    :param clippings: List of clipping definitions. Clippings can be `Clipping` objects
        or dictionaries of arguments for `Clipping.parse`. Each clipping has a
        ``normal`` that points toward the removed material (the discarded side),
        not toward the kept material; see :func:`clip_solid` for details.
    :param booleans: List of any existing IfcBooleanResults.
    :return: IfcShapeRepresentation.
    """
    usecase = Usecase()
    usecase.file = file
    return usecase.execute(
        context,
        length,
        height,
        direction_sense,
        offset,
        thickness,
        x_angle,
        clippings if clippings is not None else [],
        booleans if booleans is not None else [],
    )


class Usecase:
    file: ifcopenshell.file
    unit_scale: float

    def execute(
        self,
        context: ifcopenshell.entity_instance,
        length: float,
        height: float,
        direction_sense: str,
        offset: float,
        thickness: float,
        x_angle: float,
        clippings: list[Clipping | dict[str, Any]],
        booleans: list[ifcopenshell.entity_instance],
    ) -> ifcopenshell.entity_instance:
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        parsed_clippings = [Clipping.parse(c) for c in clippings]

        length = self.convert_si_to_unit(length)
        thickness = self.convert_si_to_unit(thickness)
        thickness *= 1 / cos(x_angle)
        if direction_sense == "NEGATIVE":
            thickness *= -1
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
        if x_angle:
            extrusion_direction = self.file.createIfcDirection((0.0, sin(x_angle), cos(x_angle)))
        else:
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
            self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, self.convert_si_to_unit(offset), 0.0)),
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            ),
            extrusion_direction,
            self.convert_si_to_unit(height) * abs(1 / cos(x_angle)),
        )
        if booleans:
            extrusion = self.apply_booleans(extrusion, booleans)
        if parsed_clippings:
            extrusion = self.apply_clippings(extrusion, parsed_clippings)

        return self.file.createIfcShapeRepresentation(
            context,
            context.ContextIdentifier,
            "Clipping" if parsed_clippings or booleans else "SweptSolid",
            [extrusion],
        )

    def apply_booleans(
        self, first_operand: ifcopenshell.entity_instance, booleans: list[ifcopenshell.entity_instance]
    ) -> ifcopenshell.entity_instance:
        for boolean in reversed(booleans):
            boolean.FirstOperand = first_operand
            first_operand = boolean
        return first_operand

    def apply_clippings(
        self,
        first_operand: ifcopenshell.entity_instance,
        clippings: list[ifcopenshell.entity_instance | Clipping],
    ) -> ifcopenshell.entity_instance:
        for clipping in reversed(clippings):
            if isinstance(clipping, ifcopenshell.entity_instance):
                new = ifcopenshell.util.element.copy(self.file, clipping)
                new.FirstOperand = first_operand
                first_operand = new
            else:  # Clipping
                first_operand = clipping.apply(self.file, first_operand, self.unit_scale)
        return first_operand

    def convert_si_to_unit(self, co: float) -> float:
        return co / self.unit_scale
