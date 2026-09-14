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
    tool.Alignment.safe_layout_horizontal_by_pi_method(ifc, h_layout, hpoints, radii)
    ifcopenshell.api.alignment.create_representation(ifc, alignment)

    tool.Alignment.refresh_alignment_representation_object(alignment)

    n_curved = sum(1 for r in radii if (r[0] if isinstance(r, tuple) else r))
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


def _pi_curve_radii_entry(marker):
    """One radii[] element (see solve_horizontal_alignment_by_pi_method) for a PI marker.

    TANGENT stays a plain 0.0 (no curve). CIRCULAR stays a plain radius float
    for backward compatibility. The three spiral curve types become a
    (radius, entry_length, exit_length) tuple with whichever length(s) don't
    apply left at 0.0 — only the clothoid spiral family is supported, per
    solve_horizontal_alignment_by_pi_method.
    """
    curve_type = marker.curve_type
    if curve_type == "TANGENT":
        return 0.0
    if curve_type == "CIRCULAR":
        return marker.radius
    if curve_type == "SPIRAL_CIRCULAR":
        return (marker.radius, marker.spiral_in_length, 0.0)
    if curve_type == "CIRCULAR_SPIRAL":
        return (marker.radius, 0.0, marker.spiral_out_length)
    # SPIRAL_CIRCULAR_SPIRAL
    return (marker.radius, marker.spiral_in_length, marker.spiral_out_length)


def _pi_curve_marker_label(marker) -> str:
    """Short label for a PI marker's name, reflecting its curve settings."""
    curve_type = marker.curve_type
    if curve_type == "TANGENT":
        return "tangent"
    if curve_type == "CIRCULAR":
        return f"R={marker.radius:.2f}"
    if curve_type == "SPIRAL_CIRCULAR":
        return f"R={marker.radius:.2f}, Lin={marker.spiral_in_length:.2f}"
    if curve_type == "CIRCULAR_SPIRAL":
        return f"R={marker.radius:.2f}, Lout={marker.spiral_out_length:.2f}"
    # SPIRAL_CIRCULAR_SPIRAL
    return f"R={marker.radius:.2f}, Lin={marker.spiral_in_length:.2f}, Lout={marker.spiral_out_length:.2f}"


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
        radii = [_pi_curve_radii_entry(m.bonsai_pi_curve_marker) for m in interior_markers]

        ok, message = _generate_alignment_segments(context, alignment, hpoints, radii)

        marker = marker_obj.bonsai_pi_curve_marker
        marker_obj.name = f"PI {marker.pi_index} ({_pi_curve_marker_label(marker)})"
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
    space.show_gizmo = False

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
        "Elevation is exaggerated by the VE factor. Use middle-mouse to pan/zoom."
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


# =============================================================================
# Vertical Alignment Drawing (draw-by-PI in the profile view)
# =============================================================================


def _generate_vertical_alignment_segments(context, alignment, vpoints, lengths):
    """Build vertical alignment segments from PI points and per-PI curve lengths.

    Mirrors _generate_alignment_segments() for the vertical layout. ``vpoints``
    are (distance_along, elevation) pairs already in project length units —
    unlike the horizontal case, no unit-scale/georeferencing conversion is
    needed, because the profile view's world coordinates already are raw
    project-unit distance/elevation values (see
    VerticalProfileDecorator.screen_to_data). ``lengths`` has exactly
    len(vpoints) - 2 entries, one per interior PI (0.0 = sharp grade break).
    """
    ifc = tool.Ifc.get()

    v_layout = ifcopenshell.api.alignment.get_vertical_layout(alignment)
    if v_layout is None:
        v_layout = ifcopenshell.api.alignment.add_vertical_layout(ifc, alignment)

    tool.Alignment.clear_layout_segments(v_layout)
    tool.Alignment.safe_layout_vertical_by_pi_method(ifc, v_layout, vpoints, lengths)
    ifcopenshell.api.alignment.create_representation(ifc, alignment)

    tool.Alignment.refresh_alignment_representation_object(alignment)

    n_curved = sum(1 for l in lengths if l)
    return True, f"Drew vertical alignment with {len(vpoints)} PIs ({n_curved} curved)"


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
        alignment = tool.Alignment.get_active_alignment()
        if not alignment:
            cls.poll_message_set("Add or select an alignment first")
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

        ok, message = _generate_vertical_alignment_segments(context, alignment, vpoints, lengths)
        if ok:
            _sync_vertical_pi_markers(context, vpoints)
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
        alignment = tool.Alignment.get_active_alignment()
        try:
            start, end = tool.Alignment.get_vertical_alignment_start_end_points(alignment)
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}

        markers = list(context.scene.CivilAlignmentProperties.vertical_pi_markers)
        vpoints = [start] + [(m.dist_along, m.elevation) for m in markers] + [end]
        lengths = [m.curve_length if m.curve_type == "PARABOLIC" else 0.0 for m in markers]

        ok, message = _generate_vertical_alignment_segments(context, alignment, vpoints, lengths)
        if ok:
            _refresh_vertical_profile_view(context, alignment)
        self.report({"INFO"} if ok else {"WARNING"}, message)
        return {"FINISHED"}


class ALIGN_OT_clear_vertical_pi_markers(Operator):
    """Clear the vertical PI list without changing the vertical alignment"""

    bl_idname = "align.clear_vertical_pi_markers"
    bl_label = "Clear Vertical PI List"
    bl_description = "Clear the interior-PI list (does not affect the vertical alignment already drawn)"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.CivilAlignmentProperties.vertical_pi_markers)

    def execute(self, context):
        context.scene.CivilAlignmentProperties.vertical_pi_markers.clear()
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
            cls.poll_message_set("Finish or cancel the current segment edit first")
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

        # Every segment id in this layout just changed.
        props.selected_h_segment_id = 0
        alignment_decorator.AlignmentSegmentDecorator.uninstall()

        n = len(rows)
        props.h_segment_rows.clear()
        props.editing_segment_kind = "NONE"
        props.editing_layout_id = 0

        tool.Blender.update_viewport()
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
            cls.poll_message_set("Finish or cancel the current segment edit first")
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
            cls.poll_message_set("Finish or cancel the current segment edit first")
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
            if seg_type in ("CONSTANTCANT", "LINEARTRANSITION"):
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
            is_transition = row.predefined_type == "LINEARTRANSITION"
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

