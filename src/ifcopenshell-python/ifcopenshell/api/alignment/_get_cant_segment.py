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
import ifcopenshell.api.geometry
from ifcopenshell import entity_instance

import math
from collections.abc import Sequence


def _get_cant_segment(horizontal_segment: entity_instance) -> entity_instance:
    """
    Returns the IfcAlignmentSegment from the cant layout that corresponds to horizontal_segment.
    Returns None if the cant segment cannot be found
    """

    expected_type = "IfcAlignmentSegment"
    if not horizontal_segment.is_a(expected_type):
        raise TypeError(f"Expected {expected_type} but got {horizontal_segment.is_a()}")

    if not horizontal_segment.DesignParameters.is_a("IfcAlignmentHorizontalSegment"):
        raise TypeError(
            f"Expect DesignParameter to be IfcAlignmentHorizontal but got {horizontal_segment.DesignParameters.is_a()}"
        )

    # get the index of horizontal_segment in the horizontal_layout
    horizontal_layout = horizontal_segment.Nests[0].RelatingObject
    index = 0
    for segment in horizontal_layout.IsNestedBy[0].RelatedObjects:
        if segment == horizontal_segment:
            break
        else:
            index += 1

    cant_segment = None

    # first check CT 4.1.4.4.1.1 Alignment Layout - Horizontal, Vertical and Cant
    nests_layouts = horizontal_layout.Nests[0]
    for layout in nests_layouts.RelatedObjects:
        if layout.is_a("IfcAlignmentCant"):
            cant_segment = layout.IsNestedBy[0].RelatedObjects[index]
            break

    # if a cant_segment wasn't found, check CT 4.1.4.4.1.2 Alignment Layout - Reusing Horizontal Layout
    # Note that nothing forbids multiple child alignments to have cant layouts. However, this would not make
    # sense for Viennese Bend because the Viennese Bend cant segment influences the geometry of the horizontal
    # Viennese Bend transition curve segment. The horizontal geometry would not be unique if there are
    # multiple child alignments with cant layouts.
    # For this reason, use the first cant layout found
    if cant_segment == None:
        alignment = ifcopenshell.api.alignment.get_alignment(horizontal_layout)
        for child_alignment in alignment.IsDecomposedBy[0].RelatedObjects:
            for layout in child_alignment.Nests[0].RelatedObjects:
                if layout.is_a("IfcAlignmentCant"):
                    cant_segment = layout.IsNestedBy[0].RelatedObjects[index]
                    break
            if cant_segment:
                break

    return cant_segment
