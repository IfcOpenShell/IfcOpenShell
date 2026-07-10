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

from typing import Union
import numpy as np

import ifcopenshell
import ifcopenshell.api.alignment
import ifcopenshell.geom
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint
from ifcopenshell.api.alignment._update_zero_length_segment_placement import _update_zero_length_segment_placement

from ifcopenshell.api.alignment._map_alignment_cant_segment import (
    _map_alignment_cant_segment,
)
from ifcopenshell.api.alignment._map_alignment_horizontal_segment import (
    _map_alignment_horizontal_segment,
)
from ifcopenshell.api.alignment._map_alignment_vertical_segment import (
    _map_alignment_vertical_segment,
)
from ifcopenshell.api.alignment._update_curve_segment_transition_code import (
    _update_curve_segment_transition_code,
)


def _add_curve_segment_to_composite_curve(
    file: ifcopenshell.file,
    layout_segment: entity_instance,
    curve_segment: entity_instance,
    composite_curve: entity_instance,
) -> Union[np.array, None]:
    """
    Adds a curve segment to a composite curve and returns the end point of the added segment.

    :param file: The IFC file
    :param layout_segment: The layout segment
    :param curve_segment: The curve segment to be added
    :param composite_curve: The composite curve to which the segment will be added
    :return: The end point of the added segment or None if an error occurs
    """
    if 0 < len(curve_segment.UsingCurves):
        raise TypeError("IfcCurveSegment cannot belong to other curves")

    prev_segment = None
    zero_length_segment = None

    settings = ifcopenshell.geom.settings()
    if composite_curve.Segments == None or 0 == len(composite_curve.Segments):
        # this is the first segment so just add it
        if composite_curve.Segments == None:
            composite_curve.Segments = []

        # the last segment is always discontinuous
        curve_segment.Transition = "DISCONTINUOUS"

        composite_curve.Segments += (curve_segment,)
        assert len(curve_segment.UsingCurves) == 1
    else:
        # not the first segment, so get the zero_length segment (if it exists)
        zero_length_segment = (
            composite_curve.Segments[-1]
            if ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)
            else None
        )

        # get the previous segment, which is either the on preceeding the zero length segment (if it exists) or
        # the last curve segment if there is no zero length segment.
        # This segment's transition code will need to be updated to match the new curve segment.
        if zero_length_segment and 1 < len(composite_curve.Segments):
            prev_segment = composite_curve.Segments[-2]
        elif zero_length_segment == None:
            prev_segment = composite_curve.Segments[-1]

        # IfcCompositeCurve is supposed to be comprised of continuous segments
        curve_segment.Transition = "DISCONTINUOUS"

        # get a list of all but the last segment (skips the zero length segment, if it exists)
        segments = composite_curve.Segments[0:-1]
        if zero_length_segment:
            # if there is a zero length segment, need to append new curve_segment and the zero length segment to the array
            # them update the composite curve segments with the new array
            segments += (
                curve_segment,
                zero_length_segment,
            )
            composite_curve.Segments = []
            composite_curve.Segments += segments
        else:
            # if there is no zero length segment, we can just append the new curve segment to the existing array of segments
            composite_curve.Segments += (curve_segment,)

    if prev_segment:
        _update_curve_segment_transition_code(prev_segment, curve_segment)

    end_point = _get_segment_endpoint(file, layout_segment)
    if zero_length_segment:
        _update_zero_length_segment_placement(file, zero_length_segment, end_point)
        _update_curve_segment_transition_code(curve_segment, zero_length_segment)

    return end_point


def _add_segment_to_curve(
    file: ifcopenshell.file, layout_segment: entity_instance, curve: entity_instance
) -> Union[np.array, None]:
    """
    Creates an IfcCurveSegment from the IfcAlignmentSegment and adds it to the representation curve. The IfcCurveSegment is added
    at the end of the curve, but before the manditory zero length segment. The IfcCurveSegment.Transition for the segment
    that preceeds the new segment is updated.

    :param segment: The segment to be added to the curve
    :param curve: The representation curve receiving the segment
    :return: None
    """
    expected_types = ["IfcAlignmentSegment"]
    if not layout_segment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{layout_segment.is_a()}"
        )

    if layout_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment") and not curve.is_a("IfcCompositeCurve"):
        raise TypeError(f"Expected to see IfcCompositeCurve, instead received '{curve.is_a()}'.")
    elif layout_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment") and not curve.is_a("IfcGradientCurve"):
        raise TypeError(f"Expected to see IfcGradientCurve, instead received '{curve.is_a()}'.")
    elif layout_segment.DesignParameters.is_a("IfcAlignmentCantSegment") and not curve.is_a(
        "IfcSegmentedReferenceCurve"
    ):
        raise TypeError(f"Expected to see IfcSegmentedReferenceCurve, instead received '{curve.is_a()}'.")

    expected_type = "IfcCompositeCurve"
    if not curve.is_a(expected_type):
        raise TypeError(f"Expected to see {expected_type}, instead received {curve.is_a()}.")

    # map the IfcAlignmentSegment to an IfcCurveSegment (or two in the case of helmert curves)
    if layout_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        mapped_segments = _map_alignment_horizontal_segment(file, layout_segment)
    elif layout_segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        mapped_segments = _map_alignment_vertical_segment(file, layout_segment)
    elif layout_segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
        cant_layout = layout_segment.Nests[0].RelatingObject
        mapped_segments = _map_alignment_cant_segment(file, layout_segment, cant_layout.RailHeadDistance)
    else:
        assert False

    for mapped_segment in mapped_segments:
        if mapped_segment:
            end_point = _add_curve_segment_to_composite_curve(file, layout_segment, mapped_segment, curve)

    return end_point
