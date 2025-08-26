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
from ifcopenshell import ifcopenshell_wrapper
import ifcopenshell.geom
from ifcopenshell import entity_instance
import numpy as np
import math


def _update_curve_segment_transition_code(prev_segment: entity_instance, segment: entity_instance) -> None:
    """
    Updates IfcCurveSegment.Transition of prev_segment based on a comparison of
    the position, ref. direction, and curvature at the end of the prev_segment and the start of segment.
    """
    prev_segment.Transition = ifcopenshell.api.alignment.get_curve_segment_transition_code(prev_segment, segment)
