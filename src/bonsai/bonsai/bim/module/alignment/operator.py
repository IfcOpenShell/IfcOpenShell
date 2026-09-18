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
import math
import mathutils
import time
from typing import TYPE_CHECKING
import bonsai.core.alignment as core
import bonsai.tool as tool
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import ifcopenshell.util.unit
from bpy_extras.io_utils import ImportHelper
from bpy_extras.view3d_utils import region_2d_to_location_3d
from bpy.types import Operator, SpaceView3D
from bpy.props import StringProperty, FloatProperty, EnumProperty, IntProperty, BoolProperty
from . import decorator as alignment_decorator
from . import prop
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

        alignment = core.import_alignment_csv(tool.Ifc, tool.Alignment, filepath=self.filepath)

        # Make the imported alignment the active/selected object so it's
        # immediately picked up by tool.Alignment.get_active_alignment() —
        # same convention as ALIGN_OT_add_alignment/ALIGN_OT_draw_horizontal_alignment.
        alignment_obj = tool.Ifc.get_object(alignment)
        if alignment_obj:
            for obj in context.selected_objects:
                obj.select_set(False)
            alignment_obj.select_set(True)
            context.view_layer.objects.active = alignment_obj

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


# =============================================================================
# Alignments tab authoring workflow (Add Element + interactive drawing).
#
# No persistent PI table, no dependency on CivilAlignmentProperties beyond
# the alignment selector: an alignment is added as a bare IfcAlignment, then
# its horizontal geometry is drawn directly in the viewport and committed to
# IFC on completion.
# =============================================================================


class ALIGN_OT_add_alignment(Operator, tool.Ifc.Operator):
    """Add a new, empty IfcAlignment to the project"""

    bl_idname = "align.add_alignment"
    bl_label = "Add Alignment"
    bl_description = "Add a new alignment to the project. Draw its horizontal geometry next."
    bl_options = {"REGISTER", "UNDO"}

    alignment_name: StringProperty(name="Name", default="Alignment")
    start_station: StringProperty(
        name="Start Station",
        description="Station value at the start of the alignment (distance along 0). "
        "Accepts a plain number or stationing notation, e.g. 10+00 or 1+000",
        default="0",
    )

    @classmethod
    def poll(cls, context):
        return poll_ifc4x3(cls, context)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        try:
            start_station = tool.Alignment.parse_station(self.start_station)
        except ValueError as e:
            self.report({"ERROR"}, f"Invalid start station: {e}")
            return {"CANCELLED"}

        try:
            alignment = core.create_alignment(tool.Ifc, tool.Alignment, self.alignment_name, start_station)
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
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Select an alignment first")
            return False
        if _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        props = context.scene.CivilAlignmentProperties
        if props.horizontal_pi_rows and props.editing_horizontal_pi_alignment_id == alignment.id():
            cls.poll_message_set("Finish or clear the PI table edit first")
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

    station: StringProperty(
        name="Start Station",
        description="Accepts a plain number or stationing notation, e.g. 10+00 or 1+000",
        default="0",
    )

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
        current = ifcopenshell.api.alignment.get_alignment_start_station(tool.Ifc.get(), alignment) or 0.0
        self.station = tool.Alignment.format_station(current)
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        try:
            station = tool.Alignment.parse_station(self.station)
        except ValueError as e:
            self.report({"ERROR"}, f"Invalid station: {e}")
            return {"CANCELLED"}

        alignment = tool.Alignment.get_active_alignment()
        start_referent = tool.Alignment.find_stationing_referent_at(alignment, 0.0)
        if start_referent is None:
            # No stationing at all yet (e.g. an alignment from before this
            # feature existed) -- add the start referent rather than error.
            start_referent = ifcopenshell.api.alignment.add_stationing_referent(
                tool.Ifc.get(), tool.Alignment.format_station(station), alignment, 0.0, station
            )
        else:
            tool.Alignment.set_stationing_referent_station(start_referent, station)
        tool.Alignment.create_object_for_referent(start_referent)
        alignment_decorator.AlignmentSegmentDecorator.refresh()
        self.report({"INFO"}, f"Start station set to {tool.Alignment.format_station(station)}")
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
    station: StringProperty(
        name="Outgoing Station",
        description="The station value immediately after this point. Accepts a plain "
        "number or stationing notation, e.g. 10+00 or 1+000",
        default="0",
        update=_on_station_equation_station_update,
    )
    incoming_station: StringProperty(
        name="Incoming Station",
        description="The station value immediately before this point. Leave equal to Outgoing "
        "Station (the default) for no gap/overlap. Accepts a plain number or stationing "
        "notation, e.g. 10+00 or 1+000",
        default="0",
    )
    reverse_direction: BoolProperty(
        name="Reverse Stationing Direction",
        description="Stations decrease with distance along from this point on, instead of increasing",
        default=False,
    )
    # Bookkeeping only, for _on_station_equation_station_update — not shown, not saved.
    station_snapshot: StringProperty(options={"HIDDEN", "SKIP_SAVE"}, default="0")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "distance_along")
        layout.prop(self, "incoming_station")
        layout.prop(self, "station")
        layout.prop(self, "reverse_direction")

    def _parse_stations(self):
        """Parse the station/incoming_station text fields.

        Returns (station, incoming_station, has_gap_or_overlap) — comparing
        the parsed values rather than raw text so "1000" and "1+000" (the
        same station, different notation) don't register as a gap.

        Raises:
            ValueError: If either field isn't a valid station.
        """
        station = tool.Alignment.parse_station(self.station)
        incoming_station = tool.Alignment.parse_station(self.incoming_station)
        return station, incoming_station, incoming_station != station


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
        try:
            station, incoming_station, has_gap_or_overlap = self._parse_stations()
        except ValueError as e:
            self.report({"ERROR"}, f"Invalid station: {e}")
            return {"CANCELLED"}

        alignment = tool.Alignment.get_active_alignment()
        name = tool.Alignment.format_station(station)
        referent = ifcopenshell.api.alignment.add_stationing_referent(
            tool.Ifc.get(),
            name,
            alignment,
            self.distance_along,
            station,
            incoming_station=incoming_station if has_gap_or_overlap else None,
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
        station_val = ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="Station") or 0.0
        self.station = tool.Alignment.format_station(station_val)
        incoming = ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="IncomingStation")
        self.incoming_station = tool.Alignment.format_station(incoming if incoming is not None else station_val)
        self.reverse_direction = (
            ifcopenshell.util.element.get_pset(referent, name="Pset_Stationing", prop="HasIncreasingStation") is False
        )
        self.station_snapshot = self.station
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        try:
            station, incoming_station, has_gap_or_overlap = self._parse_stations()
        except ValueError as e:
            self.report({"ERROR"}, f"Invalid station: {e}")
            return {"CANCELLED"}

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

        name = tool.Alignment.format_station(station)
        new_referent = ifcopenshell.api.alignment.add_stationing_referent(
            ifc,
            name,
            alignment,
            self.distance_along,
            station,
            incoming_station=incoming_station if has_gap_or_overlap else None,
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


def _tag_all_areas_redraw(context):
    """Tag every area in every window for redraw, not just the active 3D viewport.

    tool.Blender.update_viewport() (called alongside this at most of this module's call sites)
    only tags a VIEW_3D area. That's fine for the alignment mesh/decorators, but this module's IFC
    writes (creating/replacing IfcAlignmentSegments) never touch Blender's own RNA data, so nothing
    tells Blender's dependency graph anything changed -- the read-only "Alignment Segments" panel
    (ALIGN_PT_alignment_segments, in the Properties editor's Scene tab, reading straight from the
    live IFC file on every draw()) doesn't get a fresh draw() call at all unless something
    explicitly tags its area, and is left showing stale segment data (start point, radius, type...)
    until some unrelated interaction happens to repaint it.
    """
    wm = getattr(context, "window_manager", None)
    if wm is None:
        return
    for window in wm.windows:
        for area in window.screen.areas:
            area.tag_redraw()


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

    Uses layout_horizontal_alignment_by_pi_method, which now also accepts
    (radius, entry_length, exit_length) tuples for clothoid spiral-circular,
    circular-spiral, and spiral-circular-spiral PIs alongside plain-radius
    circular curves — see solve_horizontal_alignment_by_pi_method.
    """
    ifc = tool.Ifc.get()

    # Viennese Bend's own geometry depends on a real cant segment at the same station
    # (ifcopenshell.api.alignment._get_cant_segment has no fallback for "no cant layout anywhere on
    # this alignment") -- same check as the raw segment table's ALIGN_OT_apply_h_segments, applied
    # here too since the PI-method dropdown (prop._spiral_family_items) only *usually* keeps
    # Viennese Bend hidden until a cant layout exists; a marker/row that already had it selected
    # before the cant layout was deleted would otherwise slip through. Returning early here (rather
    # than raising) keeps this a clean, reportable failure through the same (ok, message) contract
    # every caller already handles, instead of the generic "partially completed" recovery path
    # tool.Ifc.Operator falls back to for an uncaught exception.
    if any(isinstance(r, tuple) and len(r) >= 4 and r[3] == "VIENNESEBEND" for r in radii):
        if not tool.Alignment.has_real_cant_segments(alignment):
            return False, "Viennese Bend needs a cant layout first -- use Generate Cant Layout, then retry Apply."

    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    if h_layout is None:
        h_layout = tool.Alignment.add_horizontal_layout_to_alignment(alignment)

    if not tool.Ifc.get_object(alignment):
        tool.Alignment.create_object_for_alignment(alignment)

    # Drop any layout/segment objects a previous draw on this alignment left
    # behind (e.g. from before this single-mesh approach existed) so the
    # scene collection converges on exactly one object for the alignment —
    # what loading it from a file would give you — rather than accumulating
    # per-layout/per-segment objects alongside it.
    tool.Alignment.remove_layout_and_child_layout_objects(alignment)

    tool.Alignment.clear_layout_segments(h_layout)
    try:
        tool.Alignment.safe_layout_horizontal_by_pi_method(ifc, h_layout, hpoints, radii)
    except ValueError as e:
        # solve_horizontal_alignment_by_pi_method() is a streaming generator that
        # layout_horizontal_alignment_by_pi_method() writes to IFC segment-by-segment as it goes
        # (e.g. entry+exit spiral deflection exceeding the PI's own deflection angle, raised only
        # once it reaches that PI) -- so by the time this raises, earlier PIs' segments may already
        # be written. Clear them rather than leaving a half-built, broken layout sitting in IFC:
        # this keeps the same clean (ok, message) contract every caller here already handles
        # (see the VIENNESEBEND check above) instead of the generic "partially completed" recovery
        # path tool.Ifc.Operator falls back to for an uncaught exception.
        tool.Alignment.clear_layout_segments(h_layout)
        return False, f"Could not lay out alignment: {e}"
    ifcopenshell.api.alignment.create_representation(ifc, alignment)

    tool.Alignment.refresh_alignment_representation_object(alignment)

    # create_representation() just "restated" any origin-placed stationing
    # referent onto the real curve at the IFC level (see add_stationing_referent's
    # docstring) -- sync the Blender objects to match, or the start-station marker
    # stays stuck at the origin forever regardless of where the alignment ended up.
    tool.Alignment.sync_stationing_referent_placements(alignment)

    # Keep an already-generated cant layout's curve types matching the
    # horizontal's own (a no-op if there's no cant layout yet, or if the
    # segment counts have drifted apart -- see sync_cant_segment_types).
    tool.Alignment.sync_cant_segment_types(alignment)

    _tag_all_areas_redraw(context)

    n_curved = sum(1 for r in radii if (r[0] if isinstance(r, tuple) else r))
    return True, f"Drew alignment '{alignment.Name}' with {len(hpoints)} PIs ({n_curved} curved)"


def _create_pi_markers(context, alignment_id, raw_points):
    """Place a marker empty at every interior PI, plus the Start and End points
    (Blender-world position, metres).

    ``pi_index`` keeps counting from the full point list (0 for Start, 1-based
    among interior PIs, the last index for End) purely for sort order — see
    _find_pi_markers — and, for interior PIs, the "PI n" label.

    Tagged via Object.bonsai_pi_curve_marker so ALIGN_OT_apply_pi_curve /
    ALIGN_OT_finish_pi_editing can find them without any operator-instance
    state (the drawing operator that created them has already finished by
    the time a curve is applied).
    """
    n = len(raw_points)
    markers = [_create_endpoint_marker(context, alignment_id, "START", raw_points[0], pi_index=0)]
    for i, (x, y, z) in enumerate(raw_points):
        if i == 0 or i == n - 1:
            continue
        empty = bpy.data.objects.new(f"PI {i} (tangent)", None)
        # A minimal, small click target -- PIMarkerDecorator's colored
        # screen-space dot (red/green by curve state) plus its "PI n" label
        # is the actual visual cue now; a full-size SPHERE display here would
        # just double it up with a second, competing circle.
        empty.empty_display_type = "PLAIN_AXES"
        empty.empty_display_size = 0.3
        empty.location = (x, y, z)
        _lock_pi_marker_transform(empty)
        marker = empty.bonsai_pi_curve_marker
        marker.is_pi_marker = True
        marker.alignment_id = alignment_id
        marker.pi_index = i
        marker.curve_type = "TANGENT"
        context.collection.objects.link(empty)
        markers.append(empty)
    markers.append(_create_endpoint_marker(context, alignment_id, "END", raw_points[n - 1], pi_index=n - 1))
    return markers


def _create_endpoint_marker(context, alignment_id, role, point, pi_index=0):
    """Create a draggable Start/End Point marker Empty at ``point`` (Blender-world XYZ).

    Mirrors _create_pi_markers()'s interior-PI markers exactly (same PLAIN_AXES/size and
    XY-plane-only lock, same Object.bonsai_pi_curve_marker tagging), but for the alignment's own
    endpoint rather than an interior PI -- it has no curve to define, just a position. Read back by
    ALIGN_OT_apply_pi_curve in place of tool.Alignment.get_alignment_start_end_points() whenever a
    Start/End marker exists.
    """
    label = "Start Point" if role == "START" else "End Point"
    empty = bpy.data.objects.new(label, None)
    empty.empty_display_type = "PLAIN_AXES"
    empty.empty_display_size = 0.3
    empty.location = point
    _lock_pi_marker_transform(empty)
    marker = empty.bonsai_pi_curve_marker
    marker.is_pi_marker = True
    marker.alignment_id = alignment_id
    marker.role = role
    marker.pi_index = pi_index
    context.collection.objects.link(empty)
    return empty


def _lock_pi_marker_transform(empty) -> None:
    """Restrict a PI marker empty to dragging in the XY plane.

    Dragging a marker to reposition it (mentioned in ALIGN_OT_edit_horizontal_pis's
    own docstring as a supported way to edit a PI, alongside typing curve_type/
    radius in the panel) is just Blender's native move tool -- ALIGN_OT_apply_pi_curve
    already reads every marker's *current* .location when it regenerates the
    alignment, so nothing further is needed to wire dragging up. But a horizontal
    alignment is inherently 2D (_world_point_to_local_ifc always discards Z), so an
    accidental drag off the XY plane would silently do nothing at Apply Curve time
    while leaving the marker floating above/below the curve -- confusing, not
    dangerous. Locking Z, plus rotation/scale (meaningless for a point marker),
    heads that off instead of relying on the user not to trigger it.
    """
    empty.lock_location[2] = True
    empty.lock_rotation = (True, True, True)
    empty.lock_scale = (True, True, True)


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


def _alignment_id_owning_layout(layout_entity) -> int | None:
    """Top-level IfcAlignment id that nests ``layout_entity`` (an
    IfcAlignmentHorizontal/Vertical/Cant), or None if it isn't nested under one.

    A per-row UI button (e.g. the per-vertical Edit Segments / Edit PIs
    buttons in ALIGN_PT_alignment_segments) needs to check the *specific*
    alignment that row belongs to -- not tool.Alignment.get_active_alignment(),
    which only ever reflects whatever object happens to be active/selected
    right now, and has no visibility into which layout_id a given row's
    button is about to set once clicked. A classmethod poll() can't see that
    either (operator properties aren't set until after the button fires), so
    rows that need to grey out a specific button use this to compute their
    own alignment_id and disable that button directly in the draw call.
    """
    for rel in getattr(layout_entity, "Nests", []) or []:
        if rel.RelatingObject.is_a("IfcAlignment"):
            return tool.Alignment._get_top_level_alignment(rel.RelatingObject).id()
    return None


def _is_interior_pi_marker(obj) -> bool:
    """Whether ``obj`` is an interior-PI marker specifically (has a curve to define),
    as opposed to a Start/End Point marker (see _is_endpoint_marker) -- only an
    interior PI marker gets the curve-type/radius/spiral fields in the panel.
    """
    return obj.bonsai_pi_curve_marker.is_pi_marker and obj.bonsai_pi_curve_marker.role == "PI"


def _is_endpoint_marker(obj) -> bool:
    """Whether ``obj`` is a Start/End Point marker (see _create_endpoint_marker)."""
    return obj.bonsai_pi_curve_marker.is_pi_marker and obj.bonsai_pi_curve_marker.role in {"START", "END"}


def _refresh_pi_marker_visuals(context, alignment_id) -> None:
    """(Re)draw, or clear, both viewport cues for this alignment's PI markers:
    the persistent status-bar hint (outstanding TANGENT markers) and the
    PIMarkerDecorator dot/label overlay (every marker, curved or not).

    Drawing an alignment leaves the same kind of silence: the finished
    ALIGN_OT_draw_horizontal_alignment clears its own D/A/X/Y modal
    instructions and there's nothing telling the user PI markers are now
    sitting in the viewport waiting for a curve, short of the report() toast
    and a properties-panel box easy to miss if that tab isn't open.
    status_text_set() persists in the header on its own once called -- no
    running modal needed to keep it alive -- so this is called once after
    drawing/editing finishes and again whenever apply_pi_curve/finish_pi_editing
    changes which markers are still pending, keeping both cues in sync with
    current state.

    Known gap: switching the active alignment via the dropdown, or an undo,
    doesn't re-run this, so the cues can go stale until the next
    draw/edit/apply/clear touches PI markers. Acceptable for now -- revisit
    if it proves confusing in practice.
    """
    alignment_decorator.PIMarkerDecorator.refresh(context, alignment_id)

    pending = [m for m in _find_pi_markers(alignment_id) if _is_interior_pi_marker(m) and m.bonsai_pi_curve_marker.curve_type == "TANGENT"]
    if not pending:
        context.workspace.status_text_set(text=None)
        return

    noun = "PI" if len(pending) == 1 else "PIs"
    hint = f"{len(pending)} {noun} still need a curve — select a marker and click Apply Curve, or click Finish"

    def draw(self, context):
        self.layout.label(text=hint, icon="INFO")

    context.workspace.status_text_set(draw)


def _cant_lookup_for_pi_markers(alignment, n):
    """(cant, rail_head_distance) per interior PI, in PI order, for feeding into
    _pi_curve_radii_entry's VIENNESEBEND handling -- a fresh read of the alignment's *current* real
    segments and cant layout (via _reconstruct_horizontal_pis, which already does this exact
    positional lookup when reconstructing markers) taken right before a PI-method Apply rebuilds
    everything, so a marker/row that doesn't itself store cant data still gets the real value.

    Always returns exactly n entries, defaulting to (0.0, 1.0) for any PI
    _reconstruct_horizontal_pis doesn't account for (a different count than n means something --
    typically a manually added/removed marker -- has already broken the positional correspondence
    this relies on, same as the reason _reconstruct_horizontal_pis/sync_cant_segment_types both
    already tolerate a mismatched count elsewhere rather than erroring on it).
    """
    h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
    if h_layout is None:
        return [(0.0, 1.0)] * n
    specs, _ = _reconstruct_horizontal_pis(h_layout)
    lookup = [(spec["cant"], spec["rail_head_distance"]) for spec in specs]
    lookup += [(0.0, 1.0)] * (n - len(lookup))
    return lookup[:n]


def _pi_curve_radii_entry(marker, cant_and_rail_head_distance=(0.0, 1.0)):
    """One radii[] element (see solve_horizontal_alignment_by_pi_method) for a PI marker.

    TANGENT stays a plain 0.0 (no curve). CIRCULAR stays a plain radius float
    for backward compatibility. The three spiral curve types become a
    (radius, entry_length, exit_length, spiral_family, vb_params) tuple with
    whichever length(s) don't apply left at 0.0 -- entry and exit always
    share one family per PI (marker.spiral_family). vb_params is None unless
    spiral_family is VIENNESEBEND, in which case it's (marker.
    gravity_centerline_height, cant, rail_head_distance) -- see
    _cant_lookup_for_pi_markers for where cant/rail_head_distance come from.
    """
    curve_type = marker.curve_type
    if curve_type == "TANGENT":
        return 0.0
    if curve_type == "CIRCULAR":
        return marker.radius

    vb_params = None
    if marker.spiral_family == "VIENNESEBEND":
        cant, rail_head_distance = cant_and_rail_head_distance
        vb_params = (marker.gravity_centerline_height, cant, rail_head_distance)

    if curve_type == "SPIRAL_CIRCULAR":
        return (marker.radius, marker.spiral_in_length, 0.0, marker.spiral_family, vb_params)
    if curve_type == "CIRCULAR_SPIRAL":
        return (marker.radius, 0.0, marker.spiral_out_length, marker.spiral_family, vb_params)
    # SPIRAL_CIRCULAR_SPIRAL
    return (marker.radius, marker.spiral_in_length, marker.spiral_out_length, marker.spiral_family, vb_params)


def _pi_curve_marker_label(marker) -> str:
    """Short label for a PI marker's name, reflecting its curve settings."""
    curve_type = marker.curve_type
    if curve_type == "TANGENT":
        return "tangent"
    if curve_type == "CIRCULAR":
        return f"R={marker.radius:.2f}"
    # the three spiral shapes all carry a family; only name it when it isn't the default, so a
    # plain clothoid PI's label doesn't grow noisier than it already was
    family_suffix = "" if marker.spiral_family == "CLOTHOID" else f" [{marker.spiral_family}]"
    if curve_type == "SPIRAL_CIRCULAR":
        return f"R={marker.radius:.2f}, Lin={marker.spiral_in_length:.2f}{family_suffix}"
    if curve_type == "CIRCULAR_SPIRAL":
        return f"R={marker.radius:.2f}, Lout={marker.spiral_out_length:.2f}{family_suffix}"
    # SPIRAL_CIRCULAR_SPIRAL
    return f"R={marker.radius:.2f}, Lin={marker.spiral_in_length:.2f}, Lout={marker.spiral_out_length:.2f}{family_suffix}"


def _local_ifc_to_world_point(ifc, unit_scale, xy):
    """Inverse of _world_point_to_local_ifc: local IFC (x, y) -> Blender-world (metres)."""
    e, n = ifcopenshell.util.geolocation.auto_xyz2enh(ifc, xy[0], xy[1], 0.0)[:2]
    local = tool.Georeference.enh2xyz((e, n, 0.0))
    return (local[0] * unit_scale, local[1] * unit_scale, 0.0)


def _tangent_line_intersection(dp_a, dp_b):
    """Where two LINE segments' own tangent lines cross, in local IFC coords.

    Same technique as AlignmentSegmentDecorator._compute_tangent_data's PI
    computation. Returns None if the two tangents are parallel (no PI).
    """
    sx, sy = dp_a.StartPoint.Coordinates[0], dp_a.StartPoint.Coordinates[1]
    ex, ey = dp_b.StartPoint.Coordinates[0], dp_b.StartPoint.Coordinates[1]
    d1x, d1y = math.cos(dp_a.StartDirection), math.sin(dp_a.StartDirection)
    d2x, d2y = math.cos(dp_b.StartDirection), math.sin(dp_b.StartDirection)
    denom = d1x * d2y - d1y * d2x
    if abs(denom) < 1e-10:
        return None
    t1 = ((ex - sx) * d2y - (ey - sy) * d2x) / denom
    return sx + t1 * d1x, sy + t1 * d1y


def _reconstruct_horizontal_pis(h_layout):
    """Classify every interior PI of h_layout's current real segments.

    Only the five shapes PICurveMarkerProperties.curve_type already supports
    are recognized: a sharp corner between two LINEs (TANGENT), a lone
    CIRCULARARC (CIRCULAR), or a CIRCULARARC with a spiral (any one family in
    prop.PI_METHOD_SPIRAL_TYPES) on one or both sides (SPIRAL_CIRCULAR /
    CIRCULAR_SPIRAL / SPIRAL_CIRCULAR_SPIRAL) -- matching what
    solve_horizontal_alignment_by_pi_method can (re)generate. A two-spiral PI
    whose entry and exit families differ is reported as skipped: entry and
    exit always share one family per PI (see PICurveMarkerProperties.
    spiral_family), so there's no marker shape to reconstruct it into.

    Returns (specs, skipped). ``specs`` is a list of dicts with pi_local
    (x, y) plus curve_type/radius/spiral_in_length/spiral_out_length/
    spiral_family/gravity_centerline_height, one per interior PI, in order.
    ``skipped`` is a list of (segment, reason) for any segment that isn't
    part of one of those five shapes -- callers should refuse to create
    markers at all when this is non-empty (regenerating from a partial
    marker list would silently drop whatever those segments were).
    """
    segments = tool.Alignment.get_real_layout_segments(h_layout)
    line_indices = [i for i, s in enumerate(segments) if s.DesignParameters.PredefinedType == "LINE"]

    specs = []
    skipped = []
    if len(line_indices) < 2:
        return specs, [(s, "no bounding tangent") for s in segments]

    # Positionally match the arc segment (see below) to a real cant segment at the same station,
    # the same correspondence tool.Alignment.sync_cant_segment_types relies on -- only meaningful
    # for VIENNESEBEND (see _pi_curve_radii_entry), but cheap enough to always compute here rather
    # than duplicate this lookup at Apply time on a fresh walk of the same segments.
    alignment = ifcopenshell.api.alignment.get_alignment(h_layout)
    cant_layouts = tool.Alignment.get_all_cant_layouts(alignment)
    cant_layout = cant_layouts[0] if cant_layouts else None
    cant_segments = tool.Alignment.get_real_layout_segments(cant_layout) if cant_layout else []
    cant_matches_positionally = bool(cant_layout) and len(cant_segments) == len(segments)
    rail_head_distance = cant_layout.RailHeadDistance if cant_layout else 1.0

    for s in segments[: line_indices[0]]:
        skipped.append((s, "before the first tangent"))
    for s in segments[line_indices[-1] + 1 :]:
        skipped.append((s, "after the last tangent"))

    for k in range(len(line_indices) - 1):
        a_idx, b_idx = line_indices[k], line_indices[k + 1]
        line_a, line_b = segments[a_idx], segments[b_idx]
        between = segments[a_idx + 1 : b_idx]
        types = [s.DesignParameters.PredefinedType for s in between]
        family = "CLOTHOID"  # unused (no spiral), but every spec needs the key

        if types == []:
            curve_type, arc, spiral_in, spiral_out = "TANGENT", None, None, None
        elif types == ["CIRCULARARC"]:
            curve_type, arc, spiral_in, spiral_out = "CIRCULAR", between[0], None, None
        elif len(types) == 2 and types[1] == "CIRCULARARC" and types[0] in prop.PI_METHOD_SPIRAL_TYPES:
            curve_type, arc, spiral_in, spiral_out, family = "SPIRAL_CIRCULAR", between[1], between[0], None, types[0]
        elif len(types) == 2 and types[0] == "CIRCULARARC" and types[1] in prop.PI_METHOD_SPIRAL_TYPES:
            curve_type, arc, spiral_in, spiral_out, family = "CIRCULAR_SPIRAL", between[0], None, between[1], types[1]
        elif (
            len(types) == 3
            and types[1] == "CIRCULARARC"
            and types[0] in prop.PI_METHOD_SPIRAL_TYPES
            and types[2] in prop.PI_METHOD_SPIRAL_TYPES
        ):
            if types[0] != types[2]:
                skipped.extend((s, "entry and exit spiral families differ") for s in between)
                continue
            curve_type, arc, spiral_in, spiral_out, family = (
                "SPIRAL_CIRCULAR_SPIRAL",
                between[1],
                between[0],
                between[2],
                types[0],
            )
        else:
            skipped.extend((s, "unsupported curve family/shape") for s in between)
            continue

        pi_local = _tangent_line_intersection(line_a.DesignParameters, line_b.DesignParameters)
        if pi_local is None:
            # Degenerate (colinear tangents) -- report whatever's between them, or
            # the two LINEs themselves if there's nothing between (sharp-corner case).
            skipped.extend((s, "tangents are parallel") for s in (between or [line_a, line_b]))
            continue

        # GravityCenterLineHeight is a horizontal segment field, carried on the entry and/or exit
        # spiral (both, in practice, since one marker/row sets it for the whole PI) -- only
        # meaningful for VIENNESEBEND, 0.0 for everything else.
        gch_source = spiral_in or spiral_out
        gravity_centerline_height = (gch_source.DesignParameters.GravityCenterLineHeight or 0.0) if gch_source else 0.0

        # The outer rail's cant magnitude at the arc, read from whichever real cant segment sits at
        # the same position as `arc` -- only meaningful for VIENNESEBEND (see
        # _pi_curve_radii_entry), 0.0 when there's no cant layout, the position correspondence has
        # drifted, or this PI has no arc to match against.
        cant = 0.0
        if arc is not None and cant_matches_positionally:
            arc_idx = a_idx + 1 + between.index(arc)
            cant_dp = cant_segments[arc_idx].DesignParameters
            cant = max(abs(cant_dp.StartCantLeft or 0.0), abs(cant_dp.StartCantRight or 0.0))

        specs.append(
            {
                "pi_local": pi_local,
                "curve_type": curve_type,
                # PICurveMarkerProperties.radius (like the radii[] the solver takes) is
                # always an unsigned magnitude -- the solver infers turn direction from
                # the PI geometry itself, unlike DesignParameters.StartRadiusOfCurvature
                # which is signed (+left/-right).
                "radius": abs(arc.DesignParameters.StartRadiusOfCurvature or 0.0) if arc else 0.0,
                "spiral_in_length": (spiral_in.DesignParameters.SegmentLength or 0.0) if spiral_in else 0.0,
                "spiral_out_length": (spiral_out.DesignParameters.SegmentLength or 0.0) if spiral_out else 0.0,
                "spiral_family": family,
                "gravity_centerline_height": gravity_centerline_height,
                "cant": cant,
                "rail_head_distance": rail_head_distance,
            }
        )

    return specs, skipped


class ALIGN_OT_edit_horizontal_pis(Operator, tool.Ifc.Operator):
    """Create editable PI markers from this alignment's current real segments.

    Lets a previously-drawn (and saved) or IFC-imported alignment be tuned
    the same way a freshly-drawn one is: select a marker, adjust its curve
    type/radius/spiral lengths (or drag it), click "Apply Curve".
    """

    bl_idname = "align.edit_horizontal_pis"
    bl_label = "Edit PIs"
    bl_description = (
        "Create PI markers from this alignment's current segments, pre-filled with their "
        "existing curve type/radius/spiral lengths, so they can be adjusted or dragged "
        "and re-applied without redrawing from scratch"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if context.scene.CivilAlignmentProperties.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the PI table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Select an alignment first")
            return False
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        if not h_layout or not tool.Alignment.get_real_layout_segments(h_layout):
            cls.poll_message_set("This alignment has no horizontal segments yet")
            return False
        return True

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        alignment_id = alignment.id()
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        specs, skipped = _reconstruct_horizontal_pis(h_layout)
        if skipped:
            details = "; ".join(f"{s.DesignParameters.PredefinedType} ({reason})" for s, reason in skipped[:5])
            more = f", and {len(skipped) - 5} more" if len(skipped) > 5 else ""
            self.report(
                {"ERROR"},
                f"Can't create PI markers: {len(skipped)} segment(s) couldn't be classified: "
                f"{details}{more}.",
            )
            return {"CANCELLED"}

        for m in _find_pi_markers(alignment_id):
            bpy.data.objects.remove(m, do_unlink=True)

        ifc = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)

        try:
            start, end = tool.Alignment.get_alignment_start_end_points(alignment)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        _create_endpoint_marker(context, alignment_id, "START", _local_ifc_to_world_point(ifc, unit_scale, start), pi_index=0)

        for i, spec in enumerate(specs, start=1):
            x, y, z = _local_ifc_to_world_point(ifc, unit_scale, spec["pi_local"])
            empty = bpy.data.objects.new(f"PI {i}", None)
            # See _create_pi_markers -- PIMarkerDecorator's colored dot/label
            # is the visual cue now, so this only needs to be a click target.
            empty.empty_display_type = "PLAIN_AXES"
            empty.empty_display_size = 0.3
            empty.location = (x, y, z)
            _lock_pi_marker_transform(empty)
            marker = empty.bonsai_pi_curve_marker
            marker.is_pi_marker = True
            marker.alignment_id = alignment_id
            marker.pi_index = i
            marker.curve_type = spec["curve_type"]
            marker.radius = spec["radius"] or 100.0
            marker.spiral_in_length = spec["spiral_in_length"] or 100.0
            marker.spiral_out_length = spec["spiral_out_length"] or 100.0
            marker.spiral_family = spec["spiral_family"]
            marker.gravity_centerline_height = spec["gravity_centerline_height"]
            empty.name = f"PI {i} ({_pi_curve_marker_label(marker)})"
            context.collection.objects.link(empty)

        _create_endpoint_marker(
            context, alignment_id, "END", _local_ifc_to_world_point(ifc, unit_scale, end), pi_index=len(specs) + 1
        )

        alignment_decorator.AlignmentSegmentDecorator.uninstall()
        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Created {len(specs)} PI marker(s) plus Start/End Point markers")
        _refresh_pi_marker_visuals(context, alignment_id)
        return {"FINISHED"}


class ALIGN_OT_apply_pi_curve(Operator, tool.Ifc.Operator):
    """Regenerate the alignment using every current PI/Start/End marker's position and settings.

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
    bl_description = "Regenerate the alignment using every current PI/Start/End marker's position and settings"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        marker = _active_pi_marker(context)
        if not marker:
            cls.poll_message_set("Select a PI, Start, or End marker first")
            return False
        return True

    def _execute(self, context):
        marker_obj = _active_pi_marker(context)
        alignment_id = marker_obj.bonsai_pi_curve_marker.alignment_id
        alignment = tool.Ifc.get().by_id(alignment_id)

        ifc = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc)
        all_markers = _find_pi_markers(alignment_id)
        interior_markers = [m for m in all_markers if _is_interior_pi_marker(m)]
        start_marker = next((m for m in all_markers if m.bonsai_pi_curve_marker.role == "START"), None)
        end_marker = next((m for m in all_markers if m.bonsai_pi_curve_marker.role == "END"), None)

        if start_marker and end_marker:
            start = _world_point_to_local_ifc(ifc, unit_scale, start_marker.location)
            end = _world_point_to_local_ifc(ifc, unit_scale, end_marker.location)
        else:
            # Defensive fallback for a marker set predating Start/End markers (e.g. an older
            # session's markers still sitting in a .blend file) -- every current code path that
            # creates markers always creates Start/End alongside any interior PIs.
            try:
                start, end = tool.Alignment.get_alignment_start_end_points(alignment)
            except ValueError as e:
                self.report({"ERROR"}, str(e))
                return {"CANCELLED"}

        hpoints = (
            [start]
            + [_world_point_to_local_ifc(ifc, unit_scale, m.location) for m in interior_markers]
            + [end]
        )
        cant_lookup = _cant_lookup_for_pi_markers(alignment, len(interior_markers))
        radii = [
            _pi_curve_radii_entry(m.bonsai_pi_curve_marker, cant_lookup[i]) for i, m in enumerate(interior_markers)
        ]

        ok, message = _generate_alignment_segments(context, alignment, hpoints, radii)

        marker = marker_obj.bonsai_pi_curve_marker
        if marker.role == "PI":
            marker_obj.name = f"PI {marker.pi_index} ({_pi_curve_marker_label(marker)})"
        # _generate_alignment_segments() replaces every IfcAlignmentSegment
        # with a new one, so a previously-highlighted segment's id is gone —
        # refreshing it would silently keep showing the old, now-stale
        # highlight at its old position. Uninstalling is the correct call
        # here, same idea as the stationing operators' refresh() below.
        alignment_decorator.AlignmentSegmentDecorator.uninstall()
        tool.Blender.update_viewport()
        self.report({"INFO"} if ok else {"WARNING"}, message)
        _refresh_pi_marker_visuals(context, alignment_id)
        return {"FINISHED"}


class ALIGN_OT_finish_pi_editing(Operator, tool.Ifc.Operator):
    """Wrap up this PI-curve editing pass: remove the temporary PI marker
    empties and dismiss the "PIs still need a curve" status-bar reminder.

    The markers are scaffolding for choosing each PI's curve, not IFC data --
    the alignment's real geometry is already saved to IfcAlignmentSegments the
    moment Apply Curve (or the initial draw) runs, so there's nothing left to
    lose by removing them. Leaving some interior PIs as plain TANGENT (a
    sharp, un-curved corner) is a valid, deliberate choice, so finishing
    doesn't require every marker to have a curve first. They can always be
    brought back later via Edit PIs, which reconstructs them straight from
    the alignment's current segments -- there's no reason for them to sit
    around in the scene in the meantime.
    """

    bl_idname = "align.finish_pi_editing"
    bl_label = "Finish"
    bl_description = "Finish curve editing: remove the temporary PI markers"
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

        # The active object may have been one of the markers just removed (Blender leaves nothing
        # selected once its active object is deleted) -- select the alignment itself instead, same
        # convention as ALIGN_OT_add_alignment/ALIGN_OT_draw_horizontal_alignment, so Finish never
        # leaves the viewport with nothing selected.
        alignment = tool.Ifc.get().by_id(alignment_id)
        alignment_obj = tool.Ifc.get_object(alignment) if alignment else None
        if alignment_obj:
            for obj in context.selected_objects:
                obj.select_set(False)
            alignment_obj.select_set(True)
            context.view_layer.objects.active = alignment_obj

        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Finished — removed {len(markers)} PI marker(s)")
        _refresh_pi_marker_visuals(context, alignment_id)


def _resolve_alignment_id_for_markers(context):
    """The alignment id whose PI markers apply_pi_curve/finish_pi_editing act on.

    Works whether the active object is the alignment itself or one of its
    own (non-IFC-linked) PI markers.
    """
    marker = _active_pi_marker(context)
    if marker:
        return marker.bonsai_pi_curve_marker.alignment_id
    alignment = tool.Alignment.get_active_alignment()
    return alignment.id() if alignment else 0


class ALIGN_OT_load_horizontal_pi_table(Operator, tool.Ifc.Operator):
    """Populate the horizontal PI table from this alignment's current real segments.

    The table-editing companion to align.edit_horizontal_pis (which creates
    draggable viewport Empties for the same PIs): same underlying PI list
    (_reconstruct_horizontal_pis), staged as numeric rows instead, for
    keyboard-precise editing without leaving the panel. Mirrors
    align.load_vertical_pis / VerticalPIMarker.
    """

    bl_idname = "align.load_horizontal_pi_table"
    bl_label = "Edit PIs (Table)"
    bl_description = (
        "Populate the horizontal PI table from this alignment's current segments, pre-filled "
        "with their existing curve type/radius/spiral lengths, so they can be adjusted and "
        "re-applied without redrawing from scratch"
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if alignment and _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        if not alignment:
            cls.poll_message_set("Select an alignment first")
            return False
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        if not h_layout or not tool.Alignment.get_real_layout_segments(h_layout):
            cls.poll_message_set("This alignment has no horizontal segments yet")
            return False
        return True

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)

        specs, skipped = _reconstruct_horizontal_pis(h_layout)
        if skipped:
            details = "; ".join(f"{s.DesignParameters.PredefinedType} ({reason})" for s, reason in skipped[:5])
            more = f", and {len(skipped) - 5} more" if len(skipped) > 5 else ""
            self.report(
                {"ERROR"},
                f"Can't load PI table: {len(skipped)} segment(s) couldn't be classified: "
                f"{details}{more}.",
            )
            return {"CANCELLED"}

        props = context.scene.CivilAlignmentProperties
        props.horizontal_pi_rows.clear()
        for spec in specs:
            item = props.horizontal_pi_rows.add()
            item.x, item.y = spec["pi_local"]
            item.curve_type = spec["curve_type"]
            item.radius = spec["radius"] or 100.0
            item.spiral_in_length = spec["spiral_in_length"] or 100.0
            item.spiral_out_length = spec["spiral_out_length"] or 100.0
            item.spiral_family = spec["spiral_family"]
            item.gravity_centerline_height = spec["gravity_centerline_height"]
        props.editing_horizontal_pi_alignment_id = alignment.id()

        self.report({"INFO"}, f"Loaded {len(specs)} PI(s)")
        return {"FINISHED"}


class ALIGN_OT_apply_horizontal_pi_table(Operator, tool.Ifc.Operator):
    """Regenerate the horizontal alignment using the PI table's curve settings"""

    bl_idname = "align.apply_horizontal_pi_table"
    bl_label = "Apply Horizontal Curves"
    bl_description = "Regenerate the horizontal alignment using each PI's curve type/radius/spiral lengths"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not context.scene.CivilAlignmentProperties.horizontal_pi_rows:
            cls.poll_message_set("Load the PI table first")
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select the alignment first")
            return False
        return True

    def _execute(self, context):
        props = context.scene.CivilAlignmentProperties
        alignment = tool.Alignment.get_active_alignment()

        # editing_horizontal_pi_alignment_id, when set, names the specific
        # alignment horizontal_pi_rows came from -- resolve against that one
        # rather than whatever's active now, same guard as the vertical PI
        # table's editing_vertical_pi_layout_id.
        if props.editing_horizontal_pi_alignment_id:
            try:
                target = tool.Ifc.get().by_id(props.editing_horizontal_pi_alignment_id)
            except RuntimeError:
                target = None
            if target is not None:
                alignment = target

        try:
            start, end = tool.Alignment.get_alignment_start_end_points(alignment)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        rows = list(props.horizontal_pi_rows)
        hpoints = [start] + [(row.x, row.y) for row in rows] + [end]
        cant_lookup = _cant_lookup_for_pi_markers(alignment, len(rows))
        radii = [_pi_curve_radii_entry(row, cant_lookup[i]) for i, row in enumerate(rows)]

        ok, message = _generate_alignment_segments(context, alignment, hpoints, radii)
        if ok:
            props.editing_horizontal_pi_alignment_id = alignment.id()
            # _generate_alignment_segments() replaces every IfcAlignmentSegment
            # with a new one, so a previously-highlighted segment's id is gone --
            # refreshing it would silently keep showing the old, now-stale
            # highlight at its old position.
            alignment_decorator.AlignmentSegmentDecorator.uninstall()
        tool.Blender.update_viewport()
        self.report({"INFO"} if ok else {"WARNING"}, message)
        return {"FINISHED"}


class ALIGN_OT_finish_horizontal_pi_table(Operator):
    """Dismiss the horizontal PI table (rows are staging data, not IFC --
    whatever was last applied via Apply Horizontal Curves is already saved to
    the alignment regardless of whether the table stays open).
    """

    bl_idname = "align.finish_horizontal_pi_table"
    bl_label = "Finish"
    bl_description = "Finish table editing: dismiss the PI table (does not affect the alignment already drawn)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.CivilAlignmentProperties.horizontal_pi_rows)

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        props.horizontal_pi_rows.clear()
        props.editing_horizontal_pi_alignment_id = 0
        return {"FINISHED"}


class ALIGN_OT_draw_horizontal_alignment(bpy.types.Operator, PolylineOperator, tool.Ifc.Operator):
    """Draw the horizontal alignment of the active IfcAlignment directly in the viewport.

    Click to place each PI (tangent-to-tangent). RMB/Enter finishes and
    immediately generates the alignment with every PI a sharp corner. If
    there are interior PIs, a marker empty is left at each one — select a
    marker and use "Apply Curve" (see the Alignments tab panel) to give it a
    circular arc, a clothoid spiral-circular/circular-spiral transition, or a
    symmetric spiral-circular-spiral, and regenerate. ESC cancels without
    creating anything.

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
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if context.scene.CivilAlignmentProperties.vertical_pi_markers:
            cls.poll_message_set("Finish or clear the vertical PI marker edit first")
            return False
        if context.scene.CivilAlignmentProperties.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the PI table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Add or select an alignment first")
            return False
        if _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the PI marker edit first")
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

        # Finish: generate the alignment (sharp corners) and, if there are
        # interior PIs, leave a marker at each for later curve editing.
        #
        # This must be checked before handle_keyboard_input()/
        # _insert_polyline_point_no_close() below: those two also react to
        # RET/NUMPAD_ENTER/RIGHTMOUSE (to confirm a typed D/A/X/Y value and
        # insert that PI), and as a side effect clear is_input_on. Checking
        # is_input_on here first means a single Enter/RMB that confirms
        # numeric input is never also treated as the finish keystroke in the
        # same event.
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

        self.handle_keyboard_input(context, event)
        _insert_polyline_point_no_close(self, context, event)

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
        if ok:
            # Always create Start/End Point markers, even with no interior PIs at all (a
            # dead-straight two-point alignment still has an endpoint to drag).
            _create_pi_markers(context, alignment.id(), raw_points)
            if radii:
                message += " — select a PI marker and click Apply Curve to add a curve"
            else:
                message += " — drag the Start/End Point markers, or click Finish"

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
        _refresh_pi_marker_visuals(context, alignment.id())

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
# Vertical Profile Window Operator
# =============================================================================


def _sync_profile_visibility_items(context, dec):
    """(Re)populate the per-vertical/per-cant visibility filters for the profile window."""
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


def _refresh_vertical_profile_view(context, alignment):
    """Recompute and redraw the docked profile view after the vertical
    alignment's geometry changed (drawn or curves applied), so its background
    grid/curve reflects the new segments instead of stale/empty data.

    A no-op if the profile view isn't currently open.
    """
    dec = alignment_decorator.VerticalProfileDecorator
    if not dec.is_installed:
        return
    dec._compute_profile(alignment)
    space = next((s for s in dec.profile_area.spaces if s.type == "VIEW_3D"), None)
    if space is not None:
        dec.fit_view(space, area_width=dec.profile_area.width, area_height=dec.profile_area.height)
    _sync_profile_visibility_items(context, dec)
    dec.tag_redraw()


_PROFILE_ROTATION_GUARD_INTERVAL = 0.05


def _profile_rotation_guard_tick():
    """bpy.app.timers callback that keeps the docked vertical profile view
    locked to front-orthographic.

    Blender's native MMB-drag orbit still runs — there's no per-area way to
    disable it without hijacking the global 3D-view keymap, which would also
    affect the main viewport — so instead this polls at a short interval and
    snaps view_rotation/view_perspective back the moment they drift away
    from the locked front-ortho orientation. Pan and zoom (view_location/
    view_distance) are left untouched. Returning None stops the timer;
    returning a float reschedules it after that many seconds.
    """
    import mathutils

    dec = alignment_decorator.VerticalProfileDecorator
    if not dec.is_installed or dec.profile_area_ptr == 0:
        return None

    area = next((a for a in bpy.context.screen.areas if a.as_pointer() == dec.profile_area_ptr), None)
    if area is None:
        # Profile area vanished outside of ALIGN_OT_show_vertical_profile
        # (e.g. dragged/merged away) — stop polling rather than leak a timer.
        return None

    space = next((s for s in area.spaces if s.type == "VIEW_3D"), None)
    if space is None:
        return _PROFILE_ROTATION_GUARD_INTERVAL
    rv3d = space.region_3d

    locked_rotation = mathutils.Quaternion((0.7071068, 0.7071068, 0.0, 0.0))
    changed = False
    if rv3d.view_perspective != "ORTHO":
        rv3d.view_perspective = "ORTHO"
        changed = True
    if rv3d.view_rotation.rotation_difference(locked_rotation).angle > 1e-4:
        rv3d.view_rotation = locked_rotation
        changed = True
    if changed:
        area.tag_redraw()

    return _PROFILE_ROTATION_GUARD_INTERVAL


def _start_profile_rotation_guard():
    if not bpy.app.timers.is_registered(_profile_rotation_guard_tick):
        bpy.app.timers.register(_profile_rotation_guard_tick, first_interval=_PROFILE_ROTATION_GUARD_INTERVAL)


def _open_vertical_profile(context, alignment):
    """Open (or refresh) the docked vertical profile view for ``alignment``.

    Shared by ALIGN_OT_show_vertical_profile (toggle button) and
    ALIGN_OT_draw_vertical_alignment (which needs the profile view open
    before it can start placing PIs in it). Returns the profile
    ``bpy.types.Area``, or None if it couldn't be opened/refreshed.
    """
    import mathutils

    dec = alignment_decorator.VerticalProfileDecorator

    if dec.is_installed:
        # Already open — just refresh the data (the active alignment may
        # have changed) and re-fit the view.
        dec._compute_profile(alignment)
        space = next((s for s in dec.profile_area.spaces if s.type == "VIEW_3D"), None)
        if space is not None:
            dec.fit_view(space, area_width=dec.profile_area.width, area_height=dec.profile_area.height)
        _sync_profile_visibility_items(context, dec)
        dec.profile_area.tag_redraw()
        return dec.profile_area

    dec._compute_profile(alignment)

    # Find the 3D view area and its WINDOW region for the split call
    area = context.area
    if area is None or area.type != "VIEW_3D":
        # Button pressed from a non-3D area — find the first 3D view
        area = next((a for a in context.screen.areas if a.type == "VIEW_3D"), None)
        if area is None:
            return None
    win_region = next((r for r in area.regions if r.type == "WINDOW"), None)
    if win_region is None:
        return None

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
        return None

    # Blender's area_split places the NEW area above the original area.
    # The original area stays at the bottom — use it as the profile view.
    profile_area = area

    space = next((s for s in profile_area.spaces if s.type == "VIEW_3D"), None)
    if space is None:
        return None

    # Front orthographic: 90° rotation around X so Z is elevation, X is distance
    space.region_3d.view_perspective = "ORTHO"
    space.region_3d.view_rotation = mathutils.Quaternion((0.7071068, 0.7071068, 0.0, 0.0))

    dec.fit_view(space, area_width=profile_area.width, area_height=profile_area.height)

    space.overlay.show_floor = False
    space.overlay.show_axis_x = False
    space.overlay.show_axis_y = False
    space.overlay.show_axis_z = False
    # Keep the corner navigate gizmo (pan hand / zoom magnifier) so panning here
    # is discoverable the same way it is in the main viewport, but drop the
    # tool gizmo inherited from the split-off viewport (e.g. an active Move/
    # Rotate tool) since there's nothing meaningful to transform here.
    space.show_gizmo = True
    space.show_gizmo_navigate = True
    space.show_gizmo_tool = False

    # Hide tool shelf and N-panel so they don't obscure the profile extents.
    # Set directly on the space (absolute, not a toggle) so this works reliably
    # regardless of the panel's current visibility state.
    space.show_region_toolbar = False
    space.show_region_ui = False

    _sync_profile_visibility_items(context, dec)

    dec.install(context, profile_area)
    profile_area.tag_redraw()
    _start_profile_rotation_guard()

    return profile_area


class ALIGN_OT_show_vertical_profile(Operator):
    """Toggle the docked vertical profile view below the active 3D viewport"""

    bl_idname = "align.show_vertical_profile"
    bl_label = "Toggle Vertical Profile"
    bl_description = (
        "Dock a 2D vertical profile view below this viewport (click again to close). "
        "Elevation is exaggerated by the VE factor. Mouse wheel to zoom, Shift+wheel to pan "
        "left/right, Home to reset the view."
    )
    bl_options = {"REGISTER"}

    def execute(self, context):
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

        profile_area = _open_vertical_profile(context, alignment)
        if profile_area is None:
            self.report({"WARNING"}, "Could not open the vertical profile view")
            return {"CANCELLED"}

        return {"FINISHED"}


class ALIGN_OT_pan_vertical_profile(Operator):
    """Pan the docked vertical profile view left/right (Shift+wheel)"""

    bl_idname = "align.pan_vertical_profile"
    bl_label = "Pan Vertical Profile"
    bl_description = "Pan the vertical profile view left/right"
    bl_options = {"INTERNAL"}

    # -1 pans toward lower stations (left), 1 toward higher stations (right).
    direction: IntProperty(default=1)

    if TYPE_CHECKING:
        direction: int

    @classmethod
    def poll(cls, context):
        dec = alignment_decorator.VerticalProfileDecorator
        return (
            dec.is_installed
            and context.area is not None
            and context.area.as_pointer() == dec.profile_area_ptr
        )

    def execute(self, context):
        dec = alignment_decorator.VerticalProfileDecorator
        region = context.region
        rv3d = context.region_data
        if region is None or rv3d is None:
            return {"CANCELLED"}

        # Measure the currently visible station span from the screen corners
        # (same technique the profile decorator uses to frame its grid), so the
        # pan step scales naturally with the current zoom level.
        ref = (rv3d.view_location.x, 0.0, rv3d.view_location.z)
        bottom_left = region_2d_to_location_3d(region, rv3d, (0, 0), ref)
        top_right = region_2d_to_location_3d(region, rv3d, (region.width, region.height), ref)
        if bottom_left is None or top_right is None:
            return {"CANCELLED"}
        visible_span = top_right.x - bottom_left.x

        new_x = rv3d.view_location.x + visible_span * 0.2 * self.direction
        # Don't let the view center pan past the alignment's own station range.
        new_x = max(dec.dist_min, min(dec.dist_max, new_x))
        rv3d.view_location = mathutils.Vector((new_x, rv3d.view_location.y, rv3d.view_location.z))
        context.area.tag_redraw()
        return {"FINISHED"}


class ALIGN_OT_reset_vertical_profile_view(Operator):
    """Reset the docked vertical profile view to fit the full station range (Home)"""

    bl_idname = "align.reset_vertical_profile_view"
    bl_label = "Reset Vertical Profile View"
    bl_description = "Reset the vertical profile view to fit the full station range"
    bl_options = {"INTERNAL"}

    @classmethod
    def poll(cls, context):
        dec = alignment_decorator.VerticalProfileDecorator
        return (
            dec.is_installed
            and context.area is not None
            and context.area.as_pointer() == dec.profile_area_ptr
        )

    def execute(self, context):
        dec = alignment_decorator.VerticalProfileDecorator
        space = context.space_data
        if space is None or space.type != "VIEW_3D":
            return {"CANCELLED"}
        dec.fit_view(space, area_width=context.area.width, area_height=context.area.height)
        context.area.tag_redraw()
        return {"FINISHED"}


# =============================================================================
# Vertical Alignment Drawing (draw-by-PI in the profile view)
# =============================================================================


def _generate_vertical_alignment_segments(context, alignment, vpoints, lengths, v_layout=None):
    """Build vertical alignment segments from PI points and per-PI curve lengths.

    Mirrors _generate_alignment_segments() for the vertical layout. ``vpoints``
    are (distance_along, elevation) pairs already in project length units —
    unlike the horizontal case, no unit-scale/georeferencing conversion is
    needed, because the profile view's world coordinates already are raw
    project-unit distance/elevation values (see
    VerticalProfileDecorator.screen_to_data). ``lengths`` has exactly
    len(vpoints) - 2 entries, one per interior PI (0.0 = sharp grade break).

    ``alignment`` is always the top-level alignment — it's only used for the
    representation/Blender-object refresh below, which are keyed to the
    top-level alignment regardless of which sibling vertical changed (IFC CT
    4.1.4.4.1.2). ``v_layout``, when given, is the specific
    IfcAlignmentVertical to regenerate (resolved by the caller, e.g. from
    props.editing_vertical_pi_layout_id) instead of the one/only vertical
    ``get_vertical_layout(alignment)`` would find directly on ``alignment``
    itself — which is nothing once a second sibling vertical exists, since
    add_vertical_layout() moves every vertical onto its own child alignment
    at that point.

    Returns (ok, message, v_layout) — callers that don't already know which
    vertical they're targeting (e.g. drawing a brand new one) can use the
    returned entity to remember it for a subsequent apply.
    """
    ifc = tool.Ifc.get()

    if v_layout is None:
        v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        if v_layout is None:
            v_layout = ifcopenshell.api.alignment.add_vertical_layout(ifc, alignment)

    tool.Alignment.clear_layout_segments(v_layout)
    tool.Alignment.safe_layout_vertical_by_pi_method(ifc, v_layout, vpoints, lengths)
    ifcopenshell.api.alignment.create_representation(ifc, alignment)

    tool.Alignment.refresh_alignment_representation_object(alignment)

    n_curved = sum(1 for l in lengths if l)
    return True, f"Drew vertical alignment with {len(vpoints)} PIs ({n_curved} curved)", v_layout


def _sync_vertical_pi_markers(context, vpoints):
    """(Re)populate props.vertical_pi_markers from the interior PIs of ``vpoints``.

    Start/end are excluded — they're derived from the alignment's own
    segments when applying curves (get_vertical_alignment_start_end_points),
    same convention as the horizontal PI markers.
    """
    props = context.scene.CivilAlignmentProperties
    props.vertical_pi_markers.clear()
    for dist_along, elevation in vpoints[1:-1]:
        item = props.vertical_pi_markers.add()
        item.dist_along = dist_along
        item.elevation = elevation
        item.curve_type = "TANGENT"
        item.curve_length = 100.0


def _tangent_grade_intersection(dp_a, dp_b):
    """Where two CONSTANTGRADIENT segments' own grade lines cross, as (dist_along, elevation).

    Mirrors _tangent_line_intersection for the vertical (1D) case. Returns
    None if the two grades are equal (no PI).
    """
    d1, d2 = dp_a.StartGradient, dp_b.StartGradient
    if abs(d1 - d2) < 1e-10:
        return None
    t = (dp_b.StartHeight - dp_a.StartHeight - d2 * dp_b.StartDistAlong + d1 * dp_a.StartDistAlong) / (d1 - d2)
    elevation = dp_a.StartHeight + d1 * (t - dp_a.StartDistAlong)
    return t, elevation


def _reconstruct_vertical_pis(v_layout):
    """Classify every interior PI of v_layout's current real segments.

    Mirrors _reconstruct_horizontal_pis for the vertical case: only a sharp
    grade break between two CONSTANTGRADIENTs (TANGENT) or a CONSTANTGRADIENT
    -PARABOLICARC-CONSTANTGRADIENT run (PARABOLIC) is recognized -- the two
    states VerticalPIMarker.curve_type already has. Returns (specs, skipped)
    exactly like _reconstruct_horizontal_pis.

    A lone CIRCULARARC is a real, valid IfcAlignmentVerticalSegmentTypeEnum
    value, but layout_vertical_alignment_by_pi_method (what "Apply Vertical
    Curves" regenerates through) only ever produces PARABOLICARC/
    CONSTANTGRADIENT -- there's no solver support for it yet. So it's called
    out with its own skip reason rather than lumped in as generically
    "unsupported", but still skipped (no marker), since creating one anyway
    would let a later Apply silently discard it.
    """
    segments = tool.Alignment.get_real_layout_segments(v_layout)
    grade_indices = [i for i, s in enumerate(segments) if s.DesignParameters.PredefinedType == "CONSTANTGRADIENT"]

    specs = []
    skipped = []
    if len(grade_indices) < 2:
        return specs, [(s, "no bounding grade") for s in segments]

    for s in segments[: grade_indices[0]]:
        skipped.append((s, "before the first grade"))
    for s in segments[grade_indices[-1] + 1 :]:
        skipped.append((s, "after the last grade"))

    for k in range(len(grade_indices) - 1):
        a_idx, b_idx = grade_indices[k], grade_indices[k + 1]
        grade_a, grade_b = segments[a_idx], segments[b_idx]
        between = segments[a_idx + 1 : b_idx]
        types = [s.DesignParameters.PredefinedType for s in between]

        if types == []:
            curve_type, curve_seg = "TANGENT", None
        elif types == ["PARABOLICARC"]:
            curve_type, curve_seg = "PARABOLIC", between[0]
        elif types == ["CIRCULARARC"]:
            skipped.append((between[0], "circular vertical curve, not yet editable here"))
            continue
        else:
            skipped.extend((s, "unsupported curve type") for s in between)
            continue

        pi = _tangent_grade_intersection(grade_a.DesignParameters, grade_b.DesignParameters)
        if pi is None:
            skipped.extend((s, "equal grades") for s in (between or [grade_a, grade_b]))
            continue

        specs.append(
            {
                "dist_along": pi[0],
                "elevation": pi[1],
                "curve_type": curve_type,
                "curve_length": (curve_seg.DesignParameters.HorizontalLength or 0.0) if curve_seg else 0.0,
            }
        )

    return specs, skipped


class ALIGN_OT_load_vertical_pis(Operator, tool.Ifc.Operator):
    """Populate the vertical PI list from this alignment's current real segments.

    Lets a previously-drawn (and saved) or IFC-imported vertical alignment be
    tuned the same way a freshly-drawn one is: pick a row, adjust its curve
    type/length, click "Apply Vertical Curves".
    """

    bl_idname = "align.load_vertical_pis"
    bl_label = "Edit PIs"
    bl_description = (
        "Populate the vertical PI list from this alignment's current segments, pre-filled "
        "with their existing curve type/length, so they can be adjusted and re-applied "
        "without redrawing from scratch"
    )
    bl_options = {"REGISTER", "UNDO"}

    # Explicit target for a specific sibling vertical (IFC CT 4.1.4.4.1.2 — the
    # per-vertical button in ALIGN_PT_alignment_segments passes this). 0 falls
    # back to get_active_alignment()'s own direct vertical, the common
    # single-vertical case.
    layout_id: IntProperty(default=0, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if alignment and _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the horizontal PI marker edit first")
            return False
        if context.scene.CivilAlignmentProperties.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the horizontal PI table edit first")
            return False
        return True

    def _execute(self, context):
        ifc = tool.Ifc.get()

        if self.layout_id:
            v_layout = ifc.by_id(self.layout_id)
        else:
            alignment = tool.Alignment.get_active_alignment()
            if not alignment:
                self.report({"ERROR"}, "Select an alignment first")
                return {"CANCELLED"}
            v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)

        if not v_layout or not tool.Alignment.get_real_layout_segments(v_layout):
            self.report({"ERROR"}, "This alignment has no vertical segments yet")
            return {"CANCELLED"}

        specs, skipped = _reconstruct_vertical_pis(v_layout)
        if skipped:
            details = "; ".join(f"{s.DesignParameters.PredefinedType} ({reason})" for s, reason in skipped[:5])
            more = f", and {len(skipped) - 5} more" if len(skipped) > 5 else ""
            self.report(
                {"ERROR"},
                f"Can't load PI list: {len(skipped)} segment(s) couldn't be classified: "
                f"{details}{more}.",
            )
            return {"CANCELLED"}

        props = context.scene.CivilAlignmentProperties
        props.vertical_pi_markers.clear()
        for spec in specs:
            item = props.vertical_pi_markers.add()
            item.dist_along = spec["dist_along"]
            item.elevation = spec["elevation"]
            item.curve_type = spec["curve_type"]
            item.curve_length = spec["curve_length"] or 100.0
        props.editing_vertical_pi_layout_id = v_layout.id()

        self.report({"INFO"}, f"Loaded {len(specs)} PI(s)")
        return {"FINISHED"}


class ALIGN_OT_draw_vertical_alignment(Operator, tool.Ifc.Operator):
    """Draw the vertical alignment of the active IfcAlignment by PI, in the profile view.

    Opens (or reuses) the docked vertical profile view, then click to place
    each PI (grade break to grade break). A vertical alignment must span
    exactly the horizontal's own distance-along range, so this is enforced
    as you draw rather than left to be fixed up afterward: the first PI is
    anchored to the start station (only its elevation follows the mouse),
    and moving past the last station locks distance-along there too, so
    overshooting the end and clicking places the final PI exactly on it.
    PIs are also kept left-to-right — the mouse can't drag a candidate PI
    behind the previous one.

    RMB/Enter finishes and generates the vertical alignment with every PI a
    sharp grade break; interior PIs are then listed in the panel below — set
    a curve length and click Apply Vertical Curves to regenerate with
    parabolic curves at those PIs. ESC cancels without creating anything.
    Backspace removes the last PI.
    """

    bl_idname = "align.draw_vertical_alignment"
    bl_label = "Draw Vertical Alignment"
    bl_description = (
        "Draw the vertical alignment by PI in the profile view, spanning the "
        "horizontal's full station range. Click to place PIs, RMB/Enter to "
        "generate it. ESC cancels."
    )
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        props = context.scene.CivilAlignmentProperties
        if props.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if props.vertical_pi_markers:
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Add or select an alignment first")
            return False
        if _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the horizontal PI marker edit first")
            return False
        if props.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the horizontal PI table edit first")
            return False
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        has_real_segments = h_layout and any(
            not tool.Alignment.is_zero_length_segment(s)
            for s in ifcopenshell.api.alignment.get_layout_segments(h_layout)
        )
        if not has_real_segments:
            cls.poll_message_set("Draw the horizontal alignment first")
            return False
        return True

    def __init__(self, *args, **kwargs):
        Operator.__init__(self, *args, **kwargs)
        self._points: list = []  # [(dist_along, elevation), ...] in project units
        self._area_ptr = 0
        self._alignment_id = 0

    def invoke(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="INVOKE")

    def _invoke(self, context, event):
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            self.report({"ERROR"}, "Add or select an alignment first")
            return {"CANCELLED"}

        profile_area = _open_vertical_profile(context, alignment)
        if profile_area is None:
            self.report({"ERROR"}, "Could not open the vertical profile view")
            return {"CANCELLED"}

        self._alignment_id = alignment.id()
        self._points = []
        self._area_ptr = profile_area.as_pointer()

        alignment_decorator.VerticalDrawDecorator.install(context, self._points)
        context.workspace.status_text_set(
            text="Click: add PI    Backspace: remove last    Enter/RMB: finish    Esc: cancel"
        )
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        return IfcStore.execute_ifc_operator(self, context, event, method="MODAL")

    def _locate_profile_view(self, context):
        """Find the profile area's WINDOW region and RegionView3D, fresh on
        every call, by matching the stable pointer captured at invoke time.

        During a modal operator's event handling, context.area/region/
        region_data do NOT reliably track wherever the mouse currently is
        once it strays outside the area the operator was originally invoked
        from — unlike draw handlers, which Blender calls per-area with
        correct context (that's why the background grid draws fine here even
        when clicks don't land). So this looks the area up explicitly via
        context.screen.areas instead of trusting ambient context, and
        event.mouse_x/mouse_y (absolute, always correct) get used in place
        of event.mouse_region_x/y (relative to whatever context.region
        happens to be, which is exactly the unreliable part).

        Returns (area, region, rv3d), or None if the profile area is gone.
        """
        for area in context.screen.areas:
            if area.as_pointer() != self._area_ptr:
                continue
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            space = next((s for s in area.spaces if s.type == "VIEW_3D"), None)
            if region is None or space is None:
                return None
            return area, region, space.region_3d
        return None

    def _constrain_point(self, dist_along: float, elevation: float) -> tuple:
        """Clamp a candidate PI to the horizontal alignment's station range
        and enforce left-to-right PI ordering.

        The vertical alignment must span exactly the horizontal's own
        distance-along range, so the very first PI is always anchored to its
        start (dist_min) regardless of mouse position — only elevation is
        free for it. Every later PI is free between the previous PI's
        distance-along and the horizontal's end (dist_max); moving the mouse
        past dist_max clamps distance-along there, so overshooting the end
        and clicking places the final PI exactly at the last station.
        """
        dec = alignment_decorator.VerticalProfileDecorator
        if not self._points:
            return dec.dist_min, elevation
        lower = self._points[-1][0]
        upper = max(dec.dist_max, lower)
        return min(max(dist_along, lower), upper), elevation

    def _modal(self, context, event):
        found = self._locate_profile_view(context)
        if found is None:
            # The profile view got closed out from under us.
            context.workspace.status_text_set(text=None)
            alignment_decorator.VerticalDrawDecorator.uninstall()
            self.report({"WARNING"}, "Vertical profile view was closed")
            return {"CANCELLED"}
        area, region, rv3d = found

        # event.mouse_x/y are absolute (window) coordinates — always correct,
        # unlike mouse_region_x/y which is relative to context.region.
        mx, my = event.mouse_x, event.mouse_y
        over_profile = area.x <= mx < area.x + area.width and area.y <= my < area.y + area.height

        if event.type == "MOUSEMOVE":
            point = None
            if over_profile:
                raw = alignment_decorator.VerticalProfileDecorator.screen_to_data(
                    region, rv3d, mx - region.x, my - region.y
                )
                if raw is not None:
                    point = self._constrain_point(*raw)
            alignment_decorator.VerticalDrawDecorator.update_mouse(point)
            return {"PASS_THROUGH"}

        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            return {"PASS_THROUGH"}

        if event.type == "LEFTMOUSE" and event.value == "RELEASE":
            if not over_profile:
                return {"PASS_THROUGH"}
            raw = alignment_decorator.VerticalProfileDecorator.screen_to_data(
                region, rv3d, mx - region.x, my - region.y
            )
            if raw is not None:
                self._points.append(self._constrain_point(*raw))
                alignment_decorator.VerticalDrawDecorator.tag_redraw()
            return {"RUNNING_MODAL"}

        if event.type == "BACK_SPACE" and event.value == "RELEASE":
            if self._points:
                self._points.pop()
                alignment_decorator.VerticalDrawDecorator.tag_redraw()
            return {"RUNNING_MODAL"}

        if event.value == "RELEASE" and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}:
            context.workspace.status_text_set(text=None)
            alignment_decorator.VerticalDrawDecorator.uninstall()
            self._finish(context)
            return {"FINISHED"}

        if event.type == "ESC" and event.value == "RELEASE":
            context.workspace.status_text_set(text=None)
            alignment_decorator.VerticalDrawDecorator.uninstall()
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def _finish(self, context):
        if len(self._points) < 2:
            self.report({"WARNING"}, "Need at least 2 PIs to draw a vertical alignment")
            return

        try:
            alignment = tool.Ifc.get().by_id(self._alignment_id)
        except RuntimeError:
            self.report({"ERROR"}, "Alignment no longer exists")
            return

        # Vertical PIs must be strictly ordered by distance-along — a profile
        # is a function of distance-along, so out-of-order clicks (easy to do
        # by accident) would otherwise fold the curve back on itself.
        vpoints = sorted(self._points, key=lambda p: p[0])
        lengths = [0.0] * (len(vpoints) - 2)

        ok, message, v_layout = _generate_vertical_alignment_segments(context, alignment, vpoints, lengths)
        if ok:
            _sync_vertical_pi_markers(context, vpoints)
            # Remember which sibling vertical this is so a follow-up "Apply
            # Vertical Curves" targets it too, not whatever get_active_alignment()
            # would resolve to (nothing, once a second vertical exists — see
            # _generate_vertical_alignment_segments).
            context.scene.CivilAlignmentProperties.editing_vertical_pi_layout_id = v_layout.id()
            _refresh_vertical_profile_view(context, alignment)
        self.report({"INFO"} if ok else {"WARNING"}, message)


class ALIGN_OT_apply_vertical_pi_curve(Operator, tool.Ifc.Operator):
    """Regenerate the vertical alignment using the PI list's curve settings"""

    bl_idname = "align.apply_vertical_pi_curve"
    bl_label = "Apply Vertical Curves"
    bl_description = "Regenerate the vertical alignment using each PI's curve type/length"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if not context.scene.CivilAlignmentProperties.vertical_pi_markers:
            cls.poll_message_set("Draw a vertical alignment first")
            return False
        if not tool.Alignment.get_active_alignment():
            cls.poll_message_set("Select the alignment first")
            return False
        return True

    def _execute(self, context):
        props = context.scene.CivilAlignmentProperties
        alignment = tool.Alignment.get_active_alignment()

        # editing_vertical_pi_layout_id, when set, names the specific sibling
        # vertical vertical_pi_markers came from (see its own comment) — resolve
        # start/end from the alignment that actually owns it, not the top-level
        # one, which has no vertical of its own once a second sibling exists.
        v_layout = None
        if props.editing_vertical_pi_layout_id:
            try:
                v_layout = tool.Ifc.get().by_id(props.editing_vertical_pi_layout_id)
            except RuntimeError:
                v_layout = None

        try:
            if v_layout is not None:
                owning_alignment = ifcopenshell.api.alignment.get_alignment(v_layout)
                start, end = tool.Alignment.get_vertical_alignment_start_end_points(owning_alignment)
            else:
                start, end = tool.Alignment.get_vertical_alignment_start_end_points(alignment)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        markers = list(props.vertical_pi_markers)
        vpoints = [start] + [(m.dist_along, m.elevation) for m in markers] + [end]
        lengths = [m.curve_length if m.curve_type == "PARABOLIC" else 0.0 for m in markers]

        ok, message, v_layout = _generate_vertical_alignment_segments(
            context, alignment, vpoints, lengths, v_layout=v_layout
        )
        if ok:
            props.editing_vertical_pi_layout_id = v_layout.id()
            _refresh_vertical_profile_view(context, alignment)
        self.report({"INFO"} if ok else {"WARNING"}, message)
        return {"FINISHED"}


class ALIGN_OT_finish_vertical_pi_editing(Operator):
    """Dismiss the vertical PI list (rows are staging data, not IFC -- whatever
    was last applied via Apply Vertical Curves is already saved to the
    alignment regardless of whether the list stays open). Mirrors
    ALIGN_OT_finish_pi_editing / ALIGN_OT_finish_horizontal_pi_table.
    """

    bl_idname = "align.finish_vertical_pi_editing"
    bl_label = "Finish"
    bl_description = "Finish PI editing: dismiss the vertical PI list (does not affect the alignment already drawn)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.CivilAlignmentProperties.vertical_pi_markers)

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        props.vertical_pi_markers.clear()
        props.editing_vertical_pi_layout_id = 0
        return {"FINISHED"}


# =============================================================================
# Segment Table Editing ("stage edits, then Apply")
# =============================================================================

_SEGMENT_KIND_ITEMS = [
    ("HORIZONTAL", "Horizontal", ""),
    ("VERTICAL", "Vertical", ""),
    ("CANT", "Cant", ""),
]
_SEGMENT_ROW_FIELD = {
    "HORIZONTAL": "h_segment_rows",
    "VERTICAL": "v_segment_rows",
    "CANT": "cant_segment_rows",
}
_SEGMENT_ROW_ACTIVE_INDEX_FIELD = {
    "HORIZONTAL": "active_h_segment_row_index",
    "VERTICAL": "active_v_segment_row_index",
    "CANT": "active_cant_segment_row_index",
}


class ALIGN_OT_add_segment_row(Operator):
    """Add a new segment row to the currently-staged edit table"""

    bl_idname = "align.add_segment_row"
    bl_label = "Add Segment"
    bl_description = "Insert a new segment after the selected row"
    bl_options = {"REGISTER", "UNDO"}

    kind: EnumProperty(items=_SEGMENT_KIND_ITEMS, options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        rows = getattr(props, _SEGMENT_ROW_FIELD[self.kind])
        index_attr = _SEGMENT_ROW_ACTIVE_INDEX_FIELD[self.kind]
        active_index = getattr(props, index_attr)

        insert_at = active_index + 1 if len(rows) else 0
        prev_row = rows[active_index] if 0 <= active_index < len(rows) else None

        rows.add()
        rows.move(len(rows) - 1, insert_at)
        new_row = rows[insert_at]

        if self.kind == "VERTICAL":
            new_row.predefined_type = "CONSTANTGRADIENT"
            new_row.h_length = 10.0
            seed = prev_row.end_gradient if prev_row else 0.0
            new_row.start_gradient = seed
            new_row.end_gradient = seed
        elif self.kind == "CANT":
            new_row.predefined_type = "CONSTANTCANT"
            new_row.h_length = 10.0
            seed_left = prev_row.end_cant_left if prev_row else 0.0
            seed_right = prev_row.end_cant_right if prev_row else 0.0
            new_row.start_cant_left = seed_left
            new_row.start_cant_right = seed_right
            new_row.end_cant_left = seed_left
            new_row.end_cant_right = seed_right
        else:
            new_row.predefined_type = "LINE"
            new_row.length = 10.0

        setattr(props, index_attr, insert_at)
        return {"FINISHED"}


class ALIGN_OT_remove_segment_row(Operator):
    """Remove the selected row from the currently-staged edit table"""

    bl_idname = "align.remove_segment_row"
    bl_label = "Remove Segment"
    bl_description = "Remove the selected row"
    bl_options = {"REGISTER", "UNDO"}

    kind: EnumProperty(items=_SEGMENT_KIND_ITEMS, options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        rows = getattr(props, _SEGMENT_ROW_FIELD[self.kind])
        index_attr = _SEGMENT_ROW_ACTIVE_INDEX_FIELD[self.kind]
        active_index = getattr(props, index_attr)
        if not (0 <= active_index < len(rows)):
            return {"CANCELLED"}
        rows.remove(active_index)
        setattr(props, index_attr, max(0, min(active_index, len(rows) - 1)))
        return {"FINISHED"}


class ALIGN_OT_move_segment_row(Operator):
    """Reorder the selected row in the currently-staged edit table"""

    bl_idname = "align.move_segment_row"
    bl_label = "Move Segment"
    bl_description = "Move the selected row up or down"
    bl_options = {"REGISTER", "UNDO"}

    kind: EnumProperty(items=_SEGMENT_KIND_ITEMS, options={"HIDDEN"})
    direction: EnumProperty(items=[("UP", "Up", ""), ("DOWN", "Down", "")], options={"HIDDEN"})

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        rows = getattr(props, _SEGMENT_ROW_FIELD[self.kind])
        index_attr = _SEGMENT_ROW_ACTIVE_INDEX_FIELD[self.kind]
        active_index = getattr(props, index_attr)
        target = active_index - 1 if self.direction == "UP" else active_index + 1
        if not (0 <= target < len(rows)):
            return {"CANCELLED"}
        rows.move(active_index, target)
        setattr(props, index_attr, target)
        return {"FINISHED"}


class ALIGN_OT_enable_editing_h_segments(Operator):
    """Stage a horizontal layout's segments for table editing"""

    bl_idname = "align.enable_editing_h_segments"
    bl_label = "Edit Horizontal Segments"
    bl_description = "Edit this layout's segments as a table (add/remove/reorder/edit, then Apply)"
    bl_options = {"REGISTER", "UNDO"}

    layout_id: IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = context.scene.CivilAlignmentProperties
        if props.editing_segment_kind not in ("NONE", "HORIZONTAL"):
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if props.vertical_pi_markers:
            cls.poll_message_set("Finish or clear the vertical PI marker edit first")
            return False
        if props.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the PI table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if alignment and _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        return True

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        h_layout = ifc_file.by_id(self.layout_id)

        # IfcAlignmentHorizontalSegment's length/radius fields are in the
        # project's own length unit (e.g. feet), but a Blender FloatProperty
        # tagged unit="LENGTH" always treats its raw stored value as being in
        # Blender's internal unit (metres, scale_length=1.0) and converts
        # from there for display -- so the IFC value must be scaled into
        # that space first, or a foot-based project shows numbers inflated
        # by ~3.28x (1/0.3048). Reversed on write-back in apply_h_segments.
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")

        props.h_segment_rows.clear()
        for seg in tool.Alignment.get_real_layout_segments(h_layout):
            dp = seg.DesignParameters
            row = props.h_segment_rows.add()
            row.segment_id = seg.id()
            seg_type = dp.PredefinedType
            if seg_type in prop.SUPPORTED_HORIZONTAL_TYPES:
                row.predefined_type = seg_type
            else:
                row.predefined_type = "UNSUPPORTED"
                row.original_predefined_type = seg_type or "?"
            row.length = abs(dp.SegmentLength) * length_scale
            row.start_radius = (dp.StartRadiusOfCurvature or 0.0) * length_scale
            row.end_radius = (dp.EndRadiusOfCurvature or 0.0) * length_scale

        props.active_h_segment_row_index = 0
        props.editing_segment_kind = "HORIZONTAL"
        props.editing_layout_id = self.layout_id

        # The read-only "#" toggle disappears once the table replaces it, so
        # clear any stale highlight now -- nothing else could turn it off
        # while the table is showing.
        props.selected_h_segment_id = 0
        alignment_decorator.AlignmentSegmentDecorator.uninstall()

        tool.Blender.update_viewport()
        return {"FINISHED"}


class ALIGN_OT_disable_editing_h_segments(Operator):
    """Discard the staged horizontal segment edits without touching IFC"""

    bl_idname = "align.disable_editing_h_segments"
    bl_label = "Cancel"
    bl_description = "Discard these changes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        props.h_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0
        return {"FINISHED"}


class ALIGN_OT_apply_h_segments(Operator, tool.Ifc.Operator):
    """Rebuild a horizontal layout from the staged segment table"""

    bl_idname = "align.apply_h_segments"
    bl_label = "Apply"
    bl_description = "Rebuild this layout's segments from the table above"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        h_layout = ifc_file.by_id(props.editing_layout_id)
        if h_layout is None:
            self.report({"ERROR"}, "The layout being edited no longer exists")
            props.h_segment_rows.clear()
            props.editing_segment_kind = "NONE"
            props.editing_layout_id = 0
            return {"CANCELLED"}

        rows = props.h_segment_rows
        errors = tool.Alignment.validate_horizontal_segment_rows(rows)
        if errors:
            self.report({"ERROR"}, "; ".join(errors))
            return {"CANCELLED"}

        alignment = tool.Alignment._get_top_level_alignment(ifcopenshell.api.alignment.get_alignment(h_layout))

        # VIENNESEBEND's own geometry depends on the cant segment at the same
        # station (ifcopenshell.api.alignment.create()'s own docstring: "The
        # horizontal segment geometric representation will fail if the cant
        # segment is not defined") -- catch that here with a clear message
        # rather than letting create_layout_segment() below blow up on it.
        if any(row.predefined_type == "VIENNESEBEND" for row in rows):
            cant_layout = ifcopenshell.api.alignment.get_cant_layout(alignment)
            if not cant_layout or not tool.Alignment.get_real_layout_segments(cant_layout):
                self.report(
                    {"ERROR"},
                    "Viennese Bend needs a cant layout first -- use Generate Cant Layout, "
                    "then retry Apply.",
                )
                return {"CANCELLED"}

        # The overall start point/direction is preserved as-is (moving it is
        # a separate feature, REQUIREMENTS §4) -- read it straight off the
        # current first real segment before wiping anything.
        existing = tool.Alignment.get_real_layout_segments(h_layout)
        if existing:
            first_dp = existing[0].DesignParameters
            x, y = first_dp.StartPoint.Coordinates
            direction = first_dp.StartDirection
        else:
            x, y, direction = 0.0, 0.0, 0.0

        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")
        angle_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "PLANEANGLEUNIT")

        ifcopenshell.api.alignment.clear_layout_segments(ifc_file, h_layout)

        for row in rows:
            # row.length/start_radius/end_radius are in Blender's internal
            # unit="LENGTH" space (metres) -- see enable_editing_h_segments'
            # own comment -- so they're converted back to the project's
            # length unit here before going into IFC.
            row_length = row.length / length_scale
            if row.predefined_type == "LINE":
                start_radius, end_radius = 0.0, 0.0
            elif row.predefined_type == "CIRCULARARC":
                start_radius, end_radius = row.start_radius / length_scale, row.start_radius / length_scale
            else:  # spiral family (CLOTHOID/CUBIC/HELMERTCURVE/BLOSSCURVE/COSINECURVE/SINECURVE)
                start_radius, end_radius = row.start_radius / length_scale, row.end_radius / length_scale

            design_parameters = ifc_file.createIfcAlignmentHorizontalSegment(
                StartTag=None,
                EndTag=None,
                StartPoint=ifc_file.createIfcCartesianPoint((x, y)),
                StartDirection=direction,
                StartRadiusOfCurvature=start_radius,
                EndRadiusOfCurvature=end_radius,
                SegmentLength=row_length,
                GravityCenterLineHeight=None,
                PredefinedType=row.predefined_type,
            )
            placement = ifcopenshell.api.alignment.create_layout_segment(ifc_file, h_layout, design_parameters)
            x = float(placement[0, 3]) / length_scale
            y = float(placement[1, 3]) / length_scale
            # atan2, not atan(Rdy/Rdx) (what ifcopenshell's own internal
            # _update_zero_length_segment_placement uses) -- atan can't tell
            # a segment pointing north from one pointing south when Rdx≈0.
            direction = math.atan2(float(placement[1, 0]), float(placement[0, 0])) / angle_scale

        ifcopenshell.api.alignment.create_representation(ifc_file, alignment)
        tool.Alignment.refresh_alignment_representation_object(alignment)
        _refresh_vertical_profile_view(context, alignment)

        # Keep an already-generated cant layout's curve types matching the
        # horizontal's own (per the user, 2026-09-16: "change BLOSS to COSINE
        # in horizontal makes the same change in cant layout") -- a no-op if
        # there's no cant layout yet, or if the segment counts have drifted
        # apart (e.g. this Apply added/removed rows on the horizontal side
        # only) -- see sync_cant_segment_types.
        tool.Alignment.sync_cant_segment_types(alignment)

        # Every segment id in this layout just changed.
        props.selected_h_segment_id = 0
        alignment_decorator.AlignmentSegmentDecorator.uninstall()

        n = len(rows)
        props.h_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0

        tool.Blender.update_viewport()
        _tag_all_areas_redraw(context)
        self.report({"INFO"}, f"Rebuilt {n} horizontal segment(s)")
        return {"FINISHED"}


class ALIGN_OT_enable_editing_v_segments(Operator):
    """Stage a vertical layout's segments for table editing"""

    bl_idname = "align.enable_editing_v_segments"
    bl_label = "Edit Vertical Segments"
    bl_description = "Edit this layout's segments as a table (add/remove/reorder/edit, then Apply)"
    bl_options = {"REGISTER", "UNDO"}

    layout_id: IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = context.scene.CivilAlignmentProperties
        if props.editing_segment_kind not in ("NONE", "VERTICAL"):
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if props.vertical_pi_markers:
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if alignment and _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the horizontal PI marker edit first")
            return False
        if props.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the horizontal PI table edit first")
            return False
        return True

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        v_layout = ifc_file.by_id(self.layout_id)

        # See enable_editing_h_segments' comment: a unit="LENGTH" FloatProperty
        # always treats its raw value as Blender-internal metres, so the
        # project-unit IFC value must be scaled into that space here.
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")

        props.v_segment_rows.clear()
        for seg in tool.Alignment.get_real_layout_segments(v_layout):
            dp = seg.DesignParameters
            row = props.v_segment_rows.add()
            row.segment_id = seg.id()
            seg_type = dp.PredefinedType
            if seg_type in prop.SUPPORTED_VERTICAL_TYPES:
                row.predefined_type = seg_type
            else:
                row.predefined_type = "UNSUPPORTED"
                row.original_predefined_type = seg_type or "?"
            row.h_length = dp.HorizontalLength * length_scale
            row.start_gradient = (dp.StartGradient or 0.0) * 100.0
            row.end_gradient = (dp.EndGradient or 0.0) * 100.0

        props.active_v_segment_row_index = 0
        props.editing_segment_kind = "VERTICAL"
        props.editing_layout_id = self.layout_id
        props.selected_v_segment_id = 0

        tool.Blender.update_viewport()
        return {"FINISHED"}


class ALIGN_OT_disable_editing_v_segments(Operator):
    """Discard the staged vertical segment edits without touching IFC"""

    bl_idname = "align.disable_editing_v_segments"
    bl_label = "Cancel"
    bl_description = "Discard these changes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        props.v_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0
        return {"FINISHED"}


class ALIGN_OT_apply_v_segments(Operator, tool.Ifc.Operator):
    """Rebuild a vertical layout from the staged segment table"""

    bl_idname = "align.apply_v_segments"
    bl_label = "Apply"
    bl_description = "Rebuild this layout's segments from the table above"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        v_layout = ifc_file.by_id(props.editing_layout_id)
        if v_layout is None:
            self.report({"ERROR"}, "The layout being edited no longer exists")
            props.v_segment_rows.clear()
            props.editing_segment_kind = "NONE"
            props.editing_layout_id = 0
            return {"CANCELLED"}

        rows = props.v_segment_rows
        errors = tool.Alignment.validate_vertical_segment_rows(rows)
        if errors:
            self.report({"ERROR"}, "; ".join(errors))
            return {"CANCELLED"}

        alignment = tool.Alignment._get_top_level_alignment(ifcopenshell.api.alignment.get_alignment(v_layout))

        existing = tool.Alignment.get_real_layout_segments(v_layout)
        if existing:
            first_dp = existing[0].DesignParameters
            dist_along, height = first_dp.StartDistAlong, first_dp.StartHeight
        else:
            dist_along, height = 0.0, 0.0

        # row.h_length is in Blender's internal unit="LENGTH" space (metres) --
        # see enable_editing_v_segments -- convert back to the project's
        # length unit before mixing it with dist_along/height (already in
        # project units, read straight from IFC above).
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")

        ifcopenshell.api.alignment.clear_layout_segments(ifc_file, v_layout)

        for row in rows:
            h_length = row.h_length / length_scale
            start_gradient = row.start_gradient / 100.0
            end_gradient = (
                row.end_gradient / 100.0 if row.predefined_type in prop.VERTICAL_TWO_GRADIENT_TYPES else start_gradient
            )

            design_parameters = ifc_file.createIfcAlignmentVerticalSegment(
                StartTag=None,
                EndTag=None,
                StartDistAlong=dist_along,
                HorizontalLength=h_length,
                StartHeight=height,
                StartGradient=start_gradient,
                EndGradient=end_gradient,
                RadiusOfCurvature=None,
                PredefinedType=row.predefined_type,
            )
            placement = ifcopenshell.api.alignment.create_layout_segment(ifc_file, v_layout, design_parameters)
            # Read the next segment's start state back off the kernel-evaluated
            # end placement, rather than the closed-form "average gradient"
            # shortcut -- that's only exact for CONSTANTGRADIENT/PARABOLICARC.
            # A CIRCULARARC's height doesn't vary linearly enough for it to
            # hold (confirmed by direct comparison against this same
            # evaluation): using the real placement keeps every type exact.
            dist_along = float(placement[0, 3]) / length_scale
            height = float(placement[1, 3]) / length_scale

        ifcopenshell.api.alignment.create_representation(ifc_file, alignment)
        tool.Alignment.refresh_alignment_representation_object(alignment)
        _refresh_vertical_profile_view(context, alignment)

        props.selected_v_segment_id = 0

        n = len(rows)
        props.v_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0

        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Rebuilt {n} vertical segment(s)")
        return {"FINISHED"}


class ALIGN_OT_generate_cant_layout(Operator, tool.Ifc.Operator):
    """Generate a full cant layout from a single cant value, paired to one
    specific vertical layout.

    Mirrors the horizontal layout's own segment structure and curve family
    (see tool.Alignment.build_cant_specs_from_horizontal /
    .CANT_TYPE_FOR_HORIZONTAL_TYPE): 0 on tangents, the given value on arcs
    (raised on whichever rail is outer to the turn), ramping between them on
    the matching transition curve type. Replaces any cant layout already
    paired with that vertical outright -- edit individual values afterward
    via Edit Cant Segments (align.generate_cant_layout only sets the
    starting point; per-segment tuning is the table's job, same division of
    labour as Draw Horizontal Alignment vs. its own PI-curve editing).

    With multiple verticals (IFC CT 4.1.4.4.1.2), which one matters (per the
    user, 2026-09-16): cant's IfcSegmentedReferenceCurve wraps a specific
    vertical's own IfcGradientCurve, so it has to nest onto that same
    vertical's owning alignment (its own child alignment, not necessarily
    the top-level one that owns the shared horizontal) -- exactly the same
    "reusing horizontal" structure multiple verticals already use, just with
    cant added alongside. layout_id targets a specific vertical the same way
    ALIGN_OT_load_vertical_pis's own layout_id does; 0 falls back to
    get_vertical_layout(alignment)'s direct vertical, the common
    single-vertical case.
    """

    bl_idname = "align.generate_cant_layout"
    bl_label = "Generate Cant Layout"
    bl_description = (
        "Generate a cant layout from a single cant value, matching the horizontal "
        "layout's own segments and curve types. Replaces any cant layout already "
        "paired with this vertical."
    )
    bl_options = {"REGISTER", "UNDO"}

    cant_value: FloatProperty(
        name="Cant",
        description="Full left/right rail height difference on curves (0 on tangents)",
        default=0.1,
    )
    layout_id: IntProperty(default=0, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Select an alignment first")
            return False
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        if not h_layout or not tool.Alignment.get_real_layout_segments(h_layout):
            cls.poll_message_set("Draw the horizontal alignment first")
            return False
        # Cant is fundamentally a 3D (rail) concept -- superelevation between
        # the two rails only means something once there's a vertical profile
        # to be superelevated along, and IFC's own IfcSegmentedReferenceCurve
        # for cant is inherently 3D. Per the user (2026-09-16): "adding cant
        # can only happen if there is a horizontal and a vertical alignment."
        if not tool.Alignment.has_real_vertical_segments(alignment):
            cls.poll_message_set("Draw the vertical alignment first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        ifc = tool.Ifc.get()

        if self.layout_id:
            v_layout = ifc.by_id(self.layout_id)
        else:
            v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
        if not v_layout or not tool.Alignment.get_real_layout_segments(v_layout):
            self.report({"ERROR"}, "That vertical layout has no segments yet")
            return {"CANCELLED"}

        # The alignment that directly nests v_layout -- the top-level
        # alignment for the single-vertical case, or v_layout's own child
        # alignment once a second+ vertical has moved it there. Cant nests
        # alongside whichever one that is, not necessarily the top level.
        owning_alignment = ifcopenshell.api.alignment.get_alignment(v_layout)

        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        h_segments = tool.Alignment.get_real_layout_segments(h_layout)

        try:
            specs = tool.Alignment.build_cant_specs_from_horizontal(h_segments, self.cant_value)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        cant_layout = tool.Alignment.get_or_create_cant_layout(owning_alignment)
        ifcopenshell.api.alignment.clear_layout_segments(ifc, cant_layout)

        dist_along = 0.0
        for predefined_type, length, start_left, start_right, end_left, end_right in specs:
            design_parameters = ifc.createIfcAlignmentCantSegment(
                StartTag=None,
                EndTag=None,
                StartDistAlong=dist_along,
                HorizontalLength=length,
                StartCantLeft=start_left,
                EndCantLeft=end_left,
                StartCantRight=start_right,
                EndCantRight=end_right,
                PredefinedType=predefined_type,
            )
            ifcopenshell.api.alignment.create_layout_segment(ifc, cant_layout, design_parameters)
            dist_along += length

        ifcopenshell.api.alignment.create_representation(ifc, alignment)
        tool.Alignment.refresh_alignment_representation_object(alignment)
        _refresh_vertical_profile_view(context, alignment)

        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Generated {len(specs)} cant segment(s)")
        return {"FINISHED"}


class ALIGN_OT_remove_cant_layout(Operator, tool.Ifc.Operator):
    """Delete one cant layout -- its segments and, if present, the
    IfcSegmentedReferenceCurve that wrapped its paired vertical's own curve
    (reverted back to a plain IfcGradientCurve). Never blocked by anything
    downstream -- cant is always the leaf of the horizontal/vertical/cant
    chain.
    """

    bl_idname = "align.remove_cant_layout"
    bl_label = "Delete Cant Layout"
    bl_description = "Delete this cant layout"
    bl_options = {"REGISTER", "UNDO"}

    layout_id: IntProperty(default=0, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        cant_layout = ifc.by_id(self.layout_id) if self.layout_id else None
        if cant_layout is None:
            alignment = tool.Alignment.get_active_alignment()
            cant_layouts = tool.Alignment.get_all_cant_layouts(alignment) if alignment else []
            cant_layout = cant_layouts[0] if cant_layouts else None
        if cant_layout is None:
            self.report({"ERROR"}, "No cant layout to delete")
            return {"CANCELLED"}

        top_level = tool.Alignment._get_top_level_alignment(ifcopenshell.api.alignment.get_alignment(cant_layout))
        tool.Alignment.remove_cant_layout(cant_layout)
        tool.Alignment.refresh_alignment_representation_object(top_level)
        _refresh_vertical_profile_view(context, top_level)
        tool.Blender.update_viewport()
        self.report({"INFO"}, "Deleted the cant layout")
        return {"FINISHED"}


class ALIGN_OT_remove_vertical_layout(Operator, tool.Ifc.Operator):
    """Delete one vertical layout -- its segments and its own geometric
    representation. Blocked while that vertical has a cant layout paired
    with it (per the user, 2026-09-16): delete the cant first.
    """

    bl_idname = "align.remove_vertical_layout"
    bl_label = "Delete Vertical Layout"
    bl_description = "Delete this vertical layout. Blocked while it has a cant layout."
    bl_options = {"REGISTER", "UNDO"}

    layout_id: IntProperty(default=0, options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        ifc = tool.Ifc.get()
        if self.layout_id:
            v_layout = ifc.by_id(self.layout_id)
        else:
            alignment = tool.Alignment.get_active_alignment()
            v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment) if alignment else None
        if v_layout is None:
            self.report({"ERROR"}, "No vertical layout to delete")
            return {"CANCELLED"}

        # A per-row UI button (ui.py's _draw_vertical) already disables
        # itself once this specific vertical has a cant -- a classmethod
        # poll() can't see that (layout_id isn't set until after the button
        # fires, same reason every other per-layout_id operator in this
        # module re-checks in _execute instead of poll). This is the safety
        # net for anything that reaches here regardless (search menu, redo
        # panel, scripting).
        owning_alignment = ifcopenshell.api.alignment.get_alignment(v_layout)
        cant_layout = ifcopenshell.api.alignment.get_cant_layout(owning_alignment)
        if cant_layout and tool.Alignment.get_real_layout_segments(cant_layout):
            self.report({"ERROR"}, "Delete this vertical's cant layout first")
            return {"CANCELLED"}

        top_level = tool.Alignment._get_top_level_alignment(owning_alignment)
        tool.Alignment.remove_vertical_layout(v_layout)
        tool.Alignment.refresh_alignment_representation_object(top_level)
        _refresh_vertical_profile_view(context, top_level)
        tool.Blender.update_viewport()
        self.report({"INFO"}, "Deleted the vertical layout")
        return {"FINISHED"}


class ALIGN_OT_remove_horizontal_layout(Operator, tool.Ifc.Operator):
    """Delete the alignment's horizontal layout -- its segments, its
    stationing referents, and the alignment's whole geometric representation
    (there's nothing left to represent once horizontal, the foundation
    every vertical is defined against, is gone). Blocked while a vertical
    layout exists (per the user, 2026-09-16): delete the vertical(s) -- and,
    for each, its own cant first -- first, or delete the whole alignment to
    start over in one step.
    """

    bl_idname = "align.remove_horizontal_layout"
    bl_label = "Delete Horizontal Layout"
    bl_description = "Delete the horizontal layout and its stationing. Blocked while a vertical layout exists."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not poll_ifc4x3(cls, context):
            return False
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Select an alignment first")
            return False
        h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
        if not h_layout or not tool.Alignment.get_real_layout_segments(h_layout):
            cls.poll_message_set("This alignment has no horizontal segments yet")
            return False
        if tool.Alignment.has_real_vertical_segments(alignment):
            cls.poll_message_set("Delete the vertical layout(s) first")
            return False
        if context.scene.CivilAlignmentProperties.editing_segment_kind != "NONE":
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        if _find_pi_markers(alignment.id()):
            cls.poll_message_set("Finish or clear the PI marker edit first")
            return False
        if context.scene.CivilAlignmentProperties.horizontal_pi_rows:
            cls.poll_message_set("Finish or clear the PI table edit first")
            return False
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def _execute(self, context):
        alignment = tool.Alignment.get_active_alignment()
        for marker in _find_pi_markers(alignment.id()):
            bpy.data.objects.remove(marker, do_unlink=True)
        tool.Alignment.remove_horizontal_layout(alignment)
        tool.Blender.update_viewport()
        self.report({"INFO"}, "Deleted the horizontal layout")
        return {"FINISHED"}


class ALIGN_OT_enable_editing_cant_segments(Operator):
    """Stage a cant layout's segments for table editing"""

    bl_idname = "align.enable_editing_cant_segments"
    bl_label = "Edit Cant Segments"
    bl_description = "Edit this layout's segments as a table (add/remove/reorder/edit, then Apply)"
    bl_options = {"REGISTER", "UNDO"}

    layout_id: IntProperty(options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = context.scene.CivilAlignmentProperties
        if props.editing_segment_kind not in ("NONE", "CANT"):
            cls.poll_message_set("Finish or cancel the segment table edit first")
            return False
        return True

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        c_layout = ifc_file.by_id(self.layout_id)

        # See enable_editing_h_segments' comment: a unit="LENGTH" FloatProperty
        # always treats its raw value as Blender-internal metres, so the
        # project-unit IFC value must be scaled into that space here.
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")

        props.cant_segment_rows.clear()
        for seg in tool.Alignment.get_real_layout_segments(c_layout):
            dp = seg.DesignParameters
            row = props.cant_segment_rows.add()
            row.segment_id = seg.id()
            seg_type = dp.PredefinedType
            if seg_type in (
                "CONSTANTCANT",
                "LINEARTRANSITION",
                "HELMERTCURVE",
                "BLOSSCURVE",
                "COSINECURVE",
                "SINECURVE",
                "VIENNESEBEND",
            ):
                row.predefined_type = seg_type
            else:
                row.predefined_type = "UNSUPPORTED"
                row.original_predefined_type = seg_type or "?"
            row.h_length = dp.HorizontalLength * length_scale
            start_l = dp.StartCantLeft or 0.0
            start_r = dp.StartCantRight or 0.0
            row.start_cant_left = start_l
            row.start_cant_right = start_r
            row.end_cant_left = dp.EndCantLeft if dp.EndCantLeft is not None else start_l
            row.end_cant_right = dp.EndCantRight if dp.EndCantRight is not None else start_r

        props.active_cant_segment_row_index = 0
        props.editing_segment_kind = "CANT"
        props.editing_layout_id = self.layout_id
        props.selected_cant_segment_id = 0

        tool.Blender.update_viewport()
        return {"FINISHED"}


class ALIGN_OT_disable_editing_cant_segments(Operator):
    """Discard the staged cant segment edits without touching IFC"""

    bl_idname = "align.disable_editing_cant_segments"
    bl_label = "Cancel"
    bl_description = "Discard these changes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.CivilAlignmentProperties
        props.cant_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0
        return {"FINISHED"}


class ALIGN_OT_apply_cant_segments(Operator, tool.Ifc.Operator):
    """Rebuild a cant layout from the staged segment table"""

    bl_idname = "align.apply_cant_segments"
    bl_label = "Apply"
    bl_description = "Rebuild this layout's segments from the table above"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        props = context.scene.CivilAlignmentProperties
        c_layout = ifc_file.by_id(props.editing_layout_id)
        if c_layout is None:
            self.report({"ERROR"}, "The layout being edited no longer exists")
            props.cant_segment_rows.clear()
            props.editing_segment_kind = "NONE"
            props.editing_layout_id = 0
            return {"CANCELLED"}

        rows = props.cant_segment_rows
        errors = tool.Alignment.validate_cant_segment_rows(rows)
        if errors:
            self.report({"ERROR"}, "; ".join(errors))
            return {"CANCELLED"}

        alignment = tool.Alignment._get_top_level_alignment(ifcopenshell.api.alignment.get_alignment(c_layout))

        existing = tool.Alignment.get_real_layout_segments(c_layout)
        dist_along = existing[0].DesignParameters.StartDistAlong if existing else 0.0

        # row.h_length is in Blender's internal unit="LENGTH" space (metres) --
        # see enable_editing_cant_segments -- convert back to the project's
        # length unit before mixing it with dist_along (already in project
        # units, read straight from IFC above).
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")

        ifcopenshell.api.alignment.clear_layout_segments(ifc_file, c_layout)

        for row in rows:
            h_length = row.h_length / length_scale
            # Every cant type except CONSTANTCANT is a transition that needs
            # End* set -- see _map_alignment_cant_segment (ifcopenshell):
            # HELMERTCURVE/BLOSSCURVE/COSINECURVE/SINECURVE/VIENNESEBEND all
            # read EndCantLeft/EndCantRight the same way LINEARTRANSITION does.
            is_transition = row.predefined_type != "CONSTANTCANT"
            design_parameters = ifc_file.createIfcAlignmentCantSegment(
                StartTag=None,
                EndTag=None,
                StartDistAlong=dist_along,
                HorizontalLength=h_length,
                StartCantLeft=row.start_cant_left,
                EndCantLeft=row.end_cant_left if is_transition else None,
                StartCantRight=row.start_cant_right,
                EndCantRight=row.end_cant_right if is_transition else None,
                PredefinedType=row.predefined_type,
            )
            ifcopenshell.api.alignment.create_layout_segment(ifc_file, c_layout, design_parameters)
            dist_along += h_length

        ifcopenshell.api.alignment.create_representation(ifc_file, alignment)
        tool.Alignment.refresh_alignment_representation_object(alignment)
        _refresh_vertical_profile_view(context, alignment)

        props.selected_cant_segment_id = 0

        n = len(rows)
        props.cant_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0

        tool.Blender.update_viewport()
        self.report({"INFO"}, f"Rebuilt {n} cant segment(s)")
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

