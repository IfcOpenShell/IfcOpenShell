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
import blf
import time
import bonsai.core.alignment as core
import bonsai.tool as tool
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator, SpaceView3D
from bpy.props import StringProperty, FloatProperty, EnumProperty, IntProperty, BoolProperty
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


class ALIGN_OT_add_pi(Operator):
    """Add a new PI point to the list"""

    bl_idname = "align.add_pi"
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


class ALIGN_OT_remove_pi(Operator):
    """Remove the selected PI point"""

    bl_idname = "align.remove_pi"
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


def _insert_polyline_point_no_close(op, context, event):
    """Insert polyline points without close-polyline (C key) behavior.

    Alignments are open curves, so the C key (close polyline) is suppressed.
    All other insertion behavior is preserved: LEFTMOUSE, BACKSPACE, and
    RET/ENTER with numeric input active.

    Shared by every PolylineOperator-based alignment picker/drawer — ``op`` is
    the calling operator instance (must provide the PolylineOperator mixin's
    ``tool_state``/``input_ui``/``snapping_points``/``recalculate_inputs``).
    """
    # LEFTMOUSE: insert point at current snap/cursor position
    if not op.tool_state.is_input_on and event.value == "RELEASE" and event.type == "LEFTMOUSE":
        result = tool.Polyline.insert_polyline_point(op.input_ui, op.tool_state)
        if result:
            op.report({"WARNING"}, result)
        tool.Blender.update_viewport()

    # RET/ENTER with numeric input: validate and insert
    if (
        op.tool_state.is_input_on
        and event.value == "RELEASE"
        and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
    ):
        is_valid = op.recalculate_inputs(context)
        if is_valid:
            result = tool.Polyline.insert_polyline_point(op.input_ui, op.tool_state)
            if result:
                op.report({"WARNING"}, result)

        op.tool_state.mode = "Mouse"
        op.tool_state.is_input_on = False
        op.input_type = None
        op.tool_state.input_type = None
        op.number_input = []
        op.number_output = ""
        PolylineDecorator.update(event, op.tool_state, op.input_ui, op.snapping_points[0])
        tool.Blender.update_viewport()

    # BACKSPACE: remove last point (when not typing numeric input)
    if not op.tool_state.is_input_on:
        if event.value == "RELEASE" and event.type == "BACK_SPACE":
            tool.Polyline.remove_last_polyline_point()
            tool.Blender.update_viewport()


def _bearing_string(azimuth_from_east_ccw_deg: float) -> str:
    """Convert a math-convention azimuth to a civil-engineering quadrant bearing.

    ``azimuth_from_east_ccw_deg`` is the signed angle in degrees, measured
    counter-clockwise from world +X (East) — exactly what
    ``Polyline.PolylineUI``'s ``WORLD_ANGLE`` value holds while drawing.

    Returns a quadrant bearing string such as ``"N 30°15'24.00\" E"``, or
    ``"Due <N/S/E/W>"`` at the cardinal directions.
    """
    # Azimuth measured from North, clockwise, normalized to [0, 360).
    azimuth = (90.0 - azimuth_from_east_ccw_deg) % 360.0

    if azimuth <= 90.0:
        ns, angle, ew = "N", azimuth, "E"
    elif azimuth <= 180.0:
        ns, angle, ew = "S", 180.0 - azimuth, "E"
    elif azimuth <= 270.0:
        ns, angle, ew = "S", azimuth - 180.0, "W"
    else:
        ns, angle, ew = "N", 360.0 - azimuth, "W"

    if angle < 1e-6:
        return f"Due {ns}"
    if abs(angle - 90.0) < 1e-6:
        return f"Due {ew}"

    d = int(angle)
    m_full = (angle - d) * 60.0
    m = int(m_full)
    s = (m_full - m) * 60.0
    if round(s, 2) >= 60.0:
        s = 0.0
        m += 1
    if m >= 60:
        m = 0
        d += 1

    return f"{ns} {d}°{m:02d}'{s:05.2f}\" {ew}"


class ALIGN_OT_pick_pi_from_viewport(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    """Add PI points by clicking in the 3D viewport using polyline tools"""

    bl_idname = "align.pick_pi_from_viewport"
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
        _insert_polyline_point_no_close(self, context, event)

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

    # Make the alignment the active/selected object so it's immediately
    # visible in the outliner/properties pane without a manual click.
    if alignment_obj:
        for obj in context.selected_objects:
            obj.select_set(False)
        alignment_obj.select_set(True)
        context.view_layer.objects.active = alignment_obj

    tool.Blender.update_viewport()
    return True, f"Updated alignment '{alignment.Name}' with {len(hpoints)} PIs"


class ALIGN_OT_recalculate_pis(Operator, tool.Ifc.Operator):
    """Recalculate PI geometry and update IFC/visualization"""

    bl_idname = "align.recalculate_pis"
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


class ALIGN_OT_clear_pis(Operator, tool.Ifc.Operator):
    """Delete the active alignment and clear the PI table"""

    bl_idname = "align.clear_pis"
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


class ALIGN_OT_create_alignment_by_pis(Operator, tool.Ifc.Operator):
    """Create a new alignment and immediately start picking PI points"""

    bl_idname = "align.create_alignment_by_pis"
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
        bpy.ops.align.pick_pi_from_viewport("INVOKE_DEFAULT")

        return {"FINISHED"}


class ALIGN_OT_create_alignment_by_pi(Operator, tool.Ifc.Operator):
    """Create alignment using the PI (Point of Intersection) method"""

    bl_idname = "align.create_alignment_by_pi"
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
# Alignments tab — new authoring workflow (Add Element + interactive drawing).
#
# This is a from-scratch replacement for the CIVIL tab's PI-table workflow
# above: no persistent PI table, no CivilAlignmentProperties dependency. An
# alignment is added as a bare IfcAlignment, then its horizontal geometry is
# drawn directly in the viewport and committed to IFC on completion.
# =============================================================================


class ALIGN_OT_add_alignment(Operator, tool.Ifc.Operator):
    """Add a new, empty IfcAlignment to the project"""

    bl_idname = "align.add_alignment"
    bl_label = "Add Alignment"
    bl_description = "Add a new alignment to the project. Draw its horizontal geometry next."
    bl_options = {"REGISTER", "UNDO"}

    alignment_name: StringProperty(name="Name", default="Alignment")
    start_station: FloatProperty(
        name="Start Station",
        description="Station value at the start of the alignment (distance along 0)",
        default=0.0,
    )

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        try:
            alignment = core.create_alignment(tool.Ifc, tool.Alignment, self.alignment_name, self.start_station)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        # A viewport object for the start-station referent create_alignment()
        # added — matches what loading a file gives you; interactive creation
        # used to leave the referent with no object at all.
        start_referent = tool.Alignment.find_stationing_referent_at(alignment, 0.0)
        if start_referent:
            tool.Alignment.create_object_for_referent(start_referent)

        # Make the new alignment the active/selected object so it is
        # immediately picked up by tool.Alignment.get_active_alignment() —
        # no separate outliner click needed before drawing its geometry.
        alignment_obj = tool.Ifc.get_object(alignment)
        if alignment_obj:
            for obj in context.selected_objects:
                obj.select_set(False)
            alignment_obj.select_set(True)
            context.view_layer.objects.active = alignment_obj

        self.report({"INFO"}, f"Added alignment '{alignment.Name}' — draw its horizontal alignment next")
        return {"FINISHED"}


class ALIGN_OT_remove_alignment(Operator, tool.Ifc.Operator):
    """Delete the active alignment — its IFC entity, nested layouts/segments, and viewport objects"""

    bl_idname = "align.remove_alignment"
    bl_label = "Delete Alignment"
    bl_description = (
        "Delete the active alignment: its IFC entity, all nested layouts and "
        "segments, and its viewport objects. Cannot be undone via Blender's undo."
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            return {"CANCELLED"}

        name = alignment.Name or "Alignment"
        for marker in _find_pi_markers(alignment.id()):
            bpy.data.objects.remove(marker, do_unlink=True)
        removed_objects = tool.Alignment.remove_alignment_hierarchy(alignment)
        ifcopenshell.api.run("root.remove_product", ifc, product=alignment)

        self.report({"INFO"}, f"Deleted alignment '{name}' and removed {removed_objects} objects")
        return {"FINISHED"}


class ALIGN_OT_set_start_station(Operator, tool.Ifc.Operator):
    """Change the active alignment's start station (distance along 0)"""

    bl_idname = "align.set_start_station"
    bl_label = "Set Start Station"
    bl_description = "Change the alignment's start station"
    bl_options = {"REGISTER", "UNDO"}

    station: FloatProperty(name="Start Station", default=0.0)

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        alignment = tool.Alignment.get_active_alignment()
        self.station = ifcopenshell.api.alignment.get_alignment_start_station(tool.Ifc.get(), alignment) or 0.0
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        start_referent = tool.Alignment.find_stationing_referent_at(alignment, 0.0)
        if start_referent is None:
            # No stationing at all yet (e.g. an alignment from before this
            # feature existed) -- add the start referent rather than error.
            start_referent = ifcopenshell.api.alignment.add_stationing_referent(
                tool.Ifc.get(), tool.Alignment.format_station(self.station), alignment, 0.0, self.station
            )
        else:
            tool.Alignment.set_stationing_referent_station(start_referent, self.station)
        tool.Alignment.create_object_for_referent(start_referent)
        alignment_decorator.AlignmentSegmentDecorator.refresh()
        self.report({"INFO"}, f"Start station set to {tool.Alignment.format_station(self.station)}")
        return {"FINISHED"}


def _on_station_equation_station_update(self, context):
    """Keep Incoming Station following Outgoing Station until the user
    diverges it manually — that's what makes it "optional": leave it alone
    and there's no gap/overlap, type a different value and there is. No
    separate checkbox needed.
    """
    if self.incoming_station == self.station_snapshot:
        self.incoming_station = self.station
    self.station_snapshot = self.station


class _StationEquationFields:
    """Shared distance-along/station/incoming-station/direction fields for
    ALIGN_OT_add_station_equation and ALIGN_OT_edit_station_equation.
    """

    distance_along: FloatProperty(
        name="Distance Along", description="Distance along the alignment where the equation applies", default=0.0
    )
    station: FloatProperty(
        name="Outgoing Station",
        description="The station value immediately after this point",
        default=0.0,
        update=_on_station_equation_station_update,
    )
    incoming_station: FloatProperty(
        name="Incoming Station",
        description="The station value immediately before this point. Leave equal to Outgoing "
        "Station (the default) for no gap/overlap",
        default=0.0,
    )
    reverse_direction: BoolProperty(
        name="Reverse Stationing Direction",
        description="Stations decrease with distance along from this point on, instead of increasing",
        default=False,
    )
    # Bookkeeping only, for _on_station_equation_station_update — not shown, not saved.
    station_snapshot: FloatProperty(options={"HIDDEN", "SKIP_SAVE"}, default=0.0)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "distance_along")
        layout.prop(self, "incoming_station")
        layout.prop(self, "station")
        layout.prop(self, "reverse_direction")

    @property
    def _has_gap_or_overlap(self) -> bool:
        return self.incoming_station != self.station


class ALIGN_OT_add_station_equation(Operator, tool.Ifc.Operator, _StationEquationFields):
    """Add a station equation (an additional stationing referent) to the active alignment"""

    bl_idname = "align.add_station_equation"
    bl_label = "Add Station Equation"
    bl_description = (
        "Add a station equation at a distance along the alignment — a gap or "
        "overlap in the station numbering, or a switch to decreasing stations"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select an alignment first")
            return False
        return True

    def invoke(self, context, event):
        self.incoming_station = self.station
        self.station_snapshot = self.station
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        name = tool.Alignment.format_station(self.station)
        referent = ifcopenshell.api.alignment.add_stationing_referent(
            tool.Ifc.get(),
            name,
            alignment,
            self.distance_along,
            self.station,
            incoming_station=self.incoming_station if self._has_gap_or_overlap else None,
            has_increasing_station=False if self.reverse_direction else None,
        )
        tool.Alignment.create_object_for_referent(referent)
        alignment_decorator.AlignmentSegmentDecorator.refresh()
        self.report({"INFO"}, f"Added station equation '{name}' at distance {self.distance_along}")
        return {"FINISHED"}


class ALIGN_OT_edit_station_equation(Operator, tool.Ifc.Operator, _StationEquationFields):
    """Edit an existing station equation's distance along, station, and gap/overlap.

    A referent's distance along is baked into its placement, which
    add_stationing_referent alone can't move — so this removes and re-adds
    the referent with the new values rather than mutating it in place. The
    IFC id changes; the panel resolves the row it's editing by re-reading
    the alignment's stationing nest on redraw, not by holding onto the id.
    """

    bl_idname = "align.edit_station_equation"
    bl_label = "Edit Station Equation"
    bl_options = {"REGISTER", "UNDO"}

    referent_id: IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        import ifcopenshell.util.element
        from ifcopenshell.api.alignment._referent_distance_along import _referent_distance_along

        try:
            referent = tool.Ifc.get().by_id(self.referent_id)
        except RuntimeError:
            self.report({"ERROR"}, "Referent no longer exists")
            return {"CANCELLED"}

        self.distance_along = _referent_distance_along(referent)
        self.station = ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station") or 0.0
        incoming = ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="IncomingStation")
        self.incoming_station = incoming if incoming is not None else self.station
        self.reverse_direction = (
            ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="HasIncreasingStation") is False
        )
        self.station_snapshot = self.station
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        try:
            referent = ifc.by_id(self.referent_id)
        except RuntimeError:
            self.report({"ERROR"}, "Referent no longer exists")
            return {"CANCELLED"}

        alignment = None
        for rel in getattr(referent, "Nests", []) or []:
            if rel.RelatingObject.is_a("IfcAlignment"):
                alignment = rel.RelatingObject
                break
        if alignment is None:
            self.report({"ERROR"}, "Could not find the referent's alignment")
            return {"CANCELLED"}

        if obj := tool.Ifc.get_object(referent):
            bpy.data.objects.remove(obj, do_unlink=True)
        ifcopenshell.api.run("root.remove_product", ifc, product=referent)

        name = tool.Alignment.format_station(self.station)
        new_referent = ifcopenshell.api.alignment.add_stationing_referent(
            ifc,
            name,
            alignment,
            self.distance_along,
            self.station,
            incoming_station=self.incoming_station if self._has_gap_or_overlap else None,
            has_increasing_station=False if self.reverse_direction else None,
        )
        tool.Alignment.create_object_for_referent(new_referent)
        alignment_decorator.AlignmentSegmentDecorator.refresh()
        self.report({"INFO"}, f"Updated station equation to '{name}'")
        return {"FINISHED"}


class ALIGN_OT_remove_station_equation(Operator, tool.Ifc.Operator):
    """Remove one stationing referent (station equation) from the active alignment"""

    bl_idname = "align.remove_station_equation"
    bl_label = "Remove Station Equation"
    bl_description = "Remove this stationing referent"
    bl_options = {"REGISTER", "UNDO"}

    referent_id: IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        try:
            referent = ifc.by_id(self.referent_id)
        except RuntimeError:
            return {"CANCELLED"}
        if not referent.is_a("IfcReferent"):
            return {"CANCELLED"}

        name = referent.Name or "referent"
        if obj := tool.Ifc.get_object(referent):
            bpy.data.objects.remove(obj, do_unlink=True)
        ifcopenshell.api.run("root.remove_product", ifc, product=referent)

        alignment_decorator.AlignmentSegmentDecorator.refresh()
        self.report({"INFO"}, f"Removed station equation '{name}'")
        return {"FINISHED"}


def _world_point_to_local_ifc(ifc, unit_scale, point_xyz):
    """Convert one Blender-world (metres) point to local IFC coordinates.

    Blender world -> IFC project units -> global E/N -> local IFC coords, the
    same round trip _transfer_polyline_to_pis() uses, so georeferenced
    projects (true-north rotation, false origin) place the alignment
    correctly.
    """
    local = (point_xyz[0] / unit_scale, point_xyz[1] / unit_scale, 0.0)
    e, n = tool.Georeference.xyz2enh(local)[:2]
    return [float(o) for o in ifcopenshell.util.geolocation.auto_enh2xyz(ifc, e, n, 0.0)[:2]]


def _hpoints_from_polyline(context):
    """Read the drawn polyline and convert it to local IFC coords.

    Returns (True, (raw_points, hpoints)) on success, (False, message)
    otherwise. ``raw_points`` are the original (x, y, z) points in Blender
    world space (metres) — kept around so a caller can place viewport marker
    objects at the exact drawn positions without inverting the coordinate
    conversion below. ``hpoints`` are [x, y] pairs in local IFC coordinates,
    including the start and end points — exactly what
    layout_horizontal_alignment_by_pi_method expects.
    """
    ifc = tool.Ifc.get()
    polyline_props = tool.Model.get_polyline_props()
    polyline_data = polyline_props.insertion_polyline
    if not polyline_data or not polyline_data[0].polyline_points:
        return False, "No points were drawn"

    polyline_points = polyline_data[0].polyline_points
    if len(polyline_points) < 2:
        return False, "Need at least 2 points to draw an alignment"

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
    raw_points = [(p.x, p.y, p.z) for p in polyline_points]
    hpoints = [_world_point_to_local_ifc(ifc, unit_scale, p) for p in raw_points]
    return True, (raw_points, hpoints)


def _generate_alignment_segments(context, alignment, hpoints, radii):
    """Build horizontal alignment segments from PI points and per-PI radii.

    Mirrors _build_alignment_from_active_pis()'s IFC-side logic. ``hpoints``
    are local IFC coords (see _hpoints_from_polyline); ``radii`` has exactly
    len(hpoints) - 2 entries, one per interior PI (0.0 = sharp, no curve).

    ``alignment`` is passed explicitly rather than resolved from the active
    object — a PI marker empty (see _create_pi_markers) is typically the
    active object when this runs from ALIGN_OT_apply_pi_curve, and markers
    aren't IFC-linked, so tool.Alignment.get_active_alignment() can't find
    the alignment from them.

    Uses layout_horizontal_alignment_by_pi_method for now (circular curves
    only). Once spiral segments are needed this has to become genuinely
    one-segment-at-a-time authoring via create_layout_segment(), since that
    API only ever emits LINE/CIRCULARARC — see REQUIREMENTS.md §2 step 7.
    """
    ifc = tool.Ifc.get()

    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    if h_layout is None:
        h_layout = tool.Alignment.add_horizontal_layout_to_alignment(alignment)

    if not tool.Ifc.get_object(alignment):
        tool.Alignment.create_object_for_alignment(alignment)

    # Drop any layout/segment objects a previous draw on this alignment left
    # behind (e.g. from before this single-mesh approach existed) so the
    # scene collection converges on exactly one object for the alignment —
    # what loading it from a file would give you — rather than accumulating
    # the CIVIL tab's per-layout/per-segment objects alongside it.
    tool.Alignment.remove_layout_and_child_layout_objects(alignment)

    tool.Alignment.clear_layout_segments(h_layout)
    tool.Alignment.safe_layout_horizontal_by_pi_method(ifc, h_layout, hpoints, radii)
    ifcopenshell.api.alignment.create_representation(ifc, alignment)

    tool.Alignment.refresh_alignment_representation_object(alignment)

    n_curved = sum(1 for r in radii if r)
    return True, f"Drew alignment '{alignment.Name}' with {len(hpoints)} PIs ({n_curved} curved)"


def _create_pi_markers(context, alignment_id, raw_points):
    """Place a marker empty at every interior PI (Blender-world position, metres).

    Start and end never get a curve, so — unlike an earlier version of this
    feature — they get no marker: nothing to select, nothing to click.
    Their positions aren't needed from a marker either;
    tool.Alignment.get_alignment_start_end_points() reads them straight off
    the alignment's own current segments instead.

    ``pi_index`` keeps counting from the full point list (1-based among
    interior PIs, i.e. never 0 or the last index) purely for the "PI n"
    label; ALIGN_OT_apply_pi_curve interleaves markers with the derived
    start/end using their sort order, not that number.

    Tagged via Object.bonsai_pi_curve_marker so ALIGN_OT_apply_pi_curve /
    ALIGN_OT_clear_pi_markers can find them without any operator-instance
    state (the drawing operator that created them has already finished by
    the time a curve is applied).
    """
    n = len(raw_points)
    markers = []
    for i, (x, y, z) in enumerate(raw_points):
        if i == 0 or i == n - 1:
            continue
        empty = bpy.data.objects.new(f"PI {i} (tangent)", None)
        empty.empty_display_type = "SPHERE"
        empty.empty_display_size = 2.0
        empty.location = (x, y, z)
        marker = empty.bonsai_pi_curve_marker
        marker.is_pi_marker = True
        marker.alignment_id = alignment_id
        marker.pi_index = i
        marker.curve_type = "TANGENT"
        context.collection.objects.link(empty)
        markers.append(empty)
    return markers


def _find_pi_markers(alignment_id):
    """All PI marker empties for one alignment, sorted by PI index."""
    markers = [
        obj
        for obj in bpy.data.objects
        if obj.bonsai_pi_curve_marker.is_pi_marker and obj.bonsai_pi_curve_marker.alignment_id == alignment_id
    ]
    markers.sort(key=lambda o: o.bonsai_pi_curve_marker.pi_index)
    return markers


def _active_pi_marker(context):
    obj = context.active_object
    if obj is not None and obj.bonsai_pi_curve_marker.is_pi_marker:
        return obj
    return None


def _is_interior_pi_marker(obj) -> bool:
    """Whether ``obj`` is one of our PI markers — _create_pi_markers() never
    makes one for Start/End (they can't have a curve), so is_pi_marker being
    set is enough now; kept as its own function since callers read it as an
    "is this an editable PI" check.
    """
    return obj.bonsai_pi_curve_marker.is_pi_marker


class ALIGN_OT_apply_pi_curve(Operator, tool.Ifc.Operator):
    """Regenerate the alignment using the active PI marker's curve settings.

    A plain button click — a top-level operator invocation, not one nested
    inside another operator's still-running modal() — which is what the
    curve-editing popup used to be. That nesting is what silently broke the
    alignment regeneration: Blender operators must not invoke another
    operator's dialog from inside a live modal() callback (the rest of this
    module's modal tools — and Bonsai's own gizmo/product-placement modals —
    only ever do that from invoke()/exit(), never mid-modal).
    """

    bl_idname = "align.apply_pi_curve"
    bl_label = "Apply Curve"
    bl_description = "Regenerate the alignment using this PI's curve type/radius"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        marker = _active_pi_marker(context)
        if not marker or not _is_interior_pi_marker(marker):
            cls.poll_message_set("Select an interior PI marker first")
            return False
        return True

    def _execute(self, context):
        marker_obj = _active_pi_marker(context)
        alignment_id = marker_obj.bonsai_pi_curve_marker.alignment_id
        alignment = tool.Ifc.get().by_id(alignment_id)

        try:
            start, end = tool.Alignment.get_alignment_start_end_points(alignment)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        ifc = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
        interior_markers = _find_pi_markers(alignment_id)
        hpoints = (
            [start]
            + [_world_point_to_local_ifc(ifc, unit_scale, m.location) for m in interior_markers]
            + [end]
        )
        radii = [
            (m.bonsai_pi_curve_marker.radius if m.bonsai_pi_curve_marker.curve_type == "CIRCULAR" else 0.0)
            for m in interior_markers
        ]

        ok, message = _generate_alignment_segments(context, alignment, hpoints, radii)

        marker = marker_obj.bonsai_pi_curve_marker
        marker_obj.name = (
            f"PI {marker.pi_index} (R={marker.radius:.2f})"
            if marker.curve_type == "CIRCULAR"
            else f"PI {marker.pi_index} (tangent)"
        )
        # _generate_alignment_segments() replaces every IfcAlignmentSegment
        # with a new one, so a previously-highlighted segment's id is gone —
        # refreshing it would silently keep showing the old, now-stale
        # highlight at its old position. Uninstalling is the correct call
        # here, same idea as the stationing operators' refresh() below.
        alignment_decorator.AlignmentSegmentDecorator.uninstall()
        tool.Blender.update_viewport()
        self.report({"INFO"} if ok else {"WARNING"}, message)
        return {"FINISHED"}


class ALIGN_OT_clear_pi_markers(Operator, tool.Ifc.Operator):
    """Remove the PI marker empties left over from drawing/curve-editing"""

    bl_idname = "align.clear_pi_markers"
    bl_label = "Clear PI Markers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not _resolve_alignment_id_for_markers(context):
            cls.poll_message_set("Select an alignment or one of its PI markers")
            return False
        return True

    def _execute(self, context):
        alignment_id = _resolve_alignment_id_for_markers(context)
        markers = _find_pi_markers(alignment_id)
        for m in markers:
            bpy.data.objects.remove(m, do_unlink=True)
        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Removed {len(markers)} PI markers")


def _resolve_alignment_id_for_markers(context):
    """The alignment id whose PI markers apply_pi_curve/clear_pi_markers act on.

    Works whether the active object is the alignment itself or one of its
    own (non-IFC-linked) PI markers.
    """
    marker = _active_pi_marker(context)
    if marker:
        return marker.bonsai_pi_curve_marker.alignment_id
    alignment = tool.Alignment.get_active_alignment()
    return alignment.id() if alignment else 0


class ALIGN_OT_draw_horizontal_alignment(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    """Draw the horizontal alignment of the active IfcAlignment directly in the viewport.

    Click to place each PI (tangent-to-tangent). RMB/Enter finishes and
    immediately generates the alignment with every PI a sharp corner. If
    there are interior PIs, a marker empty is left at each one — select a
    marker and use "Apply Curve" (see the Alignments tab panel) to give it a
    circular curve and regenerate. ESC cancels without creating anything.

    Numeric Distance/Angle input is available via the D/A keys, same as the
    rest of Bonsai's polyline tools.
    """

    bl_idname = "align.draw_horizontal_alignment"
    bl_label = "Draw Horizontal Alignment"
    bl_description = (
        "Draw the horizontal alignment in the viewport. Click to place PIs, "
        "RMB/Enter to generate it. ESC cancels."
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Add or select an alignment first")
            return False
        return True

    def __init__(self, *args, **kwargs):
        bpy.types.Operator.__init__(self, *args, **kwargs)
        PolylineOperator.__init__(self)
        # Remove instructions that don't apply to alignments
        self.instructions.pop("Close Polyline", None)
        self.instructions.pop("Offset", None)
        self._bearing_handle = None
        self._last_mouse_pos = (0, 0)

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        # Find the 3D viewport — the operator is invoked from the Properties
        # panel, so we need to override context for PolylineOperator.invoke(),
        # and for snapping the view to plan (top-down).
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
            # Step: automatically rotate the viewport to the XY plane (Z-up,
            # looking straight down) so the alignment is drawn in plan.
            bpy.ops.view3d.view_axis(type="TOP")
            super().invoke(context, event)

        self.tool_state.use_default_container = False
        self.tool_state.plane_method = "XY"

        args = (context,)
        self._bearing_handle = SpaceView3D.draw_handler_add(self._draw_bearing_hud, args, "WINDOW", "POST_PIXEL")

        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _modal(self, context, event):
        self._last_mouse_pos = (event.mouse_region_x, event.mouse_region_y)
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
        _insert_polyline_point_no_close(self, context, event)

        # Finish: generate the alignment (sharp corners) and, if there are
        # interior PIs, leave a marker at each for later curve editing.
        if (
            not self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            self._uninstall_bearing_hud()
            context.workspace.status_text_set(text=None)
            PolylineDecorator.uninstall()
            self._finish(context)
            tool.Polyline.clear_polyline()
            tool.Blender.update_viewport()
            return {"FINISHED"}

        cancel = self.handle_cancelation(context, event)
        if cancel is not None:
            self._uninstall_bearing_hud()
            return cancel

        return {"RUNNING_MODAL"}

    def _finish(self, context):
        ok, result = _hpoints_from_polyline(context)
        if not ok:
            self.report({"WARNING"}, result)
            return

        raw_points, hpoints = result
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            self.report({"WARNING"}, "Add or select an alignment first")
            return

        # Redrawing replaces the alignment's geometry outright, so any markers
        # left over from a previous draw on this same alignment are stale —
        # drop them first rather than accumulating duplicates.
        for old_marker in _find_pi_markers(alignment.id()):
            bpy.data.objects.remove(old_marker, do_unlink=True)

        radii = [0.0] * (len(hpoints) - 2)
        ok, message = _generate_alignment_segments(context, alignment, hpoints, radii)
        if ok and radii:
            _create_pi_markers(context, alignment.id(), raw_points)
            message += " — select a PI marker and click Apply Curve to add a curve"

        # Make the alignment the active/selected object so it's immediately
        # visible in the outliner/properties pane without a manual click —
        # _generate_alignment_segments()/_create_pi_markers() don't leave
        # any particular object selected.
        if ok:
            alignment_obj = tool.Ifc.get_object(alignment)
            if alignment_obj:
                for obj in context.selected_objects:
                    obj.select_set(False)
                alignment_obj.select_set(True)
                context.view_layer.objects.active = alignment_obj

        self.report({"INFO"} if ok else {"WARNING"}, message)

    def _uninstall_bearing_hud(self):
        if self._bearing_handle is not None:
            SpaceView3D.draw_handler_remove(self._bearing_handle, "WINDOW")
            self._bearing_handle = None

    def _draw_bearing_hud(self, context):
        """Draw the current tangent's bearing alongside the Distance/Angle HUD.

        Positioned below the existing D/A/X/Y readout (which floats near the
        mouse cursor) so both are visible together while drawing.
        """
        azimuth = self.input_ui.get_number_value("WORLD_ANGLE") if self.input_ui else None
        if not azimuth and azimuth != 0.0:
            return
        mouse_pos = self._last_mouse_pos

        addon_prefs = tool.Blender.get_addon_preferences()
        font_id = 0
        font_size = tool.Blender.scale_font_size()
        offset = tool.Blender.scale_font_size() * 1.5
        line_height = tool.Blender.scale_font_size() * 1.25
        # One line below the D/A/X/Y stack (up to 4 lines tall).
        below_stack = line_height * (len(self.input_ui.input_options) + 1)

        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)
        blf.color(font_id, *addon_prefs.decorations_colour)
        blf.position(font_id, mouse_pos[0] + offset, mouse_pos[1] - below_stack, 0)
        blf.draw(font_id, "Bearing: " + _bearing_string(azimuth))
        blf.disable(font_id, blf.SHADOW)


# =============================================================================
# Stationing Operators
# =============================================================================


class ALIGN_OT_add_stationing_referent(Operator, tool.Ifc.Operator):
    """Add a stationing referent to the alignment"""

    bl_idname = "align.add_stationing_referent"
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


class ALIGN_OT_name_segments(Operator, tool.Ifc.Operator):
    """Auto-name segments based on station values"""

    bl_idname = "align.name_segments"
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
# Vertical Profile Window Operator
# =============================================================================


class ALIGN_OT_show_vertical_profile(Operator):
    """Toggle the docked vertical profile view below the active 3D viewport"""

    bl_idname = "align.show_vertical_profile"
    bl_label = "Toggle Vertical Profile"
    bl_description = (
        "Dock a 2D vertical profile view below this viewport (click again to close). "
        "Elevation is exaggerated by the VE factor. Use middle-mouse to pan/zoom."
    )
    bl_options = {"REGISTER"}

    def execute(self, context):
        import mathutils

        dec = alignment_decorator.VerticalProfileDecorator

        # --- Toggle off ---
        if dec.is_installed:
            context.scene.CivilAlignmentProperties.vertical_items.clear()
            dec.uninstall()
            return {"FINISHED"}

        # --- Toggle on ---
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            self.report({"WARNING"}, "No alignment selected")
            return {"CANCELLED"}

        dec._compute_profile(alignment)
        if not dec.segments_polylines:
            self.report({"WARNING"}, "No vertical alignment data found for this alignment")
            return {"CANCELLED"}

        ve = context.scene.CivilAlignmentProperties.vertical_exaggeration

        # Find the 3D view area and its WINDOW region for the split call
        area = context.area
        if area.type != "VIEW_3D":
            # Button pressed from a non-3D area — find the first 3D view
            area = next((a for a in context.screen.areas if a.type == "VIEW_3D"), None)
            if area is None:
                self.report({"WARNING"}, "No 3D Viewport found")
                return {"CANCELLED"}
        win_region = next((r for r in area.regions if r.type == "WINDOW"), None)
        if win_region is None:
            return {"CANCELLED"}

        # Split with a horizontal dividing line so the profile appears below the
        # main 3D view.  factor=0.7 keeps 70% for the existing area (top) and
        # gives 30% to the new profile area (bottom).
        # direction="HORIZONTAL" = horizontal split line = top/bottom areas.
        # Use as_pointer() (stable C address) rather than id() (Python wrapper ID,
        # which can change after Blender reshuffles wrappers following area_close).
        ptrs_before = {a.as_pointer() for a in context.screen.areas}
        with context.temp_override(area=area, region=win_region):
            bpy.ops.screen.area_split(direction="HORIZONTAL", factor=0.7)

        new_areas = [a for a in context.screen.areas if a.as_pointer() not in ptrs_before]
        if not new_areas:
            self.report({"WARNING"}, "Could not split the viewport")
            return {"CANCELLED"}

        # Blender's area_split places the NEW area above the original area.
        # The original area stays at the bottom — use it as the profile view.
        profile_area = area

        space = next((s for s in profile_area.spaces if s.type == "VIEW_3D"), None)
        if space is None:
            return {"CANCELLED"}

        # Front orthographic: 90° rotation around X so Z is elevation, X is distance
        space.region_3d.view_perspective = "ORTHO"
        space.region_3d.view_rotation = mathutils.Quaternion((0.7071068, 0.7071068, 0.0, 0.0))

        dec.fit_view(space, ve, area_width=profile_area.width, area_height=profile_area.height)

        space.overlay.show_floor = False
        space.overlay.show_axis_x = False
        space.overlay.show_axis_y = False
        space.overlay.show_axis_z = False
        space.show_gizmo = False

        # Hide tool shelf and N-panel so they don't obscure the profile extents.
        # Set directly on the space (absolute, not a toggle) so this works reliably
        # regardless of the panel's current visibility state.
        space.show_region_toolbar = False
        space.show_region_ui = False

        # Populate per-vertical and per-cant visibility filters (all visible by default)
        props = context.scene.CivilAlignmentProperties
        props.vertical_items.clear()
        for v_id, v_label in dec.available_verticals:
            item = props.vertical_items.add()
            item.entity_id = v_id
            item.label = v_label
            item.is_visible = True

        props.cant_items.clear()
        for c_id, c_label in dec.available_cants:
            item = props.cant_items.add()
            item.entity_id = c_id
            item.label = c_label
            item.is_visible = True

        dec.install(context, profile_area)
        profile_area.tag_redraw()

        return {"FINISHED"}


# =============================================================================
# Segment Selection Operator
# =============================================================================


class ALIGN_OT_select_h_segment(Operator):
    """Toggle highlight of a horizontal alignment segment in the 3D viewport"""

    bl_idname = "align.select_h_segment"
    bl_label = "Select Horizontal Segment"
    bl_description = "Highlight this segment in the 3D viewport"
    bl_options = {"REGISTER"}

    segment_id: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties

        if props.selected_h_segment_id == self.segment_id:
            props.selected_h_segment_id = 0
            alignment_decorator.AlignmentSegmentDecorator.uninstall()
        else:
            props.selected_h_segment_id = self.segment_id
            alignment_decorator.AlignmentSegmentDecorator.install(context, self.segment_id)

        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.tag_redraw()
        return {"FINISHED"}


class ALIGN_OT_select_v_segment(Operator):
    """Toggle highlight of a vertical alignment segment in the profile view"""

    bl_idname = "align.select_v_segment"
    bl_label = "Select Vertical Segment"
    bl_description = "Highlight this segment in the profile view"
    bl_options = {"REGISTER"}

    segment_id: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties

        if props.selected_v_segment_id == self.segment_id:
            props.selected_v_segment_id = 0
        else:
            props.selected_v_segment_id = self.segment_id

        alignment_decorator.VerticalProfileDecorator.tag_redraw()
        return {"FINISHED"}


class ALIGN_OT_select_cant_segment(Operator):
    """Toggle highlight of a cant segment in the profile view"""

    bl_idname = "align.select_cant_segment"
    bl_label = "Select Cant Segment"
    bl_description = "Highlight this cant segment in the profile view"
    bl_options = {"REGISTER"}

    segment_id: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties

        if props.selected_cant_segment_id == self.segment_id:
            props.selected_cant_segment_id = 0
        else:
            props.selected_cant_segment_id = self.segment_id

        alignment_decorator.VerticalProfileDecorator.tag_redraw()
        return {"FINISHED"}


# =============================================================================
# PI Edit Mode Operator
# =============================================================================


class ALIGN_OT_enter_pi_edit_mode(Operator, tool.Ifc.Operator):
    """Enter PI editing mode - move PIs with G key, press Enter to apply or Escape to cancel"""

    bl_idname = "align.enter_pi_edit_mode"
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
