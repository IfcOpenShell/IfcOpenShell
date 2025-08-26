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
import ifcopenshell.util
from ifcopenshell import entity_instance
from collections.abc import Sequence

import ifcopenshell.util.element


def get_layout_segments(layout: entity_instance) -> Sequence[entity_instance]:
    """
    Returns the IfcAlignmentSegment nested to this alignment layout

    Example:

    .. code:: python

        horizontal = model.by_type("IfcAlignmentHorizontal")[0]
        segments = ifcopenshell.api.alignment.get_layout_segments(horizontal)
    """
    segments = []
    for rel in layout.IsNestedBy:
        for segment in rel.RelatedObjects:
            if segment.is_a("IfcAlignmentSegment"):
                segments.append(segment)

    return segments
