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

"""Alignment module for Saikei Civil

This module provides horizontal alignment tools using ifcopenshell.api.alignment.
"""

import bpy
from . import ui, prop, operator

# All classes that need to be registered with Blender
classes = (
    # Property groups (must be registered before classes that use them)
    prop.AlignmentPI,
    prop.AlignmentSegmentItem,
    prop.AlignmentDisplayRow,
    prop.SaikeiAlignmentProperties,
    # UILists
    ui.SAIKEI_UL_alignment_pis,
    ui.SAIKEI_UL_alignment_segments,
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
    ui.SAIKEI_PT_alignment_layout,
    ui.SAIKEI_PT_alignment_properties,
    ui.SAIKEI_PT_alignment_stationing,
    ui.SAIKEI_PT_alignment_utilities,
)


def register():
    """Register alignment module properties"""
    bpy.types.Scene.SaikeiAlignmentProperties = bpy.props.PointerProperty(
        type=prop.SaikeiAlignmentProperties
    )


def unregister():
    """Unregister alignment module properties"""
    del bpy.types.Scene.SaikeiAlignmentProperties
