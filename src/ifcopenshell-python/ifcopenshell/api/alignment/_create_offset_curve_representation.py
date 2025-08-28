# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2025 Thomas Krijnen <thomas@aecgeeks.com>
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

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.api.geometry
from ifcopenshell import entity_instance

import math
from collections.abc import Sequence


def _create_offset_curve_representation(
    file: ifcopenshell.file, alignment: entity_instance, offsets: Sequence[entity_instance]
) -> None:
    """
    Create geometric representation for the alignment based on an IfcPolyline

    :param alignment: The alignment for which the representation is being created
    :return: None
    """
    expected_type = "IfcAlignment"
    if not alignment.is_a(expected_type):
        raise TypeError(f"Expected {expected_type} but got {alignment.is_a()}")

    axis_geom_subcontext = ifcopenshell.api.alignment.get_axis_subcontext(file)

    basis_curve = offsets[0].BasisCurve  # IfcPointByDistanceExpression.BasisCurve

    if basis_curve.Dim == 3:
        placement = file.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=file.createIfcAxis2Placement3D(
                Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0, 0.0))
            ),
        )
        representation_type = "Curve3D"
    else:
        placement = file.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0))
            ),
        )
        representation_type = "Curve2D"

    curve = file.createIfcOffsetCurveByDistances(BasisCurve=basis_curve, OffsetValues=offsets)

    representation = file.createIfcShapeRepresentation(
        ContextOfItems=axis_geom_subcontext,
        RepresentationIdentifier="Axis",
        RepresentationType=representation_type,
        Items=(curve,),
    )

    alignment.ObjectPlacement = placement
    ifcopenshell.api.geometry.assign_representation(file, alignment, representation)
