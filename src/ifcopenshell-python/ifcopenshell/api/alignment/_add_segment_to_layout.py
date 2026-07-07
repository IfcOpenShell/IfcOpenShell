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
from ifcopenshell.api.alignment._update_zero_length_segment_placement import _update_zero_length_segment_placement
import ifcopenshell.api.nest
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._add_segment_to_curve import _add_segment_to_curve
from ifcopenshell.api.alignment._get_segment_endpoint import _get_segment_endpoint


def _add_segment_to_layout(
    file: ifcopenshell.file, layout: entity_instance, layout_segment: entity_instance
) -> Union[np.array, None]:
    """
    Adds an IfcAlignmentSegment to a layout alignment (IfcAlignmentHorizontal/Vertical/Cant). This segment is added at the end
    of the layout, before the manditory zero length segment (if it exists).
    If the layout has a corresponding geometric representation, an IfcCurveSegment is created for it and appended at the end
    of the representation curve, before the zero length segment (if it exists).

    :param layout: The layout alignment
    :param segment: The segment to be appended
    :return: None
    """

    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    if not (layout_segment.is_a("IfcAlignmentSegment")):
        raise TypeError(f"Expected to see IfcAlignmentSegment, instead received {layout_segment.is_a()}.")

    # add the new segment to the layout
    ifcopenshell.api.nest.assign_object(file, related_objects=[layout_segment], relating_object=layout)

    # segment is attached at the end, but this is after the zero length segment
    # swap the last two segments
    ifcopenshell.api.nest.reorder_nesting(file, layout_segment, -1, -1)

    # For cant segments, the end point depends on the next segment. The next segment is the
    # zero-length segment and it hasn't been updated to match the end point.
    # For this reason, we can't compute the end point from the IfcCurveSegment, but instead we
    # compute it from the layout segment design parameters.
    end_point = _get_segment_endpoint(file, layout_segment)

    # update the position of the zero length layout segment to be at the end point of the newly added segment
    segment_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
    zero_length_layout_segment = segment_nest.RelatedObjects[-1]
    _update_zero_length_segment_placement(file, zero_length_layout_segment, end_point)

    # if there is a curve defined, add a new IfcCurveSegment to it.
    # _add_segment_to_curve maps the layout segment to the appropriate IfcCurveSegment type and adds it to the curve.
    curve = ifcopenshell.api.alignment.get_layout_curve(layout)
    if curve:
        _add_segment_to_curve(file, layout_segment, curve)

    return end_point
