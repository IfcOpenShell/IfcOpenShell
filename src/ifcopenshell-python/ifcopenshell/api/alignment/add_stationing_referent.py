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
import ifcopenshell.api.nest
import ifcopenshell.api.pset
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell import entity_instance
from ifcopenshell import ifcopenshell_wrapper
import numpy as np


def add_stationing_referent(
    file: ifcopenshell.file,
    alignment: entity_instance,
    distance_along: float,
    station: float,
    name: str,
    positioned_product: entity_instance,
) -> entity_instance:
    """
    Adds an IfcReferent to the alignment with the Pset_Stationing property set.

    :param alignment: the alignment to receive the referent
    :param distance_along: distance along the alignment basis curve
    :param station: station value
    :param name: name to assign to IfcReferent.Name, typically a stringized version of the station value
    :param positioned_product: the product whose position is informed by the referent
    :return: referent

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]
        ifcopenshell.api.alignment.add_stationing_referent(model,alignment=alignment,distance_along=0.0,station=100.0)
    """

    basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)

    object_placement = None
    representation = None
    if basis_curve:
        object_placement = file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(distance_along),
                    OffsetLateral=None,
                    OffsetVertical=None,
                    OffsetLongitudinal=None,
                    BasisCurve=basis_curve,
                )
            ),
        )

        is_valid_curve = True
        if basis_curve.is_a("IfcCompositeCurve") and len(basis_curve.Segments) == 0:
            is_valid_curve = False
        if basis_curve.is_a("IfcPolyline") and len(basis_curve.Points) < 2:
            is_valid_curve = False
        elif basis_curve.is_a("IfcIndexedPolyCurve") and len(basis_curve.Points.CoordList) < 2:
            is_valid_curve = False

        if is_valid_curve:
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

            settings = ifcopenshell.geom.settings()
            fn = ifcopenshell_wrapper.map_shape(settings, basis_curve.wrapped_data)

            if basis_curve.is_a("IfcPolyline") or basis_curve.is_a("IfcIndexedPolyCurve"):
                fn = ifcopenshell_wrapper.convert_loop_to_function_item(fn)

            evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, fn)

            p = evaluator.evaluate(distance_along * unit_scale)
            p = np.array(p)

            x = float(p[0, 3]) / unit_scale
            y = float(p[1, 3]) / unit_scale
            z = float(p[2, 3]) / unit_scale

            rx = float(p[0, 0])
            ry = float(p[1, 0])
            rz = float(p[2, 0])

            ax = float(p[0, 2])
            ay = float(p[1, 2])
            az = float(p[2, 2])
        else:
            x = 0.0
            y = 0.0
            z = 0.0
            rx = 1.0
            ry = 0.0
            rz = 0.0
            ax = 0.0
            ay = 0.0
            az = 1.0

        object_placement.CartesianPosition = file.createIfcAxis2Placement3D(
            Location=file.createIfcCartesianPoint((x, y, z)),
            Axis=file.createIfcDirection((ax, ay, az)),
            RefDirection=file.createIfcDirection((rx, ry, rz)),
        )

    # this commented out code is what you would do to add a geometric representation of the referent
    # the example is a circle. a better way would be to pass a representation into the function
    #    representation = file.create_entity(
    #        name="IfcCircle",
    #        position=file.createIfcAxis2Placement2D(Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0)),
    #        radius=1.0)
    #    )

    # create referent for the station
    referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=name,
        Description=None,
        ObjectType=None,
        ObjectPlacement=object_placement,
        Representation=representation,
        PredefinedType="STATION",
    )
    pset_stationing = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties={"Station": station})

    nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
    nest.RelatedObjects += (referent,)

    nest.RelatedObjects = sorted(
        nest.RelatedObjects, key=lambda x: ifcopenshell.util.element.get_pset(x, name="Pset_Stationing", prop="Station")
    )

    if len(referent.Positions) == 0:
        rel_positions = file.createIfcRelPositions(
            GlobalId=ifcopenshell.guid.new(),
            RelatingPositioningElement=referent,
            RelatedProducts=[
                positioned_product,
            ],
        )
    else:
        referent.Positions[0].RelatedProducts += (positioned_product,)

    return referent
