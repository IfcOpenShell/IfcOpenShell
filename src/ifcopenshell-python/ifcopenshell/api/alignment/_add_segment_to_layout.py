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
import ifcopenshell.util.alignment
import ifcopenshell.util.unit
from ifcopenshell import ifcopenshell_wrapper
import numpy as np
import math
from ifcopenshell import entity_instance
from collections.abc import Sequence

from ifcopenshell.api.alignment._add_segment_to_curve import _add_segment_to_curve
from ifcopenshell.api.alignment._get_segment_start_point_label import _get_segment_start_point_label


def _add_segment_to_layout(file: ifcopenshell.file, layout: entity_instance, segment: entity_instance) -> None:
    """
    Adds an IfcAlignmentSegment to a layout alignment (IfcAlignmentHorizontal/Vertical/Cant). This segment is added at the end
    of the layout, before the manditory zero length segment. An IfcCurveSegment is created for the corresponding geometric representation.

    :param layout: The layout alignment
    :param segment: The segment to be appended
    :return: None
    """

    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if not (segment.is_a("IfcAlignmentSegment")):
        raise TypeError(f"Expected to see IfcAlignmentSegment, instead received {segment.is_a()}.")

    curve = ifcopenshell.api.alignment.get_layout_curve(layout)

    # add the new segment to the layout
    ifcopenshell.api.nest.assign_object(file, related_objects=[segment], relating_object=layout)

    # segment is attached at the end, but this is after the zero length segment
    # swap the last two segments
    ifcopenshell.api.nest.reorder_nesting(file, segment, -1, -1)

    if curve:
        # add the new segment to the geometric representation curve
        _add_segment_to_curve(file, segment, curve)

        # gather information to:
        # (1) add a referent at the start of this segment
        # (2) update the name of the zero length segment's referent

        # get the distance along the alignment to the start of the new segment
        dist_along = 0.0
        if layout.is_a("IfcAlignmentHorizontal"):
            for nest in layout.IsNestedBy:
                for seg in nest.RelatedObjects:
                    if seg.is_a("IfcAlignmentSegment"):
                        dist_along += seg.DesignParameters.SegmentLength

            # the length of the current segment is in dist_along, so subtract it out
            dist_along -= segment.DesignParameters.SegmentLength
        else:
            dist_along = segment.DesignParameters.StartDistAlong

        # get the station of the start of the segment
        alignment = ifcopenshell.api.alignment.get_alignment(layout)
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
        station = start_station + dist_along

        # update the zero length layout segment
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)

        segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
        zero_length_segment = segment_nest.RelatedObjects[-1]
        mapped_segments = ifcopenshell.api.alignment.get_mapped_segments(segment)
        mapped_segment = mapped_segments[0] if mapped_segments[1] == None else mapped_segments[1]

        # compute the end point matrix
        settings = ifcopenshell.geom.settings()
        segment_fn = ifcopenshell_wrapper.map_shape(settings, mapped_segment.wrapped_data)
        segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
        e = segment_evaluator.evaluate(segment_fn.end())
        end = np.array(e)

        # update the zero length segment semantic representation parameters
        if zero_length_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
            x = float(end[0, 3]) / unit_scale
            y = float(end[1, 3]) / unit_scale
            dx = float(end[0, 0])
            dy = float(end[1, 0])
            zero_length_segment.DesignParameters.StartPoint.Coordinates = (x, y)
            zero_length_segment.DesignParameters.StartDirection = dy / dx
        elif zero_length_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
            y = float(end[1, 3]) / unit_scale
            zero_length_segment.DesignParameters.StartHeight = y
            dx = float(end[0, 0])
            dy = float(end[1, 0])
            zero_length_segment.DesignParameters.StartGradient = dy / dx
            zero_length_segment.DesignParameters.EndGradient = zero_length_segment.DesignParameters.StartGradient
        else:
            z = float(end[2, 3]) / unit_scale
            dx = float(end[0, 1])
            dy = float(end[1, 1])
            dz = float(end[2, 1])
            ds = math.sqrt(dx * dx + dy * dy)
            slope = dz / ds
            railhead = layout.RailHeadDistance

            zero_length_segment.DesignParameters.StartCantLeft = z + slope * railhead / 2.0
            zero_length_segment.DesignParameters.StartCantRight = z - slope * railhead / 2.0

        # updated the referent's name because the referent is now at a new station
        start_dist_along = 0.0
        if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
            start_dist_along = dist_along + segment.DesignParameters.SegmentLength
        else:
            start_dist_along = segment.DesignParameters.StartDistAlong + segment.DesignParameters.HorizontalLength
            zero_length_segment.DesignParameters.StartDistAlong = start_dist_along

        end_referent = zero_length_segment.PositionedRelativeTo[0].RelatingPositioningElement
        end_referent.Name = f"{_get_segment_start_point_label(zero_length_segment,None)} ({ifcopenshell.util.alignment.station_as_string(file,start_station+start_dist_along)})"

        # update the referent's geometric representation's location
        end_referent.ObjectPlacement.RelativePlacement.Location.DistanceAlong.wrappedValue = start_dist_along
        settings = ifcopenshell.geom.settings()
        basis_curve = ifcopenshell.api.alignment.get_basis_curve(alignment)
        curve_fn = ifcopenshell_wrapper.map_shape(settings, basis_curve.wrapped_data)
        curve_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, curve_fn)
        p = curve_evaluator.evaluate(start_dist_along * unit_scale)
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

        end_referent.ObjectPlacement.CartesianPosition.Location.Coordinates = (x, y, z)
        end_referent.ObjectPlacement.CartesianPosition.Axis.DirectionRatios = (ax, ay, az)
        end_referent.ObjectPlacement.CartesianPosition.RefDirection.DirectionRatios = (rx, ry, rz)

        start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
        end_referent_station = start_station + start_dist_along
        pset_stationing = ifcopenshell.api.pset.add_pset(file, product=end_referent, name="Pset_Stationing")
        ifcopenshell.api.pset.edit_pset(file, pset=pset_stationing, properties={"Station": end_referent_station})

        # create the start of segment referent

        # get the previous segment. Working from the end of the basis curve, -1 is zero length segment
        # -2 is the newly added segment, so -3 is the segment occuring just before the newly added segment
        prev_segment = segment_nest.RelatedObjects[-3] if 2 < len(segment_nest.RelatedObjects) else None
        name = f"{_get_segment_start_point_label(prev_segment,segment)} ({ifcopenshell.util.alignment.station_as_string(file,station)})"
        referent = ifcopenshell.api.alignment.add_stationing_referent(
            file, alignment, distance_along=dist_along, station=station, name=name, positioned_product=segment
        )

        if len(curve.Segments) == 2 and layout.is_a("IfcAlignmentHorizontal"):
            # this is the first real segment in the horizontal alignment
            # update the location of the alignment's stationing referent
            alignment = ifcopenshell.api.alignment.get_alignment(layout)
            ref_nest = ifcopenshell.api.alignment.get_referent_nest(file, alignment)
            stationing_referent = ref_nest.RelatedObjects[0]
            p = curve_evaluator.evaluate(
                stationing_referent.ObjectPlacement.RelativePlacement.Location.DistanceAlong.wrappedValue
            )
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

            stationing_referent.ObjectPlacement.CartesianPosition.Location.Coordinates = (x, y, z)
            stationing_referent.ObjectPlacement.CartesianPosition.Axis.DirectionRatios = (ax, ay, az)
            stationing_referent.ObjectPlacement.CartesianPosition.RefDirection.DirectionRatios = (rx, ry, rz)
