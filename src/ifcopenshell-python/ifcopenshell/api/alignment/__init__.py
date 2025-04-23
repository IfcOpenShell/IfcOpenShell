# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

"""
Manages alignment layout (business logical) and alignment geometry (geometric representations).

This API does not determine alignment parameters based on rules, such as minimum curve radius as a function of design speed or sight distance.

This API is under development and subject to code breaking changes in the future.

Presently, this API supports:
    1. Creating alignments, both horizontal and vertical, using the PI method. Alignment definition can be read from a CSV file.
    2. Adding business logic and geometric segments to the end of an alignment
    3. Adding and removing the zero length segment at the end of alignments
    4. Creating geometric representations from a business logical definition
    5. Mapping individual business logical segments to geometric segments (complete for horizontal, missing clothoid for vertical, not implemented for cant)
    6. Using curve geometry to determine IfcCurveSegment.Transition transition code.
    7. Utility functions for printing business logical and geometric representations, as well as minimumal geometry evaluations

Future versions of this API will support:
    1. Defining alignments using the PI method, including transition spirals
    2. Updating horizontal curve definitions by revising transition spiral parameters and circular curve radii
    3. Updating vertical curve definitions by revising horizontal length of curves
    4. Removing a segment at any location along a curve
    5. Adding a segment at any location along a curve
"""

from .add_segment_to_curve import add_segment_to_curve
from .add_segment_to_layout import add_segment_to_layout
from .add_stationing_to_alignment import add_stationing_to_alignment
from .add_vertical_alignment_by_pi_method import add_vertical_alignment_by_pi_method
from .add_vertical_alignment import add_vertical_alignment
from .add_zero_length_segment import add_zero_length_segment
from .create_alignment_by_pi_method import create_alignment_by_pi_method
from .create_alignment_from_csv import create_alignment_from_csv
from .create_horizontal_alignment_by_pi_method import create_horizontal_alignment_by_pi_method
from .create_geometric_representation import create_geometric_representation
from .create_vertical_alignment_by_pi_method import create_vertical_alignment_by_pi_method
from .distance_along_from_station import distance_along_from_station
from .get_alignment_layouts import get_alignment_layouts
from .get_axis_subcontext import get_axis_subcontext
from .get_basis_curve import get_basis_curve
from .get_child_alignments import get_child_alignments
from .get_curve import get_curve
from .get_parent_alignment import get_parent_alignment
from .has_zero_length_segment import has_zero_length_segment
from .map_alignment_segments import map_alignment_segments
from .map_alignment_horizontal_segment import map_alignment_horizontal_segment
from .map_alignment_vertical_segment import map_alignment_vertical_segment
from .map_alignment_cant_segment import map_alignment_cant_segment
from .name_segments import name_segments
from .remove_last_segment import remove_last_segment
from .remove_zero_length_segment import remove_zero_length_segment
from .update_curve_segment_transition_code import update_curve_segment_transition_code
from .util import *

__all__ = [
    "add_segment_to_curve",
    "add_segment_to_layout",
    "add_stationing_to_alignment",
    "add_vertical_alignment_by_pi_method",
    "add_vertical_alignment",
    "add_zero_length_segment",
    "create_alignment_by_pi_method",
    "create_alignment_from_csv",
    "create_horizontal_alignment_by_pi_method",
    "create_geometric_representation",
    "create_vertical_alignment_by_pi_method",
    "distance_along_from_station",
    "get_alignment_layouts",
    "get_axis_subcontext",
    "get_basis_curve",
    "get_child_alignments",
    "get_curve",
    "get_parent_alignment",
    "has_zero_length_segment",
    "map_alignment_segments",
    "map_alignment_horizontal_segment",
    "map_alignment_vertical_segment",
    "map_alignment_cant_segment",
    "name_segments",
    "remove_last_segment",
    "remove_zero_length_segment",
    "update_curve_segment_transition_code",
]
