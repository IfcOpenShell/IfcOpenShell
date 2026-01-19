# Saikei Civil - Civil Engineering Tools for IfcOpenShell
# Copyright (C) 2025 IfcOpenShell Contributors
#
# This file is part of Saikei Civil.
#
# Saikei Civil is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Saikei Civil is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Saikei Civil.  If not, see <http://www.gnu.org/licenses/>.

"""Core alignment business logic - Pure Python, NO bpy imports.

This module contains all alignment-related calculations and logic that
can be tested outside of Blender. Functions receive tool classes as
parameters following Bonsai's dependency injection pattern.
"""

from __future__ import annotations
import math
from typing import TYPE_CHECKING, List, Tuple, Optional
from dataclasses import dataclass

if TYPE_CHECKING:
    import ifcopenshell
    from .. import tool


# =============================================================================
# Data Classes for Pure Python PI Handling
# =============================================================================


@dataclass
class PIPoint:
    """Pure Python representation of a PI (Point of Intersection).

    This mirrors the Blender PropertyGroup but without bpy dependencies,
    allowing for testing and core logic operations.
    """
    x: float
    y: float
    pi_type: str = "TANGENT"  # ENDPOINT, TANGENT, or CURVE
    radius: float = 0.0
    length_to_next: float = 0.0
    direction_to_next: float = 0.0
    station: float = 0.0


@dataclass
class PIGeometryResult:
    """Result of PI geometry calculation."""
    stations: List[float]
    lengths: List[float]
    directions: List[float]
    total_length: float


# =============================================================================
# Pure Python Calculation Functions
# =============================================================================


def calculate_pi_geometry(
    pis: List[Tuple[float, float]],
    start_station: float = 0.0
) -> PIGeometryResult:
    """Calculate lengths, stations, and directions for a list of PI points.

    This is a pure Python function with no Blender dependencies.

    Args:
        pis: List of (x, y) coordinate tuples for each PI
        start_station: Starting station value

    Returns:
        PIGeometryResult containing calculated values
    """
    if len(pis) < 2:
        return PIGeometryResult(
            stations=[start_station] if pis else [],
            lengths=[0.0] if pis else [],
            directions=[0.0] if pis else [],
            total_length=0.0
        )

    stations = []
    lengths = []
    directions = []
    cumulative_length = start_station

    for i, pi in enumerate(pis):
        stations.append(cumulative_length)

        if i < len(pis) - 1:
            next_pi = pis[i + 1]
            dx = next_pi[0] - pi[0]
            dy = next_pi[1] - pi[1]
            length = math.sqrt(dx * dx + dy * dy)
            direction = math.atan2(dy, dx)
            lengths.append(length)
            directions.append(direction)
            cumulative_length += length
        else:
            lengths.append(0.0)
            directions.append(0.0)

    total_length = cumulative_length - start_station

    return PIGeometryResult(
        stations=stations,
        lengths=lengths,
        directions=directions,
        total_length=total_length
    )


def calculate_deflection_angle(
    incoming_direction: float,
    outgoing_direction: float
) -> float:
    """Calculate the deflection angle between two tangent directions.

    Args:
        incoming_direction: Direction angle of incoming tangent (radians)
        outgoing_direction: Direction angle of outgoing tangent (radians)

    Returns:
        Deflection angle in radians (always positive)
    """
    delta = outgoing_direction - incoming_direction
    # Normalize to -pi to pi
    while delta > math.pi:
        delta -= 2 * math.pi
    while delta < -math.pi:
        delta += 2 * math.pi
    return abs(delta)


def calculate_tangent_length(radius: float, deflection_angle: float) -> float:
    """Calculate tangent length for a circular curve.

    T = R * tan(Δ/2)

    Args:
        radius: Curve radius
        deflection_angle: Deflection angle in radians

    Returns:
        Tangent length
    """
    if deflection_angle == 0 or radius == 0:
        return 0.0
    return radius * math.tan(deflection_angle / 2)


def calculate_arc_length(radius: float, deflection_angle: float) -> float:
    """Calculate arc length for a circular curve.

    L = R * Δ

    Args:
        radius: Curve radius
        deflection_angle: Deflection angle in radians

    Returns:
        Arc length
    """
    return radius * deflection_angle


def calculate_bc_ec_points(
    pi_x: float,
    pi_y: float,
    incoming_direction: float,
    outgoing_direction: float,
    tangent_length: float
) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Calculate Begin Curve (BC) and End Curve (EC) points.

    BC = PI - incoming_tangent_vector * T
    EC = PI + outgoing_tangent_vector * T

    Args:
        pi_x: PI X coordinate
        pi_y: PI Y coordinate
        incoming_direction: Direction of incoming tangent (radians)
        outgoing_direction: Direction of outgoing tangent (radians)
        tangent_length: Calculated tangent length

    Returns:
        Tuple of (BC point, EC point) as (x, y) tuples
    """
    # BC is along the incoming tangent, before the PI
    bc_x = pi_x - tangent_length * math.cos(incoming_direction)
    bc_y = pi_y - tangent_length * math.sin(incoming_direction)

    # EC is along the outgoing tangent, after the PI
    ec_x = pi_x + tangent_length * math.cos(outgoing_direction)
    ec_y = pi_y + tangent_length * math.sin(outgoing_direction)

    return ((bc_x, bc_y), (ec_x, ec_y))


# =============================================================================
# Alignment Visualization Logic (Pure Python)
# =============================================================================


def create_alignment_hierarchy(
    ifc_tool: type[tool.Ifc],
    alignment_tool: type[tool.Alignment],
    alignment: ifcopenshell.entity_instance,
) -> object:
    """Create the Blender object hierarchy for an IFC alignment.

    This is a core function that orchestrates the creation process
    by calling tool methods. It contains the business logic but
    delegates actual Blender operations to the tool layer.

    Args:
        ifc_tool: The IFC tool class for IFC operations
        alignment_tool: The Alignment tool class for Blender operations
        alignment: The IFC alignment entity

    Returns:
        The root Blender object for the alignment
    """
    # Create the alignment object
    alignment_obj = alignment_tool.create_object_for_alignment(alignment)
    if not alignment_obj:
        return None

    # Get nested layouts via IfcRelNests
    layouts = []
    for rel in getattr(alignment, "IsNestedBy", []) or []:
        for obj in rel.RelatedObjects or []:
            if obj.is_a() in ("IfcAlignmentHorizontal", "IfcAlignmentVertical", "IfcAlignmentCant"):
                layouts.append(obj)

    # Create Blender objects for each layout and its segments
    for layout in layouts:
        layout_obj = alignment_tool.create_object_for_layout(layout, alignment_obj)
        if layout_obj:
            create_layout_segment_objects(alignment_tool, layout, layout_obj)

    return alignment_obj


def create_layout_segment_objects(
    alignment_tool: type[tool.Alignment],
    layout: ifcopenshell.entity_instance,
    layout_obj: object,
) -> list:
    """Create Blender objects for all segments in a layout.

    Args:
        alignment_tool: The Alignment tool class
        layout: The IFC layout entity
        layout_obj: The parent Blender object

    Returns:
        List of created segment Blender objects
    """
    segment_objs = []

    for rel in getattr(layout, "IsNestedBy", []) or []:
        for i, segment in enumerate(rel.RelatedObjects or []):
            if segment.is_a() == "IfcAlignmentSegment":
                seg_obj = alignment_tool.create_object_for_segment(segment, i, layout_obj)
                if seg_obj:
                    segment_objs.append(seg_obj)

    return segment_objs
