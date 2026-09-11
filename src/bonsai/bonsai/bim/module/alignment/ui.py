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

All panels appear in the Properties sidebar under the CIVIL tab,
nested under BIM_PT_tab_horizontal_alignment.
"""

import bpy
import math
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import bonsai.tool as tool
from bpy.types import Panel, UIList, Operator
from bpy.props import IntProperty, BoolProperty
from .prop import _alignment_enum_items
from .operator import _find_pi_markers, _resolve_alignment_id_for_markers, _is_interior_pi_marker


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


# =============================================================================
# UILists
# =============================================================================


class ALIGN_UL_alignment_pis(UIList):
    """UIList for displaying interleaved points and segments (Civil 3D style)

    Row types:
    - POINT rows: End (endpoint), Mid (interior PI without curve)
    - SEGMENT rows: Tan (tangent line), Curve (circular arc)

    When a Mid point has radius > 0, it becomes a Curve segment row.
    """

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)

            if item.row_type == "POINT":
                # Point row: No., Type, X, Y, Length, Radius
                row.label(text="")  # No segment number for points

                # Type with point/dot icon
                # "End" = endpoint (POB/POE), "Mid" = interior PI point
                row.label(text=item.display_type, icon="DOT")

                # X, Y coordinates - get actual PI for editing
                pi = data.pis[item.pi_index] if item.pi_index < len(data.pis) else None
                if pi:
                    sub = row.row(align=True)
                    sub.prop(pi, "e", text="")
                    sub.prop(pi, "n", text="")
                else:
                    row.label(text=f"{float(item.e):.2f}")
                    row.label(text=f"{float(item.n):.2f}")

                # Length column - empty for point rows
                row.label(text="")

                # Radius column - editable for Mid points (where curves can be added)
                if item.display_type == "Mid" and pi:
                    row.prop(pi, "radius", text="")
                else:
                    row.label(text="")

            elif item.row_type == "SEGMENT":
                if item.display_type == "Curve":
                    # Curve segment row: No., Type (arc icon), X, Y, Arc Length, Radius
                    row.label(text=f"{item.segment_number}")
                    row.label(text="Curve", icon="SPHERECURVE")

                    # Show PI coordinates on curve row
                    row.label(text=f"{float(item.e):.2f}")
                    row.label(text=f"{float(item.n):.2f}")

                    # Arc length
                    row.label(text=f"{item.arc_length:.2f}")

                    # Radius - editable so user can modify or delete curve (set to 0)
                    pi = data.pis[item.pi_index] if item.pi_index < len(data.pis) else None
                    if pi:
                        row.prop(pi, "radius", text="")
                    else:
                        row.label(text=f"{item.radius:.2f}")
                else:
                    # Tangent segment row: No., Type (line icon), -, -, Length, -
                    row.label(text=f"{item.segment_number}")
                    row.label(text="Tan", icon="IPO_LINEAR")

                    # No X, Y for tangent segments
                    row.label(text="")
                    row.label(text="")

                    # Length
                    row.label(text=f"{item.length:.2f}")

                    # No radius for tangent segments
                    row.label(text="-")

        elif self.layout_type == "GRID":
            layout.alignment = "CENTER"
            layout.label(text="", icon="DECORATE")


# =============================================================================
# Creation Sub-Panel
# =============================================================================


class ALIGN_PT_alignment_creation(Panel):
    """Sub-panel for alignment creation tools"""

    bl_label = "Creation"
    bl_idname = "ALIGN_PT_alignment_creation"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_horizontal_alignment"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Blender.should_show_panel(context, "CIVIL", cls.bl_idname) and is_ifc4x3()

    def draw(self, context):
        layout = self.layout
        props = context.scene.CivilAlignmentProperties

        # New alignment properties
        box = layout.box()
        box.label(text="New Alignment:", icon="ADD")
        box.prop(props, "new_alignment_name")
        box.prop(props, "start_station")

        # Creation operators
        col = layout.column(align=True)
        col.operator("align.create_alignment_by_pi", icon="CURVE_DATA")


# =============================================================================
# PI Editor Sub-Panel
# =============================================================================


class ALIGN_PT_pi_editor(Panel):
    """Sub-panel for PI point table editor (Civil 3D style grid view)"""

    bl_label = "PI Editor"
    bl_idname = "ALIGN_PT_pi_editor"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_horizontal_alignment"
    bl_options = set()  # Open by default

    @classmethod
    def poll(cls, context):
        return tool.Blender.should_show_panel(context, "CIVIL", cls.bl_idname) and is_ifc4x3()

    def draw(self, context):
        layout = self.layout
        props = context.scene.CivilAlignmentProperties

        # PI Edit Mode indicator
        if props.is_pi_edit_mode:
            box = layout.box()
            box.alert = True
            box.label(text="PI Edit Mode Active", icon="EDITMODE_HLT")
            col = box.column(align=True)
            col.label(text="Move PIs with G key")
            col.label(text="Press Enter to apply")
            col.label(text="Press Escape to cancel")
            layout.separator()
            return  # Don't show normal UI while in edit mode

        # Edit existing alignment button
        if props.active_alignment_id != 0:
            box = layout.box()
            box.label(text="Edit Alignment:", icon="EDITMODE_HLT")
            box.operator("align.enter_pi_edit_mode", icon="PIVOT_CURSOR", text="Edit PIs (G key)")
            layout.separator()

        # Header row with column labels
        header = layout.row(align=True)
        header.label(text="No.")
        header.label(text="Type")
        header.label(text="E")
        header.label(text="N")
        header.label(text="Length")
        header.label(text="Radius")

        # Combined point/segment list (interleaved view)
        row = layout.row()
        row.template_list(
            "ALIGN_UL_alignment_pis",
            "",
            props,
            "display_rows",
            props,
            "active_display_row_index",
            rows=8,
        )

        # Side buttons for list management
        col = row.column(align=True)
        col.operator("align.add_pi", icon="ADD", text="")
        col.operator("align.remove_pi", icon="REMOVE", text="")
        col.separator()
        col.operator("align.pick_pi_from_viewport", icon="EYEDROPPER", text="")

        # Bottom actions
        layout.separator()
        row = layout.row(align=True)
        row.operator("align.recalculate_pis", icon="FILE_REFRESH", text="Recalculate")
        row.operator("align.clear_pis", icon="TRASH", text="Clear All")


# =============================================================================
# Stationing Sub-Panel
# =============================================================================


class ALIGN_PT_alignment_stationing(Panel):
    """Sub-panel for stationing and referents"""

    bl_label = "Stationing"
    bl_idname = "ALIGN_PT_alignment_stationing"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_horizontal_alignment"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return tool.Blender.should_show_panel(context, "CIVIL", cls.bl_idname) and is_ifc4x3()

    def draw(self, context):
        layout = self.layout

        # Stationing operators
        col = layout.column(align=True)
        col.operator("align.add_stationing_referent", icon="EMPTY_AXIS")
        col.operator("align.name_segments", icon="FONT_DATA")


# =============================================================================
# Alignments Tab – Segment Breakdown Panel
# =============================================================================


def _rad_to_bearing(rad: float) -> str:
    """Convert IFC start direction (radians, CCW from east) to compass bearing.

    IFC: 0 = east, increasing CCW.  Bearing: 0 = north, increasing CW.
    Result: N dd°mm'ss" E / S dd°mm'ss" E / S dd°mm'ss" W / N dd°mm'ss" W
    """
    bearing_deg = (90.0 - math.degrees(rad)) % 360.0

    def dms(angle_deg: float) -> str:
        d = int(angle_deg)
        m = int((angle_deg - d) * 60)
        s = (angle_deg - d - m / 60) * 3600
        return f"{d}°{m:02d}'{s:04.1f}\""

    if bearing_deg < 90.0:
        return f"N {dms(bearing_deg)} E"
    elif bearing_deg < 180.0:
        return f"S {dms(180.0 - bearing_deg)} E"
    elif bearing_deg < 270.0:
        return f"S {dms(bearing_deg - 180.0)} W"
    else:
        return f"N {dms(360.0 - bearing_deg)} W"


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

    This is a from-scratch authoring workflow, independent of the CIVIL tab's
    PI-table tools: add a bare alignment, then draw its horizontal geometry
    directly in the viewport.
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

        alignment = tool.Alignment.get_active_alignment()
        row = col.row(align=True)
        row.enabled = bool(alignment)
        row.operator("align.draw_horizontal_alignment", icon="EYEDROPPER")
        row.operator("align.remove_alignment", text="", icon="TRASH")
        if not alignment:
            col.label(text="Add or select an alignment first", icon="INFO")

        marker = context.active_object
        is_marker = bool(marker) and _is_interior_pi_marker(marker)
        markers_present = _pi_markers_present(context)

        if is_marker or markers_present:
            box = layout.box()
            if is_marker:
                pi_data = marker.bonsai_pi_curve_marker
                box.label(text=f"PI {pi_data.pi_index}", icon="EMPTY_AXIS")
                box.prop(pi_data, "curve_type")
                if pi_data.curve_type == "CIRCULAR":
                    box.prop(pi_data, "radius")
                box.operator("align.apply_pi_curve", icon="CHECKMARK")
            else:
                box.label(text="Select a PI marker to define its curve", icon="INFO")

            if markers_present:
                box.operator("align.clear_pi_markers", icon="TRASH")


class ALIGN_PT_alignment_stationing_authoring(Panel):
    """Start station and station equations — Alignments tab.

    A from-scratch equivalent of the CIVIL tab's stationing panel: edit the
    start station, and add/remove additional stationing referents (station
    equations) for gaps, overlaps, or reversed stationing direction.
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

        # --- Vertical layouts (direct + child alignments) ---
        all_verticals = tool.Alignment.get_all_vertical_layouts(alignment)

        if all_verticals:
            from .decorator import VerticalProfileDecorator
            dec = VerticalProfileDecorator
            row = layout.row(align=True)
            row.label(text="Vertical Profile:", icon="FCURVE")
            row.prop(props, "vertical_exaggeration", text="VE")
            row.operator(
                "align.show_vertical_profile", text="",
                icon="GRAPH", depress=dec.is_installed,
            )

        for layout_entity in all_verticals:
            self._draw_vertical(layout, context, layout_entity)

        # --- Cant layouts (after vertical) ---
        for layout_entity in all_cants:
            self._draw_cant(layout, context, layout_entity)

    def _segments(self, layout_entity):
        for rel in getattr(layout_entity, "IsNestedBy", []) or []:
            for seg in rel.RelatedObjects or []:
                if seg.is_a("IfcAlignmentSegment"):
                    yield seg

    def _draw_horizontal(self, layout, context, layout_entity, alignment_id=0):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        selected_id = props.selected_h_segment_id
        expanded = _H_EXPANDED.get(alignment_id, True)
        box = layout.box()

        # Collapsible header with label toggle
        row = box.row(align=True)
        op = row.operator(
            "align.toggle_h_segments",
            text="", icon="TRIA_DOWN" if expanded else "TRIA_RIGHT", emboss=False,
        )
        op.alignment_id = alignment_id
        row.label(text="Horizontal", icon="DRIVER_ROTATIONAL_DIFFERENCE")
        row.prop(props, "show_h_segment_labels", text="", icon="FONT_DATA")

        if not expanded:
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
            bearing = _rad_to_bearing(dp.StartDirection) if hasattr(dp, "StartDirection") else ""
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
        # Prefer the name of the alignment that owns this vertical layout.
        # For CT 4.1.4.4.1.2 this is the child alignment (e.g. "Design Grade");
        # for a simple alignment it is the top-level alignment name.
        label = None
        for rel in getattr(layout_entity, "Nests", []) or []:
            if rel.RelatingObject.is_a("IfcAlignment"):
                label = rel.RelatingObject.Name
                break
        label = label or layout_entity.Name or f"Vertical #{v_id}"
        expanded = _V_EXPANDED.get(v_id, True)
        selected_v_id = props.selected_v_segment_id

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

        row.label(text=label, icon="FCURVE")

        # Per-vertical eye-icon — only shown when the profile window is open
        if dec.is_installed and v_item is not None:
            vis_icon = "HIDE_OFF" if v_item.is_visible else "HIDE_ON"
            row.prop(v_item, "is_visible", text="", icon=vis_icon, emboss=False)

        # Per-vertical label toggle — only shown when the profile window is open
        if dec.is_installed and v_item is not None:
            row.prop(v_item, "show_labels", text="", icon="FONT_DATA")

        if not expanded:
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

        if not expanded:
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
