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
from ifcopenshell.util.data import Clipping
from math import sin, cos
from typing import Any, Optional, Union


def add_slab_representation(
    file,
    # IfcGeometricRepresentationContext
    context: ifcopenshell.entity_instance,
    # in meters
    depth: float = 0.2,
    # in radians
    x_angle: float = 0.0,
    # A list of planes that define clipping half space solids
    # Planes are defined either by Clipping objects
    # or by dictionaries of arguments for `Clipping.parse`
    clippings: Optional[list[Union[Clipping, dict[str, Any]]]] = None,
) -> ifcopenshell.entity_instance:
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "context": context,
        "depth": depth,
        "x_angle": x_angle,
        "clippings": clippings if clippings is not None else [],
    }
    return usecase.execute()


class Usecase:
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
            curve = self.file.createIfcIndexedPolyCurve(self.file.createIfcCartesianPointList2D(points))
        if self.settings["x_angle"]:
            extrusion_direction = self.file.createIfcDirection(
                (0.0, sin(self.settings["x_angle"]), cos(self.settings["x_angle"]))
            )
        else:
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))

        position = None
        # default position for IFC2X3 where .Position is not optional
        if self.file.schema == "IFC2X3":
            position = self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                self.file.createIfcDirection((0.0, 0.0, 1.0)),
                self.file.createIfcDirection((1.0, 0.0, 0.0)),
            )

        extrusion = self.file.createIfcExtrudedAreaSolid(
            self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
            position,
            extrusion_direction,
            self.convert_si_to_unit(self.settings["depth"]) * 1 / cos(self.settings["x_angle"]),
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
