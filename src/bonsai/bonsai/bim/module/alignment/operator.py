# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2022 Yassine Oualid <yassine@sigmadimensions.com>, 2026 Michael Yoder <myoder@desertspringscivil.com>
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

# pyright: reportUnnecessaryTypeIgnoreComment=error


import bpy
import time
import bonsai.core.alignment as core
import bonsai.tool as tool
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty
from . import decorator as alignment_decorator
from bonsai.bim.module.model.polyline import PolylineOperator
from bonsai.bim.module.model.decorator import PolylineDecorator
from bonsai.bim.ifc import IfcStore


class ImportAlignmentCSV(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_alignment_csv"
    bl_label = "Import Alignment CSV"
    bl_description = (
        "Import alignment(s) from a .csv file — one horizontal row (X,Y,R "
        "triples) plus any number of vertical rows (D,Z,L triples)"
    )
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def _execute(self, context):
        start = time.time()
        props = context.scene.CivilAlignmentProperties

        alignment = core.import_alignment_csv(tool.Ifc, tool.Alignment, filepath=self.filepath)

        props.active_alignment_name = alignment.Name or "Imported Alignment"
        props.active_alignment_id = alignment.id()

        self.report({"INFO"}, "Imported in %s seconds" % (time.time() - start))


def poll_ifc4x3(cls, context):
    """Standard poll method for IFC4X3 requirement"""
    ifc = tool.Ifc.get()
    if ifc is None:
        cls.poll_message_set("No IFC file loaded. Open an IFC file via Bonsai.")
        return False
    if ifc.schema != "IFC4X3":
        cls.poll_message_set(f"Schema is {ifc.schema}. Alignments require IFC4X3.")
        return False
    return True


def _resolve_active_alignment(context):
    """Return the IfcAlignment for ``props.active_alignment_id``, or None.

    Operators that act on an existing alignment store it as
    ``active_alignment_id`` (set on create/visualize) and their ``_execute``
    uses that id — so their ``poll`` must resolve the alignment the same way,
    NOT via the active viewport object (which is typically a segment curve
    after PI/curve editing).
    """
    props = context.scene.CivilAlignmentProperties
    if props.active_alignment_id == 0:
        return None
    ifc_file = tool.Ifc.get()
    if ifc_file is None:
        return None
    try:
        alignment = ifc_file.by_id(props.active_alignment_id)
    except RuntimeError:
        return None
    return alignment if alignment.is_a("IfcAlignment") else None


def sync_pis_from_ifc(props):
    """Sync PI Editor data from IFC alignment.

    This is called on undo/redo to ensure the PI Editor reflects the current
    IFC state. It extracts PI data from the alignment's horizontal segments.

    If no active alignment exists or it's invalid, clears the PI Editor.

    Returns:
        bool: True if sync was successful, False if alignment was cleared.
    """
    ifc = tool.Ifc.get()
    if ifc is None:
        # No IFC file - clear everything
        props.pis.clear()
        props.active_pi_index = 0
        rebuild_display_rows(props)
        return False

    alignment = tool.Alignment.get_active_alignment()
    if not alignment:
        # Alignment no longer exists - clear everything
        props.pis.clear()
        props.active_pi_index = 0
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
    extracted_pis = tool.Alignment.extract_pis_from_segments(segments)

    if not extracted_pis:
        # Couldn't extract - keep current props.pis
        rebuild_display_rows(props)
        return True

    # Update props.pis with extracted data
    props.pis.clear()
    # pi.radius is a Blender LENGTH property (metres); the extracted radius is in
    # project units, so scale it so the table displays the correct value.
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    for pi_data in extracted_pis:
        pi = props.pis.add()
        pi.e = str(pi_data["e"])
        pi.n = str(pi_data["n"])
        pi.pi_type = pi_data["pi_type"]
        pi.radius = pi_data.get("radius", 0.0) * unit_scale

    props.active_pi_index = 0

    # Recalculate geometry and rebuild display
    recalculate_pi_geometry(props)
    return True


def on_radius_changed(pi, context):
    """Callback when PI radius is changed. Triggers geometry recalculation.

    This is called from the AlignmentPI.radius property's update callback.
    When a radius is entered on a Mid point, this triggers:
    1. Recalculation of PI geometry (lengths, stations)
    2. Rebuild of display_rows (Mid point becomes Curve segment)
    3. If an active alignment exists, regeneration of IFC entities
    """
    props = context.scene.CivilAlignmentProperties
    recalculate_pi_geometry(props)

    # If there's an active alignment, trigger IFC regeneration
    # This is handled by recalculate_pi_geometry when active_alignment_id is set


def recalculate_pi_geometry(props):
    """Recalculate lengths and stations for all PIs using tool layer."""
    pis = props.pis
    if len(pis) < 2:
        rebuild_display_rows(props)
        return

    # Extract PI coordinates for calculation
    pi_coords = [(float(pi.e), float(pi.n)) for pi in pis]

    # Use tool layer for calculation (math belongs in tool, not core)
    result = tool.Alignment.calculate_pi_geometry(pi_coords, props.start_station)

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

    # Pre-compute coordinate tuples for tool method calls
    pi_coords = [(float(pi.e), float(pi.n)) for pi in pis]

    while i < len(pis):
        pi = pis[i]
        is_interior = i > 0 and i < len(pis) - 1
        has_curve = is_interior and pi.radius > 0

        if has_curve:
            # Interior PI with curve: becomes a CURVE SEGMENT row
            segment_num += 1
            curve_row = props.display_rows.add()
            curve_row.row_type = "SEGMENT"
            curve_row.segment_number = segment_num
            curve_row.pi_index = i
            curve_row.display_type = "Curve"
            curve_row.e = pi.e
            curve_row.n = pi.n
            curve_row.radius = pi.radius
            curve_row.arc_length = tool.Alignment.arc_length_at_pi(
                pi_coords[i - 1], pi_coords[i], pi_coords[i + 1], pi.radius
            )
        else:
            # Regular point row (End or Mid without curve)
            point_row = props.display_rows.add()
            point_row.row_type = "POINT"
            point_row.pi_index = i

            if pi.pi_type == "ENDPOINT":
                point_row.display_type = "End"
            else:
                point_row.display_type = "Mid"

            point_row.e = pi.e
            point_row.n = pi.n

        # Add tangent segment row after this point/curve (except after last PI)
        if i < len(pis) - 1:
            segment_num += 1
            seg_row = props.display_rows.add()
            seg_row.row_type = "SEGMENT"
            seg_row.segment_number = segment_num
            seg_row.pi_index = i
            seg_row.display_type = "Tan"

            # Compute tangent lengths at each end to subtract from full distance
            start_t = 0.0
            end_t = 0.0
            if has_curve:
                start_t = tool.Alignment.tangent_length_at_pi(
                    pi_coords[i - 1], pi_coords[i], pi_coords[i + 1], pi.radius
                )
            next_pi = pis[i + 1]
            next_is_interior = (i + 1 > 0) and (i + 1 < len(pis) - 1)
            next_has_curve = next_is_interior and next_pi.radius > 0
            if next_has_curve:
                end_t = tool.Alignment.tangent_length_at_pi(
                    pi_coords[i], pi_coords[i + 1], pi_coords[i + 2], next_pi.radius
                )

            seg_row.length = tool.Alignment.tangent_segment_length(
                pi_coords[i], pi_coords[i + 1], start_t, end_t
            )

        i += 1


# =============================================================================
# PI Management Operators
# =============================================================================


class CIVIL_OT_add_pi(Operator):
    """Add a new PI point to the list"""

    bl_idname = "civil.add_pi"
    bl_label = "Add PI"
    bl_description = "Add a new PI (Point of Intersection) to the alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties

        # Add new PI
        pi = props.pis.add()

        # Set default position based on existing PIs
        if len(props.pis) == 1:
            # First PI - start at origin
            pi.e = str(0.0)
            pi.n = str(0.0)
            pi.pi_type = "ENDPOINT"
        elif len(props.pis) == 2:
            # Second PI - offset from first
            prev = props.pis[0]
            pi.e = str(float(prev.e) + 100.0)
            pi.n = prev.n
            pi.pi_type = "ENDPOINT"
        else:
            # Additional PIs - extrapolate from last two
            prev = props.pis[-2]
            prev_prev = props.pis[-3] if len(props.pis) > 2 else prev
            de = float(prev.e) - float(prev_prev.e) if len(props.pis) > 2 else 100.0
            dn = float(prev.n) - float(prev_prev.n) if len(props.pis) > 2 else 0.0
            pi.e = str(float(prev.e) + de)
            pi.n = str(float(prev.n) + dn)
            pi.pi_type = "TANGENT"

            # Previous endpoint becomes tangent or curve
            props.pis[-2].pi_type = "TANGENT"

        # Make new PI active
        props.active_pi_index = len(props.pis) - 1

        # Recalculate geometry
        recalculate_pi_geometry(props)

        return {"FINISHED"}


class CIVIL_OT_remove_pi(Operator):
    """Remove the selected PI point"""

    bl_idname = "civil.remove_pi"
    bl_label = "Remove PI"
    bl_description = "Remove the selected PI from the alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
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
        props = context.scene.CivilAlignmentProperties

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


class CIVIL_OT_pick_pi_from_viewport(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    """Add PI points by clicking in the 3D viewport using polyline tools"""

    bl_idname = "civil.pick_pi_from_viewport"
    bl_label = "Pick PI from Viewport"
    bl_description = "Click in the viewport to add PI points with snapping and numeric input. RMB/Enter to finish, ESC to cancel."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        # Remove instructions that don't apply to alignments
        self.instructions.pop("Close Polyline", None)
        self.instructions.pop("Offset", None)

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        # Find the 3D viewport — the operator is invoked from the Properties
        # panel, so we need to override context for PolylineOperator.invoke()
        # which requires bpy.context.space_data to be SpaceView3D.
        area_3d = None
        region_3d = None
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area_3d = area
                for region in area.regions:
                    if region.type == "WINDOW":
                        region_3d = region
                        break
                break

        if not area_3d or not region_3d:
            self.report({"ERROR"}, "No 3D Viewport found")
            return {"CANCELLED"}

        with context.temp_override(area=area_3d, region=region_3d):
            super().invoke(context, event)

        self.tool_state.use_default_container = False
        self.tool_state.plane_method = "XY"
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()

        self.handle_lock_axis(context, event)

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.handle_mouse_move(context, event)
            return {"PASS_THROUGH"}

        self.handle_instructions(context)
        self.handle_mouse_move(context, event, should_round=True)
        self.choose_axis(event)
        self.handle_snap_selection(context, event)
        self.handle_keyboard_input(context, event)
        self._handle_inserting_polyline_no_close(context, event)

        # Finish: transfer polyline points to PI table
        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self._transfer_polyline_to_pis(context)
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            tool.Polyline.clear_polyline()
            # Auto-visualize: build the IFC segments as soon as picking finishes,
            # so the user no longer needs a separate "Visualize" click.
            ok, message = _build_alignment_from_active_pis(context)
            if not ok:
                self.report({"WARNING"}, message)
            tool.Blender.update_viewport()
            return {"FINISHED"}

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            return cancel

        return {"RUNNING_MODAL"}

    def _handle_inserting_polyline_no_close(self, context, event):
        """Insert polyline points without close-polyline (C key) behavior.

        Alignments are open curves, so the C key (close polyline) is suppressed.
        All other insertion behavior is preserved: LEFTMOUSE, BACKSPACE, and
        RET/ENTER with numeric input active.
        """
        # LEFTMOUSE: insert point at current snap/cursor position
        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type == "LEFTMOUSE":
            result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
            if result:
                self.report({"WARNING"}, result)
            tool.Blender.update_viewport()

        # RET/ENTER with numeric input: validate and insert
        if (
            self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            is_valid = self.recalculate_inputs(context)
            if is_valid:
                result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                if result:
                    self.report({"WARNING"}, result)

            self.tool_state.mode = "Mouse"
            self.tool_state.is_input_on = False
            self.input_type = None
            self.tool_state.input_type = None
            self.number_input = []
            self.number_output = ""
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        # BACKSPACE: remove last point (when not typing numeric input)
        if not self.tool_state.is_input_on:
            if event.value == "RELEASE" and event.type == "BACK_SPACE":
                tool.Polyline.remove_last_polyline_point()
                tool.Blender.update_viewport()

    def _transfer_polyline_to_pis(self, context):
        """Transfer collected polyline points to the PI Editor table.

        Polyline points are in Blender coordinate space. This method converts
        each point to IFC coordinate space before storing in props.pis.
        """
        props = context.scene.CivilAlignmentProperties
        polyline_props = tool.Model.get_polyline_props()
        polyline_data = polyline_props.insertion_polyline
        if not polyline_data:
            return

        polyline_points = polyline_data[0].polyline_points
        if not polyline_points:
            return

        # Blender world space is metres (1 BU = 1 m); the georeference helpers
        # work in IFC project length units. Convert before storing so the
        # alignment is recreated at the correct scale (e.g. feet projects).
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        num_points = len(polyline_points)
        for i, point in enumerate(polyline_points):
            # Blender metres -> IFC project units -> global easting/northing (stored on props.pis).
            local = (point.x / unit_scale, point.y / unit_scale, 0.0)
            ifc_coord = tool.Georeference.xyz2enh(local)

            pi = props.pis.add()
            pi.e = str(ifc_coord[0])
            pi.n = str(ifc_coord[1])

            # Determine PI type based on position
            if i == 0 or i == num_points - 1:
                pi.pi_type = "ENDPOINT"
            else:
                pi.pi_type = "TANGENT"

        props.active_pi_index = len(props.pis) - 1
        recalculate_pi_geometry(props)
        rebuild_display_rows(props)


def _build_alignment_from_active_pis(context):
    """Build/refresh the IFC horizontal segments from props.pis on the active
    alignment and visualize them.

    Shared by the Recalculate/Visualize operator and the PI picker (so picking
    auto-visualizes on completion). Returns (ok: bool, message: str).
    """
    import ifcopenshell.api.alignment as align_api

    ifc = tool.Ifc.get()
    props = context.scene.CivilAlignmentProperties
    recalculate_pi_geometry(props)

    alignment = tool.Alignment.get_active_alignment()
    if not alignment:
        total_length = sum(pi.length_to_next for pi in props.pis)
        return (
            False,
            f"Select an IfcAlignment in the outliner first. "
            f"(Recalculated {len(props.pis)} PIs, total length: {total_length:.2f})",
        )
    if len(props.pis) < 2:
        return False, "Need at least 2 PIs to build the alignment"

    props.active_alignment_id = alignment.id()

    # Bootstrap horizontal layout if the alignment is bare (e.g. from Add Element)
    h_layout = align_api.get_horizontal_layout(alignment)
    if h_layout is None:
        h_layout = tool.Alignment.add_horizontal_layout_to_alignment(alignment)

    # Ensure Blender objects exist for the alignment hierarchy
    alignment_obj = tool.Ifc.get_object(alignment)
    if not alignment_obj:
        alignment_obj = tool.Alignment.create_hierarchy_for_alignment(alignment)

    # Stored PI E/N (IFC project units) -> local IFC coords for the API.
    hpoints = [
        [float(o) for o in ifcopenshell.util.geolocation.auto_enh2xyz(ifc, float(pi.e), float(pi.n), 0.0)[:2]]
        for pi in props.pis
    ]
    # pi.radius is a Blender LENGTH property (stored in metres); the API expects
    # project units, so convert back via unit_scale — same as the coordinates.
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
    radii = [pi.radius / unit_scale for pi in props.pis[1:-1]]

    tool.Alignment.remove_layout_segment_objects(h_layout)
    tool.Alignment.clear_layout_segments(h_layout)
    align_api.layout_horizontal_alignment_by_pi_method(ifc, h_layout, hpoints, radii)

    layout_obj = tool.Ifc.get_object(h_layout)
    if not layout_obj:
        layout_obj = tool.Alignment.create_object_for_layout(h_layout, alignment_obj)
    if layout_obj:
        tool.Alignment.create_objects_for_layout_segments(h_layout, layout_obj)

    tool.Blender.update_viewport()
    return True, f"Updated alignment '{alignment.Name}' with {len(hpoints)} PIs"


class CIVIL_OT_recalculate_pis(Operator, tool.Ifc.Operator):
    """Recalculate PI geometry and update IFC/visualization"""

    bl_idname = "civil.recalculate_pis"
    bl_label = "Recalculate PIs"
    bl_description = "Recalculate geometry, update IFC segments, and refresh visualization"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if len(props.pis) < 2:
            cls.poll_message_set("Need at least 2 PIs to recalculate")
            return False
        return True

    def _execute(self, context):
        ok, message = _build_alignment_from_active_pis(context)
        self.report({"INFO"} if ok else {"WARNING"}, message)


class CIVIL_OT_clear_pis(Operator, tool.Ifc.Operator):
    """Delete the active alignment and clear the PI table"""

    bl_idname = "civil.clear_pis"
    bl_label = "Clear All PIs"
    bl_description = (
        "Delete the entire active alignment — its IFC entity, all nested "
        "layouts and segments, and its viewport objects — and clear the PI table"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if len(props.pis) == 0:
            cls.poll_message_set("No PIs to clear")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties

        removed_objects = 0

        # Delete the active alignment entirely (Blender + IFC) so the file is
        # never left with an orphaned, PI-less alignment. Resolved through
        # props.active_alignment_id — the same reference every other panel
        # operator uses — not the viewport's active object.
        if alignment := _resolve_active_alignment(context):
            removed_objects = tool.Alignment.remove_alignment_hierarchy(alignment)
            ifcopenshell.api.run("root.remove_product", ifc, product=alignment)
            props.active_alignment_id = 0
            props.active_alignment_name = ""

        # Clear the PI list in the UI
        props.pis.clear()
        props.active_pi_index = 0

        # Clear the display rows
        props.display_rows.clear()
        props.active_display_row_index = 0

        if removed_objects > 0:
            self.report({"INFO"}, f"Deleted alignment and removed {removed_objects} objects")
        else:
            self.report({"INFO"}, "Cleared all PIs")


# =============================================================================
# Creation Operators
# =============================================================================


class CIVIL_OT_create_alignment_by_pis(Operator, tool.Ifc.Operator):
    """Create a new alignment and immediately start picking PI points"""

    bl_idname = "civil.create_alignment_by_pis"
    bl_label = "New Alignment (PI Method)"
    bl_description = "Create a new alignment and pick PI points from the viewport"
    bl_options = {"REGISTER", "UNDO"}

    alignment_name: StringProperty(name="Name", default="Alignment")

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        props = context.scene.CivilAlignmentProperties

        # Create full alignment via core → tool → API
        try:
            alignment = core.create_alignment(
                tool.Ifc, tool.Alignment, self.alignment_name
            )
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        props.active_alignment_id = alignment.id()
        props.active_alignment_name = alignment.Name or self.alignment_name

        # Clear any existing PIs from previous work
        props.pis.clear()
        props.active_pi_index = 0
        props.display_rows.clear()
        props.active_display_row_index = 0

        self.report({"INFO"}, f"Created alignment '{alignment.Name}' — pick PI points now")

        # Chain into PI picker (runs as separate modal with its own undo)
        bpy.ops.civil.pick_pi_from_viewport("INVOKE_DEFAULT")

        return {"FINISHED"}


class CIVIL_OT_create_alignment_by_pi(Operator, tool.Ifc.Operator):
    """Create alignment using the PI (Point of Intersection) method"""

    bl_idname = "civil.create_alignment_by_pi"
    bl_label = "Create by PI Method"
    bl_description = "Create alignment using PI points and curve radii. If an active alignment exists with no segments, adds to it instead of creating new."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if len(props.pis) < 2:
            cls.poll_message_set("Need at least 2 PI points")
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select an alignment to edit")
            return False
        return True

    def _execute(self, context):
        props = context.scene.CivilAlignmentProperties

        # Convert global E/N coords (stored in props.pis) -> local IFC coords for the IfcOpenShell API
        hpoints = [
            [
                float(o)
                for o in ifcopenshell.util.geolocation.auto_enh2xyz(tool.Ifc.get(), float(pi.e), float(pi.n), 0.0)[:2]
            ]
            for pi in props.pis
        ]
        radii = [pi.radius for pi in props.pis[1:-1]]

        existing_alignment = tool.Alignment.get_active_alignment()
        if not (h_layout := ifcopenshell.api.alignment.get_horizontal_layout(existing_alignment)):
            return
        # Check if horizontal layout is empty (only has zero-length terminal or no segments)
        segments = ifcopenshell.api.alignment.get_layout_segments(h_layout)
        has_real_segments = bool([s for s in segments if not tool.Alignment.is_zero_length_segment(s)])

        ifcopenshell.api.alignment.create_representation(tool.Ifc.get(), existing_alignment)

        if not has_real_segments:
            # Use existing alignment - add segments to it
            # Use safe wrapper to validate layout has parent alignment
            tool.Alignment.safe_layout_horizontal_by_pi_method(tool.Ifc.get(), h_layout, hpoints, radii)

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


# CSV import lives on the single upstream operator id `bim.import_alignment_csv`
# (class ImportAlignmentCSV above) — it now routes through
# core.import_alignment_csv, which builds the Saikei viewport hierarchy for the
# parent and any aggregated child alignments.


# =============================================================================
# Stationing Operators
# =============================================================================


class CIVIL_OT_add_stationing_referent(Operator, tool.Ifc.Operator):
    """Add a stationing referent to the alignment"""

    bl_idname = "civil.add_stationing_referent"
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
        props = context.scene.CivilAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        # Default station to start_station from props
        props = context.scene.CivilAlignmentProperties
        self.station = props.start_station
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "station")
        layout.prop(self, "name")
        # Show station notation preview
        station_str = tool.Alignment.format_station(self.station)
        layout.label(text=f"Station notation: {station_str}")

    def _execute(self, context):
        ifc = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties

        alignment = _resolve_active_alignment(context)
        if alignment is None:
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        # Compute distance_along from station and start_station
        # distance_along = station - start_station
        distance_along = self.station - props.start_station

        # Auto-generate name if not provided
        name = self.name if self.name else tool.Alignment.format_station(self.station)

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


class CIVIL_OT_name_segments(Operator, tool.Ifc.Operator):
    """Auto-name segments based on station values"""

    bl_idname = "civil.name_segments"
    bl_label = "Name Segments"
    bl_description = "Automatically name segments with station-based labels"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if props.active_alignment_id == 0:
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def _execute(self, context):
        ifc = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties

        alignment = _resolve_active_alignment(context)
        if alignment is None:
            self.report({"ERROR"}, "Alignment no longer exists. Reference cleared.")
            return {"CANCELLED"}

        ifcopenshell.api.alignment.name_segments(ifc, alignment)

        self.report({"INFO"}, "Named alignment segments")


# =============================================================================
# PI Edit Mode Operator
# =============================================================================


class CIVIL_OT_enter_pi_edit_mode(Operator, tool.Ifc.Operator):
    """Enter PI editing mode - move PIs with G key, press Enter to apply or Escape to cancel"""

    bl_idname = "civil.enter_pi_edit_mode"
    bl_label = "Edit PIs"
    bl_description = "Enter PI edit mode. Move PI points with G key. Press Enter to apply changes, Escape to cancel."
    bl_options = {"REGISTER", "UNDO"}

    # Instance state for modal operation
    _pi_empties: list = []
    _last_positions: list = []
    _area = None
    _alignment_id: int = 0

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if props.is_pi_edit_mode:
            cls.poll_message_set("Already in PI edit mode")
            return False
        if props.active_alignment_id == 0:
            cls.poll_message_set("No alignment selected")
            return False
        # Verify alignment still exists
        alignment = _resolve_active_alignment(context)
        if alignment is None:
            cls.poll_message_set("Selected alignment no longer exists")
            return False
        return True

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        props = context.scene.CivilAlignmentProperties
        self._alignment_id = props.active_alignment_id

        # Enter edit mode via core layer (validates and creates empties)
        try:
            empties = core.enter_pi_edit_mode(
                tool.Ifc, tool.Alignment, self._alignment_id
            )
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        if not empties:
            self.report({"ERROR"}, "Failed to create PI empties")
            return {"CANCELLED"}

        # Cache references to empties and their positions
        self._pi_empties = empties
        self._last_positions = [e.location.copy() for e in empties]

        # Find viewport for redraws
        self._area = None
        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                self._area = area
                break

        # Install visual feedback decorator
        alignment_decorator.PIEditDecorator.install(context, empties)

        # Make the segment curves non-selectable so viewport clicks land on the
        # PI empties, and deselect everything so the user starts clean.
        alignment = tool.Ifc.get().by_id(self._alignment_id)
        h_layout = tool.Alignment.get_horizontal_layout(alignment)
        tool.Alignment.set_layout_segments_selectable(h_layout, False)
        for obj in list(context.selected_objects):
            obj.select_set(False)

        # Update UI state
        props.is_pi_edit_mode = True
        props.pi_edit_alignment_id = self._alignment_id

        # Start modal loop
        context.window_manager.modal_handler_add(self)
        self.report({"INFO"}, "PI Edit Mode: Move PIs with G. Press Enter to apply, Escape to cancel.")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        props = context.scene.CivilAlignmentProperties

        # Safety: check if empties still exist (handles undo edge case)
        if not self._empties_still_exist():
            self.report({"WARNING"}, "PI Edit Mode cancelled - empties were removed")
            return self._cleanup_and_finish(context, apply=False)

        # Detect position changes and update decorator
        positions_changed = False
        for i, empty in enumerate(self._pi_empties):
            if empty.location != self._last_positions[i]:
                positions_changed = True
                self._last_positions[i] = empty.location.copy()

        if positions_changed:
            # Update decorator to show new tangent lines
            alignment_decorator.PIEditDecorator.update_positions(self._pi_empties)
            if self._area:
                self._area.tag_redraw()

        # Handle keyboard input
        if event.type in {"RET", "NUMPAD_ENTER"} and event.value == "PRESS":
            return self._cleanup_and_finish(context, apply=True)

        if event.type == "ESC" and event.value == "PRESS":
            return self._cleanup_and_finish(context, apply=False)

        # Let all other events pass through (G key, mouse, viewport navigation, etc.)
        return {"PASS_THROUGH"}

    def _empties_still_exist(self) -> bool:
        """Check if all PI empties still exist in the scene."""
        for empty in self._pi_empties:
            if empty is None:
                return False
            if empty.name not in bpy.data.objects:
                return False
        return True

    def _cleanup_and_finish(self, context, apply: bool):
        """Exit edit mode, optionally applying changes."""
        props = context.scene.CivilAlignmentProperties

        try:
            if apply:
                # Regenerate alignment from new PI positions
                core.exit_pi_edit_mode(
                    tool.Ifc, tool.Alignment, self._alignment_id, apply=True
                )
                self.report({"INFO"}, "PI changes applied - alignment updated")
            else:
                # Just cleanup without regenerating
                core.exit_pi_edit_mode(
                    tool.Ifc, tool.Alignment, self._alignment_id, apply=False
                )
                self.report({"INFO"}, "PI Edit Mode cancelled")
        except ValueError as e:
            self.report({"ERROR"}, str(e))

        # Cleanup decorator
        alignment_decorator.PIEditDecorator.uninstall()

        # Restore segment selectability (on apply the segments are rebuilt and
        # already selectable; on cancel this re-enables the originals).
        try:
            alignment = tool.Ifc.get().by_id(self._alignment_id)
            h_layout = tool.Alignment.get_horizontal_layout(alignment)
            tool.Alignment.set_layout_segments_selectable(h_layout, True)
        except (RuntimeError, AttributeError):
            pass

        # Reset UI state
        props.is_pi_edit_mode = False
        props.pi_edit_alignment_id = 0

        # Clear instance state
        self._pi_empties = []
        self._last_positions = []

        if self._area:
            self._area.tag_redraw()

        if apply:
            return {"FINISHED"}
        return {"CANCELLED"}
