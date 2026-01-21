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


"""UI panels for the alignment module

All panels appear in the VIEW_3D N-panel under the "Saikei Civil" tab.
"""

import bpy
from bpy.types import Panel, UIList


def get_ifc_file():
    """Get the current IFC file from Bonsai"""
    try:
        import bonsai.tool as tool

        return tool.Ifc.get()
    except (ImportError, AttributeError):
        return None


def is_ifc4x3():
    """Check if the current IFC file is IFC4X3 schema"""
    ifc = get_ifc_file()
    return ifc is not None and ifc.schema == "IFC4X3"


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
                    sub.prop(pi, "x", text="")
                    sub.prop(pi, "y", text="")
                else:
                    row.label(text=f"{item.x:.2f}")
                    row.label(text=f"{item.y:.2f}")

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
                    row.label(text=f"{item.x:.2f}")
                    row.label(text=f"{item.y:.2f}")

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
# Main Panel
# =============================================================================


class SAIKEI_PT_horizontal_alignment(Panel):
    """Main Horizontal Alignment panel in the N-panel"""

    bl_label = "Horizontal Alignment"
    bl_idname = "SAIKEI_PT_horizontal_alignment"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Saikei Civil"

    def draw(self, context):
        layout = self.layout
        props = context.scene.SaikeiAlignmentProperties

        # Status box
        box = layout.box()
        ifc = get_ifc_file()

        if ifc is None:
            box.label(text="No IFC file loaded", icon="ERROR")
            box.label(text="Open an IFC4X3 file via Bonsai")
            return

        if ifc.schema != "IFC4X3":
            box.label(text=f"Schema: {ifc.schema}", icon="ERROR")
            box.label(text="Alignments require IFC4X3")
            return

        # IFC file is loaded and correct schema
        row = box.row()
        row.label(text="IFC4X3", icon="CHECKMARK")

        # Count alignments
        alignments = ifc.by_type("IfcAlignment")
        row.label(text=f"Alignments: {len(alignments)}")

        # Active alignment selector
        if alignments:
            box = layout.box()
            box.label(text="Active Alignment:", icon="CURVE_PATH")
            row = box.row()
            row.prop(props, "active_alignment_name", text="")


# =============================================================================
# Creation Sub-Panel
# =============================================================================


class SAIKEI_PT_alignment_creation(Panel):
    """Sub-panel for alignment creation tools"""

    bl_label = "Creation"
    bl_idname = "SAIKEI_PT_alignment_creation"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Saikei Civil"
    bl_parent_id = "SAIKEI_PT_horizontal_alignment"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return is_ifc4x3()

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
        col.operator("saikei.create_alignment", icon="ADD")
        col.operator("saikei.create_alignment_by_pi", icon="CURVE_PATH")
        col.operator("saikei.import_alignment_csv", icon="IMPORT")


# =============================================================================
# PI Editor Sub-Panel
# =============================================================================


class SAIKEI_PT_pi_editor(Panel):
    """Sub-panel for PI point table editor (Civil 3D style grid view)"""

    bl_label = "PI Editor"
    bl_idname = "SAIKEI_PT_pi_editor"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Saikei Civil"
    bl_parent_id = "SAIKEI_PT_horizontal_alignment"
    bl_options = set()  # Open by default

    @classmethod
    def poll(cls, context):
        return is_ifc4x3()

    def draw(self, context):
        layout = self.layout
        props = context.scene.SaikeiAlignmentProperties

        # Header row with column labels
        header = layout.row(align=True)
        header.label(text="No.")
        header.label(text="Type")
        header.label(text="X")
        header.label(text="Y")
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

        # Active item details - show details based on selected row
        if props.display_rows and 0 <= props.active_display_row_index < len(props.display_rows):
            active_row = props.display_rows[props.active_display_row_index]

            if active_row.row_type == "POINT" and active_row.pi_index < len(props.pis):
                pi = props.pis[active_row.pi_index]

                box = layout.box()
                box.label(text=f"PI {active_row.pi_index + 1} Details:", icon="PROPERTIES")

                row = box.row()
                row.prop(pi, "pi_type", text="Type")

                row = box.row(align=True)
                row.prop(pi, "x", text="X")
                row.prop(pi, "y", text="Y")

                # Show radius for interior points (can add curve)
                if pi.pi_type != "ENDPOINT":
                    row = box.row()
                    row.prop(pi, "radius", text="Radius")

                # Display computed values
                row = box.row()
                row.label(text=f"Station: {pi.station:.2f}")
                row.label(text=f"Length: {pi.length_to_next:.2f}")

            elif active_row.row_type == "SEGMENT":
                if active_row.display_type == "Curve":
                    # Curve segment - show curve details with editable radius
                    pi = props.pis[active_row.pi_index] if active_row.pi_index < len(props.pis) else None

                    box = layout.box()
                    box.label(text=f"Curve {active_row.segment_number} Details:", icon="SPHERECURVE")

                    row = box.row()
                    row.label(text=f"PI Location: ({active_row.x:.2f}, {active_row.y:.2f})")

                    row = box.row()
                    row.label(text=f"Arc Length: {active_row.arc_length:.2f}")

                    # Editable radius
                    if pi:
                        row = box.row()
                        row.prop(pi, "radius", text="Radius")
                    else:
                        row = box.row()
                        row.label(text=f"Radius: {active_row.radius:.2f}")
                else:
                    # Tangent segment
                    box = layout.box()
                    box.label(text=f"Tangent {active_row.segment_number} Details:", icon="IPO_LINEAR")

                    row = box.row()
                    row.label(text=f"Length: {active_row.length:.2f}")

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
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Saikei Civil"
    bl_parent_id = "SAIKEI_PT_horizontal_alignment"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return is_ifc4x3()

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
