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
import bonsai.tool as tool
from bpy.types import Panel, UIList


def is_ifc4x3():
    """Check if the current IFC file is IFC4X3 schema"""
    return tool.Ifc.get_schema() == "IFC4X3"


# =============================================================================
# UILists
# =============================================================================


class SAIKEI_UL_alignment_pis(UIList):
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
# Main Status Panel
# =============================================================================


class SAIKEI_PT_alignment_status(Panel):
    """Status panel showing IFC schema and alignment count"""

    bl_label = "Status"
    bl_idname = "SAIKEI_PT_alignment_status"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_horizontal_alignment"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        return tool.Blender.should_show_panel(context, "CIVIL", cls.bl_idname) and tool.Ifc.get()

    def draw(self, context):
        layout = self.layout
        props = context.scene.SaikeiAlignmentProperties
        ifc = tool.Ifc.get()

        if ifc is None:
            row = layout.row()
            row.label(text="No IFC file loaded", icon="ERROR")
            return

        if ifc.schema != "IFC4X3":
            row = layout.row()
            row.label(text=f"Schema: {ifc.schema}", icon="ERROR")
            row = layout.row()
            row.label(text="Alignments require IFC4X3")
            return

        # IFC file is loaded and correct schema
        row = layout.row()
        row.label(text="IFC4X3", icon="CHECKMARK")

        # Count alignments
        alignments = ifc.by_type("IfcAlignment")
        row.label(text=f"Alignments: {len(alignments)}")

        # Active alignment selector
        if alignments:
            row = layout.row()
            row.label(text="Active Alignment:", icon="CURVE_DATA")
            row = layout.row()
            row.prop(props, "active_alignment_name", text="")


# =============================================================================
# Creation Sub-Panel
# =============================================================================


class SAIKEI_PT_alignment_creation(Panel):
    """Sub-panel for alignment creation tools"""

    bl_label = "Creation"
    bl_idname = "SAIKEI_PT_alignment_creation"
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
        props = context.scene.SaikeiAlignmentProperties

        # New alignment properties
        box = layout.box()
        box.label(text="New Alignment:", icon="ADD")
        box.prop(props, "new_alignment_name")
        box.prop(props, "start_station")

        # Creation operators
        col = layout.column(align=True)
        col.operator("saikei.create_alignment_by_pi", icon="CURVE_DATA")


# =============================================================================
# PI Editor Sub-Panel
# =============================================================================


class SAIKEI_PT_pi_editor(Panel):
    """Sub-panel for PI point table editor (Civil 3D style grid view)"""

    bl_label = "PI Editor"
    bl_idname = "SAIKEI_PT_pi_editor"
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
        props = context.scene.SaikeiAlignmentProperties

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
            box.operator("saikei.enter_pi_edit_mode", icon="PIVOT_CURSOR", text="Edit PIs (G key)")
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
            "SAIKEI_UL_alignment_pis",
            "",
            props,
            "display_rows",
            props,
            "active_display_row_index",
            rows=8,
        )

        # Side buttons for list management
        col = row.column(align=True)
        col.operator("saikei.add_pi", icon="ADD", text="")
        col.operator("saikei.remove_pi", icon="REMOVE", text="")
        col.separator()
        col.operator("saikei.pick_pi_from_viewport", icon="EYEDROPPER", text="")

        # Bottom actions
        layout.separator()
        row = layout.row(align=True)
        row.operator("saikei.recalculate_pis", icon="FILE_REFRESH", text="Recalculate")
        row.operator("saikei.clear_pis", icon="TRASH", text="Clear All")


# =============================================================================
# Stationing Sub-Panel
# =============================================================================


class SAIKEI_PT_alignment_stationing(Panel):
    """Sub-panel for stationing and referents"""

    bl_label = "Stationing"
    bl_idname = "SAIKEI_PT_alignment_stationing"
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
        props = context.scene.SaikeiAlignmentProperties

        # Station display options
        box = layout.box()
        box.label(text="Display:", icon="HIDE_OFF")
        box.prop(props, "show_station_labels")
        box.prop(props, "station_interval")

        layout.separator()

        # Stationing operators
        col = layout.column(align=True)
        col.operator("saikei.add_stationing_referent", icon="EMPTY_AXIS")
        col.operator("saikei.name_segments", icon="FONT_DATA")
