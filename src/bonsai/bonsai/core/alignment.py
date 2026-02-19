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
orchestration. All calculations, algorithms, and IFC operations are
in the tool layer. Functions receive tool classes as parameters
following Bonsai's dependency injection pattern.

NOTE: Math, calculations, algorithms, and IFC API calls belong in
tool/alignment.py. This module only handles:
- Business rules and validation
- Workflow orchestration (calling tool methods in sequence)
- Decision-making about what should happen
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ifcopenshell
    from .. import tool


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

    # Validate alignment has horizontal layout (delegated to tool)
    h_layout = alignment_tool.get_horizontal_layout(alignment)
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
       - Update alignment segments in-place (preserves alignment ID)
    2. Always:
       - Remove temporary EMPTY objects
       - Return success status

    This function modifies the alignment segments in-place rather than
    deleting and recreating the alignment. This preserves the alignment's
    IFC entity ID, preventing stale reference issues.

    Args:
        ifc_tool: The IFC tool class
        alignment_tool: The Alignment tool class
        alignment_id: The IFC ID of the alignment being edited
        apply: If True, update alignment with new PI positions

    Returns:
        True if successful

    Raises:
        ValueError: If alignment doesn't exist or update fails
    """
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

        # Get horizontal layout (delegated to tool)
        h_layout = alignment_tool.get_horizontal_layout(alignment)
        if h_layout is None:
            raise ValueError("Alignment has no horizontal layout")

        # Remove empties before modifying segments
        alignment_tool.remove_pi_edit_empties(alignment_id)

        # Remove Blender visualization for segments (not the whole hierarchy)
        alignment_tool.remove_layout_segment_objects(h_layout)

        # Clear existing IFC segments and add new ones (delegated to tool)
        alignment_tool.clear_layout_segments(h_layout)
        alignment_tool.layout_by_pi_method(h_layout, hpoints, radii)

        # Refresh Blender visualization for new segments
        layout_obj = ifc_tool.get_object(h_layout)
        if layout_obj:
            alignment_tool.create_objects_for_layout_segments(h_layout, layout_obj)

        return True
    else:
        # Cancel - just remove empties without regenerating
        alignment_tool.remove_pi_edit_empties(alignment_id)
        return True
