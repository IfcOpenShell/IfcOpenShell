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

from typing import Optional

import ifcopenshell
import ifcopenshell.api.alignment
from ifcopenshell.api.alignment.update_fallback_position import update_fallback_position
import ifcopenshell.api.pset
import ifcopenshell.guid
import ifcopenshell.util.element
from ifcopenshell import entity_instance


def add_stationing_referent(
    file: ifcopenshell.file,
    name: str,
    alignment: entity_instance,
    distance_along: float,
    station: float,
    incoming_station: Optional[float] = None,
    on_basis_curve: Optional[bool] = None,
) -> entity_instance:
    """
    Adds an IfcReferent to the alignment that defines the stationing system.

    :param name: name to assign to IfcReferent.Name, typically a stringized version of the station value
    :param alignment: the alignment to receive the referent
    :param distance_along: distance along the alignment basis curve
    :param station: station value
    :param incoming_station: station value of the incoming segment, only set to specify a station equation
    :param on_basis_curve: whether the referent is positioned on the basis curve or the alignment curve, if None the function will default to the basis curve
    :return: referent

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]
        ifcopenshell.api.alignment.add_stationing_referent(model,name="1+00.0",alignment=alignment,distance_along=0.0,station=100.0)
    """

    if on_basis_curve is None:
        on_basis_curve = True

    curve = (
        ifcopenshell.api.alignment.get_basis_curve(alignment)
        if on_basis_curve
        else ifcopenshell.api.alignment.get_curve(alignment)
    )

    object_placement = None
    representation = None
    if curve and curve.is_a("IfcCompositeCurve") and 0 < len(curve.Segments):
        object_placement = file.createIfcLinearPlacement(
            RelativePlacement=file.createIfcAxis2PlacementLinear(
                Location=file.createIfcPointByDistanceExpression(
                    DistanceAlong=file.createIfcLengthMeasure(distance_along),
                    OffsetLateral=None,
                    OffsetVertical=None,
                    OffsetLongitudinal=None,
                    BasisCurve=curve,
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
    properties = {"Station": station}
    if incoming_station is not None:
        properties["IncomingStation"] = incoming_station

    pset_stationing = ifcopenshell.api.pset.add_pset(file, product=referent, name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties=properties)

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

    return referent
