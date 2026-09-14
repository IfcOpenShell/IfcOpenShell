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


# Blender requires a dynamic EnumProperty callback to keep a reference to the
# items it returns — the strings are read by the C/RNA layer after the Python
# call returns, and if the list is only local to the function it can be
# garbage-collected before that happens. Without this cache, the dropdown can
# resolve its stored index against a stale/freed items list — e.g. right
# after adding and drawing a new alignment — leaving the dropdown (and the
# segment table, which reads its value) showing a different alignment than
# the one actually active in the viewport. See bpy.props.EnumProperty docs.
_alignment_enum_items_cache: list[tuple[str, str, str]] = []


def _alignment_enum_items(self, context):
    """Dynamic items: all top-level IfcAlignment entities in the current file."""
    import bonsai.tool as tool

    global _alignment_enum_items_cache

    items = [("0", "— select alignment —", "")]
    ifc_file = tool.Ifc.get()
    if not ifc_file:
        _alignment_enum_items_cache = items
        return _alignment_enum_items_cache
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
    _alignment_enum_items_cache = items
    return _alignment_enum_items_cache


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


class VerticalPIMarker(PropertyGroup):
    """One interior PI of a vertical alignment, for post-draw curve editing.

    Unlike horizontal PI markers (real Blender Empties positioned at their
    actual 3D location — see PICurveMarkerProperties), a vertical PI has no
    meaningful position in real 3D space, only in the profile view's own
    synthetic (distance-along, elevation) space. So instead of a scene
    object, interior vertical PIs are tracked here as a plain list, edited
    via a table in the panel (ALIGN_PT_alignment_authoring), and applied by
    align.apply_vertical_pi_curve.
    """

    dist_along: FloatProperty(name="Distance Along", default=0.0, precision=2)
    elevation: FloatProperty(name="Elevation", default=0.0, precision=3, unit="LENGTH")
    curve_type: EnumProperty(
        name="Curve Type",
        items=[
            ("TANGENT", "None (sharp PI)", "No curve — the two grades meet directly"),
            ("PARABOLIC", "Parabolic", "A parabolic vertical curve"),
        ],
        default="TANGENT",
    )
    curve_length: FloatProperty(
        name="Curve Length", description="Horizontal length of the parabolic curve", default=100.0, min=0.0001, unit="LENGTH"
    )


class CivilAlignmentProperties(PropertyGroup):
    """Properties for the alignment module"""

    # Alignment selector dropdown (top-level alignments only)
    active_alignment_id_str: EnumProperty(
        name="Alignment",
        description="Active alignment shown in this panel",
        items=_alignment_enum_items,
        update=_on_active_alignment_update,
        default=0,
    )

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

    # Interior PIs of the most recently drawn/edited vertical alignment
    vertical_pi_markers: CollectionProperty(type=VerticalPIMarker)
    active_vertical_pi_marker_index: IntProperty(name="Active Vertical PI", default=0)

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
            (
                "SPIRAL_CIRCULAR",
                "Spiral-Circular",
                "An entry clothoid spiral transitions into the circular arc, which runs to the forward tangent",
            ),
            (
                "CIRCULAR_SPIRAL",
                "Circular-Spiral",
                "The circular arc leaves the back tangent directly and transitions to the forward tangent via an exit clothoid spiral",
            ),
            (
                "SPIRAL_CIRCULAR_SPIRAL",
                "Spiral-Circular-Spiral",
                "An entry clothoid spiral, a circular arc, and an exit clothoid spiral, symmetric about the PI",
            ),
            # Only the clothoid spiral family is supported for now — see
            # solve_horizontal_alignment_by_pi_method. Other families (Bloss,
            # cosine, sine, cubic, Helmert) would need their own
            # curvature-vs-length integrand.
        ],
        default="TANGENT",
    )
    radius: FloatProperty(name="Radius", default=100.0, min=0.0001, unit="LENGTH")
    spiral_in_length: FloatProperty(
        name="Entry Spiral Length",
        description="Length of the clothoid spiral ahead of the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    spiral_out_length: FloatProperty(
        name="Exit Spiral Length",
        description="Length of the clothoid spiral following the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
