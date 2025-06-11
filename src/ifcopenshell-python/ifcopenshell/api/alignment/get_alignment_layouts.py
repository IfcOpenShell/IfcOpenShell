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

import ifcopenshell.util.representation


def get_alignment_layouts(alignment: entity_instance) -> Sequence[entity_instance]:
    """
    Returns the layout alignments nested to this alignment
    """
    layouts = []
    for rel in alignment.IsNestedBy:
        for layout in rel.RelatedObjects:
            if (
                layout.is_a("IfcAlignmentHorizontal")
                or layout.is_a("IfcAlignmentVertical")
                or layout.is_a("IfcAlignmentCant")
            ):
                layouts.append(layout)

    return layouts
