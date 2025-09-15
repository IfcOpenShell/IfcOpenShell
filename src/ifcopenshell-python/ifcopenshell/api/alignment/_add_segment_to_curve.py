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
import ifcopenshell.api
import ifcopenshell.api.alignment
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.ifcopenshell_wrapper as ifcopenshell_wrapper
import numpy as np
from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._update_curve_segment_transition_code import _update_curve_segment_transition_code
from ifcopenshell.api.alignment._map_alignment_horizontal_segment import _map_alignment_horizontal_segment
from ifcopenshell.api.alignment._map_alignment_vertical_segment import _map_alignment_vertical_segment
from ifcopenshell.api.alignment._map_alignment_cant_segment import _map_alignment_cant_segment


def _add_curve_segment_to_composite_curve(
    file: ifcopenshell.file, curve_segment: entity_instance, composite_curve: entity_instance
):
    if 0 < len(curve_segment.UsingCurves):
        raise TypeError("IfcCurveSegment cannot belong to other curves")

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
        zero_length_segment = (
            composite_curve.Segments[-1]
            if ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)
            else None
        )
        prev_segment = None

        if zero_length_segment and 1 < len(composite_curve.Segments):
            prev_segment = composite_curve.Segments[-2]
        elif zero_length_segment == None:
            prev_segment = composite_curve.Segments[-1]

        curve_segment.Transition = "CONTINUOUS"

        segments = composite_curve.Segments[0:-1]
        if zero_length_segment:
            segments += (
                curve_segment,
                zero_length_segment,
            )
            composite_curve.Segments = []
            composite_curve.Segments += segments
        else:
            composite_curve.Segments += (curve_segment,)

        if prev_segment:
            _update_curve_segment_transition_code(prev_segment, curve_segment)

        if zero_length_segment:
            settings = ifcopenshell.geom.settings()
            segment_fn = ifcopenshell_wrapper.map_shape(settings, curve_segment.wrapped_data)
            segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
            e = segment_evaluator.evaluate(segment_fn.end())
            end = np.array(e)
            unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
            x = float(end[0, 3]) / unit_scale
            y = float(end[1, 3]) / unit_scale
            dx = float(end[0, 0])
            dy = float(end[1, 0])

            # assume IfcAxis2Placement2D
            zero_length_segment.Placement.Location.Coordinates = (x, y)
            zero_length_segment.Placement.RefDirection.DirectionRatios = (dx, dy)

            _update_curve_segment_transition_code(curve_segment, zero_length_segment)


def _add_segment_to_curve(file: ifcopenshell.file, segment: entity_instance, curve: entity_instance) -> None:
    """
    Creates an IfcCurveSegment from the IfcAlignmentSegment and adds it to the representation curve. The IfcCurveSegment is added
    at the end of the curve, but before the manditory zero length segment. The IfcCurveSegment.Transition for the segment
    that preceeds the new segment is updated.

    :param segment: The segment to be added to the curve
    :param curve: The representation curve receiving the segment
    :return: None
    """
    expected_types = ["IfcAlignmentSegment"]
    if not segment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{segment.is_a()}"
        )

    if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment") and not curve.is_a("IfcCompositeCurve"):
        raise TypeError(f"Expected to see IfcCompositeCurve, instead received '{curve.is_a()}'.")
    elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment") and not curve.is_a("IfcGradientCurve"):
        raise TypeError(f"Expected to see IfcGradientCurve, instead received '{curve.is_a()}'.")
    elif segment.DesignParameters.is_a("IfcAlignmentCantSegment") and not curve.is_a("IfcSegmentedReferenceCurve"):
        raise TypeError(f"Expected to see IfcSegmentedReferenceCurve, instead received '{curve.is_a()}'.")

    expected_type = "IfcCompositeCurve"
    if not curve.is_a(expected_type):
        raise TypeError(f"Expected to see {expected_type}, instead received {curve.is_a()}.")

    # map the IfcAlignmentSegment to an IfcCurveSegment (or two in the case of helmert curves)
    if segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        mapped_segments = _map_alignment_horizontal_segment(file, segment)
    elif segment.DesignParameters.is_a("IfcAlignmentVerticalSegment"):
        mapped_segments = _map_alignment_vertical_segment(file, segment)
    elif segment.DesignParameters.is_a("IfcAlignmentCantSegment"):
        cant_layout = segment.Nests[0].RelatingObject
        mapped_segments = _map_alignment_cant_segment(file, segment, cant_layout.RailHeadDistance)
    else:
        assert False

    for mapped_segment in mapped_segments:
        if mapped_segment:
            _add_curve_segment_to_composite_curve(file, mapped_segment, curve)
