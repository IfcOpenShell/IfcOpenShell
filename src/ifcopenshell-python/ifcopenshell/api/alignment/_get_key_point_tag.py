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
import ifcopenshell.util.alignment


def _get_key_point_tag(file: ifcopenshell.file, label: str, station: float) -> str:
    """
    Builds the station-and-label text shared by update_alignment_parameter_segment_tags (used
    directly as IfcAlignmentParameterSegment.StartTag/EndTag) and update_key_point_referents (used,
    prefixed with the alignment name, as IfcReferent.Name): "<station> (<label>)", e.g.
    "145+98.32 (P.O.B.)".
    """
    return f"{ifcopenshell.util.alignment.station_as_string(file, station)} ({label})"
