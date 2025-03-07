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
from ifcopenshell import entity_instance
from typing import Sequence


def add_segment_to_layout(file: ifcopenshell.file, alignment: entity_instance, segment: entity_instance) -> None:
    """
    Adds a segment to a layout alignment (horizontal, vertical, or cant)

    :param alignment: The alignment
    :param segment: The segment to be appended
    :return: None
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not alignment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{alignment.is_a()}"
        )

    if not (segment.is_a("IfcAlignmentSegment")):
        raise TypeError(f"Expected to see IfcAlignmentSegment, instead received '{segment.is_a()}.")

    zero_length_segment = (
        ifcopenshell.api.alignment.remove_zero_length_segment(file, alignment)
        if ifcopenshell.api.alignment.has_zero_length_segment(alignment)
        else None
    )

    ifcopenshell.api.nest.assign_object(file, related_objects=[segment], relating_object=alignment)

    if zero_length_segment:
        ifcopenshell.api.nest.assign_object(file, related_objects=[zero_length_segment], relating_object=alignment)
