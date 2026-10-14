# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Thomas Krijnen <thomas@aecgeeks.com>
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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.util.unit
from ifcopenshell import entity_instance


def _get_start_direction(design_parameters: entity_instance) -> float:
    """
    The StartDirection of an IfcAlignmentHorizontalSegment in radians.

    StartDirection is an IfcPlaneAngleMeasure in the project's plane angle unit, which may be the
    degree or the gradian rather than the radian.
    """
    scale = ifcopenshell.util.unit.calculate_unit_scale(design_parameters.file, "PLANEANGLEUNIT")
    return design_parameters.StartDirection * scale


def _to_start_direction(file: ifcopenshell.file, radians: float) -> float:
    """A direction in radians, in the project's plane angle unit, to write to StartDirection."""
    return radians / ifcopenshell.util.unit.calculate_unit_scale(file, "PLANEANGLEUNIT")
