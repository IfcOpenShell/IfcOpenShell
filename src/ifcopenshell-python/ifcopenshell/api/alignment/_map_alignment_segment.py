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

from collections.abc import Sequence

import ifcopenshell
from ifcopenshell import entity_instance

from ifcopenshell.api.alignment._map_alignment_cant_segment import (
    _map_alignment_cant_segment,
)
from ifcopenshell.api.alignment._map_alignment_horizontal_segment import (
    _map_alignment_horizontal_segment,
)
from ifcopenshell.api.alignment._map_alignment_vertical_segment import (
    _map_alignment_vertical_segment,
)


def _map_alignment_segment(
    file: ifcopenshell.file, layout: entity_instance, segment: entity_instance
) -> Sequence[entity_instance]:
    """
    Maps an IfcAlignmentSegment to its corresponding IfcCurveSegment(s) in the geometric representation.
    The mapping is done based on the layout type and segment type.
    """
    if layout.is_a("IfcAlignmentHorizontal"):
        mapped_segments = _map_alignment_horizontal_segment(file, segment)
    elif layout.is_a("IfcAlignmentVertical"):
        mapped_segments = _map_alignment_vertical_segment(file, segment)
    else:
        mapped_segments = _map_alignment_cant_segment(file, segment, layout.RailHeadDistance)

    return mapped_segments
