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


# Horizontal spiral transition curve families that _map_alignment_horizontal_segment
# (ifcopenshell.api.alignment) maps to real geometry. Shared between HorizontalSegmentRow's
# predefined_type (which also needs LINE/CIRCULARARC/VIENNESEBEND/UNSUPPORTED), HorizontalPIMarker,
# and PICurveMarkerProperties -- the latter two both need a spiral-family choice per PI (entry and
# exit spirals at one PI always share the same family), reusing the same six items so the choice
# reads identically everywhere it appears.
SPIRAL_FAMILY_ITEMS = [
    ("CLOTHOID", "Clothoid", "A spiral transition curve (linear curvature change)"),
    ("CUBIC", "Cubic", "A spiral transition curve (cubic parabola)"),
    ("HELMERTCURVE", "Helmert Curve", "A spiral transition curve (sine-based curvature change)"),
    ("BLOSSCURVE", "Bloss Curve", "A spiral transition curve (S-shaped curvature change)"),
    ("COSINECURVE", "Cosine Curve", "A spiral transition curve (cosine-based curvature change)"),
    ("SINECURVE", "Sine Curve", "A spiral transition curve (sine-based curvature change)"),
]

# Viennese Bend needs a real cant segment at the same station to resolve its representation
# against -- ifcopenshell.api.alignment._get_cant_segment has no fallback for "no cant layout
# anywhere on this alignment" (see the raw segment table's own "Viennese Bend needs a cant layout
# first" check in ALIGN_OT_apply_h_segments). Kept out of SPIRAL_FAMILY_ITEMS itself -- unlike the
# other six, its availability is conditional (see _spiral_family_items below), and
# HorizontalSegmentRow.predefined_type already lists it separately with its own longer
# description, so folding it into the shared list would duplicate that enum id there.
VIENNESE_BEND_ITEM = (
    "VIENNESEBEND",
    "Viennese Bend",
    "A spiral transition curve whose shape also depends on cant -- only available once this "
    "alignment has a cant layout",
)

# Two pre-built, stable item lists for PICurveMarkerProperties.spiral_family /
# HorizontalPIMarker.spiral_family's dynamic items callback (_spiral_family_items) to choose
# between at draw time. Built once at import time, not freshly per call: Blender's dynamic
# EnumProperty items callbacks must return a stable list each time a given result is wanted, not
# newly constructed tuples/strings, or the returned strings can be garbage collected out from under
# the UI (a well-known EnumProperty pitfall).
_SPIRAL_FAMILY_ITEMS_NO_VIENNESE_BEND = list(SPIRAL_FAMILY_ITEMS)
_SPIRAL_FAMILY_ITEMS_WITH_VIENNESE_BEND = list(SPIRAL_FAMILY_ITEMS) + [VIENNESE_BEND_ITEM]


def _spiral_family_items(self, context):
    """items= callback for spiral_family: Viennese Bend only appears once the marker/row's own
    alignment has a real cant layout (see VIENNESE_BEND_ITEM's docstring) -- unavailable rather
    than merely unselectable, since a plain EnumProperty dropdown can't grey out one entry.

    PICurveMarkerProperties carries its own alignment_id; HorizontalPIMarker rows don't (the whole
    table belongs to one alignment, tracked on CivilAlignmentProperties.
    editing_horizontal_pi_alignment_id instead) -- try the former first, since it's cheaper and
    more direct when present.
    """
    import bonsai.tool as tool

    alignment_id = getattr(self, "alignment_id", 0) or getattr(
        context.scene.CivilAlignmentProperties, "editing_horizontal_pi_alignment_id", 0
    )
    ifc = tool.Ifc.get()
    alignment = ifc.by_id(alignment_id) if ifc and alignment_id else None
    if alignment and tool.Alignment.has_real_cant_segments(alignment):
        return _SPIRAL_FAMILY_ITEMS_WITH_VIENNESE_BEND
    return _SPIRAL_FAMILY_ITEMS_NO_VIENNESE_BEND


def _on_vertical_visibility_update(self, context):
    from .decorator import VerticalProfileDecorator

    VerticalProfileDecorator.tag_redraw()


def _on_vertical_exaggeration_update(self, context):
    """Re-fit the profile camera to the new fixed elevation zone (see
    VerticalProfileDecorator._refit_zones/fit_view) -- mirrors the same
    re-fit _on_active_object_changed does when the active alignment changes.
    """
    from .decorator import VerticalProfileDecorator as dec

    if not dec.is_installed or dec.profile_area_ptr == 0:
        return
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.as_pointer() == dec.profile_area_ptr:
                space = next((s for s in area.spaces if s.type == "VIEW_3D"), None)
                if space:
                    dec.fit_view(space, area_width=area.width, area_height=area.height)
    dec.tag_redraw()


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


# How a join_next (PCC/PRC) junction is placed -- see operator._apply_join_next_radii.
JOIN_MODE_ITEMS = [
    ("RADIUS", "Radius", "This curve's radius is given; the next PI's radius is computed to close the join"),
    (
        "DISTANCE",
        "Distance",
        "The distance from this PI to the junction is given; both this and the next PI's radii are computed",
    ),
]


class HorizontalPIMarker(PropertyGroup):
    """One interior PI of a horizontal alignment, for table-based curve editing.

    The table-editing companion to the draggable viewport Empties (see
    PICurveMarkerProperties) -- same underlying PI list
    (operator._reconstruct_horizontal_pis), staged as numeric rows instead
    via align.load_horizontal_pi_table / align.apply_horizontal_pi_table, for
    users who'd rather type/tab through numbers than drag a marker in the
    viewport. Mirrors VerticalPIMarker's "PI list as a plain table" pattern.

    x/y are local IFC plan coordinates (not Blender-world/metres) -- what
    _generate_alignment_segments expects directly, so applying this table
    needs no world<->local conversion the Empty-based flow requires.
    """

    x: FloatProperty(name="Easting (Local)", default=0.0, precision=3, unit="LENGTH")
    y: FloatProperty(name="Northing (Local)", default=0.0, precision=3, unit="LENGTH")
    curve_type: EnumProperty(
        name="Curve Type",
        items=[
            ("TANGENT", "None (sharp PI)", "No curve — the two tangents meet directly"),
            ("CIRCULAR", "Circular", "A simple circular arc"),
            (
                "SPIRAL_CIRCULAR",
                "Spiral-Circular",
                "An entry spiral transitions into the circular arc, which runs to the forward tangent",
            ),
            (
                "CIRCULAR_SPIRAL",
                "Circular-Spiral",
                "The circular arc leaves the back tangent directly and transitions to the forward tangent via an exit spiral",
            ),
            (
                "SPIRAL_CIRCULAR_SPIRAL",
                "Spiral-Circular-Spiral",
                "An entry spiral, a circular arc, and an exit spiral, symmetric about the PI",
            ),
        ],
        default="TANGENT",
    )
    radius: FloatProperty(name="Radius", default=100.0, min=0.0001, unit="LENGTH")
    spiral_in_length: FloatProperty(
        name="Entry Spiral Length",
        description="Length of the spiral ahead of the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    spiral_out_length: FloatProperty(
        name="Exit Spiral Length",
        description="Length of the spiral following the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    spiral_family: EnumProperty(
        name="Spiral Family",
        description="Curve family for the entry and exit spirals -- both share the same family at a given PI",
        items=_spiral_family_items,
        default=0,  # CLOTHOID -- dynamic items (a callback) can't take a string default
    )
    gravity_centerline_height: FloatProperty(
        name="Gravity Centerline Height",
        description=(
            "Viennese Bend only: IfcAlignmentHorizontalSegment.GravityCenterLineHeight, the vehicle's "
            "center of gravity height above rail. Combined with this PI's cant (read live from the "
            "existing cant layout) to drive the cant-derived part of the curve's shape -- 0.0 gives a "
            "Viennese Bend with no cant contribution, same as every other spiral family"
        ),
        default=0.0,
        min=0.0,
        unit="LENGTH",
    )
    join_next: BoolProperty(
        name="Join to Next PI",
        description=(
            "Connect this curve directly to the curve at the next PI, at a shared tangency point, "
            "with no intermediate tangent run -- a compound (PCC, same-direction curves) or reverse "
            "(PRC, opposite-direction curves) curve junction. Only valid when this curve has no exit "
            "spiral and the next PI's curve has no entry spiral (spirals remain fine on the outer, "
            "non-joined side of either curve); not valid on the last PI, which has no next curve to "
            "join to"
        ),
        default=False,
    )
    join_mode: EnumProperty(
        name="Solve Join Using",
        description="Which value places the compound/reverse curve junction",
        items=JOIN_MODE_ITEMS,
        default="RADIUS",
    )
    join_distance: FloatProperty(
        name="Distance to Junction",
        description=(
            "Distance from this PI to the compound/reverse curve junction (PCC/PRC), measured along "
            "the tangent toward the next PI. Both this curve's and the next PI's radii are computed "
            "from it on Apply"
        ),
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )


# Horizontal spiral transition curve families that _map_alignment_horizontal_segment
# (ifcopenshell.api.alignment) maps to real geometry, all sharing the exact same
# DesignParameters shape as CLOTHOID (StartPoint/StartDirection/StartRadiusOfCurvature/
# EndRadiusOfCurvature/SegmentLength -- no extra fields), so the table can treat every
# one of them identically to CLOTHOID. VIENNESEBEND is kept separate from this specific
# tuple (rather than folded in) since its own geometry additionally depends on the
# alignment's CANT segment at the same station -- HorizontalSegmentRow.predefined_type
# still lists it explicitly, gated at Apply time (see the "Viennese Bend needs a cant
# layout first" check in ALIGN_OT_apply_h_segments) rather than editable unconditionally
# like the other six.
HORIZONTAL_SPIRAL_TYPES = tuple(item[0] for item in SPIRAL_FAMILY_ITEMS)
SUPPORTED_HORIZONTAL_TYPES = ("LINE", "CIRCULARARC") + HORIZONTAL_SPIRAL_TYPES + ("VIENNESEBEND",)

# Every spiral family the PI-curve marker/table workflow can reconstruct an existing PI's shape
# into (see operator._reconstruct_horizontal_pis) -- HORIZONTAL_SPIRAL_TYPES plus VIENNESEBEND,
# which isn't in that tuple (see above) but is still one of PICurveMarkerProperties.spiral_family's
# possible values once a cant layout exists (_spiral_family_items).
PI_METHOD_SPIRAL_TYPES = HORIZONTAL_SPIRAL_TYPES + ("VIENNESEBEND",)

# Vertical types whose EndGradient can genuinely differ from StartGradient
# (a CONSTANTGRADIENT segment always has EndGradient == StartGradient by
# definition, so it gets no separate "G Out" field).
SUPPORTED_VERTICAL_TYPES = ("CONSTANTGRADIENT", "PARABOLICARC", "CIRCULARARC")
VERTICAL_TWO_GRADIENT_TYPES = ("PARABOLICARC", "CIRCULARARC")


class HorizontalSegmentRow(PropertyGroup):
    """One staged edit to a horizontal alignment segment, for the
    Alignment Segments table's "stage edits, then Apply" editing flow (see
    ALIGN_OT_enable_editing_h_segments / ALIGN_OT_apply_h_segments).

    segment_id is the originating IfcAlignmentSegment's entity id (0 for a
    row added during this edit session, with no IFC counterpart yet) — used
    only for provenance/debugging, not read by the Apply operator, which
    always rebuilds every segment from scratch in row order.
    """

    segment_id: IntProperty(name="Source Segment ID", default=0)
    predefined_type: EnumProperty(
        name="Type",
        items=[
            ("LINE", "Line", "A straight tangent run"),
            ("CIRCULARARC", "Circular Arc", "A constant-radius curve"),
            *SPIRAL_FAMILY_ITEMS,
            (
                "VIENNESEBEND",
                "Viennese Bend",
                "A spiral transition curve whose shape also depends on cant -- the alignment's "
                "cant layout must already cover this segment's station range before Apply, or "
                "the geometry kernel has nothing to resolve it against",
            ),
            ("UNSUPPORTED", "Unsupported", "A segment type this table can't edit — remove it or fix it in IFC directly"),
        ],
        default="LINE",
    )
    original_predefined_type: StringProperty(
        name="Original Type", description="The real IFC PredefinedType, when it's not one this table supports editing"
    )
    length: FloatProperty(name="Length", default=10.0, min=0.0001, unit="LENGTH")
    start_radius: FloatProperty(name="Radius", default=0.0, unit="LENGTH")
    end_radius: FloatProperty(name="End Radius", default=0.0, unit="LENGTH")


class VerticalSegmentRow(PropertyGroup):
    """One staged edit to a vertical alignment segment (see
    HorizontalSegmentRow for the general pattern this mirrors).

    start_gradient/end_gradient are stored as PERCENT (matching the existing
    read-only panel's display, e.g. 2.5 for 2.5%) — the Apply operator must
    divide by 100 before writing IfcAlignmentVerticalSegment.StartGradient/
    EndGradient, which are unitless ratios.

    CIRCULARARC is supported (_map_alignment_vertical_segment implements it,
    deriving the true radius from StartGradient/EndGradient/HorizontalLength
    rather than reading RadiusOfCurvature) -- CLOTHOID is not (that mapper
    raises NotImplementedError), so it's intentionally left off this list.
    """

    segment_id: IntProperty(name="Source Segment ID", default=0)
    predefined_type: EnumProperty(
        name="Type",
        items=[
            ("CONSTANTGRADIENT", "Constant Grade", "A straight tangent grade"),
            ("PARABOLICARC", "Parabolic", "A parabolic vertical curve"),
            ("CIRCULARARC", "Circular Arc", "A constant-radius vertical curve"),
            ("UNSUPPORTED", "Unsupported", "A segment type this table can't edit — remove it or fix it in IFC directly"),
        ],
        default="CONSTANTGRADIENT",
    )
    original_predefined_type: StringProperty(
        name="Original Type", description="The real IFC PredefinedType, when it's not one this table supports editing"
    )
    h_length: FloatProperty(name="Length", default=10.0, min=0.0001, unit="LENGTH")
    start_gradient: FloatProperty(name="G In %", default=0.0, precision=3)
    end_gradient: FloatProperty(name="G Out %", default=0.0, precision=3)


class CantSegmentRow(PropertyGroup):
    """One staged edit to a cant alignment segment (see HorizontalSegmentRow
    for the general pattern this mirrors).

    predefined_type mirrors the horizontal spiral family 1:1 where a direct
    cant equivalent exists (HELMERTCURVE/BLOSSCURVE/COSINECURVE/SINECURVE/
    VIENNESEBEND -- _map_alignment_cant_segment implements all of these);
    CLOTHOID and CUBIC have no matching cant curve type in the IFC schema, so
    both map to LINEARTRANSITION instead (see
    tool.Alignment.CANT_TYPE_FOR_HORIZONTAL_TYPE, the same table
    align.generate_cant_layout and the horizontal-edit-time sync use).
    """

    segment_id: IntProperty(name="Source Segment ID", default=0)
    predefined_type: EnumProperty(
        name="Type",
        items=[
            ("CONSTANTCANT", "Constant Cant", "A constant left/right cant"),
            ("LINEARTRANSITION", "Linear Transition", "Cant that changes linearly over the segment"),
            ("HELMERTCURVE", "Helmert Curve", "A cant transition (sine-based curvature change)"),
            ("BLOSSCURVE", "Bloss Curve", "A cant transition (S-shaped curvature change)"),
            ("COSINECURVE", "Cosine Curve", "A cant transition (cosine-based curvature change)"),
            ("SINECURVE", "Sine Curve", "A cant transition (sine-based curvature change)"),
            ("VIENNESEBEND", "Viennese Bend", "A cant transition paired with a horizontal Viennese Bend segment"),
            ("UNSUPPORTED", "Unsupported", "A segment type this table can't edit — remove it or fix it in IFC directly"),
        ],
        default="CONSTANTCANT",
    )
    original_predefined_type: StringProperty(
        name="Original Type", description="The real IFC PredefinedType, when it's not one this table supports editing"
    )
    h_length: FloatProperty(name="Length", default=10.0, min=0.0001, unit="LENGTH")
    start_cant_left: FloatProperty(name="Start L", default=0.0)
    start_cant_right: FloatProperty(name="Start R", default=0.0)
    end_cant_left: FloatProperty(name="End L", default=0.0)
    end_cant_right: FloatProperty(name="End R", default=0.0)


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
    # Which IfcAlignmentVertical vertical_pi_markers belongs to -- a horizontal can be
    # reused by several sibling verticals (IFC CT 4.1.4.4.1.2), each on its own child
    # IfcAlignment, so "the active alignment" alone can't identify one. Set by
    # align.load_vertical_pis / align.draw_vertical_alignment, read by
    # align.apply_vertical_pi_curve so it regenerates the right one; 0 falls back to
    # resolving a single vertical straight off the active alignment (the common case).
    editing_vertical_pi_layout_id: IntProperty(name="Editing Vertical PI Layout ID", default=0)

    # Interior PIs of the horizontal alignment, table-editing companion to the
    # draggable viewport Empties (PICurveMarkerProperties) -- see
    # HorizontalPIMarker.
    horizontal_pi_rows: CollectionProperty(type=HorizontalPIMarker)
    active_horizontal_pi_row_index: IntProperty(name="Active Horizontal PI", default=0)
    # Which IfcAlignment horizontal_pi_rows belongs to -- guards against
    # applying stale rows to a different alignment if the active alignment
    # is switched while the table is populated. 0 falls back to the active
    # alignment (the common case), same convention as
    # editing_vertical_pi_layout_id.
    editing_horizontal_pi_alignment_id: IntProperty(name="Editing Horizontal PI Alignment ID", default=0)

    # Per-vertical visibility filter for the profile window
    vertical_items: CollectionProperty(type=VerticalAlignmentItem)

    # Fixed vertical exaggeration for the profile view -- world-Z = (elevation -
    # elev_ref) * this, unaffected by zoom/pan (see VerticalProfileDecorator._ez).
    vertical_exaggeration: FloatProperty(
        name="Vertical Exaggeration",
        description=(
            "How much elevation is exaggerated relative to distance in the profile "
            "view (10 draws 1 unit of elevation as 10 units of distance)"
        ),
        default=10.0,
        min=0.01,
        soft_max=100.0,
        update=_on_vertical_exaggeration_update,
    )

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

    # Segment table editing ("stage edits, then Apply") -- only one of
    # horizontal/vertical/cant can be mid-edit at a time; editing_layout_id
    # names the specific IfcAlignmentHorizontal/Vertical/Cant entity being
    # staged (vertical/cant layouts can have several sibling layouts, e.g.
    # "Road Profile" vs "Existing Ground", so the kind alone isn't enough).
    editing_segment_kind: EnumProperty(
        name="Editing Segments",
        items=[
            ("NONE", "None", ""),
            ("HORIZONTAL", "Horizontal", ""),
            ("VERTICAL", "Vertical", ""),
            ("CANT", "Cant", ""),
        ],
        default="NONE",
    )
    editing_layout_id: IntProperty(name="Editing Layout ID", default=0)

    h_segment_rows: CollectionProperty(type=HorizontalSegmentRow)
    active_h_segment_row_index: IntProperty(default=0)

    v_segment_rows: CollectionProperty(type=VerticalSegmentRow)
    active_v_segment_row_index: IntProperty(default=0)

    cant_segment_rows: CollectionProperty(type=CantSegmentRow)
    active_cant_segment_row_index: IntProperty(default=0)


class PICurveMarkerProperties(PropertyGroup):
    """Tags a transient Empty object placed at an interior PI while its
    smoothing curve is being defined (ALIGN_OT_draw_horizontal_alignment /
    align.set_pi_curve), or at the alignment's Start/End point while it's
    being repositioned (role == "START"/"END" — see _create_endpoint_marker).
    Registered as Object.bonsai_pi_curve_marker.

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
    role: EnumProperty(
        name="Role",
        description="What this marker represents -- only an interior PI has a smoothing curve",
        items=[
            ("PI", "Interior PI", "An interior PI, optionally with a smoothing curve"),
            ("START", "Start Point", "The alignment's start point"),
            ("END", "End Point", "The alignment's end point"),
        ],
        default="PI",
    )
    alignment_id: IntProperty(
        name="Alignment ID", description="IFC ID of the IfcAlignment this PI belongs to", default=0
    )
    pi_index: IntProperty(
        name="PI Index", description="0-based index among the alignment's interior PIs", default=0
    )
    join_next: BoolProperty(
        name="Join to Next PI",
        description=(
            "Connect this curve directly to the curve at the next PI, at a shared tangency point, "
            "with no intermediate tangent run -- a compound (PCC, same-direction curves) or reverse "
            "(PRC, opposite-direction curves) curve junction. Only valid when this curve has no exit "
            "spiral and the next PI's curve has no entry spiral (spirals remain fine on the outer, "
            "non-joined side of either curve); not valid on the last PI, which has no next curve to "
            "join to"
        ),
        default=False,
    )
    join_mode: EnumProperty(
        name="Solve Join Using",
        description="Which value places the compound/reverse curve junction",
        items=JOIN_MODE_ITEMS,
        default="RADIUS",
    )
    join_distance: FloatProperty(
        name="Distance to Junction",
        description=(
            "Distance from this PI to the compound/reverse curve junction (PCC/PRC), measured along "
            "the tangent toward the next PI. Both this curve's and the next PI's radii are computed "
            "from it on Apply"
        ),
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    curve_type: EnumProperty(
        name="Curve Type",
        items=[
            ("TANGENT", "None (sharp PI)", "No curve — the two tangents meet directly"),
            ("CIRCULAR", "Circular", "A simple circular arc"),
            (
                "SPIRAL_CIRCULAR",
                "Spiral-Circular",
                "An entry spiral transitions into the circular arc, which runs to the forward tangent",
            ),
            (
                "CIRCULAR_SPIRAL",
                "Circular-Spiral",
                "The circular arc leaves the back tangent directly and transitions to the forward tangent via an exit spiral",
            ),
            (
                "SPIRAL_CIRCULAR_SPIRAL",
                "Spiral-Circular-Spiral",
                "An entry spiral, a circular arc, and an exit spiral, symmetric about the PI",
            ),
        ],
        default="TANGENT",
    )
    radius: FloatProperty(name="Radius", default=100.0, min=0.0001, unit="LENGTH")
    spiral_in_length: FloatProperty(
        name="Entry Spiral Length",
        description="Length of the spiral ahead of the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    spiral_out_length: FloatProperty(
        name="Exit Spiral Length",
        description="Length of the spiral following the circular arc",
        default=100.0,
        min=0.0001,
        unit="LENGTH",
    )
    spiral_family: EnumProperty(
        name="Spiral Family",
        description="Curve family for the entry and exit spirals -- both share the same family at a given PI",
        items=_spiral_family_items,
        default=0,  # CLOTHOID -- dynamic items (a callback) can't take a string default
    )
    gravity_centerline_height: FloatProperty(
        name="Gravity Centerline Height",
        description=(
            "Viennese Bend only: IfcAlignmentHorizontalSegment.GravityCenterLineHeight, the vehicle's "
            "center of gravity height above rail. Combined with this PI's cant (read live from the "
            "existing cant layout) to drive the cant-derived part of the curve's shape -- 0.0 gives a "
            "Viennese Bend with no cant contribution, same as every other spiral family"
        ),
        default=0.0,
        min=0.0,
        unit="LENGTH",
    )
