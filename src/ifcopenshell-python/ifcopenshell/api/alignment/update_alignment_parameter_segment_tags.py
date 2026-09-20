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
from ifcopenshell import entity_instance
from ifcopenshell.api.alignment._get_key_point_tag import _get_key_point_tag
from ifcopenshell.api.alignment._get_segment_start_point_label import (
    _get_segment_start_point_label,
)


def update_alignment_parameter_segment_tags(
    file: ifcopenshell.file, layout: entity_instance, label_end_tag: bool = False
) -> None:
    """
    Sets IfcAlignmentParameterSegment.StartTag (and, optionally, EndTag) for every segment
    transition in an alignment layout. Unlike update_key_point_referents, this does not create any
    IfcReferent or IfcRelNests -- it only mutates the StartTag/EndTag string attributes already
    present on each segment's DesignParameters.

    Every real segment's StartTag is set to a computed tag describing the point where it begins,
    using the same label-and-station format as update_key_point_referents' Name minus the alignment
    name (via _get_key_point_tag), e.g. "145+98.32 (P.C.)". The first segment's StartTag comes from
    the "Beginning of Alignment" boundary label.

    EndTag is left untouched unless `label_end_tag` is True. When enabled, for each transition
    between two consecutive segments, the outgoing segment's EndTag is set to the same tag as the
    incoming segment's StartTag (they describe the same physical point), and the last segment's
    EndTag is set from the "End of Alignment" boundary label.

    Labels come from _get_segment_start_point_label -- if a callback has been registered via
    register_referent_name_callback(), its output is used instead of the built-in labels, exactly as
    in update_key_point_referents.

    :param layout: IfcAlignmentHorizontal, IfcAlignmentVertical, or IfcAlignmentCant
    :param label_end_tag: if True, also sets EndTag on every real segment. If False (default),
        EndTag is left untouched.
    :return: None -- this function mutates segment.DesignParameters.StartTag/EndTag in place

    Example:

    .. code:: python

        horizontal = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        ifcopenshell.api.alignment.update_alignment_parameter_segment_tags(model, horizontal)
    """

    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received {layout.is_a()}"
        )

    alignment = ifcopenshell.api.alignment.get_alignment(layout)
    if alignment is None:
        raise ValueError(f"{layout.is_a()} #{layout.id()} is not nested under an IfcAlignment.")

    segments = list(ifcopenshell.api.alignment.get_layout_segments(layout))
    if segments and ifcopenshell.api.alignment.has_zero_length_segment(layout):
        segments = segments[:-1]

    if not segments:
        return

    start_station = ifcopenshell.api.alignment.get_alignment_start_station(file, alignment)
    is_horizontal = layout.is_a("IfcAlignmentHorizontal")

    distance_along = 0.0
    prev_segment = None
    for segment in segments:
        dp = segment.DesignParameters
        seg_distance_along = distance_along if is_horizontal else dp.StartDistAlong

        label = _get_segment_start_point_label(prev_segment, segment)
        station = start_station + seg_distance_along
        tag = _get_key_point_tag(file, label, station)

        dp.StartTag = tag
        if prev_segment is not None and label_end_tag:
            prev_segment.DesignParameters.EndTag = tag

        if is_horizontal:
            distance_along += dp.SegmentLength
        else:
            distance_along = dp.StartDistAlong + dp.HorizontalLength

        prev_segment = segment

    if label_end_tag:
        label = _get_segment_start_point_label(prev_segment, None)
        station = start_station + distance_along
        prev_segment.DesignParameters.EndTag = _get_key_point_tag(file, label, station)
