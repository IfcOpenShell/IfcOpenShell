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
Manages alignment layout (semantic definition) and alignment geometry (geometric definition).

This API is defined in terms of the semantic definition of an alignment. The corresponding geometric definition
is created and maintained automatically. The manditory zero length segment for the semantic and geometric definitions
are automatically created and maintained.

Alignments are created with stationing referents. Each layout segment is assigned a position referent that informs about
the start point of the segment. An example is the point of curvature of a horizontal circular curve. The referent is
nested to the segment representing the circular arc and is named with a indicator of the position and the station, e.g. "P.C. (145+98.32)"

This API does not determine alignment parameters based on rules, such as minimum curve radius as a function of design speed or sight distance.

This API is under development and subject to code breaking changes in the future.

Presently, this API supports:
    1. Creating alignments, both horizontal and vertical, using the PI method. Alignment definition can be read from a CSV file.
    2. Creating alignments segment by segment.
    3. Automatic creation of geometric definitions (IfcCompositeCurve, IfcGradientCurve, IfcSegmentedReferenceCurve)
    4. Automatic definition of stationing
    5. Automatic definition of alignment transition point referents
    6. Utility functions for printing business logical and geometric representations, as well as minimal geometry evaluations

Future versions of this API may support:
    1. Defining alignments using the PI method, including transition spirals
    2. Updating horizontal curve definitions by revising transition spiral parameters and circular curve radii
    3. Updating vertical curve definitions by revising horizontal length of curves
    4. Removing a segment at any location along a curve
    5. Adding a segment at any location along a curve
"""

from .add_stationing_referent import add_stationing_referent
from .add_vertical_layout import add_vertical_layout
from .add_zero_length_segment import add_zero_length_segment
from .create_layout_segment import create_layout_segment
from .create import create
from .create_as_offset_curve import create_as_offset_curve
from .create_as_polyline import create_as_polyline
from .create_by_pi_method import create_by_pi_method
from .create_from_csv import create_from_csv
from .create_segment_representations import create_segment_representations
from .create_representation import create_representation
from .distance_along_from_station import distance_along_from_station
from .get_alignment import get_alignment
from .get_alignment_layout_nest import get_alignment_layout_nest
from .get_alignment_segment_nest import get_alignment_segment_nest
from .get_alignment_start_station import get_alignment_start_station
from .get_curve_segment_transition_code import get_curve_segment_transition_code
from .get_layout_segments import get_layout_segments
from .get_horizontal_layout import get_horizontal_layout
from .get_vertical_layout import get_vertical_layout
from .get_cant_layout import get_cant_layout
from .get_alignment_layouts import get_alignment_layouts
from .get_axis_subcontext import get_axis_subcontext
from .get_basis_curve import get_basis_curve
from .get_child_alignments import get_child_alignments
from .get_curve import get_curve
from .get_layout_curve import get_layout_curve
from .get_mapped_segments import get_mapped_segments
from .get_parent_alignment import get_parent_alignment
from .get_referent_nest import get_referent_nest
from .has_zero_length_segment import has_zero_length_segment
from .layout_horizontal_alignment_by_pi_method import layout_horizontal_alignment_by_pi_method
from .layout_vertical_alignment_by_pi_method import layout_vertical_alignment_by_pi_method
from .name_segments import name_segments
from .update_fallback_position import update_fallback_position
from .util import *

from ._get_segment_start_point_label import register_referent_name_callback

__all__ = [
    "add_stationing_referent",
    "add_vertical_layout",
    "add_zero_length_segment",
    "create",
    "create_as_offset_curve",
    "create_as_polyline",
    "create_by_pi_method",
    "create_from_csv",
    "create_layout_segment",
    "create_representation",
    "create_segment_representations",
    "distance_along_from_station",
    "get_alignment",
    "get_alignment_layout_nest",
    "get_alignment_layouts",
    "get_alignment_segment_nest",
    "get_alignment_start_station",
    "get_axis_subcontext",
    "get_basis_curve",
    "get_cant_layout",
    "get_child_alignments",
    "get_curve",
    "get_curve_segment_transition_code",
    "get_horizontal_layout",
    "get_layout_curve",
    "get_layout_segments",
    "get_parent_alignment",
    "get_referent_nest",
    "get_vertical_layout",
    "has_zero_length_segment",
    "layout_horizontal_alignment_by_pi_method",
    "layout_vertical_alignment_by_pi_method",
    "name_segments",
    "register_referent_name_callback",
    "update_fallback_position",
]
