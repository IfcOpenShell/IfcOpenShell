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
import ifcopenshell.geom
from ifcopenshell import entity_instance


def add_segment_to_curve(file: ifcopenshell.file, segment: entity_instance, composite_curve: entity_instance) -> None:
    """
    Adds a segment to a composite curve. The segment must not belong to another composite curve (len(segment.UsingCurves) == 0).
    If the composite curve does not have any segments, the segment is simply appended to the curve.
    If the composite curve has segments, the position, ref. direction, and curvature at the end of the last segment is
    compared to the position, ref. direction and curvature at the start of the new segment. The IfcCurveSegment.Transition of the last curve segment is updated.

    :param segment: The segment to be added to the curve
    :param composite_curve: The curve receiving the segment
    :return: None
    """
    expected_type = "IfcCurveSegment"
    if not segment.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{segment.is_a()}'.")

    if 0 < len(segment.UsingCurves):
        raise TypeError("IfcCurveSegment cannot belong to other curves")

    expected_type = "IfcCompositeCurve"
    if not composite_curve.is_a(expected_type):
        raise TypeError(f"Expected to see '{expected_type}', instead received '{composite_curve.is_a()}'.")

    settings = ifcopenshell.geom.settings()
    if composite_curve.Segments == None or 0 == len(composite_curve.Segments):
        # this is the first segment so just add it
        if composite_curve.Segments == None:
            composite_curve.Segments = []

        # the last segment is always discontinuous
        segment.Transition = "DISCONTINUOUS"

        composite_curve.Segments += (segment,)
        assert len(segment.UsingCurves) == 1
    else:
        zero_length_segment = (
            ifcopenshell.api.alignment.remove_zero_length_segment(file, composite_curve)
            if ifcopenshell.api.alignment.has_zero_length_segment(composite_curve)
            else None
        )

        prev_segment = composite_curve.Segments[-1]

        # the last segment is always discontinuous
        segment.Transition = "DISCONTINUOUS"

        # must add the new segment to the curve before updating the transition code
        composite_curve.Segments += (segment,)

        ifcopenshell.api.alignment.update_curve_segment_transition_code(prev_segment, segment)

        if zero_length_segment:
            ifcopenshell.api.alignment.add_segment_to_curve(zero_length_segment, composite_curve)
