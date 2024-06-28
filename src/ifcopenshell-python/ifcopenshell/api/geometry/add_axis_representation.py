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
from typing import Union

COORD = Union[tuple[float, float], tuple[float, float, float]]


def add_axis_representation(
    file: ifcopenshell.file, context: ifcopenshell.entity_instance, axis: tuple[COORD, COORD]
) -> ifcopenshell.entity_instance:
    """Adds a new axis representation

    Certain objects are typically "axis-based", such as walls, beams,
    and columns. This means you can represent them abstractly by simply
    drawing a single line either in 2D (such as for walls) or 3D (for beams
    and columns). Humans can understand this axis-based representation as
    being a simplification of a layered extrusion or a profile that is being
    extruded along that axis and joined to other elements.

    Using an axis-based representation makes it easy for users and computers
    to analyse connectivity and spatial relationships, as well as makes it
    easy to parametrically edit these objects by simply stretching the start
    or end of the axis.

    For now, only simple straight line axes are supported, represented by a
    start and end coordinate. The order is important. For walls, the start
    must be at the minimum local X ordinate, and the end at the maximum
    local X ordinate. For beams and columns, the start is at the minimum
    local Z ordinate, and the end of the maximum local Z ordinate. The first
    coordinate is the "start" and the second coordinate is the "end". This
    stat and end is then used to determine any parametric junctions with
    other elements.

    Using an axis-representation is optional, but highly recommended for
    "standard" representations of walls, beams, columns, and other
    structural members. A rule of thumb is that if you can draw it as a line
    on paper, you can probably represent it using an axis.

    :param context: The IfcGeometricRepresentationContext that the
        representation is part of. This must be either a
        Model/Axis/GRAPH_VIEW (3D) or Plan/Axis/GRAPH_VIEW (2D).
    :type context: ifcopenshell.entity_instance
    :param axis: The axis, as a list of two coordinates, the coordinates
        being either a list of 2 or 3 float coordinates depending on whether
        the axis is 2D or 3D.
    :type axis: list[list[float]]
    :return: The newly created IfcShapeRepresentation entity
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        context = ifcopenshell.util.representation.get_context(model, "Plan", "Axis", "GRAPH_VIEW")
        axis = ifcopenshell.api.geometry.add_axis_representation(model,
            context=context, axis=[(0.0, 0.0), (1.0, 0.0)])
    """
    usecase = Usecase()
    usecase.file = file
    usecase.settings = {
        "context": context,
        "axis": axis or [],
    }
    return usecase.execute()


class Usecase:
    def execute(self):
        self.settings["unit_scale"] = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        is_2d = len(self.settings["axis"][0]) == 2
        points = [self.convert_si_to_unit(p) for p in self.settings["axis"]]
        if self.file.schema == "IFC2X3":
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
        else:
            if is_2d:
                curve = self.file.createIfcIndexedPolyCurve(
                    self.file.createIfcCartesianPointList2D(points), None, False
                )
            else:
                curve = self.file.createIfcIndexedPolyCurve(
                    self.file.createIfcCartesianPointList3D(points), None, False
                )
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Curve2D" if is_2d else "Curve3D",
            [curve],
        )

    def convert_si_to_unit(self, co):
        if isinstance(co, (tuple, list)):
            return [self.convert_si_to_unit(o) for o in co]
        return co / self.settings["unit_scale"]
