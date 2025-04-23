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
import ifcopenshell.guid
from ifcopenshell import entity_instance


def add_stationing_to_alignment(file: ifcopenshell.file, alignment: entity_instance, start_station: float) -> None:
    """
    Adds stationing to an alignment by creating an IfcReferent with the Pset_Stationing property set to establish the stationing at the start of the alignment.
    Note - this function assumes the stationing has not been previously defined

    :param alignment: the alignment to be stationed
    :param start_station: station value at the start of the alignment
    :return: None

    Example:

    .. code:: python

        alignment = model.by_type("IfcAlignment")[0]
        ifcopenshell.api.alignment.add_stationing_to_alignment(model,alignment=alignment,start_station=100.0)
    """
    # this commented out code is what you would do to add a geometric representation of the referent
    # the example is a circle. a better way would be to pass a representation into the function
    object_placement = None
    representation = None
    # basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
    # if basis_curve:
    #    object_placement = file.createIfcLinearPlacement(
    #        RelativePlacement=file.createIfcAxis2PlacementLinear(
    #            Location=file.createIfcPointByDistanceExpression(
    #                DistanceAlong=file.createIfcLengthMeasure(0.0),
    #                OffsetLateral=None,
    #                OffsetVertical=None,
    #                OffsetLongitudinal=None,
    #                BasisCurve=basis_curve,
    #            )
    #        ),
    #        CartesianPosition=None,
    #    )
    #    representation = file.create_entity(
    #        name="IfcCircle",
    #        position=file.createIfcAxis2Placement2D(Location=file.createIfcCartesianPoint(Coordinates=(0.0, 0.0)),
    #        radius=1.0)
    #    )

    # create referent for start station
    start_referent = file.createIfcReferent(
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=None,
        Name=ifcopenshell.util.stationing.station_as_string(start_station),
        Description=None,
        ObjectType=None,
        ObjectPlacement=object_placement,
        Representation=representation,
        PredefinedType="STATION",
    )
    pset_stationing = ifcopenshell.api.pset.add_pset(file, product=start_referent, name="Pset_Stationing")
    ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties={"Station": start_station})
    ifcopenshell.api.nest.assign_object(file, related_objects=[start_referent], relating_object=alignment)
