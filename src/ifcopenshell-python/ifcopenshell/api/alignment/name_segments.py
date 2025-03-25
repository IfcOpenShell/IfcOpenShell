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
from typing import Sequence


def name_segments(prefix: str, alignment: entity_instance) -> None:
    """
    Sets the segment name like ("H1" for horizontal, "V1" for vertical, "C1" for cant)

    :param prefix: The naming prefix
    :param alignment: The alignment whose segments are to be named. This should be a IfcAlignmentHorizontal, IfcAlignmentVertical or IfcAlignmentCant
    """
    expected_types = ["IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"]
    if not alignment.is_a() in expected_types:
        raise TypeError(
            f"Expected entity type to be one of {[_ for _ in expected_types]}, instead received '{v.is_a()}"
        )

    i = 1
    for rel in alignment.IsNestedBy:
        for segment in rel.RelatedObjects:
            if segment.is_a("IfcAlignmentSegment"):
                segment.Name = f"{prefix}{i}"
                i += 1
