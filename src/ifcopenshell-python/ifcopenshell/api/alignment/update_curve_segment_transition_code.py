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
from typing import Sequence
import numpy as np
import math


def update_curve_segment_transition_code(prev_segment: entity_instance, segment: entity_instance) -> None:
    """
    Updates IfcCurveSegment.Transition of prev_segment based on a comparison of
    the position, ref. direction, and curvature at the end of the prev_segment and the start of segment.
    """
    expected_type = "IfcCurveSegment"
    if not prev_segment.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{prev_segment.is_a()}'.")

    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{segment.is_a()}'.")

    if len(prev_segment.UsingCurves) != 1:
        raise TypeError("prev_segment must belong to exactly one curve")

    if len(segment.UsingCurves) != 1:
        raise TypeError("segment must belong to exactly one curve")

    if prev_segment.UsingCurves[0] != segment.UsingCurves[0]:
        raise TypeError("Both segments must belong to the same curve")

    settings = ifcopenshell.geom.settings()
    settings.set("COMPUTE_CURVATURE", True)

    prev_segment_fn = ifcopenshell_wrapper.map_shape(settings, prev_segment.wrapped_data)
    prev_segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, prev_segment_fn)
    e = prev_segment_evaluator.evaluate(prev_segment_fn.end())
    end = np.array(e)

    # must add the new segment to the container before mapping it, otherwise the segment doesn't
    # have enough context to know if it is for horizontal, vertical, cant

    segment_fn = ifcopenshell_wrapper.map_shape(settings, segment.wrapped_data)
    segment_evaluator = ifcopenshell_wrapper.function_item_evaluator(settings, segment_fn)
    s = segment_evaluator.evaluate(segment_fn.start())
    start = np.array(s)

    same_position = True if np.allclose(end[:3], start[:3]) else False
    same_gradient = True if np.allclose(end[:0], start[:0]) else False
    same_curvature = True if np.allclose(end[3:], start[3:]) else False

    if same_position:
        prev_segment.Transition = "CONTINUOUS"
        if same_gradient:
            prev_segment.Transition = "CONTSAMEGRADIENT"
            if same_curvature:
                prev_segment.Transition = "CONTSAMEGRADIENTSAMECURVATURE"
    else:
        prev_segment.Transition = "DISCONTINUOUS"
