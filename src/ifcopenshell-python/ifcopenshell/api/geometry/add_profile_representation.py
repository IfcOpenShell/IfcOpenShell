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
import ifcopenshell.util.element
import ifcopenshell.util.shape
import ifcopenshell.util.unit
from ifcopenshell.util.data import Clipping
from typing import Any, Union, Optional, Literal, get_args

VECTOR_3D = tuple[float, float, float]
CardinalPointNumeric = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
CardinalPointString = Literal[
    "bottom left",
    "bottom centre",
    "bottom right",
    "mid-depth left",
    "mid-depth centre",
    "mid-depth right",
    "top left",
    "top centre",
    "top right",
    "geometric centroid",
    "bottom in line with the geometric centroid",
    "left in line with the geometric centroid",
    "right in line with the geometric centroid",
    "top in line with the geometric centroid",
    "shear centre",
    "bottom in line with the shear centre",
    "left in line with the shear centre",
    "right in line with the shear centre",
    "top in line with the shear centre",
]
CARDINAL_POINT_VALUES: tuple[CardinalPointString, ...] = get_args(CardinalPointString)
CardinalPoint = Union[CardinalPointNumeric, CardinalPointString]


def add_profile_representation(
    file: ifcopenshell.file,
    context: ifcopenshell.entity_instance,
    profile: ifcopenshell.entity_instance,
    depth: float = 1.0,
    # TODO: None makes more sense as default value?
    cardinal_point: Union[CardinalPoint, None] = 5,
    clippings: Optional[list[Union[Clipping, dict[str, Any]]]] = None,
    placement_zx_axes: tuple[Union[VECTOR_3D, None], Union[VECTOR_3D, None]] = (None, None),
) -> ifcopenshell.entity_instance:
    """Add profile representation.

    :param context: The IfcGeometricRepresentationContext for the representation,
        only Model/Body/MODEL_VIEW type of representations are currently supported.
    :param profile: The IfcProfileDef to extrude.
    :param depth: The depth of the extrusion in meters.
    :param cardinal_point: The cardinal point of the profile.
    :param clippings: A list of planes that define clipping half space solids.
        Planes are defined either by Clipping objects
        or by dictionaries of arguments for `Clipping.parse`.
    :param placement_zx_axes: A tuple of two vectors that define the placement of the profile.
        The first vector is the Z axis, the second vector is the X axis.
    :return: IfcShapeRepresentation.
    """
    usecase = Usecase()
    usecase.file = file
    clippings = clippings if clippings is not None else []
    return usecase.execute(context, profile, depth, cardinal_point, clippings, placement_zx_axes)


class Usecase:
    file: ifcopenshell.file
    clippings: list[Clipping]

    def execute(
        self,
        context: ifcopenshell.entity_instance,
        profile: ifcopenshell.entity_instance,
        depth: float,
        cardinal_point: Union[CardinalPoint, None],
        clippings: list[Union[Clipping, dict[str, Any]]],
        placement_zx_axes: tuple[Union[VECTOR_3D, None], Union[VECTOR_3D, None]],
    ) -> ifcopenshell.entity_instance:
        if isinstance(cardinal_point, int):
            cardinal_point = CARDINAL_POINT_VALUES[cardinal_point - 1]

        self.cardinal_point = cardinal_point
        self.profile = profile
        self.clippings = [Clipping.parse(c) for c in clippings]
        self.depth = depth
        self.placement_zx_axes = placement_zx_axes
        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        return self.file.create_entity(
            "IfcShapeRepresentation",
            context,
            context.ContextIdentifier,
            "Clipping" if self.clippings else "SweptSolid",
            [self.create_item()],
        )

    def create_item(self) -> ifcopenshell.entity_instance:
        point = self.get_point()
        placement = self.file.createIfcAxis2Placement3D(
            point,
            self.file.create_entity("IfcDirection", self.placement_zx_axes[0] or (0.0, 0.0, 1.0)),
            self.file.create_entity("IfcDirection", self.placement_zx_axes[1] or (1.0, 0.0, 0.0)),
        )
        extrusion = self.file.create_entity(
            "IfcExtrudedAreaSolid",
            self.profile,
            placement,
            self.file.createIfcDirection((0.0, 0.0, 1.0)),
            self.convert_si_to_unit(self.depth),
        )
        if self.clippings:
            return self.apply_clippings(extrusion)
        return extrusion

    def apply_clippings(self, first_operand: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        while self.clippings:
            clipping = self.clippings.pop()
            if isinstance(clipping, ifcopenshell.entity_instance):
                new = ifcopenshell.util.element.copy(self.file, clipping)
                new.FirstOperand = first_operand
                first_operand = new
            else:  # Clipping
                first_operand = clipping.apply(self.file, first_operand, self.unit_scale)
        return first_operand

    def convert_si_to_unit(self, co: float) -> float:
        return co / self.unit_scale

    def get_point(self) -> ifcopenshell.entity_instance:
        if not self.cardinal_point:
            return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        elif self.cardinal_point == "bottom left":
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, self.get_y() / 2, 0.0))
        elif self.cardinal_point == "bottom centre":
            return self.file.createIfcCartesianPoint((0.0, self.get_y() / 2, 0.0))
        elif self.cardinal_point == "bottom right":
            return self.file.createIfcCartesianPoint((self.get_x() / 2, self.get_y() / 2, 0.0))
        elif self.cardinal_point == "mid-depth left":
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, 0.0, 0.0))
        elif self.cardinal_point == "mid-depth centre":
            return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))
        elif self.cardinal_point == "mid-depth right":
            return self.file.createIfcCartesianPoint((self.get_x() / 2, 0.0, 0.0))
        elif self.cardinal_point == "top left":
            return self.file.createIfcCartesianPoint((-self.get_x() / 2, -self.get_y() / 2, 0.0))
        elif self.cardinal_point == "top centre":
            return self.file.createIfcCartesianPoint((0.0, -self.get_y() / 2, 0.0))
        elif self.cardinal_point == "top right":
            return self.file.createIfcCartesianPoint((self.get_x() / 2, -self.get_y() / 2, 0.0))
        # TODO other cardinal points
        return self.file.createIfcCartesianPoint((0.0, 0.0, 0.0))

    def get_x(self) -> float:
        if self.profile.is_a("IfcAsymmetricIShapeProfileDef"):
            return self.profile.OverallWidth
        elif self.profile.is_a("IfcCShapeProfileDef"):
            return self.profile.Width
        elif self.profile.is_a("IfcCircleProfileDef"):
            return self.profile.Radius * 2
        elif self.profile.is_a("IfcEllipseProfileDef"):
            return self.profile.SemiAxis1 * 2
        elif self.profile.is_a("IfcIShapeProfileDef"):
            return self.profile.OverallWidth
        elif self.profile.is_a("IfcLShapeProfileDef"):
            return self.profile.Width
        elif self.profile.is_a("IfcRectangleProfileDef"):
            return self.profile.XDim
        elif self.profile.is_a("IfcTShapeProfileDef"):
            return self.profile.FlangeWidth
        elif self.profile.is_a("IfcUShapeProfileDef"):
            return self.profile.FlangeWidth
        elif self.profile.is_a("IfcZShapeProfileDef"):
            return (self.profile.FlangeWidth * 2) - self.profile.WebThickness
        else:
            settings = ifcopenshell.geom.settings()
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            shape = ifcopenshell.geom.create_shape(settings, self.profile)
            return self.convert_si_to_unit(ifcopenshell.util.shape.get_x(shape))
        return 0.0

    def get_y(self) -> float:
        if self.profile.is_a("IfcAsymmetricIShapeProfileDef"):
            return self.profile.OverallDepth
        elif self.profile.is_a("IfcCShapeProfileDef"):
            return self.profile.Depth
        elif self.profile.is_a("IfcCircleProfileDef"):
            return self.profile.Radius * 2
        elif self.profile.is_a("IfcEllipseProfileDef"):
            return self.profile.SemiAxis2 * 2
        elif self.profile.is_a("IfcIShapeProfileDef"):
            return self.profile.OverallDepth
        elif self.profile.is_a("IfcLShapeProfileDef"):
            return self.profile.Depth
        elif self.profile.is_a("IfcRectangleProfileDef"):
            return self.profile.YDim
        elif self.profile.is_a("IfcTShapeProfileDef"):
            return self.profile.Depth
        elif self.profile.is_a("IfcUShapeProfileDef"):
            return self.profile.Depth
        elif self.profile.is_a("IfcZShapeProfileDef"):
            return self.profile.Depth
        else:
            settings = ifcopenshell.geom.settings()
            settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
            shape = ifcopenshell.geom.create_shape(settings, self.profile)
            return self.convert_si_to_unit(ifcopenshell.util.shape.get_y(shape))
        return 0.0
