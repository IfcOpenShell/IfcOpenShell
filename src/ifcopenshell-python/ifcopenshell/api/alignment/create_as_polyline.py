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
import ifcopenshell.api.aggregate
import ifcopenshell.api.alignment
import ifcopenshell.api.nest
import ifcopenshell.util.alignment

from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._create_polyline_representation import _create_polyline_representation

import math
from collections.abc import Sequence


def _create_layout(file: ifcopenshell.file, alignment: entity_instance, points: Sequence[entity_instance]):
    """
    I don't believe it is required for polylines, but the validation serivce gives an error if the alignment doesn't have a layout
    """
    include_vertical = False if points[0].Dim == 2 else True

    alignment_layouts = []

    alignment_layouts.append(file.createIfcAlignmentHorizontal(GlobalId=ifcopenshell.guid.new()))

    if include_vertical:
        alignment_layouts.append(file.createIfcAlignmentVertical(GlobalId=ifcopenshell.guid.new()))

    ifcopenshell.api.nest.assign_object(file, related_objects=alignment_layouts, relating_object=alignment)

    start_dist_along = 0.0
    for p1, p2 in zip(points, points[1:]):
        x1, y1, z1 = p1.Coordinates
        x2, y2, z2 = p2.Coordinates
        dir = math.atan2(y2 - y1, x2 - x1)
        gradient = (z2 - z1) / (x2 - x1)
        length = math.sqrt(math.pow((x2 - x1), 2.0) + math.pow((y2 - y1), 2.0))

        hsegment = file.createIfcAlignmentSegment(
            ifcopenshell.guid.new(),
            DesignParameters=file.createIfcAlignmentHorizontalSegment(
                StartPoint=p1,
                StartDirection=dir,
                StartRadiusOfCurvature=0.0,
                EndRadiusOfCurvature=0.0,
                SegmentLength=length,
                PredefinedType="LINE",
            ),
        )

        ifcopenshell.api.nest.assign_object(file, related_objects=[hsegment], relating_object=alignment_layouts[0])

        if include_vertical:
            vsegment = file.createIfcAlignmentSegment(
                ifcopenshell.guid.new(),
                DesignParameters=file.createIfcAlignmentVerticalSegment(
                    StartDistAlong=start_dist_along,
                    HorizontalLength=length,
                    StartHeight=z1,
                    StartGradient=gradient,
                    EndGradient=gradient,
                    PredefinedType="CONSTANTGRADIENT",
                ),
            )

            ifcopenshell.api.nest.assign_object(file, related_objects=[vsegment], relating_object=alignment_layouts[1])

        start_dist_along += length

    # zero length segment
    hsegment = file.createIfcAlignmentSegment(
        ifcopenshell.guid.new(),
        DesignParameters=file.createIfcAlignmentHorizontalSegment(
            StartPoint=points[-1],
            StartDirection=dir,
            StartRadiusOfCurvature=0.0,
            EndRadiusOfCurvature=0.0,
            SegmentLength=0.0,
            PredefinedType="LINE",
        ),
    )

    ifcopenshell.api.nest.assign_object(file, related_objects=[hsegment], relating_object=alignment_layouts[0])

    if include_vertical:
        vsegment = file.createIfcAlignmentSegment(
            ifcopenshell.guid.new(),
            DesignParameters=file.createIfcAlignmentVerticalSegment(
                StartDistAlong=start_dist_along,
                HorizontalLength=0.0,
                StartHeight=points[-1].Coordinates[-1],
                StartGradient=gradient,
                EndGradient=gradient,
                PredefinedType="CONSTANTGRADIENT",
            ),
        )

        ifcopenshell.api.nest.assign_object(file, related_objects=[vsegment], relating_object=alignment_layouts[1])


def create_as_polyline(
    file: ifcopenshell.file,
    name: str,
    points: Sequence[entity_instance],
    start_station: float = 0.0,
) -> entity_instance:
    """
    Creates a new IfcAlignment with an IfcPolyline representation.

    The IfcAlignment is aggreated to IfcProject

    :param file:
    :param name: name assigned to IfcAlignment.Name
    :param points: sequence of points defining the polyline
    :param start_station: station value at the start of the alignment
    :return: Returns an IfcAlignment
    """
    alignment = file.createIfcAlignment(
        GlobalId=ifcopenshell.guid.new(),
        Name=name,
    )

    _create_polyline_representation(file, alignment, points)

    # define stationing
    name = ifcopenshell.util.alignment.station_as_string(file, start_station)
    referent = ifcopenshell.api.alignment.add_stationing_referent(file, alignment, 0.0, start_station, name, alignment)

    # IFC 4.1.4.1.1 Alignment Aggregation To Project
    project = file.by_type("IfcProject")[0]
    if project:
        ifcopenshell.api.aggregate.assign_object(file, products=[alignment], relating_object=project)

    return alignment
