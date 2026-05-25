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

import numpy as np

import ifcopenshell
import ifcopenshell.api.alignment
from ifcopenshell.api.alignment.update_fallback_position import update_fallback_position
import ifcopenshell.api.pset
import ifcopenshell.geom
import ifcopenshell.guid
import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell import entity_instance, ifcopenshell_wrapper


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
    if basis_curve and basis_curve.is_a("IfcCompositeCurve") and 0 < len(basis_curve.Segments):
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

        update_fallback_position(file, object_placement)
    else:
        object_placement = file.createIfcLocalPlacement(
            PlacementRelTo=None,
            RelativePlacement=file.createIfcAxis2Placement2D(
                Location=file.createIfcCartesianPoint(alignment.ObjectPlacement.RelativePlacement.Location.Coordinates)
            ),
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
    if nest is None:
        nest = file.createIfcRelNests(
            GlobalId=ifcopenshell.guid.new(), RelatingObject=alignment, RelatedObjects=(referent,)
        )
    else:
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
