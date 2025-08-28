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

from ifcopenshell.api.alignment._create_geometric_representation import _create_geometric_representation
from ifcopenshell.api.alignment._add_segment_to_curve import _add_segment_to_curve


def create_representation(
    file: ifcopenshell.file,
    alignment: entity_instance,
) -> None:
    """
    Creates the geometric representation of an alignment if it does not already exist.
    This function is intended to be used when a model has only the semantic definition of an alignment
    and you want to add the geometric representation.

    If the alignments are complete, it is recommended that add_zero_length_segment is called after this method to ensure
    the proper structure of the semantic and geometric definitions of the alignment

    :param alignment: The alignment to create the representation.
    """
    expected_type = "IfcAlignment"
    if not alignment.is_a(expected_type):
        raise TypeError(f"Expected to see type '{expected_type}', instead received '{alignment.is_a()}'.")

    if alignment.Representation:
        return

    _create_geometric_representation(file, alignment)

    layouts = ifcopenshell.api.alignment.get_alignment_layouts(alignment)
    for layout in layouts:
        curve = ifcopenshell.api.alignment.get_layout_curve(layout)
        layout_nest = ifcopenshell.api.alignment.get_alignment_segment_nest(layout)
        for segment in layout_nest.RelatedObjects:
            _add_segment_to_curve(file, segment, curve)
