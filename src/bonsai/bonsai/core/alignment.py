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

    Delegates to the tool layer which creates both:
    - A curve from the IFC representation (for visualization)
    - Empty objects for each segment (for selection/editing)

    Args:
        alignment_tool: The Alignment tool class
        layout: The IFC layout entity
        layout_obj: The parent Blender object

    Returns:
        List of created Blender objects (curve + segment empties)
    """
    return alignment_tool.create_objects_for_layout_segments(layout, layout_obj)


# =============================================================================
# PI Edit Mode Functions
# =============================================================================


def enter_pi_edit_mode(
    ifc_tool: "type[tool.Ifc]",
    alignment_tool: "type[tool.Alignment]",
    alignment_id: int,
) -> list:
    """Enter PI edit mode for an alignment.

    Business logic for entering PI edit mode:
    1. Validates that the alignment exists
    2. Validates that the alignment has a horizontal layout with real segments
    3. Back-calculates PI positions from segments
    4. Creates temporary EMPTY objects at each PI location

    Args:
        ifc_tool: The IFC tool class
        alignment_tool: The Alignment tool class
        alignment_id: The IFC ID of the alignment to edit

    Returns:
        List of created PI EMPTY objects

    Raises:
        ValueError: If alignment doesn't exist, has no horizontal layout,
                   or has no real segments
    """
    import ifcopenshell.api.alignment as align_api

    # Validate alignment exists
    ifc_file = ifc_tool.get()
    if ifc_file is None:
        raise ValueError("No IFC file loaded")

    try:
        alignment = ifc_file.by_id(alignment_id)
    except RuntimeError:
        raise ValueError(f"Alignment with ID {alignment_id} not found")

    if not alignment.is_a("IfcAlignment"):
        raise ValueError(f"Entity {alignment_id} is not an IfcAlignment")

    # Validate alignment has horizontal layout
    h_layout = align_api.get_horizontal_layout(alignment)
    if h_layout is None:
        raise ValueError(f"Alignment '{alignment.Name}' has no horizontal layout")

    # Validate layout has real segments (not just zero-length terminator)
    if not alignment_tool.layout_has_real_segments(h_layout):
        raise ValueError(f"Alignment '{alignment.Name}' has no editable segments")

    # Back-calculate PI positions from segments
    pis = alignment_tool.back_calculate_pis_from_alignment(alignment)

    if len(pis) < 2:
        raise ValueError(f"Alignment '{alignment.Name}' must have at least 2 PIs")

    # Create temporary EMPTY objects at each PI location
    empties = alignment_tool.create_pi_edit_empties(alignment, pis)

    return empties


def exit_pi_edit_mode(
    ifc_tool: "type[tool.Ifc]",
    alignment_tool: "type[tool.Alignment]",
    alignment_id: int,
    apply: bool,
) -> bool:
    """Exit PI edit mode for an alignment.

    Business logic for exiting PI edit mode:
    1. If apply=True:
       - Collect new PI positions from empties
       - Validate the new configuration
       - Regenerate alignment segments
    2. Always:
       - Remove temporary EMPTY objects
       - Return success status

    Args:
        ifc_tool: The IFC tool class
        alignment_tool: The Alignment tool class
        alignment_id: The IFC ID of the alignment being edited
        apply: If True, regenerate alignment with new PI positions

    Returns:
        True if successful

    Raises:
        ValueError: If alignment doesn't exist or regeneration fails
    """
    import ifcopenshell
    import ifcopenshell.api.alignment as align_api

    ifc_file = ifc_tool.get()
    if ifc_file is None:
        # No file loaded, just clean up empties
        alignment_tool.remove_pi_edit_empties(alignment_id)
        return True

    # Get alignment
    try:
        alignment = ifc_file.by_id(alignment_id)
    except RuntimeError:
        # Alignment was deleted, just clean up empties
        alignment_tool.remove_pi_edit_empties(alignment_id)
        return True

    if apply:
        # Collect PI positions from empties
        hpoints, radii = alignment_tool.collect_pis_from_empties(alignment_id)

        if len(hpoints) < 2:
            raise ValueError("At least 2 PIs are required")

        # Get alignment metadata for recreation
        alignment_name = alignment.Name or "Alignment"

        # Get start station from existing alignment (or default)
        start_station = 0.0
        try:
            h_layout = align_api.get_horizontal_layout(alignment)
            if h_layout:
                # Try to get existing start station from referent
                for rel in getattr(alignment, "IsNestedBy", []) or []:
                    for child in rel.RelatedObjects or []:
                        if child.is_a("IfcReferent"):
                            pos_el = child.ObjectPlacement
                            if pos_el and hasattr(pos_el, "PlacementRelTo"):
                                # Extract station value if available
                                pass
        except Exception:
            pass  # Use default start_station

        # Remove empties BEFORE deleting alignment (they're parented to it)
        alignment_tool.remove_pi_edit_empties(alignment_id)

        # Remove old alignment hierarchy from Blender
        alignment_tool.remove_alignment_hierarchy(alignment)

        # Delete old IFC alignment
        ifcopenshell.api.run("root.remove_product", ifc_file, product=alignment)

        # Create new alignment with updated PI positions
        new_alignment = alignment_tool.safe_create_alignment_by_pi_method(
            ifc_file,
            name=alignment_name,
            hpoints=hpoints,
            radii=radii,
            start_station=start_station,
        )

        # Create new Blender hierarchy
        alignment_tool.create_hierarchy_for_alignment(new_alignment)

        return True
    else:
        # Cancel - just remove empties without regenerating
        alignment_tool.remove_pi_edit_empties(alignment_id)
        return True
