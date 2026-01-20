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


"""Operators for the alignment module

These operators wrap ifcopenshell.api.alignment functions and integrate
with Bonsai for IFC file management.

Architecture (following Bonsai pattern):
- Operators call core functions, passing tool implementations
- core/ contains pure Python logic (no bpy)
- tool/ contains Blender implementations
"""

import math

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty, IntProperty
from bpy_extras.io_utils import ImportHelper

import ifcopenshell.api.alignment

# Import from Saikei's layered architecture (relative imports)
# From civil/module/alignment/operator.py -> go up 4 levels to package root
from .... import tool
from ....core import alignment as core


def poll_ifc4x3(cls, context):
    """Standard poll method for IFC4X3 requirement"""
    ifc = tool.Alignment.get_ifc_file()
    if ifc is None:
        cls.poll_message_set("No IFC file loaded. Open an IFC file via Bonsai.")
        return False
    if ifc.schema != "IFC4X3":
        cls.poll_message_set(f"Schema is {ifc.schema}. Alignments require IFC4X3.")
        return False
    return True


def get_alignment_by_id(ifc, alignment_id):
    """Safely get an alignment by ID, returning None if not found.

    This handles the case where the IFC entity no longer exists
    (e.g., after undo or external modification).
    """
    if alignment_id == 0:
        return None
    try:
        entity = ifc.by_id(alignment_id)
        # Verify it's actually an alignment
        if entity and entity.is_a("IfcAlignment"):
            return entity
        return None
    except RuntimeError:
        # Entity not found in IFC file
        return None


def clear_invalid_alignment_reference(props):
    """Clear active alignment reference if it's invalid."""
    props.active_alignment_id = 0
    props.active_alignment_name = ""


def sync_pis_from_ifc(props):
    """Sync PI Editor data from IFC alignment.

    This is called on undo/redo to ensure the PI Editor reflects the current
    IFC state. It extracts PI data from the alignment's horizontal segments.

    If no active alignment exists or it's invalid, clears the PI Editor.

    Returns:
        bool: True if sync was successful, False if alignment was cleared.
    """
    ifc = tool.Alignment.get_ifc_file()
    if ifc is None:
        # No IFC file - clear everything
        props.pis.clear()
        props.active_pi_index = 0
        clear_invalid_alignment_reference(props)
        rebuild_display_rows(props)
        return False

    if props.active_alignment_id == 0:
        # No active alignment - just rebuild display
        rebuild_display_rows(props)
        return True

    alignment = get_alignment_by_id(ifc, props.active_alignment_id)
    if alignment is None:
        # Alignment no longer exists - clear everything
        props.pis.clear()
        props.active_pi_index = 0
        clear_invalid_alignment_reference(props)
        rebuild_display_rows(props)
        return False

    # Alignment exists - extract PI data from IFC segments
    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    if not h_layout:
        # No horizontal layout - rebuild display with current props
        rebuild_display_rows(props)
        return True

    segments = ifcopenshell.api.alignment.get_layout_segments(h_layout)
    if not segments:
        # No segments - rebuild display with current props
        rebuild_display_rows(props)
        return True

    # Extract PIs from segment data
    # This reconstructs approximate PIs from the IFC segment geometry
    extracted_pis = _extract_pis_from_segments(segments)

    if not extracted_pis:
        # Couldn't extract - keep current props.pis
        rebuild_display_rows(props)
        return True

    # Update props.pis with extracted data
    props.pis.clear()
    for pi_data in extracted_pis:
        pi = props.pis.add()
        pi.x = pi_data["x"]
        pi.y = pi_data["y"]
        pi.pi_type = pi_data["pi_type"]
        pi.radius = pi_data.get("radius", 0.0)

    props.active_pi_index = 0

    # Recalculate geometry and rebuild display
    recalculate_pi_geometry(props)
    return True


def _extract_pis_from_segments(segments):
    """Extract PI data from IFC alignment segments.

    This reconstructs PI coordinates and types from the horizontal segment
    design parameters. It handles:
    - LINE segments (tangent lines)
    - CIRCULARARC segments (horizontal curves)

    Args:
        segments: List of IfcAlignmentSegment entities

    Returns:
        List of dicts with keys: x, y, pi_type, radius (optional)
    """
    pis = []

    # Filter out zero-length terminal segments
    real_segments = []
    for seg in segments:
        if hasattr(seg, "DesignParameters") and seg.DesignParameters:
            dp = seg.DesignParameters
            if dp.SegmentLength > 0.0001:
                real_segments.append(seg)

    if not real_segments:
        return []

    # Track which segments are curves and their indices
    curve_indices = set()
    for i, seg in enumerate(real_segments):
        dp = seg.DesignParameters
        if dp.PredefinedType == "CIRCULARARC":
            curve_indices.add(i)

    # First PI: start of first segment
    first_dp = real_segments[0].DesignParameters
    start_coords = first_dp.StartPoint.Coordinates
    pis.append(
        {
            "x": float(start_coords[0]),
            "y": float(start_coords[1]),
            "pi_type": "ENDPOINT",
            "radius": 0.0,
        }
    )

    # Process interior points
    i = 0
    while i < len(real_segments):
        dp = real_segments[i].DesignParameters

        if dp.PredefinedType == "CIRCULARARC":
            # This is a curve - calculate PI from curve geometry
            # PI is at the intersection of incoming and outgoing tangents
            pi_data = _calculate_pi_from_curve(real_segments, i)
            if pi_data:
                pis.append(pi_data)
            i += 1
        elif dp.PredefinedType == "LINE":
            # Check if next segment is also a LINE (sharp angle, no curve)
            if i < len(real_segments) - 1:
                next_dp = real_segments[i + 1].DesignParameters
                if next_dp.PredefinedType == "LINE":
                    # End of this LINE is a PI with no curve
                    end_coords = _calculate_segment_endpoint(dp)
                    pis.append(
                        {
                            "x": float(end_coords[0]),
                            "y": float(end_coords[1]),
                            "pi_type": "TANGENT",
                            "radius": 0.0,
                        }
                    )
            i += 1
        else:
            # Other segment type - skip for now
            i += 1

    # Last PI: end of last segment
    last_dp = real_segments[-1].DesignParameters
    end_coords = _calculate_segment_endpoint(last_dp)
    # Only add if it's different from the last PI we added
    if pis:
        last_pi = pis[-1]
        dist = math.sqrt((end_coords[0] - last_pi["x"]) ** 2 + (end_coords[1] - last_pi["y"]) ** 2)
        if dist > 0.001:  # More than 1mm apart
            pis.append(
                {
                    "x": float(end_coords[0]),
                    "y": float(end_coords[1]),
                    "pi_type": "ENDPOINT",
                    "radius": 0.0,
                }
            )

    return pis


def _calculate_segment_endpoint(design_params):
    """Calculate the endpoint of a horizontal segment.

    Args:
        design_params: IfcAlignmentHorizontalSegment

    Returns:
        Tuple (x, y) of endpoint coordinates
    """
    start = design_params.StartPoint.Coordinates
    start_x = float(start[0])
    start_y = float(start[1])

    # StartDirection is in radians (counter-clockwise from east)
    direction = float(design_params.StartDirection)
    length = float(design_params.SegmentLength)

    if design_params.PredefinedType == "LINE":
        # Simple line endpoint
        end_x = start_x + length * math.cos(direction)
        end_y = start_y + length * math.sin(direction)
        return (end_x, end_y)

    elif design_params.PredefinedType == "CIRCULARARC":
        # Arc endpoint calculation
        radius = abs(float(design_params.StartRadiusOfCurvature or design_params.EndRadiusOfCurvature or 0))
        if radius == 0:
            # Fallback to line calculation
            end_x = start_x + length * math.cos(direction)
            end_y = start_y + length * math.sin(direction)
            return (end_x, end_y)

        # Determine curve direction (clockwise or counter-clockwise)
        start_radius = design_params.StartRadiusOfCurvature
        is_clockwise = start_radius is not None and start_radius < 0

        # Arc length to angle: theta = L / R
        theta = length / radius

        if is_clockwise:
            # Center is to the right of start direction
            center_dir = direction - math.pi / 2
            end_dir = direction - theta
        else:
            # Center is to the left of start direction
            center_dir = direction + math.pi / 2
            end_dir = direction + theta

        # Calculate center
        center_x = start_x + radius * math.cos(center_dir)
        center_y = start_y + radius * math.sin(center_dir)

        # Calculate endpoint
        if is_clockwise:
            end_x = center_x + radius * math.cos(end_dir + math.pi / 2)
            end_y = center_y + radius * math.sin(end_dir + math.pi / 2)
        else:
            end_x = center_x + radius * math.cos(end_dir - math.pi / 2)
            end_y = center_y + radius * math.sin(end_dir - math.pi / 2)

        return (end_x, end_y)

    else:
        # Unknown type - linear approximation
        end_x = start_x + length * math.cos(direction)
        end_y = start_y + length * math.sin(direction)
        return (end_x, end_y)


def _calculate_pi_from_curve(segments, curve_index):
    """Calculate the PI point from a curve segment.

    The PI is at the intersection of the incoming and outgoing tangents.
    For a circular arc: PI = PC + T * incoming_tangent = PT + T * (-outgoing_tangent)
    where T = R * tan(delta/2).

    Args:
        segments: List of all segments
        curve_index: Index of the curve segment

    Returns:
        Dict with PI data, or None if can't calculate
    """
    curve_seg = segments[curve_index]
    curve_dp = curve_seg.DesignParameters

    if curve_dp.PredefinedType != "CIRCULARARC":
        return None

    # Get curve parameters
    pc_coords = curve_dp.StartPoint.Coordinates
    pc_x = float(pc_coords[0])
    pc_y = float(pc_coords[1])

    start_dir = float(curve_dp.StartDirection)  # Incoming tangent direction
    arc_length = float(curve_dp.SegmentLength)

    radius = abs(float(curve_dp.StartRadiusOfCurvature or curve_dp.EndRadiusOfCurvature or 0))
    if radius == 0:
        return None

    # Determine if clockwise
    start_radius = curve_dp.StartRadiusOfCurvature
    is_clockwise = start_radius is not None and start_radius < 0

    # Calculate deflection angle from arc length: delta = L / R
    delta = arc_length / radius

    # Calculate tangent length: T = R * tan(delta/2)
    tangent_length = radius * math.tan(delta / 2)

    # PI = PC + T * incoming_tangent_unit_vector
    pi_x = pc_x + tangent_length * math.cos(start_dir)
    pi_y = pc_y + tangent_length * math.sin(start_dir)

    return {
        "x": pi_x,
        "y": pi_y,
        "pi_type": "CURVE",
        "radius": radius,
    }


# =============================================================================
# Curve Geometry Helper Functions
# =============================================================================


def compute_deflection_angle(prev_pi, curr_pi, next_pi):
    """Compute the deflection angle at a PI point.

    Args:
        prev_pi: Previous PI (with x, y attributes)
        curr_pi: Current PI (with x, y attributes)
        next_pi: Next PI (with x, y attributes)

    Returns:
        Deflection angle in radians (signed: positive=left, negative=right)
    """
    # Incoming tangent direction
    dx1 = curr_pi.x - prev_pi.x
    dy1 = curr_pi.y - prev_pi.y
    angle1 = math.atan2(dy1, dx1)

    # Outgoing tangent direction
    dx2 = next_pi.x - curr_pi.x
    dy2 = next_pi.y - curr_pi.y
    angle2 = math.atan2(dy2, dx2)

    # Deflection angle
    deflection = angle2 - angle1

    # Normalize to [-pi, pi]
    while deflection > math.pi:
        deflection -= 2 * math.pi
    while deflection < -math.pi:
        deflection += 2 * math.pi

    return deflection


def compute_arc_length_for_pi(props, pi_index):
    """Compute arc length for a curve at the given PI.

    Arc length L = R * |delta| where delta is the deflection angle.

    Args:
        props: SaikeiAlignmentProperties
        pi_index: Index of the PI with the curve

    Returns:
        Arc length in same units as radius (meters)
    """
    pis = props.pis
    if pi_index <= 0 or pi_index >= len(pis) - 1:
        return 0.0

    prev_pi = pis[pi_index - 1]
    curr_pi = pis[pi_index]
    next_pi = pis[pi_index + 1]

    if curr_pi.radius <= 0:
        return 0.0

    deflection = compute_deflection_angle(prev_pi, curr_pi, next_pi)
    return curr_pi.radius * abs(deflection)


def compute_tangent_length_at_pi(props, pi_index):
    """Compute the tangent length T at a PI with a curve.

    Tangent length T = R * tan(|delta|/2)

    Args:
        props: SaikeiAlignmentProperties
        pi_index: Index of the PI with the curve

    Returns:
        Tangent length (distance from PI to PC or PT)
    """
    pis = props.pis
    if pi_index <= 0 or pi_index >= len(pis) - 1:
        return 0.0

    prev_pi = pis[pi_index - 1]
    curr_pi = pis[pi_index]
    next_pi = pis[pi_index + 1]

    if curr_pi.radius <= 0:
        return 0.0

    deflection = compute_deflection_angle(prev_pi, curr_pi, next_pi)
    return curr_pi.radius * math.tan(abs(deflection) / 2)


def compute_segment_length(props, start_pi_index, account_for_curves=True):
    """Compute the length of a tangent segment between two PIs.

    If curves exist at the start or end PI, the segment is shortened
    to PC (Point of Curvature) or PT (Point of Tangency).

    Args:
        props: SaikeiAlignmentProperties
        start_pi_index: Index of the starting PI
        account_for_curves: If True, subtract tangent lengths for adjacent curves

    Returns:
        Segment length in meters
    """
    pis = props.pis
    if start_pi_index < 0 or start_pi_index >= len(pis) - 1:
        return 0.0

    start_pi = pis[start_pi_index]
    end_pi = pis[start_pi_index + 1]

    # Full length between PIs
    dx = end_pi.x - start_pi.x
    dy = end_pi.y - start_pi.y
    full_length = math.sqrt(dx * dx + dy * dy)

    if not account_for_curves:
        return full_length

    # Subtract tangent length if start PI has a curve (segment starts at PT)
    if start_pi_index > 0 and start_pi.radius > 0:
        full_length -= compute_tangent_length_at_pi(props, start_pi_index)

    # Subtract tangent length if end PI has a curve (segment ends at PC)
    if start_pi_index + 1 < len(pis) - 1 and end_pi.radius > 0:
        full_length -= compute_tangent_length_at_pi(props, start_pi_index + 1)

    return max(0.0, full_length)


def on_radius_changed(pi, context):
    """Callback when PI radius is changed. Triggers geometry recalculation.

    This is called from the AlignmentPI.radius property's update callback.
    When a radius is entered on a Mid point, this triggers:
    1. Recalculation of PI geometry (lengths, stations)
    2. Rebuild of display_rows (Mid point becomes Curve segment)
    3. If an active alignment exists, regeneration of IFC entities
    """
    props = context.scene.SaikeiAlignmentProperties
    recalculate_pi_geometry(props)

    # If there's an active alignment, trigger IFC regeneration
    # This is handled by recalculate_pi_geometry when active_alignment_id is set


def recalculate_pi_geometry(props):
    """Recalculate lengths and stations for all PIs using core logic."""
    pis = props.pis
    if len(pis) < 2:
        rebuild_display_rows(props)
        return

    # Extract PI coordinates for pure Python calculation
    pi_coords = [(pi.x, pi.y) for pi in pis]

    # Use core function for calculation
    result = core.calculate_pi_geometry(pi_coords, props.start_station)

    # Update Blender properties with results
    tool.Alignment.update_pi_properties(props, result)

    # Rebuild the display rows for the interleaved table view
    rebuild_display_rows(props)


def rebuild_display_rows(props):
    """Rebuild the display_rows collection from the pis collection.

    Creates an interleaved view of points and segments in Civil 3D style:
        End point (POB)
          Tangent segment 1
        Mid point (or Curve segment if radius > 0)
          Tangent segment 2
        End point (POE)

    When a Mid point has a curve (radius > 0), it becomes a Curve segment row
    instead of a point row, showing PI coordinates + arc length + radius.
    """
    props.display_rows.clear()

    pis = props.pis
    if len(pis) == 0:
        return

    segment_num = 0
    i = 0

    while i < len(pis):
        pi = pis[i]
        is_interior = i > 0 and i < len(pis) - 1
        has_curve = is_interior and pi.radius > 0

        if has_curve:
            # Interior PI with curve: becomes a CURVE SEGMENT row
            # This replaces what would have been a Mid point row
            segment_num += 1
            curve_row = props.display_rows.add()
            curve_row.row_type = "SEGMENT"
            curve_row.segment_number = segment_num
            curve_row.pi_index = i
            curve_row.display_type = "Curve"
            curve_row.x = pi.x  # Show PI coordinates on curve row
            curve_row.y = pi.y
            curve_row.radius = pi.radius
            curve_row.arc_length = compute_arc_length_for_pi(props, i)
        else:
            # Regular point row (End or Mid without curve)
            point_row = props.display_rows.add()
            point_row.row_type = "POINT"
            point_row.pi_index = i

            if pi.pi_type == "ENDPOINT":
                point_row.display_type = "End"
            else:
                point_row.display_type = "Mid"

            point_row.x = pi.x
            point_row.y = pi.y

        # Add tangent segment row after this point/curve (except after last PI)
        if i < len(pis) - 1:
            # Check if next PI also has a curve (affects segment length calculation)
            next_pi = pis[i + 1]
            next_has_curve = (i + 1 < len(pis) - 1) and next_pi.radius > 0

            segment_num += 1
            seg_row = props.display_rows.add()
            seg_row.row_type = "SEGMENT"
            seg_row.segment_number = segment_num
            seg_row.pi_index = i
            seg_row.display_type = "Tan"

            # Compute segment length accounting for curves at either end
            seg_row.length = compute_segment_length(props, i, account_for_curves=True)

        i += 1


# =============================================================================
# PI Management Operators
# =============================================================================


class SAIKEI_OT_add_pi(Operator):
    """Add a new PI point to the list"""

    bl_idname = "saikei.add_pi"
    bl_label = "Add PI"
    bl_description = "Add a new PI (Point of Intersection) to the alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        props = context.scene.SaikeiAlignmentProperties

        # Add new PI
        pi = props.pis.add()

        # Set default position based on existing PIs
        if len(props.pis) == 1:
            # First PI - start at origin
            pi.x = 0.0
            pi.y = 0.0
            pi.pi_type = "ENDPOINT"
        elif len(props.pis) == 2:
            # Second PI - offset from first
            prev = props.pis[0]
            pi.x = prev.x + 100.0
            pi.y = prev.y
            pi.pi_type = "ENDPOINT"
        else:
            # Additional PIs - extrapolate from last two
            prev = props.pis[-2]
            prev_prev = props.pis[-3] if len(props.pis) > 2 else prev
            dx = prev.x - prev_prev.x if len(props.pis) > 2 else 100.0
            dy = prev.y - prev_prev.y if len(props.pis) > 2 else 0.0
            pi.x = prev.x + dx
            pi.y = prev.y + dy
            pi.pi_type = "TANGENT"

            # Previous endpoint becomes tangent or curve
            props.pis[-2].pi_type = "TANGENT"

        # Make new PI active
        props.active_pi_index = len(props.pis) - 1

        # Recalculate geometry
        recalculate_pi_geometry(props)

        return {"FINISHED"}


class SAIKEI_OT_remove_pi(Operator):
    """Remove the selected PI point"""

    bl_idname = "saikei.remove_pi"
    bl_label = "Remove PI"
    bl_description = "Remove the selected PI from the alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if len(props.pis) == 0:
            cls.poll_message_set("No PIs to remove")
            return False
        # Check if a POINT row is selected (can't remove from SEGMENT row selection)
        if props.display_rows:
            idx = props.active_display_row_index
            if 0 <= idx < len(props.display_rows):
                if props.display_rows[idx].row_type != "POINT":
                    cls.poll_message_set("Select a point row to remove")
                    return False
        return True

    def execute(self, context):
        props = context.scene.SaikeiAlignmentProperties

        # Get the PI index from the selected display row
        pi_index = -1
        if props.display_rows:
            idx = props.active_display_row_index
            if 0 <= idx < len(props.display_rows):
                row = props.display_rows[idx]
                if row.row_type == "POINT":
                    pi_index = row.pi_index

        # Fallback to active_pi_index if display_rows isn't being used
        if pi_index < 0:
            pi_index = props.active_pi_index

        if 0 <= pi_index < len(props.pis):
            props.pis.remove(pi_index)
            props.active_pi_index = min(pi_index, len(props.pis) - 1)

            # Recalculate geometry (also rebuilds display_rows)
            recalculate_pi_geometry(props)

            # Reset display row index to first row if needed
            if len(props.display_rows) > 0:
                props.active_display_row_index = min(props.active_display_row_index, len(props.display_rows) - 1)
            else:
                props.active_display_row_index = 0

        return {"FINISHED"}


class SAIKEI_OT_pick_pi_from_viewport(Operator):
    """Add PI points by clicking in the 3D viewport"""

    bl_idname = "saikei.pick_pi_from_viewport"
    bl_label = "Pick PI from Viewport"
    bl_description = "Click in the viewport to add PI points. Right-click or Escape to finish."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        context.window.cursor_set("CROSSHAIR")
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "Click to add PIs. Right-click or Escape to finish.")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            # Raycast to ground plane (Z=0)
            coord = self.get_ground_intersection(context, event)
            if coord:
                self.add_pi_at_location(context, coord)
                context.area.tag_redraw()
            return {"RUNNING_MODAL"}

        elif event.type in {"RIGHTMOUSE", "ESC"}:
            context.window.cursor_set("DEFAULT")
            self.report({"INFO"}, "Finished adding PIs")
            return {"FINISHED"}

        # Allow viewport navigation
        elif event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            return {"PASS_THROUGH"}

        return {"RUNNING_MODAL"}

    def get_ground_intersection(self, context, event):
        """Raycast from mouse to Z=0 ground plane"""
        from bpy_extras.view3d_utils import region_2d_to_origin_3d, region_2d_to_vector_3d

        region = context.region
        rv3d = context.region_data
        coord = (event.mouse_region_x, event.mouse_region_y)

        origin = region_2d_to_origin_3d(region, rv3d, coord)
        direction = region_2d_to_vector_3d(region, rv3d, coord)

        # Intersect with Z=0 plane
        if direction.z != 0:
            t = -origin.z / direction.z
            if t > 0:  # In front of camera
                hit = origin + direction * t
                return (hit.x, hit.y)
        return None

    def add_pi_at_location(self, context, coord):
        """Add a new PI at the given (x, y) coordinate"""
        props = context.scene.SaikeiAlignmentProperties

        pi = props.pis.add()
        pi.x = coord[0]
        pi.y = coord[1]

        # Determine PI type based on position in list
        if len(props.pis) == 1:
            pi.pi_type = "ENDPOINT"
        elif len(props.pis) == 2:
            pi.pi_type = "ENDPOINT"
        else:
            pi.pi_type = "TANGENT"
            # Previous endpoint becomes tangent
            if len(props.pis) >= 2:
                props.pis[-2].pi_type = "TANGENT"

        props.active_pi_index = len(props.pis) - 1
        recalculate_pi_geometry(props)


class SAIKEI_OT_recalculate_pis(Operator):
    """Recalculate PI geometry and update IFC/visualization"""

    bl_idname = "saikei.recalculate_pis"
    bl_label = "Recalculate PIs"
    bl_description = "Recalculate geometry, update IFC segments, and refresh visualization"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if len(props.pis) < 2:
            cls.poll_message_set("Need at least 2 PIs to recalculate")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        # Recalculate geometry in UI properties
        recalculate_pi_geometry(props)

        # If there's an active alignment, recreate it with updated data
        # We recreate the entire alignment because modifying segments in place
        # can leave the IFC layout in an inconsistent state
        if props.active_alignment_id != 0:
            alignment = get_alignment_by_id(ifc, props.active_alignment_id)
            if alignment is None:
                # Alignment no longer exists (e.g., after undo) - clear reference
                clear_invalid_alignment_reference(props)
                self.report({"WARNING"}, "Active alignment no longer exists. Reference cleared.")
                return {"FINISHED"}
            if alignment:
                # Save the alignment name
                alignment_name = alignment.Name or props.new_alignment_name

                # Remove the entire alignment hierarchy (Blender objects)
                tool.Alignment.remove_alignment_hierarchy(alignment)

                # Remove the IFC alignment entity entirely
                ifcopenshell.api.run("root.remove_product", ifc, product=alignment)

                # Collect updated PI data
                hpoints = [(pi.x, pi.y) for pi in props.pis]
                radii = [pi.radius for pi in props.pis[1:-1]]

                # Create a fresh alignment with the same name
                # Use safe wrapper to validate/cleanup before creating
                new_alignment = tool.Alignment.safe_create_alignment_by_pi_method(
                    ifc,
                    name=alignment_name,
                    hpoints=hpoints,
                    radii=radii,
                    start_station=props.start_station,
                )

                # Create Blender hierarchy for the new alignment
                tool.Alignment.create_hierarchy_for_alignment(new_alignment)

                # Update the active alignment ID to reference the new entity
                props.active_alignment_id = new_alignment.id()
                props.active_alignment_name = alignment_name

                self.report({"INFO"}, f"Updated alignment '{alignment_name}' with {len(hpoints)} PIs")
                return {"FINISHED"}

        # No active alignment - just report geometry recalculation
        total_length = sum(pi.length_to_next for pi in props.pis)
        self.report({"INFO"}, f"Recalculated {len(props.pis)} PIs, total length: {total_length:.2f}")
        return {"FINISHED"}


class SAIKEI_OT_clear_pis(Operator):
    """Clear all PI points and optionally remove visualization/IFC data"""

    bl_idname = "saikei.clear_pis"
    bl_label = "Clear All PIs"
    bl_description = "Remove all PI points and clear segment visualization"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if len(props.pis) == 0:
            cls.poll_message_set("No PIs to clear")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        removed_objects = 0

        # If there's an active alignment, remove it entirely (Blender + IFC)
        # This ensures we don't leave the IFC in an inconsistent state
        if props.active_alignment_id != 0:
            alignment = get_alignment_by_id(ifc, props.active_alignment_id)
            if alignment:
                # Remove all Blender objects for this alignment
                removed_objects = tool.Alignment.remove_alignment_hierarchy(alignment)

                # Remove the IFC alignment entity entirely
                ifcopenshell.api.run("root.remove_product", ifc, product=alignment)

                # Clear the active alignment reference
                props.active_alignment_id = 0
                props.active_alignment_name = ""

        # Clear the PI list in the UI
        props.pis.clear()
        props.active_pi_index = 0

        # Clear the display rows
        props.display_rows.clear()
        props.active_display_row_index = 0

        if removed_objects > 0:
            self.report({"INFO"}, f"Cleared all PIs and removed {removed_objects} objects")
        else:
            self.report({"INFO"}, "Cleared all PIs")
        return {"FINISHED"}


# =============================================================================
# Creation Operators
# =============================================================================


class SAIKEI_OT_create_alignment(Operator):
    """Create a new IFC alignment"""

    bl_idname = "saikei.create_alignment"
    bl_label = "Create Alignment"
    bl_description = "Create a new empty IFC alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = ifcopenshell.api.alignment.create(
            ifc,
            name=props.new_alignment_name,
        )

        # Create full Blender hierarchy (alignment + layouts + segments)
        obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

        # Update UI
        props.active_alignment_name = props.new_alignment_name
        props.active_alignment_id = alignment.id()

        if obj:
            self.report({"INFO"}, f"Created alignment: {props.new_alignment_name}")
        else:
            self.report({"WARNING"}, f"Created IFC alignment but could not create Blender object")
        return {"FINISHED"}


class SAIKEI_OT_create_alignment_by_pi(Operator):
    """Create alignment using the PI (Point of Intersection) method"""

    bl_idname = "saikei.create_alignment_by_pi"
    bl_label = "Create by PI Method"
    bl_description = "Create alignment using PI points and curve radii. If an active alignment exists with no segments, adds to it instead of creating new."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if len(props.pis) < 2:
            cls.poll_message_set("Need at least 2 PI points")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        # Collect PI data
        hpoints = [(pi.x, pi.y) for pi in props.pis]
        radii = [pi.radius for pi in props.pis[1:-1]]

        # Check if there's an active alignment we should add to instead of creating new
        if props.active_alignment_id != 0:
            existing_alignment = get_alignment_by_id(ifc, props.active_alignment_id)
            if existing_alignment:
                h_layout = ifcopenshell.api.alignment.get_horizontal_layout(existing_alignment)
                if h_layout:
                    # Check if horizontal layout is empty (only has zero-length terminal or no segments)
                    segments = ifcopenshell.api.alignment.get_layout_segments(h_layout)
                    has_real_segments = False
                    for seg in segments:
                        if hasattr(seg, "DesignParameters") and seg.DesignParameters:
                            if seg.DesignParameters.SegmentLength > 0.0001:
                                has_real_segments = True
                                break

                    if not has_real_segments:
                        # Use existing alignment - add segments to it
                        # Use safe wrapper to validate layout has parent alignment
                        tool.Alignment.safe_layout_horizontal_by_pi_method(ifc, h_layout, hpoints, radii)

                        # Create/update Blender objects for the segments
                        alignment_obj = tool.Ifc.get_object(existing_alignment)
                        h_layout_obj = tool.Ifc.get_object(h_layout)

                        if not h_layout_obj and alignment_obj:
                            h_layout_obj = tool.Alignment.create_object_for_layout(h_layout, alignment_obj)

                        if h_layout_obj:
                            tool.Alignment.create_objects_for_layout_segments(h_layout, h_layout_obj)

                        self.report(
                            {"INFO"}, f"Added {len(hpoints)} PIs to existing alignment '{existing_alignment.Name}'"
                        )
                        return {"FINISHED"}

        # No suitable existing alignment - create a new one
        # Use safe wrapper to validate/cleanup before creating
        alignment = tool.Alignment.safe_create_alignment_by_pi_method(
            ifc,
            name=props.new_alignment_name,
            hpoints=hpoints,
            radii=radii,
            start_station=props.start_station,
        )

        # Create full Blender hierarchy (alignment + layouts + segments)
        obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

        props.active_alignment_name = props.new_alignment_name
        props.active_alignment_id = alignment.id()

        if obj:
            self.report({"INFO"}, f"Created new alignment '{props.new_alignment_name}' with {len(hpoints)} PIs")
        else:
            self.report({"WARNING"}, f"Created IFC alignment but could not create Blender object")
        return {"FINISHED"}


class SAIKEI_OT_import_alignment_csv(Operator, ImportHelper):
    """Import alignment from CSV file"""

    bl_idname = "saikei.import_alignment_csv"
    bl_label = "Import Alignment CSV"
    bl_description = "Import alignment definition from a CSV file"
    bl_options = {"REGISTER", "UNDO"}

    filename_ext = ".csv"
    filter_glob: StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = ifcopenshell.api.alignment.create_from_csv(ifc, self.filepath)

        # Create full Blender hierarchy (alignment + layouts + segments)
        obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

        props.active_alignment_name = alignment.Name or "Imported Alignment"
        props.active_alignment_id = alignment.id()

        self.report({"INFO"}, f"Imported alignment from {self.filepath}")
        return {"FINISHED"}


class SAIKEI_OT_create_alignment_polyline(Operator):
    """Create alignment as a polyline"""

    bl_idname = "saikei.create_alignment_polyline"
    bl_label = "Create as Polyline"
    bl_description = "Create alignment from a polyline (no curves)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        # Collect points from PIs (no radii)
        points = [(pi.x, pi.y) for pi in props.pis]

        if len(points) < 2:
            self.report({"ERROR"}, "Need at least 2 points for polyline")
            return {"CANCELLED"}

        alignment = ifcopenshell.api.alignment.create_as_polyline(
            ifc,
            name=props.new_alignment_name,
            points=points,
        )

        # Create full Blender hierarchy (alignment + layouts + segments)
        obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

        props.active_alignment_name = props.new_alignment_name
        props.active_alignment_id = alignment.id()

        self.report({"INFO"}, f"Created polyline alignment with {len(points)} points")
        return {"FINISHED"}


class SAIKEI_OT_create_alignment_offset(Operator):
    """Create alignment as an offset from existing alignment"""

    bl_idname = "saikei.create_alignment_offset"
    bl_label = "Create as Offset Curve"
    bl_description = "Create a new alignment offset from an existing alignment"
    bl_options = {"REGISTER", "UNDO"}

    offset_distance: FloatProperty(
        name="Offset Distance",
        description="Distance to offset (positive = right, negative = left)",
        default=10.0,
        unit="LENGTH",
    )

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        base_alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if base_alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Base alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        alignment = ifcopenshell.api.alignment.create_as_offset_curve(
            ifc,
            name=f"{props.new_alignment_name} (Offset)",
            base_alignment=base_alignment,
            offset=self.offset_distance,
        )

        # Create full Blender hierarchy (alignment + layouts + segments)
        obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

        self.report({"INFO"}, f"Created offset alignment at {self.offset_distance}m")
        return {"FINISHED"}


# =============================================================================
# Layout Operators
# =============================================================================


class SAIKEI_OT_add_vertical_layout(Operator):
    """Add vertical layout to an alignment"""

    bl_idname = "saikei.add_vertical_layout"
    bl_label = "Add Vertical Layout"
    bl_description = "Add an IfcAlignmentVertical to the active alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        vertical = ifcopenshell.api.alignment.add_vertical_layout(ifc, alignment)

        self.report({"INFO"}, "Added vertical layout")
        return {"FINISHED"}


class SAIKEI_OT_add_layout_segment(Operator):
    """Add a segment to an alignment layout"""

    bl_idname = "saikei.add_layout_segment"
    bl_label = "Add Layout Segment"
    bl_description = "Add a new segment to the alignment layout"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        # This operator would open a dialog for segment parameters
        self.report({"INFO"}, "Add segment - dialog coming soon")
        return {"FINISHED"}


class SAIKEI_OT_layout_horizontal_by_pi(Operator):
    """Layout horizontal alignment using PI method"""

    bl_idname = "saikei.layout_horizontal_by_pi"
    bl_label = "Layout Horizontal by PI"
    bl_description = "Layout the horizontal alignment using PI points"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        if len(props.pis) < 2:
            cls.poll_message_set("Need at least 2 PI points")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        if not h_layout:
            self.report({"ERROR"}, "Alignment has no horizontal layout")
            return {"CANCELLED"}

        pis = [(pi.x, pi.y) for pi in props.pis]
        radii = [pi.radius for pi in props.pis[1:-1]]

        # Create the IFC segments
        # Use safe wrapper to validate layout has parent alignment
        tool.Alignment.safe_layout_horizontal_by_pi_method(ifc, h_layout, pis, radii)

        # Find or create Blender object for the horizontal layout
        # Use Bonsai's Ifc tool (re-exported via saikei.tool)
        alignment_obj = tool.Ifc.get_object(alignment)
        h_layout_obj = tool.Ifc.get_object(h_layout)

        if not h_layout_obj and alignment_obj:
            # Create the horizontal layout object if it doesn't exist
            h_layout_obj = tool.Alignment.create_object_for_layout(h_layout, alignment_obj)

        # Create Blender objects for the newly created segments
        if h_layout_obj:
            tool.Alignment.create_objects_for_layout_segments(h_layout, h_layout_obj)

        self.report({"INFO"}, f"Laid out horizontal alignment with {len(pis)} PIs")
        return {"FINISHED"}


class SAIKEI_OT_layout_vertical_by_pi(Operator):
    """Layout vertical alignment using PI method"""

    bl_idname = "saikei.layout_vertical_by_pi"
    bl_label = "Layout Vertical by PI"
    bl_description = "Layout the vertical alignment using PVI points"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        # This would collect vertical PIs and create vertical layout
        self.report({"INFO"}, "Layout vertical - implementation coming soon")
        return {"FINISHED"}


# =============================================================================
# Stationing Operators
# =============================================================================


class SAIKEI_OT_add_stationing_referent(Operator):
    """Add a stationing referent to the alignment"""

    bl_idname = "saikei.add_stationing_referent"
    bl_label = "Add Stationing Referent"
    bl_description = "Add an IfcReferent for stationing"
    bl_options = {"REGISTER", "UNDO"}

    station: FloatProperty(
        name="Station",
        description="Station value for the referent (e.g., 10000 for 100+00)",
        default=10000.0,
    )

    name: StringProperty(
        name="Name",
        description="Name for the referent (leave blank to auto-generate)",
        default="",
    )

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        # Default station to start_station from props
        props = context.scene.SaikeiAlignmentProperties
        self.station = props.start_station
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "station")
        layout.prop(self, "name")
        # Show station notation preview
        station_str = format_station(self.station)
        layout.label(text=f"Station notation: {station_str}")

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        # Compute distance_along from station and start_station
        # distance_along = station - start_station
        distance_along = self.station - props.start_station

        # Auto-generate name if not provided
        name = self.name if self.name else format_station(self.station)

        # Use the alignment itself as the positioned product
        # (The referent marks a point on the alignment)
        positioned_product = alignment

        ifcopenshell.api.alignment.add_stationing_referent(
            ifc,
            alignment=alignment,
            distance_along=distance_along,
            station=self.station,
            name=name,
            positioned_product=positioned_product,
        )

        self.report({"INFO"}, f"Added referent '{name}' at station {self.station}")
        return {"FINISHED"}


def format_station(station_value):
    """Format a station value in standard notation (e.g., 10000 -> '100+00')"""
    # Station notation: divide by 100 for the main part, remainder for the offset
    # e.g., 10000 -> 100+00, 10050 -> 100+50, 10123.45 -> 101+23.45
    main = int(station_value // 100)
    offset = station_value % 100
    if offset == int(offset):
        return f"{main}+{int(offset):02d}"
    else:
        return f"{main}+{offset:05.2f}"


class SAIKEI_OT_name_segments(Operator):
    """Auto-name segments based on station values"""

    bl_idname = "saikei.name_segments"
    bl_label = "Name Segments"
    bl_description = "Automatically name segments with station-based labels"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        ifcopenshell.api.alignment.name_segments(ifc, alignment)

        self.report({"INFO"}, "Named alignment segments")
        return {"FINISHED"}


# =============================================================================
# Utility Operators
# =============================================================================


class SAIKEI_OT_create_representation(Operator):
    """Create geometric representation for alignment"""

    bl_idname = "saikei.create_representation"
    bl_label = "Create Representation"
    bl_description = "Create or update the geometric representation"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        ifcopenshell.api.alignment.create_representation(ifc, alignment)

        self.report({"INFO"}, "Created geometric representation")
        return {"FINISHED"}


class SAIKEI_OT_create_segment_representations(Operator):
    """Create representations for individual segments"""

    bl_idname = "saikei.create_segment_representations"
    bl_label = "Create Segment Representations"
    bl_description = "Create geometric representations for each segment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        ifcopenshell.api.alignment.create_segment_representations(ifc, alignment)

        self.report({"INFO"}, "Created segment representations")
        return {"FINISHED"}


class SAIKEI_OT_update_fallback_position(Operator):
    """Update the fallback position for the alignment"""

    bl_idname = "saikei.update_fallback_position"
    bl_label = "Update Fallback Position"
    bl_description = "Update the fallback position point"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        ifcopenshell.api.alignment.update_fallback_position(ifc, alignment)

        self.report({"INFO"}, "Updated fallback position")
        return {"FINISHED"}


class SAIKEI_OT_validate_segments(Operator):
    """Validate alignment segments"""

    bl_idname = "saikei.validate_segments"
    bl_label = "Validate Segments"
    bl_description = "Check for issues like zero-length segments"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.SaikeiAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            clear_invalid_alignment_reference(props)
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        if h_layout:
            has_zero = ifcopenshell.api.alignment.has_zero_length_segment(h_layout)
            if has_zero:
                self.report({"WARNING"}, "Alignment has zero-length segments")
            else:
                self.report({"INFO"}, "All segments valid")
        else:
            self.report({"WARNING"}, "No horizontal layout found")

        return {"FINISHED"}


class SAIKEI_OT_refresh_alignment_data(Operator):
    """Refresh alignment data display"""

    bl_idname = "saikei.refresh_alignment_data"
    bl_label = "Refresh Data"
    bl_description = "Refresh the alignment segment list"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        ifc = tool.Alignment.get_ifc_file()
        props = context.scene.SaikeiAlignmentProperties

        # Clear existing segments
        props.segments.clear()

        if props.active_alignment_id == 0:
            return {"FINISHED"}

        alignment = get_alignment_by_id(ifc, props.active_alignment_id)
        if alignment is None:
            # Alignment no longer exists - clear reference and return
            clear_invalid_alignment_reference(props)
            self.report({"WARNING"}, "Alignment no longer exists. Reference cleared.")
            return {"FINISHED"}

        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        if h_layout:
            segments = ifcopenshell.api.alignment.get_layout_segments(h_layout)
            for i, seg in enumerate(segments):
                item = props.segments.add()
                item.name = f"Segment {i + 1}"
                if hasattr(seg, "DesignParameters") and seg.DesignParameters:
                    dp = seg.DesignParameters
                    item.segment_type = dp.PredefinedType or "UNKNOWN"
                    item.length = dp.SegmentLength or 0.0
                item.ifc_id = seg.id()

        self.report({"INFO"}, f"Loaded {len(props.segments)} segments")
        return {"FINISHED"}
