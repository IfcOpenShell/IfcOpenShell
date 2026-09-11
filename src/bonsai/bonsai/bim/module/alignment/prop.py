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


"""Property groups for the alignment module"""

from bpy.types import PropertyGroup
from bpy.props import (
    StringProperty,
    FloatProperty,
    IntProperty,
    BoolProperty,
    CollectionProperty,
    EnumProperty,
)


import bpy


def _on_vertical_visibility_update(self, context):
    from .decorator import VerticalProfileDecorator

    VerticalProfileDecorator.tag_redraw()


def _alignment_enum_items(self, context):
    """Dynamic items: all top-level IfcAlignment entities in the current file."""
    import bonsai.tool as tool

    items = [("0", "— select alignment —", "")]
    ifc_file = tool.Ifc.get()
    if not ifc_file:
        return items
    try:
        for a in ifc_file.by_type("IfcAlignment"):
            # Skip child alignments (used in multi-vertical template)
            if any(
                rel.RelatingObject.is_a("IfcAlignment")
                for rel in (getattr(a, "Decomposes", []) or [])
            ):
                continue
            label = a.Name or f"Alignment #{a.id()}"
            items.append((str(a.id()), label, ""))
    except Exception:
        pass
    return items


def _on_active_alignment_update(self, context):
    """Select the alignment's Blender object when the dropdown changes."""
    import bonsai.tool as tool

    try:
        aid = int(self.active_alignment_id_str)
    except (ValueError, TypeError):
        return
    if aid == 0:
        return
    ifc_file = tool.Ifc.get()
    if not ifc_file:
        return
    try:
        alignment = ifc_file.by_id(aid)
        obj = tool.Ifc.get_object(alignment)
        if obj and context.view_layer.objects.get(obj.name):
            # Use direct RNA — bpy.ops.object.select_all can fail from non-3D contexts
            for o in context.view_layer.objects:
                o.select_set(False)
            obj.select_set(True)
            context.view_layer.objects.active = obj
    except Exception:
        pass


class VerticalAlignmentItem(PropertyGroup):
    """Tracks one IfcAlignmentVertical available in the profile view."""

    entity_id: IntProperty(name="Entity ID", default=0)
    label: StringProperty(name="Label", default="Vertical")
    is_visible: BoolProperty(
        name="Show in profile",
        description="Show this vertical alignment in the profile view",
        default=True,
        update=_on_vertical_visibility_update,
    )
    show_segments: BoolProperty(
        name="Show Segments",
        description="Expand the segment table for this vertical alignment",
        default=True,
    )
    show_labels: BoolProperty(
        name="Show Labels",
        description="Show BVC/PVI/EVC callout labels for this vertical alignment in the profile view",
        default=True,
        update=_on_vertical_visibility_update,
    )


def _on_cant_visibility_update(self, context):
    from .decorator import VerticalProfileDecorator

    VerticalProfileDecorator.tag_redraw()


def _on_ve_update(self, context):
    from .decorator import VerticalProfileDecorator

    VerticalProfileDecorator.tag_redraw()


def _on_radius_update(self, context):
    """Callback when radius property changes.

    This dynamically imports the operator module to call on_radius_changed,
    avoiding circular imports since prop.py is imported before operator.py.
    """
    from . import operator as ops

    ops.on_radius_changed(self, context)


class CantAlignmentItem(PropertyGroup):
    """Tracks one IfcAlignmentCant available in the profile view."""

    entity_id: IntProperty(name="Entity ID", default=0)
    label: StringProperty(name="Label", default="Cant")
    is_visible: BoolProperty(
        name="Show in profile",
        description="Show this cant in the profile view",
        default=True,
        update=_on_cant_visibility_update,
    )
    show_segments: BoolProperty(
        name="Show Segments",
        description="Expand the segment table for this cant",
        default=True,
    )


class AlignmentPI(PropertyGroup):
    """Property group for a single PI (Point of Intersection)

    In the PI method, alignments are defined by:
    - Endpoint PIs: Start (POB) and End (POE) points
    - Interior PIs: Points where tangents intersect, optionally with curves
    """

    # Coordinates stored as global easting/northing (map coordinates).
    # Coordinate flow: Blender coords -> xyz2enh() -> global E/N (stored here)
    #                  global E/N -> ifcopenshell.util.geolocation.auto_enh2xyz() -> local IFC coords (for IfcOpenShell API)
    e: StringProperty(name="E", description="Easting (global map coordinates)", default="0.0")
    n: StringProperty(name="N", description="Northing (global map coordinates)", default="0.0")

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
    e: StringProperty(name="E", default="0.0")
    n: StringProperty(name="N", default="0.0")

    # Segment properties (only for SEGMENT rows)
    length: FloatProperty(name="Length", default=0.0, precision=2, unit="LENGTH")
    radius: FloatProperty(name="Radius", default=0.0, precision=2, unit="LENGTH")
    arc_length: FloatProperty(name="Arc Length", default=0.0, precision=2, unit="LENGTH")


class CivilAlignmentProperties(PropertyGroup):
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

    # Alignment selector dropdown (top-level alignments only)
    active_alignment_id_str: EnumProperty(
        name="Alignment",
        description="Active alignment shown in this panel",
        items=_alignment_enum_items,
        update=_on_active_alignment_update,
        default=0,
    )

    # Panel collapse state
    show_horizontal_segments: BoolProperty(
        name="Show Horizontal Segments",
        description="Expand the horizontal segment table",
        default=True,
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

    # Combined point/segment display rows (for Civil 3D-style table)
    display_rows: CollectionProperty(type=AlignmentDisplayRow)
    active_display_row_index: IntProperty(name="Active Display Row", default=0)

    # Vertical profile window settings
    vertical_exaggeration: FloatProperty(
        name="Vertical Exaggeration",
        description="Multiply elevation differences by this factor for the profile view",
        default=10.0,
        min=1.0,
        max=1000.0,
        precision=1,
        update=_on_ve_update,
    )

    # Selected horizontal segment (for viewport highlight)
    selected_h_segment_id: IntProperty(
        name="Selected Horizontal Segment",
        description="IFC entity ID of the highlighted horizontal segment",
        default=0,
    )

    # Selected vertical segment (for profile view highlight)
    selected_v_segment_id: IntProperty(
        name="Selected Vertical Segment",
        description="IFC entity ID of the highlighted vertical segment in the profile view",
        default=0,
    )

    # Label visibility toggles
    show_h_segment_labels: BoolProperty(
        name="Show Horizontal Labels",
        description="Show PC/PT/PI labels for the selected horizontal segment in the 3D viewport",
        default=True,
    )

    show_v_segment_labels: BoolProperty(
        name="Show Vertical Labels",
        description="Show BVC/PVI/EVC callout labels in the profile view",
        default=True,
    )

    # Per-vertical visibility filter for the profile window
    vertical_items: CollectionProperty(type=VerticalAlignmentItem)

    # Per-cant visibility filter for the profile window
    cant_items: CollectionProperty(type=CantAlignmentItem)

    # Selected cant segment (for profile view highlight)
    selected_cant_segment_id: IntProperty(
        name="Selected Cant Segment",
        description="IFC entity ID of the highlighted cant segment in the profile view",
        default=0,
    )

    # Label visibility toggle for cant callouts
    show_cant_segment_labels: BoolProperty(
        name="Show Cant Labels",
        description="Show cant start/end value labels in the profile view",
        default=True,
    )

    # PI Edit Mode state (for moving PIs with G key)
    is_pi_edit_mode: BoolProperty(
        name="PI Edit Mode Active",
        description="Whether PI edit mode is currently active",
        default=False,
    )

    pi_edit_alignment_id: IntProperty(
        name="Editing Alignment ID",
        description="IFC ID of alignment being edited in PI edit mode",
        default=0,
    )


class PICurveMarkerProperties(PropertyGroup):
    """Tags a transient Empty object placed at an interior PI while its
    smoothing curve is being defined (ALIGN_OT_draw_horizontal_alignment /
    align.set_pi_curve). Registered as Object.bonsai_pi_curve_marker.

    Deliberately edited via plain panel widgets bound directly to this
    PropertyGroup (see ALIGN_PT_alignment_authoring), not a popup dialog —
    Blender operators must not invoke another operator's dialog from inside
    a still-running modal's modal() callback (this is why the alignment
    wouldn't regenerate after the very first version of this feature: the
    curve popup was invoked from inside the drawing operator's own modal
    loop). A plain "Apply" button clicked from the panel is a top-level
    operator invocation, not a nested one, so it's safe.
    """

    is_pi_marker: BoolProperty(default=False)
    alignment_id: IntProperty(
        name="Alignment ID", description="IFC ID of the IfcAlignment this PI belongs to", default=0
    )
    pi_index: IntProperty(
        name="PI Index", description="0-based index among the alignment's interior PIs", default=0
    )
    curve_type: EnumProperty(
        name="Curve Type",
        items=[
            ("TANGENT", "None (sharp PI)", "No curve — the two tangents meet directly"),
            ("CIRCULAR", "Circular", "A simple circular arc"),
            # Spiral-Circular / Circular-Spiral / Spiral-Circular-Spiral are not
            # implemented yet. See REQUIREMENTS.md §2 step 7 — they need each
            # segment authored individually (create_layout_segment), which
            # layout_horizontal_alignment_by_pi_method does not support.
        ],
        default="TANGENT",
    )
    radius: FloatProperty(name="Radius", default=100.0, min=0.0001, unit="LENGTH")
