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


"""UI panels for the alignment module

All panels appear in the Properties sidebar under the Alignments tab,
nested under BIM_PT_tab_alignments.
"""

import bpy
import math
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import bonsai.tool as tool
from bpy.types import Panel, Operator, UIList
from bpy.props import IntProperty, BoolProperty
from .prop import _alignment_enum_items, _clamp_alignment_enum
from .operator import (
    _find_pi_markers,
    _resolve_alignment_id_for_markers,
    _is_interior_pi_marker,
    _is_endpoint_marker,
    _is_vertex_marker,
    _alignment_id_owning_layout,
    ALIGN_OT_drag_vertical_pis,
    _grid_rotation_deg,
    _bearing_string,
)


def _pi_markers_present(context) -> bool:
    """Whether the relevant alignment (from the active object or an active
    PI marker of its own) currently has any leftover PI marker empties."""
    alignment_id = _resolve_alignment_id_for_markers(context)
    return bool(alignment_id and _find_pi_markers(alignment_id))


def is_ifc4x3():
    """Check if the current IFC file is IFC4X3 schema"""
    return tool.Ifc.get_schema() == "IFC4X3"


# Module-level dicts store expand/collapse state for sections.
# Keys are IFC entity IDs; True = expanded (default).
# Using plain dicts avoids any RNA property modification during draw callbacks.
_H_EXPANDED: dict[int, bool] = {}   # alignment_id → bool
_V_EXPANDED: dict[int, bool] = {}   # vertical layout entity_id → bool
_C_EXPANDED: dict[int, bool] = {}   # cant layout entity_id → bool


# =============================================================================
# Section toggle operators
# =============================================================================


class ALIGN_OT_toggle_h_segments(Operator):
    """Toggle horizontal segment table"""

    bl_idname = "align.toggle_h_segments"
    bl_label = "Toggle Horizontal Segments"
    bl_options = {"INTERNAL"}

    alignment_id: IntProperty()

    def execute(self, context):
        _H_EXPANDED[self.alignment_id] = not _H_EXPANDED.get(self.alignment_id, True)
        context.area.tag_redraw()
        return {"FINISHED"}


class ALIGN_OT_toggle_v_segments(Operator):
    """Toggle vertical segment table"""

    bl_idname = "align.toggle_v_segments"
    bl_label = "Toggle Vertical Segments"
    bl_options = {"INTERNAL"}

    entity_id: IntProperty()

    def execute(self, context):
        _V_EXPANDED[self.entity_id] = not _V_EXPANDED.get(self.entity_id, True)
        context.area.tag_redraw()
        return {"FINISHED"}


class ALIGN_OT_toggle_cant_segments(Operator):
    """Toggle cant segment table"""

    bl_idname = "align.toggle_cant_segments"
    bl_label = "Toggle Cant Segments"
    bl_options = {"INTERNAL"}

    entity_id: IntProperty()

    def execute(self, context):
        _C_EXPANDED[self.entity_id] = not _C_EXPANDED.get(self.entity_id, True)
        context.area.tag_redraw()
        return {"FINISHED"}


class ALIGN_UL_vertical_pi_markers(UIList):
    """UIList for the interior PIs of a just-drawn/edited vertical alignment.

    One row per interior PI: distance along, elevation, curve type, and (when
    curved) curve length — edited inline, applied all at once via
    align.apply_vertical_pi_curve.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.row(align=True)
        row.label(text=str(index + 1))
        row.label(text=f"{item.dist_along:.2f}")
        row.label(text=f"{item.elevation:.3f}")
        row.prop(item, "curve_type", text="")
        if item.curve_type == "PARABOLIC":
            row.prop(item, "curve_length", text="")
        else:
            row.label(text="")


def _joins_by_distance(item) -> bool:
    """Whether this PI's join_next junction is placed by distance (its own radius then computed)."""
    return item.curve_type in {"CIRCULAR", "SPIRAL_CIRCULAR"} and item.join_next and item.join_mode == "DISTANCE"


def _draw_length_mismatch(box, layout_entity) -> None:
    """Under a vertical or cant layout's header: when it doesn't end where the horizontal does --
    allowed, they're edited independently -- say by how much, with the Match Horizontal Length quick
    fix."""
    delta = tool.Alignment.get_length_mismatch(layout_entity)
    if delta is None:
        return
    row = box.row(align=True)
    word = "past" if delta > 0 else "short of"
    row.label(text=f"Ends {abs(delta):.3f} {word} the horizontal", icon="ERROR")
    op = row.operator("align.match_horizontal_length", text="Match", icon="ARROW_LEFTRIGHT")
    op.layout_id = layout_entity.id()


class ALIGN_UL_polyline_points(UIList):
    """A polyline alignment's points, staged for table editing (align.load_polyline_table)."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.row(align=True)
        row.label(text=str(index + 1))
        row.prop(item, "x", text="")
        row.prop(item, "y", text="")
        if context.scene.CivilAlignmentProperties.editing_polyline_is_3d:
            row.prop(item, "z", text="")


class ALIGN_UL_horizontal_pi_markers(UIList):
    """UIList for the interior PIs of a just-drawn/edited horizontal alignment.

    Table-editing companion to the draggable viewport Empties (see
    PICurveMarkerProperties) -- same PI list, applied all at once via
    align.apply_horizontal_pi_table. Mirrors ALIGN_UL_vertical_pi_markers.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.row(align=True)
        row.label(text=str(index + 1))
        row.label(text=f"{item.x:.2f}")
        row.label(text=f"{item.y:.2f}")
        row.prop(item, "curve_type", text="")
        by_distance = _joins_by_distance(item)
        if item.curve_type != "TANGENT":
            # in Distance mode the radius is computed on Apply -- shown, but not editable
            sub = row.row(align=True)
            sub.enabled = not by_distance
            sub.prop(item, "radius", text="")
        if item.curve_type in {"SPIRAL_CIRCULAR", "SPIRAL_CIRCULAR_SPIRAL"}:
            row.prop(item, "spiral_in_length", text="")
        if item.curve_type in {"CIRCULAR_SPIRAL", "SPIRAL_CIRCULAR_SPIRAL"}:
            row.prop(item, "spiral_out_length", text="")
        if item.curve_type in {"SPIRAL_CIRCULAR", "CIRCULAR_SPIRAL", "SPIRAL_CIRCULAR_SPIRAL"}:
            row.prop(item, "spiral_family", text="")
            if item.spiral_family == "VIENNESEBEND":
                row.prop(item, "gravity_centerline_height", text="")
        # join_next needs no exit spiral on this curve (the joined side must be spiral-free) --
        # CIRCULAR_SPIRAL/SPIRAL_CIRCULAR_SPIRAL always have one, so the toggle isn't offered there.
        if item.curve_type in {"CIRCULAR", "SPIRAL_CIRCULAR"}:
            row.prop(item, "join_next", text="Join Next", toggle=True)
            if item.join_next:
                row.prop(item, "join_mode", text="")
                if by_distance:
                    row.prop(item, "join_distance", text="")


class ALIGN_UL_h_segments(UIList):
    """Editable table of a horizontal layout's staged segment edits (see
    align.enable_editing_h_segments / align.apply_h_segments).

    Columns are built via chained split(factor=...) calls -- one field per
    step -- matching the read-only segment tables' own technique (see
    ALIGN_PT_alignment_segments._draw_horizontal), rather than a plain
    row.prop() sequence: a bare row gives every widget an equal share of the
    available width, which stretches short numeric fields across the whole
    list and looks scattered instead of left-packed.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.split(factor=0.08)
        row.label(text=str(index + 1))
        if item.predefined_type == "UNSUPPORTED":
            row.label(text=item.original_predefined_type, icon="ERROR")
            return
        r2 = row.split(factor=0.35)
        r2.prop(item, "predefined_type", text="")
        r3 = r2.split(factor=0.30)
        r3.prop(item, "length", text="")
        if item.predefined_type == "CIRCULARARC":
            r4 = r3.split(factor=0.5)
            r4.prop(item, "start_radius", text="R")
        elif item.predefined_type != "LINE":
            r4 = r3.split(factor=0.5)
            r4.prop(item, "start_radius", text="R1")
            r5 = r4.split(factor=0.5)
            r5.prop(item, "end_radius", text="R2")


class ALIGN_UL_v_segments(UIList):
    """Editable table of a vertical layout's staged segment edits (see
    align.enable_editing_v_segments / align.apply_v_segments). See
    ALIGN_UL_h_segments for why chained split() is used instead of a plain
    row.prop() sequence."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.split(factor=0.08)
        row.label(text=str(index + 1))
        if item.predefined_type == "UNSUPPORTED":
            row.label(text=item.original_predefined_type, icon="ERROR")
            return
        r2 = row.split(factor=0.35)
        r2.prop(item, "predefined_type", text="")
        r3 = r2.split(factor=0.30)
        r3.prop(item, "h_length", text="")
        r4 = r3.split(factor=0.5)
        r4.prop(item, "start_gradient", text="G In")
        if item.predefined_type in ("PARABOLICARC", "CIRCULARARC"):
            r4.prop(item, "end_gradient", text="G Out")


class ALIGN_UL_cant_segments(UIList):
    """Editable table of a cant layout's staged segment edits (see
    align.enable_editing_cant_segments / align.apply_cant_segments). See
    ALIGN_UL_h_segments for why chained split() is used instead of a plain
    row.prop() sequence."""

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type not in {"DEFAULT", "COMPACT"}:
            return
        row = layout.split(factor=0.08)
        row.label(text=str(index + 1))
        if item.predefined_type == "UNSUPPORTED":
            row.label(text=item.original_predefined_type, icon="ERROR")
            return
        r2 = row.split(factor=0.30)
        r2.prop(item, "predefined_type", text="")
        r3 = r2.split(factor=0.25)
        r3.prop(item, "h_length", text="")
        r4 = r3.split(factor=0.5)
        start_pair = r4.row(align=True)
        start_pair.prop(item, "start_cant_left", text="SL")
        start_pair.prop(item, "start_cant_right", text="SR")
        if item.predefined_type == "LINEARTRANSITION":
            end_pair = r4.row(align=True)
            end_pair.prop(item, "end_cant_left", text="EL")
            end_pair.prop(item, "end_cant_right", text="ER")


# =============================================================================
# Alignments Tab – Segment Breakdown Panel
# =============================================================================


def _rad_to_bearing(rad: float) -> str:
    """Convert a direction (radians, CCW from east) to a quadrant bearing, in the same format as
    the draw tools' Bearing readout (so it can be typed back into their Angle field). Its own
    formatting used to round seconds up to 60 without carrying (e.g. N 59°59'60.0" E)."""
    return _bearing_string(math.degrees(rad))


def _start_en(ifc_file, dp) -> tuple[float | None, float | None]:
    """Return (Easting, Northing) for an IfcAlignmentHorizontalSegment.

    StartPoint is in IFC project coordinates; auto_xyz2enh applies any
    IfcMapConversion to get global map coordinates.  Returns (None, None)
    if StartPoint is absent or the conversion fails.
    """
    pt = getattr(dp, "StartPoint", None)
    if pt is None:
        return None, None
    try:
        coords = pt.Coordinates
        e, n, _ = ifcopenshell.util.geolocation.auto_xyz2enh(
            ifc_file, coords[0], coords[1], 0.0
        )
        return e, n
    except Exception:
        return None, None


class ALIGN_PT_alignment_authoring(Panel):
    """Add an alignment and draw its horizontal geometry — Alignments tab.

    Add a bare alignment, then draw its horizontal geometry directly in the
    viewport.
    """

    bl_label = "Add Alignment"
    bl_idname = "ALIGN_PT_alignment_authoring"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_alignments"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        if not tool.Blender.should_show_panel(context, "ALIGNMENTS", cls.bl_idname):
            return False
        return is_ifc4x3()

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("align.add_alignment", icon="ADD")

        props = context.scene.CivilAlignmentProperties
        marker = context.active_object
        is_marker = bool(marker) and _is_interior_pi_marker(marker)
        is_endpoint_marker = bool(marker) and _is_endpoint_marker(marker)
        markers_present = _pi_markers_present(context)
        table_present = bool(props.horizontal_pi_rows)

        alignment = tool.Alignment.get_active_alignment()
        is_polyline = bool(alignment) and tool.Alignment.is_polyline_alignment(alignment)
        is_bare = bool(alignment) and tool.Alignment.is_bare_alignment(alignment)
        polyline_table_present = bool(props.polyline_point_rows)
        is_vertex_marker = bool(marker) and _is_vertex_marker(marker)
        row = col.row(align=True)
        row.enabled = bool(alignment)
        if is_polyline:
            # a polyline alignment (REQUIREMENTS.md §5.1): its own draw/edit tools, no layouts
            row.operator("align.draw_polyline_alignment", icon="EYEDROPPER")
            row.operator("align.extend_polyline_alignment", text="", icon="FORWARD")
            row.operator("align.edit_polyline_points", text="", icon="EMPTY_AXIS", depress=markers_present)
            row.operator("align.load_polyline_table", text="", icon="ANIM_DATA", depress=polyline_table_present)
        else:
            row.operator("align.draw_horizontal_alignment", icon="EYEDROPPER")
            row.operator("align.extend_horizontal_alignment", text="", icon="FORWARD")
            row.operator("align.edit_horizontal_pis", text="", icon="EMPTY_AXIS", depress=markers_present)
            row.operator("align.load_horizontal_pi_table", text="", icon="ANIM_DATA", depress=table_present)
        row.operator("align.remove_alignment", text="", icon="TRASH")
        if is_bare:
            # nothing drawn yet: it can still become either kind
            col.operator("align.draw_polyline_alignment", icon="IPO_LINEAR")
        if not alignment:
            col.label(text="Add or select an alignment first", icon="INFO")

        if is_vertex_marker:
            box = layout.box()
            data = marker.bonsai_pi_curve_marker
            count = len(_find_pi_markers(data.alignment_id))
            if data.pi_index == 0:
                label = "Start Point"
            else:
                label = "End Point" if data.pi_index == count - 1 else f"Point {data.pi_index}"
            box.label(text=label, icon="EMPTY_AXIS")
            box.label(text="Drag in the viewport to reposition", icon="ORIENTATION_GLOBAL")
            box.operator("align.move_pi_marker", icon="DRIVER_DISTANCE")
            row = box.row(align=True)
            row.operator("align.apply_pi_curve", text="Apply", icon="CHECKMARK")
            row.operator("align.finish_pi_editing", icon="CHECKMARK")
        elif is_marker or is_endpoint_marker or markers_present:
            box = layout.box()
            if is_marker:
                pi_data = marker.bonsai_pi_curve_marker
                box.label(text=f"PI {pi_data.pi_index}", icon="EMPTY_AXIS")
                box.label(text="Drag in the viewport to reposition", icon="ORIENTATION_GLOBAL")
                box.operator("align.move_pi_marker", icon="DRIVER_DISTANCE")
                box.prop(pi_data, "curve_type")
                by_distance = _joins_by_distance(pi_data)
                if pi_data.curve_type != "TANGENT":
                    # in Distance mode the radius is computed on Apply -- shown, but not editable
                    sub = box.row()
                    sub.enabled = not by_distance
                    sub.prop(pi_data, "radius")
                if pi_data.curve_type in {"SPIRAL_CIRCULAR", "SPIRAL_CIRCULAR_SPIRAL"}:
                    box.prop(pi_data, "spiral_in_length")
                if pi_data.curve_type in {"CIRCULAR_SPIRAL", "SPIRAL_CIRCULAR_SPIRAL"}:
                    box.prop(pi_data, "spiral_out_length")
                if pi_data.curve_type in {"SPIRAL_CIRCULAR", "CIRCULAR_SPIRAL", "SPIRAL_CIRCULAR_SPIRAL"}:
                    box.prop(pi_data, "spiral_family")
                    if pi_data.spiral_family == "VIENNESEBEND":
                        box.prop(pi_data, "gravity_centerline_height")
                # join_next needs no exit spiral on this curve (the joined side must be
                # spiral-free) -- CIRCULAR_SPIRAL/SPIRAL_CIRCULAR_SPIRAL always have one, so the
                # toggle isn't offered there. The solver itself reports cleanly (via Apply Curve's
                # WARNING) if this is the last PI or the closure doesn't fit -- not pre-validated
                # here.
                if pi_data.curve_type in {"CIRCULAR", "SPIRAL_CIRCULAR"}:
                    box.prop(pi_data, "join_next", text="Join to Next PI (Compound/Reverse Curve)")
                    if pi_data.join_next:
                        box.row().prop(pi_data, "join_mode", expand=True)
                        if by_distance:
                            box.prop(pi_data, "join_distance")
                row = box.row(align=True)
                row.operator("align.apply_pi_curve", icon="CHECKMARK")
                row.operator("align.finish_pi_editing", icon="CHECKMARK")
            elif is_endpoint_marker:
                pi_data = marker.bonsai_pi_curve_marker
                label = "Start Point" if pi_data.role == "START" else "End Point"
                box.label(text=label, icon="EMPTY_AXIS")
                box.label(text="Drag in the viewport to reposition", icon="ORIENTATION_GLOBAL")
                box.operator("align.move_pi_marker", icon="DRIVER_DISTANCE")
                row = box.row(align=True)
                row.operator("align.apply_pi_curve", text="Apply", icon="CHECKMARK")
                row.operator("align.finish_pi_editing", icon="CHECKMARK")
            else:
                box.label(text="Select a marker to edit it", icon="INFO")
                box.operator("align.finish_pi_editing", icon="CHECKMARK")


        if table_present:
            box = layout.box()
            box.label(text="Horizontal PIs", icon="ANIM_DATA")
            header = box.row(align=True)
            header.label(text="#")
            header.label(text="Easting")
            header.label(text="Northing")
            header.label(text="Curve")

            box.template_list(
                "ALIGN_UL_horizontal_pi_markers",
                "",
                props,
                "horizontal_pi_rows",
                props,
                "active_horizontal_pi_row_index",
                rows=4,
            )

            row = box.row(align=True)
            row.operator("align.apply_horizontal_pi_table", icon="CHECKMARK")
            row.operator("align.finish_horizontal_pi_table", icon="CHECKMARK")


class ALIGN_PT_vertical_alignment_authoring(Panel):
    """Draw a vertical alignment by PI, in the docked profile view — Alignments tab.

    Requires the horizontal alignment to already be drawn (a vertical
    alignment is defined against the horizontal's distance-along range).
    Opens the profile view if it isn't already open, then runs the same
    draw-sharp-then-apply-curves workflow as the horizontal tool: draw all
    PIs first, then set a curve length per interior PI and Apply.
    """

    bl_label = "Vertical Alignment"
    bl_idname = "ALIGN_PT_vertical_alignment_authoring"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_alignments"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if not tool.Blender.should_show_panel(context, "ALIGNMENTS", cls.bl_idname):
            return False
        return is_ifc4x3()

    def draw(self, context):
        layout = self.layout
        props = context.scene.CivilAlignmentProperties

        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("align.draw_vertical_alignment", icon="EYEDROPPER")
        row.operator("align.load_vertical_pis", text="", icon="ANIM_DATA", depress=bool(props.vertical_pi_markers))

        if props.vertical_pi_markers:
            box = layout.box()
            box.label(text="Vertical PIs", icon="ANIM_DATA")
            header = box.row(align=True)
            header.label(text="#")
            header.label(text="Dist Along")
            header.label(text="Elevation")
            header.label(text="Curve")

            box.template_list(
                "ALIGN_UL_vertical_pi_markers",
                "",
                props,
                "vertical_pi_markers",
                props,
                "active_vertical_pi_marker_index",
                rows=4,
            )
            if props.vertical_endpoints_staged:
                row = box.row(align=True)
                row.prop(props, "vertical_start_elevation", text="Start Elev")
                row.prop(props, "vertical_end_elevation", text="End Elev")
            box.operator(
                "align.drag_vertical_pis",
                icon="VIEW_PAN",
                depress=ALIGN_OT_drag_vertical_pis.is_running,
            )

            row = box.row(align=True)
            row.operator("align.apply_vertical_pi_curve", icon="CHECKMARK")
            row.operator("align.finish_vertical_pi_editing", icon="CHECKMARK")


class ALIGN_PT_alignment_stationing_authoring(Panel):
    """Start station and station equations — Alignments tab.

    Edit the start station, and add/remove additional stationing referents
    (station equations) for gaps, overlaps, or reversed stationing direction.
    """

    bl_label = "Stationing"
    bl_idname = "ALIGN_PT_alignment_stationing_authoring"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_alignments"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if not tool.Blender.should_show_panel(context, "ALIGNMENTS", cls.bl_idname):
            return False
        if not is_ifc4x3():
            return False
        return bool(tool.Alignment.get_active_alignment())

    def draw(self, context):
        layout = self.layout
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            layout.label(text="Select an alignment", icon="INFO")
            return

        ifc_file = tool.Ifc.get()
        start_station = ifcopenshell.api.alignment.get_alignment_start_station(ifc_file, alignment) or 0.0
        row = layout.row(align=True)
        row.label(text=f"Start: {tool.Alignment.format_station(start_station)}", icon="EMPTY_AXIS")
        row.operator("align.set_start_station", text="", icon="GREASEPENCIL")

        equations = tool.Alignment.get_stationing_referents(alignment)[1:]  # skip the start referent (D 0)
        if equations:
            layout.separator()
            layout.label(text="Station Equations:")
            for referent, distance_along, station, incoming_station, has_increasing in equations:
                box = layout.box()
                row = box.row(align=True)
                label = f"D {distance_along:.2f}: {tool.Alignment.format_station(station or 0.0)}"
                if incoming_station is not None:
                    label += f" (from {tool.Alignment.format_station(incoming_station)})"
                if has_increasing is False:
                    label += " ↓"
                row.label(text=label)
                op = row.operator("align.edit_station_equation", text="", icon="GREASEPENCIL")
                op.referent_id = referent.id()
                op = row.operator("align.remove_station_equation", text="", icon="X")
                op.referent_id = referent.id()

        layout.operator("align.add_station_equation", icon="ADD")

        layout.separator()
        has_key_points = tool.Alignment.has_key_point_referents(alignment)
        row = layout.row(align=True)
        row.operator(
            "align.generate_key_points",
            text="Regenerate Key Points" if has_key_points else "Generate Key Points",
            icon="FILE_REFRESH" if has_key_points else "ADD",
        )
        if has_key_points:
            row.operator("align.remove_key_points", text="", icon="X")


class ALIGN_PT_alignment_segments(Panel):
    """Read-only segment breakdown for the selected IfcAlignment.

    Lists horizontal, vertical, and cant segments from IFC data.
    Appears in the Alignments tab whenever an alignment object is active.
    """

    bl_label = "Alignment Segments"
    bl_idname = "ALIGN_PT_alignment_segments"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_alignments"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        if not tool.Blender.should_show_panel(context, "ALIGNMENTS", cls.bl_idname):
            return False
        if not is_ifc4x3():
            return False
        ifc_file = tool.Ifc.get()
        return bool(ifc_file and next(iter(ifc_file.by_type("IfcAlignment")), None))

    def draw(self, context):
        layout = self.layout
        props = context.scene.CivilAlignmentProperties
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return

        # --- Alignment selector dropdown (always at top, above segment boxes) ---
        _clamp_alignment_enum(props, context)
        layout.prop(props, "active_alignment_id_str", text="", icon="CURVE_DATA")

        # Sync dropdown from viewport/outliner selection.
        # - Attribute access (props.active_alignment_id_str) returns the string identifier.
        # - Dict access (props["key"] = int) sets by index and bypasses the update callback,
        #   preventing the callback from calling bpy.ops from within a draw function.
        viewport_alignment = tool.Alignment.get_active_alignment()
        if viewport_alignment:
            new_val = str(viewport_alignment.id())
            if props.active_alignment_id_str != new_val:
                for idx, (ident, _, _) in enumerate(_alignment_enum_items(props, context)):
                    if ident == new_val:
                        props["active_alignment_id_str"] = idx
                        context.area.tag_redraw()  # refresh the dropdown widget
                        break

        # Resolve which alignment to display
        try:
            aid = int(props.active_alignment_id_str)
        except (ValueError, TypeError):
            aid = 0

        if aid == 0:
            layout.label(text="Select an alignment above", icon="INFO")
            return

        try:
            alignment = ifc_file.by_id(aid)
        except Exception:
            return
        if not alignment or not alignment.is_a("IfcAlignment"):
            return

        # --- Horizontal layout (collect cants but draw them after vertical) ---
        all_cants = []
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for layout_entity in rel.RelatedObjects or []:
                if layout_entity.is_a("IfcAlignmentHorizontal"):
                    self._draw_horizontal(layout, context, layout_entity, alignment.id())
                elif layout_entity.is_a("IfcAlignmentCant"):
                    all_cants.append(layout_entity)

        if tool.Alignment.is_polyline_alignment(alignment):
            self._draw_polyline(layout, props, alignment)

        # --- Vertical layouts (direct + child alignments) ---
        all_verticals = tool.Alignment.get_all_vertical_layouts(alignment)

        if all_verticals:
            from .decorator import VerticalProfileDecorator
            dec = VerticalProfileDecorator
            row = layout.row(align=True)
            row.label(text="Vertical Profile:", icon="FCURVE")
            row.operator(
                "align.show_vertical_profile", text="",
                icon="GRAPH", depress=dec.is_installed,
            )
            row.prop(props, "vertical_exaggeration", text="VE")

        for layout_entity in all_verticals:
            self._draw_vertical(layout, context, layout_entity)

        # --- Cant layouts (after vertical) ---
        for layout_entity in all_cants:
            self._draw_cant(layout, context, layout_entity)

    def _draw_polyline(self, layout, props, alignment):
        """A polyline alignment (REQUIREMENTS.md §5.1) has no layouts -- list its points instead, the
        way the horizontal section lists its segments: a header with an edit (pencil) button, which
        swaps the list for the editable point table in place, and for a 3D polyline a Show Profile
        button for its (static) distance-along/elevation profile."""
        from .decorator import VerticalProfileDecorator

        box = layout.box()
        try:
            points, dim = tool.Alignment.get_polyline_points(alignment)
        except ValueError as e:
            box.label(text=str(e), icon="ERROR")
            return
        is_editing = bool(props.polyline_point_rows) and props.editing_polyline_alignment_id == alignment.id()
        legs = [math.dist(a, b) for a, b in zip(points[:-1], points[1:])]

        row = box.row(align=True)
        row.label(text=f"Polyline ({dim}D): {len(points)} points, length {sum(legs):.3f}", icon="IPO_LINEAR")
        if is_editing:
            row.operator("align.finish_polyline_table", text="", icon="GREASEPENCIL", depress=True)
        else:
            row.operator("align.load_polyline_table", text="", icon="GREASEPENCIL")

        if dim == 3:
            row = box.row(align=True)
            shown = VerticalProfileDecorator.is_installed
            row.operator("align.show_vertical_profile", text="Hide Profile" if shown else "Show Profile", icon="GRAPH")
            row.prop(props, "vertical_exaggeration", text="VE")
        else:
            box.label(text="2D polyline: no elevations to profile", icon="INFO")

        if is_editing:
            header = box.row(align=True)
            for text in ("#", "Easting", "Northing") + (("Elevation",) if props.editing_polyline_is_3d else ()):
                header.label(text=text)
            row = box.row()
            row.template_list(
                "ALIGN_UL_polyline_points",
                "",
                props,
                "polyline_point_rows",
                props,
                "active_polyline_point_row_index",
                rows=4,
            )
            side = row.column(align=True)
            side.operator("align.add_polyline_point_row", text="", icon="ADD")
            side.operator("align.remove_polyline_point_row", text="", icon="REMOVE")
            row = box.row(align=True)
            row.operator("align.apply_polyline_table", icon="CHECKMARK")
            row.operator("align.finish_polyline_table", icon="CANCEL")
            return

        header = box.row(align=True)
        for text in ("#", "Station", "Easting", "Northing") + (("Elevation",) if dim == 3 else ()):
            header.label(text=text)
        ifc = tool.Ifc.get()
        distance = 0.0
        for i, point in enumerate(points):
            if i:
                distance += legs[i - 1]
            try:
                station = ifcopenshell.api.alignment.station_from_distance_along(ifc, alignment, distance)
            except Exception:
                station = distance
            row = box.row(align=True)
            row.label(text=str(i + 1))
            row.label(text=tool.Alignment.format_station(station))
            row.label(text=f"{point[0]:.3f}")
            row.label(text=f"{point[1]:.3f}")
            if dim == 3:
                row.label(text=f"{point[2]:.3f}")

    def _segments(self, layout_entity):
        for rel in getattr(layout_entity, "IsNestedBy", []) or []:
            for seg in rel.RelatedObjects or []:
                if seg.is_a("IfcAlignmentSegment"):
                    yield seg

    def _draw_segment_editor(
        self, box, props, uilist_idname, rows_propname, active_index_propname,
        kind, apply_idname, cancel_idname,
    ):
        """Shared "stage edits, then Apply" table UI for one layout's segments
        -- an editable UIList + Add/Remove/Move-Up/Move-Down row toolbar +
        Apply/Cancel, used identically by the horizontal/vertical/cant
        sections while that section is the active edit session (see
        align.enable_editing_*_segments)."""
        box.template_list(uilist_idname, "", props, rows_propname, props, active_index_propname, rows=5)
        toolbar = box.row(align=True)
        op = toolbar.operator("align.add_segment_row", text="", icon="ADD")
        op.kind = kind
        op = toolbar.operator("align.remove_segment_row", text="", icon="REMOVE")
        op.kind = kind
        op = toolbar.operator("align.move_segment_row", text="", icon="TRIA_UP")
        op.kind, op.direction = kind, "UP"
        op = toolbar.operator("align.move_segment_row", text="", icon="TRIA_DOWN")
        op.kind, op.direction = kind, "DOWN"

        apply_row = box.row(align=True)
        apply_row.operator(apply_idname, icon="CHECKMARK")
        apply_row.operator(cancel_idname, text="", icon="X")

    def _draw_horizontal(self, layout, context, layout_entity, alignment_id=0):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        selected_id = props.selected_h_segment_id
        expanded = _H_EXPANDED.get(alignment_id, True)
        box = layout.box()

        is_editing_this = (
            props.editing_segment_kind == "HORIZONTAL" and props.editing_layout_id == layout_entity.id()
        )

        # Collapsible header with label toggle
        row = box.row(align=True)
        op = row.operator(
            "align.toggle_h_segments",
            text="", icon="TRIA_DOWN" if expanded else "TRIA_RIGHT", emboss=False,
        )
        op.alignment_id = alignment_id
        row.label(text="Horizontal", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        row.prop(props, "show_h_segment_labels", text="", icon="FONT_DATA")
        edit_op = row.operator(
            "align.enable_editing_h_segments", text="", icon="GREASEPENCIL", depress=is_editing_this
        )
        edit_op.layout_id = layout_entity.id()

        # Delete Horizontal Layout's own poll() already checks
        # has_real_vertical_segments() against the *active* alignment -- fine
        # here since, unlike the per-vertical buttons above, there's only
        # ever one horizontal per alignment, so this row's own alignment_id
        # and "whatever's active" agree whenever this button is actually
        # reachable/relevant.
        row.operator("align.remove_horizontal_layout", text="", icon="TRASH")

        if not expanded:
            return

        if is_editing_this:
            self._draw_segment_editor(
                box, props, "ALIGN_UL_h_segments", "h_segment_rows", "active_h_segment_row_index",
                "HORIZONTAL", "align.apply_h_segments", "align.disable_editing_h_segments",
            )
            return

        # Column headers (no separate select column — index cell is the select button)
        header = box.split(factor=0.08)
        header.label(text="#")
        h2 = header.split(factor=0.30)
        h2.label(text="Type")
        h3 = h2.split(factor=0.27)
        h3.label(text="Length")
        h4 = h3.split(factor=0.37)
        h4.label(text="Radius")
        h4.label(text="Bearing")

        # grid bearings, matching the E/N shown below (StartDirection is in project coordinates)
        grid_rotation = _grid_rotation_deg(from_blender_world=False)
        idx = 1
        for seg in self._segments(layout_entity):
            dp = seg.DesignParameters
            if not dp:
                continue
            length = getattr(dp, "SegmentLength", 0.0) or 0.0
            if length == 0.0:
                continue  # zero-length terminators are invisible to users

            seg_id = seg.id()
            is_selected = selected_id == seg_id
            seg_type = dp.PredefinedType or "?"
            r_start = getattr(dp, "StartRadiusOfCurvature", None) or 0.0
            bearing = (
                _rad_to_bearing(dp.StartDirection + math.radians(grid_rotation))
                if hasattr(dp, "StartDirection")
                else ""
            )
            e, n = _start_en(ifc_file, dp)

            col = box.column(align=True)
            col.alert = is_selected

            # Row 1: index (clickable to select), type, length, radius, bearing
            row = col.split(factor=0.08)
            op = row.operator(
                "align.select_h_segment",
                text=str(idx),
                depress=is_selected,
            )
            op.segment_id = seg_id

            r2 = row.split(factor=0.30)
            r2.label(text=seg_type)
            r3 = r2.split(factor=0.27)
            r3.label(text=f"{abs(length):.2f}")
            r4 = r3.split(factor=0.37)
            r4.label(text=f"{abs(r_start):.1f}" if r_start else "-")
            r4.label(text=bearing)

            # Row 2: start Easting / Northing
            if e is not None:
                sub = col.split(factor=0.08)
                sub.label(text="")  # align under # column
                sub2 = sub.split(factor=0.50)
                sub2.label(text=f"E: {e:.3f}")
                sub2.label(text=f"N: {n:.3f}")

            idx += 1

    def _draw_vertical(self, layout, context, layout_entity):
        from .decorator import VerticalProfileDecorator

        dec = VerticalProfileDecorator
        props = context.scene.CivilAlignmentProperties
        v_id = layout_entity.id()
        # Distinct per vertical even when every child alignment carries the same generated name
        label = tool.Alignment.get_vertical_display_name(layout_entity)
        expanded = _V_EXPANDED.get(v_id, True)
        selected_v_id = props.selected_v_segment_id
        is_editing_this = props.editing_segment_kind == "VERTICAL" and props.editing_layout_id == v_id

        # Eye-icon uses vertical_items (populated when the profile window is open)
        v_item = next((it for it in props.vertical_items if it.entity_id == v_id), None)

        box = layout.box()
        row = box.row(align=True)

        # Collapsible toggle via operator (safe to call from draw)
        op = row.operator(
            "align.toggle_v_segments",
            text="", icon="TRIA_DOWN" if expanded else "TRIA_RIGHT", emboss=False,
        )
        op.entity_id = v_id

        # the name itself is the rename button
        rename_op = row.operator("align.rename_vertical", text=label, icon="FCURVE", emboss=False)
        rename_op.layout_id = v_id

        # Per-vertical eye-icon — only shown when the profile window is open
        if dec.is_installed and v_item is not None:
            vis_icon = "HIDE_OFF" if v_item.is_visible else "HIDE_ON"
            row.prop(v_item, "is_visible", text="", icon=vis_icon, emboss=False)

        # Per-vertical label toggle — only shown when the profile window is open
        if dec.is_installed and v_item is not None:
            row.prop(v_item, "show_labels", text="", icon="FONT_DATA")

        # A classmethod poll() can't see this row's own v_id (operator
        # properties like layout_id aren't set until after the button
        # fires), so it can only ever check tool.Alignment.get_active_alignment()
        # -- whatever object happens to be active/selected. That's a no-op
        # whenever the active object isn't this specific vertical's own
        # alignment, letting these buttons stay clickable (and only fail
        # with a poll-message-less error on click) even while this row's own
        # alignment has an open horizontal PI marker edit. Disable them here
        # instead, computed directly from this row's v_id.
        owning_alignment_id = _alignment_id_owning_layout(layout_entity)
        h_markers_open = bool(owning_alignment_id and _find_pi_markers(owning_alignment_id))

        edit_row = row.row(align=True)
        edit_row.enabled = not h_markers_open
        edit_op = edit_row.operator(
            "align.enable_editing_v_segments", text="", icon="GREASEPENCIL", depress=is_editing_this
        )
        edit_op.layout_id = v_id

        is_editing_pi = props.editing_vertical_pi_layout_id == v_id and bool(props.vertical_pi_markers)
        pi_row = row.row(align=True)
        pi_row.enabled = not h_markers_open
        pi_op = pi_row.operator(
            "align.load_vertical_pis", text="", icon="ANIM_DATA", depress=is_editing_pi,
        )
        pi_op.layout_id = v_id

        extend_row = row.row(align=True)
        extend_row.enabled = not h_markers_open
        extend_op = extend_row.operator("align.extend_vertical_alignment", text="", icon="FORWARD")
        extend_op.layout_id = v_id

        # Only shown once this vertical's PIs are loaded -- the button that ends the
        # edit lives right next to the one that started it, rather than only in the
        # (separate, collapsed-by-default) Vertical Alignment panel below.
        if is_editing_pi:
            row.operator("align.finish_vertical_pi_editing", text="", icon="CHECKMARK")

        # Same "poll() can't see this row's own v_id" reasoning as edit_row/
        # pi_row above -- has_cant is computed directly from this row's own
        # vertical, since a classmethod poll() has no way to know which
        # specific vertical Delete Vertical Layout's button is about to act
        # on until after it's clicked.
        owning_alignment = ifcopenshell.api.alignment.get_alignment(layout_entity)
        existing_cant = ifcopenshell.api.alignment.get_cant_layout(owning_alignment) if owning_alignment else None
        has_cant = bool(existing_cant and tool.Alignment.get_real_layout_segments(existing_cant))

        cant_row = row.row(align=True)
        cant_row.enabled = not h_markers_open
        cant_op = cant_row.operator("align.generate_cant_layout", text="", icon="MOD_CURVE")
        cant_op.layout_id = v_id

        del_row = row.row(align=True)
        del_row.enabled = not h_markers_open and not has_cant
        del_op = del_row.operator("align.remove_vertical_layout", text="", icon="TRASH")
        del_op.layout_id = v_id

        _draw_length_mismatch(box, layout_entity)

        if not expanded:
            return

        if is_editing_this:
            self._draw_segment_editor(
                box, props, "ALIGN_UL_v_segments", "v_segment_rows", "active_v_segment_row_index",
                "VERTICAL", "align.apply_v_segments", "align.disable_editing_v_segments",
            )
            return

        # Column headers (index cell is the select button)
        header = box.split(factor=0.08)
        header.label(text="#")
        h2 = header.split(factor=0.32)
        h2.label(text="Type")
        h3 = h2.split(factor=0.28)
        h3.label(text="H-Length")
        h4 = h3.split(factor=0.45)
        h4.label(text="G In")
        h4.label(text="G Out")

        idx = 1
        for seg in self._segments(layout_entity):
            dp = seg.DesignParameters
            if not dp:
                continue
            seg_type = dp.PredefinedType or "?"
            h_len = getattr(dp, "HorizontalLength", 0.0) or 0.0
            if h_len == 0.0:
                continue  # zero-length terminators are invisible to users
            g_start = getattr(dp, "StartGradient", 0.0) or 0.0
            g_end = getattr(dp, "EndGradient", 0.0) or 0.0
            dist_along = getattr(dp, "StartDistAlong", None)
            start_height = getattr(dp, "StartHeight", None)
            seg_id = seg.id()
            is_v_selected = selected_v_id == seg_id

            col = box.column(align=True)
            col.alert = is_v_selected

            # Row 1: index (clickable to select), type, length, grades
            row = col.split(factor=0.08)
            op = row.operator(
                "align.select_v_segment",
                text=str(idx),
                depress=is_v_selected,
            )
            op.segment_id = seg_id

            r2 = row.split(factor=0.32)
            r2.label(text=seg_type[:14])
            r3 = r2.split(factor=0.28)
            r3.label(text=f"{h_len:.2f}")
            r4 = r3.split(factor=0.45)
            r4.label(text=f"{g_start * 100:.3f}%")
            r4.label(text=f"{g_end * 100:.3f}%")

            # Row 2: start distance along + elevation
            if dist_along is not None or start_height is not None:
                sub = col.split(factor=0.08)
                sub.label(text="")
                sub2 = sub.split(factor=0.50)
                sub2.label(text=f"Dist: {dist_along:.2f}" if dist_along is not None else "")
                sub2.label(text=f"Elev: {start_height:.3f}" if start_height is not None else "")

            idx += 1

    def _draw_cant(self, layout, context, layout_entity):
        from .decorator import VerticalProfileDecorator

        dec = VerticalProfileDecorator
        props = context.scene.CivilAlignmentProperties
        c_id = layout_entity.id()
        label = layout_entity.Name or f"Cant #{c_id}"
        expanded = _C_EXPANDED.get(c_id, True)
        selected_c_id = props.selected_cant_segment_id
        is_editing_this = props.editing_segment_kind == "CANT" and props.editing_layout_id == c_id

        c_item = next((it for it in props.cant_items if it.entity_id == c_id), None)

        box = layout.box()
        row = box.row(align=True)

        op = row.operator(
            "align.toggle_cant_segments",
            text="", icon="TRIA_DOWN" if expanded else "TRIA_RIGHT", emboss=False,
        )
        op.entity_id = c_id
        row.label(text=label, icon="MOD_CURVE")

        if dec.is_installed and c_item is not None:
            vis_icon = "HIDE_OFF" if c_item.is_visible else "HIDE_ON"
            row.prop(c_item, "is_visible", text="", icon=vis_icon, emboss=False)

        row.prop(props, "show_cant_segment_labels", text="", icon="FONT_DATA")

        edit_op = row.operator(
            "align.enable_editing_cant_segments", text="", icon="GREASEPENCIL", depress=is_editing_this
        )
        edit_op.layout_id = c_id

        del_op = row.operator("align.remove_cant_layout", text="", icon="TRASH")
        del_op.layout_id = c_id

        _draw_length_mismatch(box, layout_entity)

        if not expanded:
            return

        if is_editing_this:
            self._draw_segment_editor(
                box, props, "ALIGN_UL_cant_segments", "cant_segment_rows", "active_cant_segment_row_index",
                "CANT", "align.apply_cant_segments", "align.disable_editing_cant_segments",
            )
            return

        # Column headers (# is the select button)
        header = box.split(factor=0.08)
        header.label(text="#")
        h2 = header.split(factor=0.30)
        h2.label(text="Type")
        h3 = h2.split(factor=0.27)
        h3.label(text="Length")
        h4 = h3.split(factor=0.37)
        h4.label(text="Start L / R")
        h4.label(text="End L / R")

        def _cant_pair(left, right):
            # cant is each rail's deviating elevation; show both, sign preserved
            return f"{left * 1000:.0f} / {right * 1000:.0f}"

        idx = 1
        for seg in self._segments(layout_entity):
            dp = seg.DesignParameters
            if not dp:
                continue
            seg_type = dp.PredefinedType or "?"
            h_len = getattr(dp, "HorizontalLength", None)
            if h_len is None:
                h_len = getattr(dp, "Length", 0.0) or 0.0
            if h_len == 0.0:
                continue  # zero-length terminators are invisible to users
            start_l = getattr(dp, "StartCantLeft", None) or 0.0
            start_r = getattr(dp, "StartCantRight", None) or 0.0
            end_l = getattr(dp, "EndCantLeft", None)
            end_r = getattr(dp, "EndCantRight", None)
            end_l = start_l if end_l is None else end_l
            end_r = start_r if end_r is None else end_r
            seg_id = seg.id()
            is_c_selected = selected_c_id == seg_id

            col = box.column(align=True)
            col.alert = is_c_selected

            row = col.split(factor=0.08)
            op = row.operator(
                "align.select_cant_segment",
                text=str(idx),
                depress=is_c_selected,
            )
            op.segment_id = seg_id

            r2 = row.split(factor=0.30)
            r2.label(text=seg_type[:14])
            r3 = r2.split(factor=0.27)
            r3.label(text=f"{h_len:.2f}" if h_len else "-")
            r4 = r3.split(factor=0.37)
            r4.label(text=_cant_pair(start_l, start_r))
            r4.label(text=_cant_pair(end_l, end_r))

            idx += 1
