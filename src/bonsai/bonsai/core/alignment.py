# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2025, 2026 Michael Yoder <myoder@desertspringscivil.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.


"""Core alignment business logic - Orchestration only, NO bpy imports.

This module contains alignment-related business logic and workflow
orchestration. All calculations and algorithms are in the tool layer.
Functions receive tool classes as parameters following Bonsai's
dependency injection pattern.

NOTE: Math, calculations, and algorithms belong in tool/alignment.py.
This module only handles:
- Business rules and validation
- Workflow orchestration (calling tool methods in sequence)
- Decision-making about what should happen
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional
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


# =============================================================================
# Alignment Visualization Logic (Business Logic Orchestration)
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
