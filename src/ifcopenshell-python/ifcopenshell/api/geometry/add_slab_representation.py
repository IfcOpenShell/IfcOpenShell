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

import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell.util.data import Clipping
from math import sin, cos
from typing import Any, Optional, Union


def add_slab_representation(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    depth: float = 0.2,
    direction_sense: str = "POSITIVE",
    offset: float = 0.0,
    x_angle: float = 0.0,
    clippings: Optional[list[Union[Clipping, dict[str, Any]]]] = None,
    polyline: Optional[list[tuple[float, float]]] = None,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for a slab.

    :param context: The IfcGeometricRepresentationContext for the representation,
        only Model/Body/MODEL_VIEW type of representations are currently supported.
    :param depth: The slab depth, in meters.
    :param x_angle: The slope angle along the slab's X-axis, in radians.
    :param clippings: List of planes that define clipping half space solids.
        Clippings can be `Clipping` objects or dictionaries of arguments for `Clipping.parse`.
    :return: IfcShapeRepresentation.

    Example:

    .. code:: python

        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        clippings = [ifcopenshell.util.data.Clipping(location=(0.0, 0.0, 0.1), normal=(0.0, 0.0, 1.0),)]
        representation = ifcopenshell.api.geometry.add_slab_representation(ifc_file, context, depth=0.2, clippings=clippings)
        ifcopenshell.api.geometry.assign_representation(ifc_file, product=element, representation=representation)
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "context": context,
        "depth": depth,
        "direction_sense": direction_sense,
        "offset": offset,
        "x_angle": x_angle,
        "clippings": clippings if clippings is not None else [],
        "polyline": polyline,
    }
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    settings: dict[str, Any]

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
        if self.settings["polyline"]:
            points = [
                (self.convert_si_to_unit(p[0]), self.convert_si_to_unit(p[1] * (1 / cos(self.settings["x_angle"]))))
                for p in self.settings["polyline"]
            ]
        if self.file.schema == "IFC2X3":
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
        else:
            curve = self.file.createIfcIndexedPolyCurve(self.file.createIfcCartesianPointList2D(points))
        if self.settings["x_angle"]:
            extrusion_direction = self.file.createIfcDirection(
                (0.0, sin(self.settings["x_angle"]), cos(self.settings["x_angle"]))
            )
            if self.settings["direction_sense"] == "NEGATIVE":
                extrusion_direction = self.file.createIfcDirection(
                    (0.0, -sin(self.settings["x_angle"]), -cos(self.settings["x_angle"]))
                )
        else:
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
            if self.settings["direction_sense"] == "NEGATIVE":
                extrusion_direction = self.file.createIfcDirection((0.0, 0.0, -1.0))

        position = None
        # default position for IFC2X3 where .Position is not optional
        if self.file.schema == "IFC2X3" or self.settings["offset"] != 0:
            position = self.file.createIfcAxis2Placement3D(
                self.file.createIfcCartesianPoint((0.0, 0.0, self.convert_si_to_unit(self.settings["offset"]))),
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
