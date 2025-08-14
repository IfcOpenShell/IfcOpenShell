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
from ifcopenshell import ifcopenshell_wrapper
import ifcopenshell.geom
from ifcopenshell import entity_instance
import numpy as np
import math


def get_curve_segment_transition_code(
    segment: entity_instance, next_segment: entity_instance, position_tolerance: float = 0.001
) -> str:
    """
    Returns the IfcCurveSegment.Transition of segment based on a comparison of
    the position, ref. direction, and curvature at the end of the segment and the start of next_segment.

    :param segment: segment for which the position curve is being being determined
    :param next_segment: next segment
    :param position_tolerance: tolerance used for evaluation positions. The default is 1mm
    :return: the transition code
    """
    expected_type = "IfcCurveSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{segment.is_a()}'.")

    if not next_segment.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{next_segment.is_a()}'.")

    if len(segment.UsingCurves) != 1:
        raise TypeError("segment must belong to exactly one curve")

    if len(next_segment.UsingCurves) != 1:
        raise TypeError("next_segment must belong to exactly one curve")

    if segment.UsingCurves[0] != next_segment.UsingCurves[0]:
        raise TypeError("Both segments must belong to the same curve")

    settings = ifcopenshell.geom.settings()
    settings.set("COMPUTE_CURVATURE", True)

    segment_fn = ifcopenshell_wrapper.map_shape(settings, segment.wrapped_data)
    segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
    e = segment_evaluator.evaluate(segment_fn.end())
    end = np.array(e)

    # must add the new segment to the container before mapping it, otherwise the segment doesn't
    # have enough context to know if it is for horizontal, vertical, cant

    next_segment_fn = ifcopenshell_wrapper.map_shape(settings, next_segment.wrapped_data)
    next_segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, next_segment_fn)
    s = next_segment_evaluator.evaluate(next_segment_fn.start())
    start = np.array(s)

    same_position = True if np.allclose(end[:3, 3], start[:3, 3], atol=position_tolerance) else False
    same_gradient = True if np.allclose(end[:3, 0], start[:3, 0]) else False
    same_curvature = True if np.allclose(end[3:, :3], start[3:, :3]) else False

    transition_code = ""
    if same_position:
        transition_code = "CONTINUOUS"
        if same_gradient:
            transition_code = "CONTSAMEGRADIENT"
            if same_curvature:
                transition_code = "CONTSAMEGRADIENTSAMECURVATURE"
    else:
        transition_code = "DISCONTINUOUS"

    return transition_code
