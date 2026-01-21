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


"""Property groups for the alignment module"""

import bpy
from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
)


def get_pi_type_items(self, context):
    """Get available PI types based on position in list"""
    # First and last PIs are always endpoints (no curve)
    # Interior PIs can have curves
    return [
        ("ENDPOINT", "Endpoint", "Start or end point (no curve)"),
        ("TANGENT", "Tangent", "Pass-through point (no curve)"),
        ("CURVE", "Curve", "Point of intersection with curve"),
    ]


def _on_radius_update(self, context):
    """Callback when radius property changes.

    This dynamically imports the operator module to call on_radius_changed,
    avoiding circular imports since prop.py is imported before operator.py.
    """
    from . import operator as ops

    ops.on_radius_changed(self, context)


class AlignmentPI(PropertyGroup):
    """Property group for a single PI (Point of Intersection)

    In the PI method, alignments are defined by:
    - Endpoint PIs: Start (POB) and End (POE) points
    - Interior PIs: Points where tangents intersect, optionally with curves
    """

    # Coordinates
    x: FloatProperty(
        name="X",
        description="X coordinate (Easting)",
        default=0.0,
        precision=3,
        unit="LENGTH",
    )

    y: FloatProperty(
        name="Y",
        description="Y coordinate (Northing)",
        default=0.0,
        precision=3,
        unit="LENGTH",
    )

    # PI Type
    pi_type: EnumProperty(
        name="Type",
        description="Type of PI point",
        items=[
            ("ENDPOINT", "Endpoint", "Start or end point (no curve)"),
            ("TANGENT", "Tangent", "Pass-through point (no curve)"),
            ("CURVE", "Curve", "Point of intersection with curve"),
        ],
        default="TANGENT",
    )

    # Curve parameters (only used when pi_type == "CURVE")
    radius: FloatProperty(
        name="Radius",
        description="Curve radius (0 = no curve, sharp angle)",
        default=0.0,
        min=0.0,
        precision=3,
        unit="LENGTH",
        update=_on_radius_update,
    )

    # Computed/display values (updated by recalculate operator)
    length_to_next: FloatProperty(
        name="Length",
        description="Length of tangent to next PI",
        default=0.0,
        precision=3,
        unit="LENGTH",
    )

    direction_to_next: FloatProperty(
        name="Direction",
        description="Bearing/direction to next PI (degrees)",
        default=0.0,
        precision=4,
        subtype="ANGLE",
    )

    # Station at this PI (computed)
    station: FloatProperty(
        name="Station",
        description="Station value at this PI",
        default=0.0,
        precision=2,
    )

    # Selection state
    is_selected: BoolProperty(
        name="Selected",
        description="Whether this PI is selected for editing",
        default=False,
    )


class AlignmentSegmentItem(PropertyGroup):
    """Property group for displaying alignment segments in a UIList"""

    name: StringProperty(name="Name", default="")
    segment_type: StringProperty(name="Type", default="LINE")
    length: FloatProperty(name="Length", default=0.0, unit="LENGTH")
    ifc_id: IntProperty(name="IFC ID", default=0)


class AlignmentDisplayRow(PropertyGroup):
    """Property group for interleaved point/segment display in the table.

    This creates the Civil 3D-style view where points and segments
    are shown on separate rows:
        Point 1 (End)
          Segment 1 (Tan)
        Point 2 (Tan)
          Segment 2 (Tan)
        ...
    """

    # Row type discriminator
    row_type: EnumProperty(
        name="Row Type",
        items=[
            ("POINT", "Point", "A PI point row"),
            ("SEGMENT", "Segment", "A segment row between points"),
        ],
        default="POINT",
    )

    # Segment number (1, 2, 3...) - only for SEGMENT rows
    segment_number: IntProperty(name="Segment #", default=0)

    # Point index in the pis collection - for both types
    # For POINT rows: the PI index
    # For SEGMENT rows: the starting PI index of this segment
    pi_index: IntProperty(name="PI Index", default=0)

    # Display type string (End, Tan, Curve for points; Tan, Curve for segments)
    display_type: StringProperty(name="Type", default="")

    # Point coordinates (only for POINT rows)
    x: FloatProperty(name="X", default=0.0, precision=3, unit="LENGTH")
    y: FloatProperty(name="Y", default=0.0, precision=3, unit="LENGTH")

    # Segment properties (only for SEGMENT rows)
    length: FloatProperty(name="Length", default=0.0, precision=2, unit="LENGTH")
    radius: FloatProperty(name="Radius", default=0.0, precision=2, unit="LENGTH")
    arc_length: FloatProperty(name="Arc Length", default=0.0, precision=2, unit="LENGTH")


class SaikeiAlignmentProperties(PropertyGroup):
    """Properties for the alignment module"""

    # Active alignment selection
    active_alignment_id: IntProperty(
        name="Active Alignment ID",
        description="IFC entity ID of the active alignment",
        default=0,
    )

    active_alignment_name: StringProperty(
        name="Active Alignment",
        description="Name of the currently active alignment",
        default="",
    )

    # New alignment creation properties
    new_alignment_name: StringProperty(
        name="Name",
        description="Name for new alignment",
        default="Alignment 1",
    )

    start_station: FloatProperty(
        name="Start Station",
        description="Starting station value (e.g., 10000 for 100+00)",
        default=10000.0,
        min=0.0,
    )

    # PI collection for PI method creation
    pis: CollectionProperty(type=AlignmentPI)
    active_pi_index: IntProperty(name="Active PI", default=0)

    # Segment display
    segments: CollectionProperty(type=AlignmentSegmentItem)
    active_segment_index: IntProperty(name="Active Segment", default=0)

    # Combined point/segment display rows (for Civil 3D-style table)
    display_rows: CollectionProperty(type=AlignmentDisplayRow)
    active_display_row_index: IntProperty(name="Active Display Row", default=0)

    # Editing state
    is_editing: BoolProperty(
        name="Is Editing",
        description="Whether alignment is being edited",
        default=False,
    )

    # Display options
    show_pi_markers: BoolProperty(
        name="Show PI Markers",
        description="Show PI markers in viewport",
        default=True,
    )

    show_station_labels: BoolProperty(
        name="Show Station Labels",
        description="Show station labels along alignment",
        default=True,
    )

    station_interval: FloatProperty(
        name="Station Interval",
        description="Interval between station markers",
        default=100.0,
        min=1.0,
        unit="LENGTH",
    )
