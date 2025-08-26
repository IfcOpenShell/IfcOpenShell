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
from ifcopenshell import entity_instance


def name_segments(prefix: str, layout: entity_instance) -> None:
    """
    Sets the IfcAlignmentSegment.Name attribute using a prefix and sequence number (e.g. "H1" for horizontal, "V1" for vertical, "C1" for cant)

    :param prefix: The naming prefix
    :param layout: The layout alignment whose segments are to be named. This should be a IfcAlignmentHorizontal, IfcAlignmentVertical or IfcAlignmentCant
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not layout.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{layout.is_a()}"
        )

    i = 1
    for rel in layout.IsNestedBy:
        for segment in rel.RelatedObjects:
            if segment.is_a("IfcAlignmentSegment"):
                segment.Name = f"{prefix}{i}"
                i += 1
