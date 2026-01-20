# ==============================================================================
# Saikei Civil - Civil Engineering Tools for Blender
# Copyright (c) 2025 Michael Yoder / Desert Springs Civil Engineering PLLC
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Primary Author: Michael Yoder
# Company: Desert Springs Civil Engineering PLLC
# ==============================================================================


"""Alignment module for Saikei Civil

This module provides horizontal alignment tools using ifcopenshell.api.alignment.
"""

import bpy
from bpy.app.handlers import persistent
from . import ui, prop, operator


@persistent
def on_undo_redo(scene):
    """Handler called after undo/redo to sync PI Editor with IFC.

    When Blender undoes, both Blender properties and IFC state may change.
    This handler syncs the PI Editor to reflect the current IFC state:
    - If the active alignment still exists, extracts PI data from IFC segments
    - If the alignment was deleted/invalidated, clears the PI Editor
    - Rebuilds display_rows to match the synced state
    """
    if not hasattr(scene, "SaikeiAlignmentProperties"):
        return
    props = scene.SaikeiAlignmentProperties
    # Sync PI Editor from IFC to ensure consistency after undo/redo
    operator.sync_pis_from_ifc(props)


# All classes that need to be registered with Blender
classes = (
    # Property groups (must be registered before classes that use them)
    prop.AlignmentPI,
    prop.AlignmentSegmentItem,
    prop.AlignmentDisplayRow,
    prop.SaikeiAlignmentProperties,
    # UILists
    ui.SAIKEI_UL_alignment_pis,
    # Operators - PI Management
    operator.SAIKEI_OT_add_pi,
    operator.SAIKEI_OT_remove_pi,
    operator.SAIKEI_OT_pick_pi_from_viewport,
    operator.SAIKEI_OT_recalculate_pis,
    operator.SAIKEI_OT_clear_pis,
    # Operators - Creation
    operator.SAIKEI_OT_create_alignment,
    operator.SAIKEI_OT_create_alignment_by_pi,
    operator.SAIKEI_OT_import_alignment_csv,
    operator.SAIKEI_OT_create_alignment_polyline,
    operator.SAIKEI_OT_create_alignment_offset,
    # Operators - Layout
    operator.SAIKEI_OT_add_vertical_layout,
    operator.SAIKEI_OT_add_layout_segment,
    operator.SAIKEI_OT_layout_horizontal_by_pi,
    operator.SAIKEI_OT_layout_vertical_by_pi,
    # Operators - Stationing
    operator.SAIKEI_OT_add_stationing_referent,
    operator.SAIKEI_OT_name_segments,
    # Operators - Utilities
    operator.SAIKEI_OT_create_representation,
    operator.SAIKEI_OT_create_segment_representations,
    operator.SAIKEI_OT_update_fallback_position,
    operator.SAIKEI_OT_validate_segments,
    operator.SAIKEI_OT_refresh_alignment_data,
    # UI Panels
    ui.SAIKEI_PT_horizontal_alignment,
    ui.SAIKEI_PT_alignment_creation,
    ui.SAIKEI_PT_pi_editor,
    ui.SAIKEI_PT_alignment_stationing,
)


def register():
    """Register alignment module properties and handlers"""
    bpy.types.Scene.SaikeiAlignmentProperties = bpy.props.PointerProperty(type=prop.SaikeiAlignmentProperties)
    # Register undo/redo handlers to keep display_rows in sync
    bpy.app.handlers.undo_post.append(on_undo_redo)
    bpy.app.handlers.redo_post.append(on_undo_redo)


def unregister():
    """Unregister alignment module properties and handlers"""
    # Unregister handlers
    if on_undo_redo in bpy.app.handlers.undo_post:
        bpy.app.handlers.undo_post.remove(on_undo_redo)
    if on_undo_redo in bpy.app.handlers.redo_post:
        bpy.app.handlers.redo_post.remove(on_undo_redo)
    del bpy.types.Scene.SaikeiAlignmentProperties
