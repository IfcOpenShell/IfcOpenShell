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

"""Alignment module decorators for GPU visualization.

This module contains decorators for rendering visual feedback during
alignment-related operations, such as segment highlighting and the
vertical profile view.
"""

import bpy
import blf
import gpu
import math
import mathutils
import numpy as np
import ifcopenshell.api.alignment
import ifcopenshell.util.geolocation
import ifcopenshell.util.shape
import ifcopenshell.util.unit
import bonsai.tool as tool
from typing import Optional, Tuple
from bpy.types import SpaceView3D
from bpy_extras.view3d_utils import location_3d_to_region_2d, region_2d_to_location_3d
from gpu_extras.batch import batch_for_shader
from ifcopenshell.api.alignment._get_segment_start_point_label import (
    _get_segment_start_point_label,
)


class AlignmentSegmentDecorator:
    """Decorator that highlights a selected horizontal alignment segment in the 3D viewport.

    Draws:
    - A thick orange polyline over the segment
    - Thin gray tangent extension lines from PC and PT to their PI intersection
    - A yellow crosshair at the PI in screen space
    - Labels at PC (start), PI, and PT (end) with station and E/N coordinates
    """

    is_installed = False
    handlers = []

    segment_id: int | None = None
    segment_verts: list[tuple[float, float, float]] = []
    segment_label: str = ""
    label_world_pos: tuple[float, float, float] | None = None
    tangent_data: dict | None = None

    # Blender selection state at the moment this segment was highlighted
    # (see _has_selection_changed) -- used to auto-clear the highlight the
    # moment the user picks something else, instead of leaving it stuck
    # until the same side-panel row is clicked again.
    _baseline_active_ptr: int = 0
    _baseline_selected_ptrs: frozenset = frozenset()

    COLOR_HIGHLIGHT = (1.0, 0.55, 0.0, 1.0)        # Orange - segment polyline
    COLOR_TANGENT = (0.75, 0.75, 0.75, 0.85)        # Light gray - tangent extension lines
    COLOR_PI = (1.0, 0.85, 0.25, 1.0)               # Yellow - PI crosshair
    COLOR_LABEL = (1.0, 1.0, 1.0, 1.0)              # White - fallback label
    COLOR_LABEL_PC = (1.0, 0.78, 0.40, 1.0)         # Warm orange - PC label
    COLOR_LABEL_PT = (0.60, 0.88, 1.0, 1.0)         # Light blue - PT label
    COLOR_LABEL_PI = (1.0, 0.90, 0.30, 1.0)         # Yellow - PI label
    LINE_WIDTH = 4.0
    LINE_TANGENT = 1.5

    @classmethod
    def install(cls, context, segment_id: int) -> None:
        if cls.is_installed:
            cls.uninstall()

        cls.segment_id = segment_id
        cls._compute_segment_geometry(segment_id)
        if not cls.segment_verts:
            return

        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_segment, (context,), "WINDOW", "POST_VIEW")
        )
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_label, (context,), "WINDOW", "POST_PIXEL")
        )
        cls.is_installed = True
        cls._capture_selection_baseline(context)

    @classmethod
    def _capture_selection_baseline(cls, context) -> None:
        try:
            active_obj = context.view_layer.objects.active
            cls._baseline_active_ptr = active_obj.as_pointer() if active_obj else 0
            cls._baseline_selected_ptrs = frozenset(o.as_pointer() for o in context.selected_objects)
        except Exception:
            cls._baseline_active_ptr = 0
            cls._baseline_selected_ptrs = frozenset()

    @classmethod
    def _has_selection_changed(cls) -> bool:
        """True if Blender's active object or selection set differs from
        what it was when this segment was highlighted.

        Selecting a segment in the side panel doesn't itself touch Blender's
        object selection, so any subsequent change to it -- clicking on
        nothing or on something else in the 3D viewport, picking a different
        object in the Outliner, or switching the active alignment via the
        dropdown (which reselects that alignment's own object, see
        _on_active_alignment_update in prop.py) -- means the user has moved
        on and the highlight/label should clear rather than stick around
        referencing a segment that's no longer the focus.
        """
        try:
            active_obj = bpy.context.view_layer.objects.active
            active_ptr = active_obj.as_pointer() if active_obj else 0
            selected_ptrs = frozenset(o.as_pointer() for o in bpy.context.selected_objects)
        except Exception:
            return False
        return active_ptr != cls._baseline_active_ptr or selected_ptrs != cls._baseline_selected_ptrs

    @classmethod
    def refresh(cls) -> None:
        """Recompute the highlighted segment's tangent/station data in place.

        Stationing (start station, station equations) can change while a
        segment is already selected and highlighted; without this its PC/PI/PT
        station labels would stay stale until the segment was deselected and
        reselected. Called by the stationing operators after they succeed.

        Also re-captures the selection baseline (see _has_selection_changed):
        the triggering operator ran with the segment's highlight still valid,
        so whatever Blender's active object/selection happens to be right now
        is the new "nothing has changed yet" baseline -- protects against a
        false-positive auto-clear on the next redraw if the operator itself
        touched object selection along the way.
        """
        if not cls.is_installed or cls.segment_id is None:
            return
        cls._compute_segment_geometry(cls.segment_id)
        cls._capture_selection_baseline(bpy.context)
        tool.Blender.update_viewport()

    @classmethod
    def uninstall(cls) -> None:
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False
        old_segment_id = cls.segment_id
        cls.segment_id = None
        cls.segment_verts = []
        cls.segment_label = ""
        cls.label_world_pos = None
        cls.tangent_data = None
        cls._baseline_active_ptr = 0
        cls._baseline_selected_ptrs = frozenset()

        # Keep the side panel's row depress-state in sync -- uninstall() can
        # now be triggered autonomously (see _has_selection_changed), not
        # just from the toggle operator, which already clears this itself.
        # Only clear it if it still points at the segment being uninstalled
        # here: install() calls uninstall() on the previously-installed
        # segment before switching to a new one, and by then
        # selected_h_segment_id already holds the *new* segment's id --
        # blindly zeroing it here (the old bug) stomped that new selection
        # right after the toggle operator set it, so every row-highlight
        # after the first got silently cleared.
        try:
            props = bpy.context.scene.CivilAlignmentProperties
            if old_segment_id and props.selected_h_segment_id == old_segment_id:
                props.selected_h_segment_id = 0
        except Exception:
            pass

    @classmethod
    def _compute_segment_geometry(cls, segment_id: int) -> None:
        """Extract world-space polyline vertices for the given IfcAlignmentSegment."""
        import logging
        import bonsai.bim.import_ifc

        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return

        try:
            segment = ifc_file.by_id(segment_id)
        except Exception:
            return

        if not segment or not segment.is_a("IfcAlignmentSegment"):
            return

        dp = segment.DesignParameters
        if dp:
            cls.segment_label = getattr(dp, "PredefinedType", "Segment") or "Segment"

        layout = segment.Nests[0].RelatingObject if segment.Nests else None
        if not layout:
            return

        layout_curve = tool.Alignment._find_layout_curve(layout)
        if not layout_curve:
            return

        mapped_segments = tool.Alignment._map_alignment_segment_to_curve_segments(
            segment, layout, layout_curve
        )

        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)
        ifc_importer.file = ifc_file
        tool.Loader.load_settings()

        all_verts: list[tuple[float, float, float]] = []
        for curve_segment in mapped_segments:
            if curve_segment is None:
                continue
            geometry = tool.Loader.create_generic_shape(curve_segment)
            if not geometry:
                continue

            mesh = ifc_importer.create_mesh(curve_segment, geometry)
            tmp_obj = bpy.data.objects.new("__seg_highlight_tmp__", mesh)

            if hasattr(geometry, "transformation_buffer"):
                mat = ifcopenshell.util.shape.get_shape_matrix(geometry)
            else:
                mat = np.eye(4)

            tmp_obj.matrix_world = tool.Loader.apply_blender_offset_to_matrix_world(tmp_obj, mat)
            tool.Geometry.record_object_position(tmp_obj)

            world_mat = tmp_obj.matrix_world
            for v in mesh.vertices:
                all_verts.append(tuple(world_mat @ v.co))

            bpy.data.objects.remove(tmp_obj)
            bpy.data.meshes.remove(mesh)

        cls.segment_verts = all_verts
        if all_verts:
            cls.label_world_pos = all_verts[len(all_verts) // 2]

        cls._compute_tangent_data(segment, ifc_file)

    @classmethod
    def _compute_tangent_data(cls, segment, ifc_file) -> None:
        """Compute PI tangent intersection, stations, and E/N labels for the segment.

        Always populates basic PC/PT data.  For non-linear segments where a finite PI
        exists, also populates PI position and the tangent-direction reference points
        used to draw perpendicular ticks at PC and PT.
        """
        cls.tangent_data = None
        if not cls.segment_verts:
            return

        dp = segment.DesignParameters
        if not dp or not getattr(dp, "StartPoint", None):
            return

        # Require a horizontal layout so we know dp is IfcAlignmentHorizontalSegment
        layout = segment.Nests[0].RelatingObject if segment.Nests else None
        if not layout or not layout.is_a("IfcAlignmentHorizontal"):
            return

        # Collect all horizontal segments in order
        segments = []
        for seg_rel in (getattr(layout, "IsNestedBy", []) or []):
            for seg in (seg_rel.RelatedObjects or []):
                if seg.is_a("IfcAlignmentSegment") and seg.DesignParameters:
                    segments.append(seg)

        if segment not in segments:
            return
        seg_idx = segments.index(segment)
        seg_type = getattr(dp, "PredefinedType", "") or ""

        # Key-point labels (P.C., T.S., S.C., P.O.B., ...) — shares
        # _get_segment_start_point_label with update_key_point_referents so the
        # on-screen labels always agree with the IfcReferents it creates,
        # including any jurisdiction-specific naming registered via
        # register_referent_name_callback().
        prev_segment = segments[seg_idx - 1] if seg_idx > 0 else None
        next_segment = segments[seg_idx + 1] if seg_idx + 1 < len(segments) else None
        if next_segment is not None and tool.Alignment.is_zero_length_segment(next_segment):
            next_segment = None  # the mandatory terminator isn't a real transition
        start_label = _get_segment_start_point_label(prev_segment, segment)
        end_label = _get_segment_start_point_label(segment, next_segment)

        # IFC local start coordinate and start tangent direction
        sx, sy = dp.StartPoint.Coordinates[0], dp.StartPoint.Coordinates[1]
        d1x, d1y = math.cos(dp.StartDirection), math.sin(dp.StartDirection)
        seg_len = getattr(dp, "SegmentLength", 0.0) or 0.0

        # Next segment data — provides the IFC end-point and end tangent
        has_next = seg_idx + 1 < len(segments)
        next_dp = segments[seg_idx + 1].DesignParameters if has_next else None
        arc_radius = getattr(dp, "StartRadiusOfCurvature", None) or 0.0
        if next_dp and getattr(next_dp, "StartPoint", None):
            ex = next_dp.StartPoint.Coordinates[0]
            ey = next_dp.StartPoint.Coordinates[1]
            d2x, d2y = math.cos(next_dp.StartDirection), math.sin(next_dp.StartDirection)
        elif seg_type == "CIRCULARARC" and abs(arc_radius) > 1e-6:
            # No next segment to read the true end tangent from (last/only
            # segment) — the straight-line fallback below would make it
            # parallel to the start tangent, degenerating the PI below to "none".
            turn = seg_len / arc_radius
            cos_t, sin_t = math.cos(turn), math.sin(turn)
            d2x, d2y = d1x * cos_t - d1y * sin_t, d1x * sin_t + d1y * cos_t
            cix, ciy = sx + arc_radius * -d1y, sy + arc_radius * d1x
            rvx, rvy = sx - cix, sy - ciy
            ex, ey = cix + rvx * cos_t - rvy * sin_t, ciy + rvx * sin_t + rvy * cos_t
        else:
            # Last segment or next has no StartPoint — approximate end along start tangent
            ex = sx + seg_len * d1x
            ey = sy + seg_len * d1y
            d2x, d2y = d1x, d1y  # same direction → parallel, no PI

        # Derive IFC → Blender world affine transform
        # (sx,sy) ↔ segment_verts[0]  and  (ex,ey) ↔ segment_verts[-1]
        s_w = cls.segment_verts[0]
        e_w = cls.segment_verts[-1]
        ifc_dx, ifc_dy = ex - sx, ey - sy
        ifc_len_sq = ifc_dx ** 2 + ifc_dy ** 2
        if ifc_len_sq < 1e-12:
            return

        w_dx, w_dy = e_w[0] - s_w[0], e_w[1] - s_w[1]
        a_c = (ifc_dx * w_dx + ifc_dy * w_dy) / ifc_len_sq
        b_c = (ifc_dx * w_dy - ifc_dy * w_dx) / ifc_len_sq

        def ifc_to_world_xy(x, y):
            rx, ry = x - sx, y - sy
            return s_w[0] + a_c * rx - b_c * ry, s_w[1] + b_c * rx + a_c * ry

        def world_to_ifc_xy(wx, wy):
            rx_w, ry_w = wx - s_w[0], wy - s_w[1]
            det = a_c * a_c + b_c * b_c
            if det < 1e-12:
                return sx, sy
            rx = (a_c * rx_w + b_c * ry_w) / det
            ry = (-b_c * rx_w + a_c * ry_w) / det
            return sx + rx, sy + ry

        # For the last segment, refine the IFC end position from the world end vertex
        if not (next_dp and getattr(next_dp, "StartPoint", None)):
            ex, ey = world_to_ifc_xy(e_w[0], e_w[1])

        # E/N for start and end
        try:
            s_enh = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, sx, sy, 0.0)
            e_enh = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, ex, ey, 0.0)
        except Exception:
            return

        # Cumulative distance along, converted to station through
        # station_from_distance_along() so gap/overlap station equations and
        # reversed stationing are accounted for — a plain
        # start_station + distance_along (what this used to do) is only
        # correct when the alignment has no equations.
        pc_distance_along = sum(
            getattr(segments[i].DesignParameters, "SegmentLength", 0.0) or 0.0
            for i in range(seg_idx)
        )
        pt_distance_along = pc_distance_along + seg_len
        alignment = cls._get_alignment(layout)
        if alignment is not None:
            pc_station = ifcopenshell.api.alignment.station_from_distance_along(
                ifc_file, alignment, pc_distance_along
            )
            pt_station = ifcopenshell.api.alignment.station_from_distance_along(
                ifc_file, alignment, pt_distance_along
            )
        else:
            pc_station = pc_distance_along
            pt_station = pt_distance_along

        unit_symbol, station_separator = _get_length_unit_info(ifc_file)

        # Base record — always present regardless of segment type
        cls.tangent_data = {
            "start_world": (s_w[0], s_w[1], s_w[2]),
            "end_world": (e_w[0], e_w[1], e_w[2]),
            "pc_station": pc_station,
            "pt_station": pt_station,
            "start_en": (s_enh[0], s_enh[1]),
            "end_en": (e_enh[0], e_enh[1]),
            "unit_symbol": unit_symbol,
            "station_separator": station_separator,
            "start_label": start_label,
            "end_label": end_label,
            "has_pi": False,
        }

        # PI and perpendicular-tick data — only for non-linear segments with a finite PI
        denom_ifc = d1x * d2y - d1y * d2x
        if seg_type == "LINE" or abs(denom_ifc) < 1e-10:
            return  # Linear or parallel tangents — labels only, no PI geometry

        dx_ifc, dy_ifc = ex - sx, ey - sy
        t1_ifc = (dx_ifc * d2y - dy_ifc * d2x) / denom_ifc
        pi_ifc_x = sx + t1_ifc * d1x
        pi_ifc_y = sy + t1_ifc * d1y
        pi_wx, pi_wy = ifc_to_world_xy(pi_ifc_x, pi_ifc_y)
        pi_wz = (s_w[2] + e_w[2]) * 0.5

        try:
            pi_enh = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, pi_ifc_x, pi_ifc_y, 0.0)
        except Exception:
            return

        # Turn direction: positive denom → left (CCW), negative → right (CW)
        sign_turn = 1 if denom_ifc > 0 else -1

        # World-space normalized perpendicular directions at PC and PT
        # pointing toward the inside of the curve (toward the center of curvature)
        def _world_perp(dx_ifc, dy_ifc):
            # IFC perp direction (unit, since d is already unit): sign_turn * (-dy, dx)
            ipx = -dy_ifc * sign_turn
            ipy = dx_ifc * sign_turn
            wpx = a_c * ipx - b_c * ipy
            wpy = b_c * ipx + a_c * ipy
            length = math.hypot(wpx, wpy)
            return (wpx / length, wpy / length) if length > 0 else (0.0, 0.0)

        pc_perp = _world_perp(d1x, d1y)
        pt_perp = _world_perp(d2x, d2y)

        # Center of curvature (circular arcs only — constant radius gives a single center)
        center_world = None
        center_en = None
        if seg_type == "CIRCULARARC":
            R = getattr(dp, "StartRadiusOfCurvature", None) or 0.0
            if abs(R) > 1e-6:
                # center = PC + R * (-d1y, d1x) in IFC local (R is signed: + left, − right)
                cix = sx + R * (-d1y)
                ciy = sy + R * d1x
                cwx, cwy = ifc_to_world_xy(cix, ciy)
                center_world = (cwx, cwy, s_w[2])
                try:
                    c_enh = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, cix, ciy, 0.0)
                    center_en = (c_enh[0], c_enh[1])
                except Exception:
                    pass

        if center_world is None:
            # Non-circular curves (spirals, etc.) have no single center, but the
            # PC/PT normals still meet at a useful reference point — same
            # line-intersection as the PI above, using the perpendicular
            # directions instead of the tangents.
            pc_perp_ifc = (-d1y * sign_turn, d1x * sign_turn)
            pt_perp_ifc = (-d2y * sign_turn, d2x * sign_turn)
            perp_denom = pc_perp_ifc[0] * pt_perp_ifc[1] - pc_perp_ifc[1] * pt_perp_ifc[0]
            if abs(perp_denom) > 1e-10:
                t2 = (dx_ifc * pt_perp_ifc[1] - dy_ifc * pt_perp_ifc[0]) / perp_denom
                cix = sx + t2 * pc_perp_ifc[0]
                ciy = sy + t2 * pc_perp_ifc[1]
                cwx, cwy = ifc_to_world_xy(cix, ciy)
                center_world = (cwx, cwy, pi_wz)
                try:
                    c_enh = ifcopenshell.util.geolocation.auto_xyz2enh(ifc_file, cix, ciy, 0.0)
                    center_en = (c_enh[0], c_enh[1])
                except Exception:
                    pass

        cls.tangent_data.update({
            "has_pi": True,
            "pi_world": (pi_wx, pi_wy, pi_wz),
            "pi_en": (pi_enh[0], pi_enh[1]),
            "pc_perp": pc_perp,          # (x, y) normalized world perp at PC
            "pt_perp": pt_perp,          # (x, y) normalized world perp at PT
            "center_world": center_world, # 3-tuple or None
            "center_en": center_en,       # (e, n) or None
        })

    @classmethod
    def _get_alignment(cls, horizontal_layout):
        """The IfcAlignment that nests ``horizontal_layout``, or None."""
        for rel in getattr(horizontal_layout, "Nests", []) or []:
            if rel.RelatingObject.is_a("IfcAlignment"):
                return rel.RelatingObject
        return None

    def draw_segment(self, context):
        """Draw the orange highlight polyline and gray tangent extension lines to PI."""
        cls = self.__class__
        if not cls.is_installed:
            return

        # Selection moved on elsewhere (viewport pick, Outliner, alignment
        # dropdown) -- clear rather than keep showing a stale highlight.
        if cls._has_selection_changed():
            cls.uninstall()
            try:
                for area in bpy.context.screen.areas:
                    if area.type == "VIEW_3D":
                        area.tag_redraw()
            except Exception:
                pass
            return

        # Never draw segment overlays inside the vertical profile area
        pa_ptr = VerticalProfileDecorator.profile_area_ptr
        if pa_ptr != 0:
            try:
                if bpy.context.area is not None and bpy.context.area.as_pointer() == pa_ptr:
                    return
            except Exception:
                pass

        verts = cls.segment_verts
        if not verts or len(verts) < 2:
            return

        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("LESS_EQUAL")
        gpu.state.depth_mask_set(False)

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()
        region = bpy.context.region
        shader.uniform_float("viewportSize", (region.width, region.height))

        # Supplementary geometry for non-linear segments
        td = self.__class__.tangent_data
        if td and td.get("has_pi"):
            sw = td["start_world"]
            ew = td["end_world"]
            pi = td["pi_world"]

            # Gray tangent extension lines: PC→PI and PT→PI
            shader.uniform_float("lineWidth", self.LINE_TANGENT)
            shader.uniform_float("color", self.COLOR_TANGENT)
            for a_pt, b_pt in [(sw, pi), (ew, pi)]:
                batch = batch_for_shader(shader, "LINES", {"pos": [a_pt, b_pt]}, indices=[[0, 1]])
                batch.draw(shader)

            # Radius / perpendicular lines
            center = td.get("center_world")
            if center:
                # Circular arc: draw full radius lines from PC and PT to center
                for endpoint in [sw, ew]:
                    batch = batch_for_shader(
                        shader, "LINES", {"pos": [endpoint, center]}, indices=[[0, 1]]
                    )
                    batch.draw(shader)

                # Center point marker (yellow crosshair scaled to view)
                rv3d = bpy.context.space_data.region_3d if bpy.context.space_data else None
                mk = rv3d.view_distance * 0.012 if rv3d else 1.0
                cx, cy, cz = center
                shader.uniform_float("lineWidth", 2.0)
                shader.uniform_float("color", self.COLOR_PI)
                mk_verts = [
                    (cx - mk, cy, cz), (cx + mk, cy, cz),
                    (cx, cy - mk, cz), (cx, cy + mk, cz),
                ]
                batch = batch_for_shader(shader, "LINES", {"pos": mk_verts}, indices=[[0, 1], [2, 3]])
                batch.draw(shader)
            else:
                # Non-circular: short perpendicular ticks at PC and PT
                rv3d = bpy.context.space_data.region_3d if bpy.context.space_data else None
                tick = rv3d.view_distance * 0.018 if rv3d else 1.0
                for endpoint, perp in [(sw, td["pc_perp"]), (ew, td["pt_perp"])]:
                    px, py = perp
                    ex_w, ey_w, ez_w = endpoint
                    tick_verts = [
                        (ex_w - px * tick, ey_w - py * tick, ez_w),
                        (ex_w + px * tick, ey_w + py * tick, ez_w),
                    ]
                    batch = batch_for_shader(
                        shader, "LINES", {"pos": tick_verts}, indices=[[0, 1]]
                    )
                    batch.draw(shader)

        # Orange highlight polyline on top
        shader.uniform_float("lineWidth", self.LINE_WIDTH)
        shader.uniform_float("color", self.COLOR_HIGHLIGHT)
        edges = [[i, i + 1] for i in range(len(verts) - 1)]
        batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=edges)
        batch.draw(shader)

        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")
        gpu.state.depth_mask_set(True)

    def _draw_screen_crosshair(self, sx: float, sy: float, color: tuple, region) -> None:
        """Draw a small + crosshair at screen pixel position (sx, sy)."""
        r = 9
        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()
        shader.uniform_float("viewportSize", (region.width, region.height))
        shader.uniform_float("lineWidth", 2.0)
        shader.uniform_float("color", color)
        verts = [(sx - r, sy, 0), (sx + r, sy, 0), (sx, sy - r, 0), (sx, sy + r, 0)]
        gpu.state.blend_set("ALPHA")
        batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=[[0, 1], [2, 3]])
        batch.draw(shader)
        gpu.state.blend_set("NONE")

    def draw_label(self, context):
        """Draw point labels with station and E/N coordinates in screen space.

        Start/end tags (P.C., T.S., S.C., P.O.B., ...) come from
        _get_segment_start_point_label — see _compute_tangent_data. Curve
        segments (has_pi=True) also get a PI crosshair + label, and — where a
        finite curve center or normals intersection exists — a labeled center.
        """
        if not self.__class__.is_installed:
            # draw_segment (POST_VIEW, runs first) may have just auto-cleared
            # the highlight this same frame because the selection moved on --
            # don't draw a label for data that's already gone.
            return

        try:
            if not bpy.context.scene.CivilAlignmentProperties.show_h_segment_labels:
                return
        except Exception:
            pass

        # Never draw segment labels inside the vertical profile area
        pa_ptr = VerticalProfileDecorator.profile_area_ptr
        if pa_ptr != 0:
            try:
                if bpy.context.area is not None and bpy.context.area.as_pointer() == pa_ptr:
                    return
            except Exception:
                pass

        region = context.region
        rv3d = context.region_data
        if not region or not rv3d:
            return

        font_id = 0
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)
        font_size = tool.Blender.scale_font_size(12)
        line_h = font_size + 3

        td = self.__class__.tangent_data
        if td:
            sep = td["station_separator"]
            has_pi = td.get("has_pi", False)

            def fmt_sta(dist: float) -> str:
                return _fmt_station(dist, 1.0, sep)

            def fmt_en(e: float, n: float) -> str:
                return f"E {e:.2f}  N {n:.2f}"

            def draw_point_label(world_pos, name, station, coords, color):
                screen = location_3d_to_region_2d(region, rv3d, world_pos)
                if not screen:
                    return
                sx, sy = screen.x, screen.y
                if name == "P.I.":
                    self._draw_screen_crosshair(sx, sy, self.COLOR_PI, region)
                blf.size(font_id, font_size)
                blf.color(font_id, *color)
                lines = [name] if name else []
                if station:
                    lines.append(f"Sta {station}")
                lines.append(coords)
                # Stack upward from the point by default; flip downward near the
                # top edge so a multi-line label can't run off-screen -- a point
                # can end up arbitrarily close to any edge once you zoom in far
                # enough.
                total_h = len(lines) * line_h
                if sy > region.height - total_h - 8:
                    for i, line in enumerate(lines):
                        blf.position(font_id, sx + 12, sy - 4 - (i + 1) * line_h, 0)
                        blf.draw(font_id, line)
                else:
                    for i, line in enumerate(reversed(lines)):
                        blf.position(font_id, sx + 12, sy + 4 + i * line_h, 0)
                        blf.draw(font_id, line)

            if has_pi:
                # Curve segment: start tag / PI / end tag
                draw_point_label(
                    td["start_world"], td["start_label"], fmt_sta(td["pc_station"]),
                    fmt_en(*td["start_en"]), self.COLOR_LABEL_PC,
                )
                draw_point_label(
                    td["pi_world"], "P.I.", None,
                    fmt_en(*td["pi_en"]), self.COLOR_LABEL_PI,
                )
                draw_point_label(
                    td["end_world"], td["end_label"], fmt_sta(td["pt_station"]),
                    fmt_en(*td["end_en"]), self.COLOR_LABEL_PT,
                )
                # Center of curvature / normals-intersection label
                if td.get("center_world") and td.get("center_en"):
                    draw_point_label(
                        td["center_world"], "Center",
                        None, fmt_en(*td["center_en"]), self.COLOR_PI,
                    )
            else:
                # Linear segment: start and end tags (e.g. P.O.B., T.S.)
                draw_point_label(
                    td["start_world"], td["start_label"], fmt_sta(td["pc_station"]),
                    fmt_en(*td["start_en"]), self.COLOR_LABEL_PC,
                )
                draw_point_label(
                    td["end_world"], td["end_label"], fmt_sta(td["pt_station"]),
                    fmt_en(*td["end_en"]), self.COLOR_LABEL_PT,
                )
        else:
            # Fallback: type label at midpoint when tangent data is unavailable
            label_pos = self.__class__.label_world_pos
            label_text = self.__class__.segment_label
            if label_pos and label_text:
                screen = location_3d_to_region_2d(region, rv3d, label_pos)
                if screen:
                    blf.size(font_id, tool.Blender.scale_font_size(13))
                    blf.color(font_id, *self.COLOR_LABEL)
                    blf.position(font_id, screen.x + 10, screen.y + 6, 0)
                    blf.draw(font_id, label_text)

        blf.disable(font_id, blf.SHADOW)


class PIMarkerDecorator:
    """Screen-space overlay for interior PI marker empties: a colored dot plus
    a "PI n" label at each marker's projected screen position.

    Color signals curve state at a glance -- red/orange while the marker is
    still a plain TANGENT (sharp PI, no curve chosen), green once a curve has
    been applied -- so it's visible which PIs still need attention without
    opening the side panel or clicking each marker.

    Deliberately drawn in screen space (POST_PIXEL) at a fixed pixel radius
    rather than sized off rv3d.view_distance the way AlignmentSegmentDecorator
    scales its PI crosshairs: that view_distance trick only approximates a
    constant apparent size in an orthographic view, whereas a literal pixel
    radius, computed straight from the projected 2D position every frame, is
    exact and holds regardless of projection mode or zoom.

    Install/refresh lifecycle mirrors AlignmentSegmentDecorator: refresh()
    is called by every operator that adds, resolves, or removes PI markers
    (ALIGN_OT_draw_horizontal_alignment._finish, ALIGN_OT_apply_pi_curve,
    ALIGN_OT_finish_pi_editing) and installs/keeps installed while the
    alignment has any marker, or uninstalls once none remain.
    """

    is_installed = False
    handlers: list = []
    alignment_id: int | None = None

    RADIUS_PX = 9.0
    COLOR_PENDING = (1.0, 0.35, 0.25, 1.0)  # Red-orange -- still a sharp PI (TANGENT)
    COLOR_DONE = (0.35, 0.9, 0.45, 1.0)  # Green -- curve applied
    COLOR_RING = (0.05, 0.05, 0.05, 0.75)  # Dark outline so the dot reads on any background
    COLOR_LABEL = (1.0, 1.0, 1.0, 1.0)

    @classmethod
    def install(cls, context, alignment_id: int) -> None:
        if cls.is_installed:
            cls.uninstall()
        cls.alignment_id = alignment_id
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw, (context,), "WINDOW", "POST_PIXEL"))
        cls.is_installed = True

    @classmethod
    def uninstall(cls) -> None:
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False
        cls.alignment_id = None

    @classmethod
    def refresh(cls, context, alignment_id: int) -> None:
        """(Re)install for ``alignment_id`` if it still has PI markers, else uninstall."""
        from . import operator as alignment_operator

        if alignment_operator._find_pi_markers(alignment_id):
            cls.install(context, alignment_id)
        else:
            cls.uninstall()

    def draw(self, context):
        # Reads bpy.context rather than the ``context`` captured at install()
        # time -- that captured context can go stale (viewport closed,
        # areas re-split) while this handler stays registered, whereas
        # bpy.context.region/region_data/area reflect whichever region is
        # actually being redrawn right now. Same reasoning as
        # AlignmentSegmentDecorator.draw_segment.
        cls = self.__class__
        if not cls.is_installed or cls.alignment_id is None:
            return

        from . import operator as alignment_operator

        markers = alignment_operator._find_pi_markers(cls.alignment_id)
        if not markers:
            cls.uninstall()
            return

        region = bpy.context.region
        rv3d = bpy.context.region_data
        if not region or not rv3d:
            return

        # Never draw inside the vertical profile area
        pa_ptr = VerticalProfileDecorator.profile_area_ptr
        if pa_ptr != 0:
            try:
                if bpy.context.area is not None and bpy.context.area.as_pointer() == pa_ptr:
                    return
            except Exception:
                pass

        font_id = 0
        font_size = tool.Blender.scale_font_size(11)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)

        gpu.state.blend_set("ALPHA")
        for marker in markers:
            screen = location_3d_to_region_2d(region, rv3d, marker.location)
            if not screen:
                continue
            sx, sy = screen.x, screen.y
            pending = marker.bonsai_pi_curve_marker.curve_type == "TANGENT"
            color = cls.COLOR_PENDING if pending else cls.COLOR_DONE
            self._draw_dot(sx, sy, cls.RADIUS_PX, color, region)

            blf.color(font_id, *cls.COLOR_LABEL)
            blf.position(font_id, sx + cls.RADIUS_PX + 4, sy - font_size * 0.35, 0)
            blf.draw(font_id, f"PI {marker.bonsai_pi_curve_marker.pi_index}")
        gpu.state.blend_set("NONE")
        blf.disable(font_id, blf.SHADOW)

    @classmethod
    def _draw_dot(cls, cx: float, cy: float, radius: float, color: tuple, region, segments: int = 16) -> None:
        perimeter = [
            (
                cx + radius * math.cos(2.0 * math.pi * i / segments),
                cy + radius * math.sin(2.0 * math.pi * i / segments),
                0,
            )
            for i in range(segments)
        ]

        fill_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        fill_shader.bind()
        fill_shader.uniform_float("color", color)
        fill_batch = batch_for_shader(fill_shader, "TRI_FAN", {"pos": [(cx, cy, 0)] + perimeter + [perimeter[0]]})
        fill_batch.draw(fill_shader)

        ring_shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        ring_shader.bind()
        ring_shader.uniform_float("viewportSize", (region.width, region.height))
        ring_shader.uniform_float("lineWidth", 1.5)
        ring_shader.uniform_float("color", cls.COLOR_RING)
        ring_indices = [[i, (i + 1) % segments] for i in range(segments)]
        ring_batch = batch_for_shader(ring_shader, "LINES", {"pos": perimeter}, indices=ring_indices)
        ring_batch.draw(ring_shader)


# ---------------------------------------------------------------------------
# Vertical profile grid helpers
# ---------------------------------------------------------------------------


def _nice_interval(span: float, target_count: int = 8) -> float:
    """Return a round-number grid interval that yields ~target_count lines."""
    if not math.isfinite(span) or span <= 0:
        return 1.0
    rough = span / target_count
    if rough <= 0:
        return 1.0
    magnitude = 10.0 ** math.floor(math.log10(rough))
    normalized = rough / magnitude
    factor = 1.0 if normalized < 1.5 else 2.0 if normalized < 3.5 else 5.0 if normalized < 7.5 else 10.0
    return factor * magnitude


def _dot_tris(centers: list, radius: float, segments: int = 12):
    """Build a triangle-fan mesh for filled circular dots, one per (x, z) in
    ``centers`` (world X/Z plane, Y=0), combined into a single TRIS batch.

    Returns (verts, indices) ready for batch_for_shader(shader, "TRIS", ...).
    """
    verts = []
    indices = []
    for cx, cz in centers:
        base = len(verts)
        verts.append((cx, 0.0, cz))
        for i in range(segments):
            ang = 2.0 * math.pi * i / segments
            verts.append((cx + radius * math.cos(ang), 0.0, cz + radius * math.sin(ang)))
        for i in range(segments):
            indices.append((base, base + 1 + i, base + 1 + (i + 1) % segments))
    return verts, indices


def _frange(start: float, stop: float, step: float):
    """Yield evenly-spaced floats aligned to step boundaries, from start to stop."""
    if step <= 0 or not math.isfinite(start) or not math.isfinite(stop):
        return
    val = math.ceil(start / step - 1e-9) * step
    while val <= stop + step * 1e-6:
        yield val
        val += step


def _fmt_station(dist: float, interval: float, separator: int = 1000) -> str:
    """Format a distance as a civil station string.

    separator=1000 (metric): 12345.0 → '12+345'
    separator=100  (feet):   12345.0 → '123+45'
    """
    major = int(dist) // separator
    minor = dist % separator
    n = len(str(separator - 1))          # digit count for minor part (3 for 1000, 2 for 100)
    if interval >= separator / 10:
        return f"{major}+{int(round(minor)):0{n}d}"
    elif interval >= 1.0:
        return f"{major}+{minor:0{n + 2}.1f}"
    else:
        return f"{major}+{minor:0{n + 3}.2f}"


def _get_length_unit_info(ifc_file) -> tuple[str, int]:
    """Return (symbol, station_separator) for the project's length unit.

    symbol: display string such as "m", "ft", "mm"
    station_separator: the value at which the station '+' splits
        1000 for metric (1+000 = 1000 m)
         100 for feet   (1+00  =  100 ft, matching US practice)
    """
    if not ifc_file:
        return "m", 1000
    try:
        unit = ifcopenshell.util.unit.get_project_unit(ifc_file, "LENGTHUNIT")
        if unit is not None:
            symbol = ifcopenshell.util.unit.get_unit_symbol(unit)
            if symbol and symbol != "?":
                return symbol, (100 if symbol in ("ft", "'") else 1000)
        # Fallback: derive from the SI scale factor
        scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file, "LENGTHUNIT")
        if abs(scale - 0.3048) < 0.01:
            return "ft", 100
        if abs(scale - 0.001) < 1e-5:
            return "mm", 1000
        if abs(scale - 0.01) < 1e-4:
            return "cm", 1000
    except Exception:
        pass
    return "m", 1000


def _fmt_elev(elev: float, interval: float) -> str:
    """Format an elevation with decimal places matched to the grid interval."""
    if interval >= 10.0:
        return f"{elev:.0f}"
    elif interval >= 1.0:
        return f"{elev:.1f}"
    elif interval >= 0.1:
        return f"{elev:.2f}"
    else:
        return f"{elev:.3f}"


class VerticalProfileDecorator:
    """GPU-drawn 2D vertical profile window.

    Opens a dedicated SpaceView3D window in front orthographic mode and draws the
    IfcGradientCurve as a distance-along vs. elevation plot with a fixed, user-
    adjustable vertical exaggeration factor (CivilAlignmentProperties.
    vertical_exaggeration). Zoom is Blender's native orthographic zoom (mouse
    wheel or the corner navigate gizmo's magnifier); panning is Shift+wheel
    (operator.ALIGN_OT_pan_vertical_profile) or the gizmo's pan hand -- same as
    the main viewport, and the exaggeration itself doesn't change as you zoom/pan,
    exactly like zooming the main viewport doesn't stretch a scene. Orbit/rotate
    is continuously suppressed by operator._profile_rotation_guard_tick (a
    bpy.app.timers poll) so the view stays locked front-on.

    Coordinate mapping inside the 3D viewport:
        world X  = distance along alignment, unscaled
        world Z  = (elevation - elev_ref) * ve -- a fixed linear scale (see _ez),
                   not a function of the current view/zoom
        world Y  = 0  (orthographic front view collapses the depth axis)
    """

    is_installed: bool = False
    handlers: list = []
    profile_area = None       # bpy.types.Area reference (may drift after redraws)
    profile_area_ptr: int = 0  # C-level area pointer — stable across Python wrapper churn

    # Profile data computed once on install
    segments_polylines: list = []  # list of [(dist, elev), ...] per segment
    segments_info: list = []       # list of metadata dicts per segment
    available_verticals: list = [] # list of (entity_id, label) for all verticals found
    alignment_name: str = ""

    # Colors for multiple vertical alignments shown simultaneously
    VERTICAL_COLORS = [
        (0.25, 0.85, 0.45, 1.0),  # Green
        (0.45, 0.65, 1.0, 1.0),   # Blue
        (1.0, 0.60, 0.25, 1.0),   # Orange
        (0.85, 0.45, 0.85, 1.0),  # Purple
        (0.95, 0.85, 0.20, 1.0),  # Yellow
    ]
    dist_min: float = 0.0
    dist_max: float = 1.0
    elev_min: float = 0.0
    elev_max: float = 1.0
    unit_symbol: str = "m"         # project length unit display string
    station_separator: int = 1000  # value at which station '+' splits
    _alignment = None              # IfcAlignment entity for station conversion at draw time

    # Fixed vertical exaggeration: world-Z = (elevation - elev_ref) * ve. Both are
    # set once by _refit_zones (from CivilAlignmentProperties.vertical_exaggeration
    # and the data range), not per-frame -- see _ez.
    elev_ref: float = 0.0
    ve: float = 10.0

    # World-Z zone boundaries, derived from elev_ref/ve/the data range by
    # _refit_zones -- fixed until the data or ve changes, not a function of the
    # current view/zoom.
    elev_zone_bot: float = 0.0
    elev_zone_top: float = 1.0
    cant_zone_bot: float = -0.4
    cant_zone_top: float = -0.04

    # Horizontal-zoom self-correction (draw_3d refines fit_view's estimate and
    # re-fits when the pane is resized).
    _xfit_frames: int = 0
    _last_region_wh: tuple = (0, 0)

    # Elevation and cant data ranges visible within their respective zones.
    # Set by fit_view; used by _ez/_cz2 for data→world-Z mapping.
    _e_display_min: float = 0.0
    _e_display_max: float = 1.0
    _c_display_min: float = 0.0
    _c_display_max: float = 0.3

    # Cant profile data (populated alongside elevation data)
    cant_polylines: list = []  # list of [(dist, cant_val), ...] per cant segment
    cant_info: list = []       # list of metadata dicts per cant segment
    available_cants: list = [] # list of (entity_id, label) for all cants found
    has_cant: bool = False
    cant_min: float = 0.0
    cant_max: float = 0.005   # default small span to avoid zero-division

    # Cant zone sizing as fractions of the elevation world-space span.
    # The cant panel sits below the elevation panel separated by a gap.
    # With cant present, elevation occupies 3/4 of total view height and cant
    # occupies 1/4.  cant_h = elev_span/3 gives exactly that 3:1 ratio.
    # The gap (4 % of elev span) visually separates the two graph boxes.
    CANT_HEIGHT_FRACTION: float = 1.0 / 3.0
    CANT_GAP_FRACTION: float = 0.04

    # Cant-specific colors
    CANT_COLORS = [
        (0.45, 0.78, 0.95, 1.0),  # Sky blue
        (0.95, 0.65, 0.35, 1.0),  # Peach
        (0.80, 0.95, 0.45, 1.0),  # Yellow-green
        (0.85, 0.45, 0.85, 1.0),  # Purple
    ]
    # Left / right rail get their own curve and colour.  Cant is the deviating
    # elevation of each rail (sign preserved from the IFC), so the two are
    # plotted independently rather than collapsed to a single difference.
    CANT_COLOR_LEFT = (0.45, 0.78, 0.95, 1.0)   # Sky blue  — left rail
    CANT_COLOR_RIGHT = (0.98, 0.72, 0.38, 1.0)  # Amber     — right rail
    CANT_COLOR_CENTER = (0.62, 0.62, 0.66, 1.0)  # Grey     — centreline
    COLOR_CANT_GRID = (0.22, 0.22, 0.26, 1.0)
    COLOR_CANT_ZERO = (0.50, 0.50, 0.52, 1.0)
    COLOR_CANT_SEP  = (0.48, 0.48, 0.48, 1.0)
    COLOR_CANT_HDR  = (0.75, 0.75, 0.82, 1.0)

    COLOR_GRID = (0.27, 0.27, 0.27, 1.0)       # Subtle dark-gray grid
    COLOR_PROFILE = (0.25, 0.85, 0.45, 1.0)   # Green profile curve
    COLOR_BOUNDARY = (0.90, 0.85, 0.25, 1.0)  # Yellow segment boundary dots
    COLOR_LABEL = (0.80, 0.80, 0.80, 1.0)     # Light-gray axis labels
    COLOR_AXIS_TITLE = (0.65, 0.65, 0.65, 1.0)
    COLOR_HEADER = (0.95, 0.95, 0.95, 1.0)
    COLOR_TANGENT_VERT = (0.70, 0.70, 0.70, 0.75)  # Gray tangent extension lines
    COLOR_BVC = (1.0, 0.78, 0.40, 1.0)             # Warm orange — BVC
    COLOR_EVC = (0.60, 0.88, 1.0, 1.0)             # Light blue — EVC
    COLOR_PVI_VERT = (1.0, 0.90, 0.30, 1.0)         # Yellow — PVI
    COLOR_GRAD = (0.75, 0.95, 0.75, 1.0)            # Light green — gradient endpoints
    LINE_GRID = 1.0
    LINE_PROFILE = 2.5
    LINE_TANGENT_VERT = 1.0

    # ------------------------------------------------------------------ public

    @classmethod
    def install(cls, context, profile_area) -> None:
        """Attach draw handlers to an already-configured profile area."""
        if cls.is_installed:
            cls.uninstall()

        cls.profile_area = profile_area
        cls.profile_area_ptr = profile_area.as_pointer()

        handler = cls()
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_3d, (context,), "WINDOW", "POST_VIEW")
        )
        cls.handlers.append(
            SpaceView3D.draw_handler_add(handler.draw_labels, (context,), "WINDOW", "POST_PIXEL")
        )
        cls.is_installed = True

    @classmethod
    def uninstall(cls) -> None:
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False

        area_ptr = cls.profile_area_ptr
        cls.profile_area = None
        cls.profile_area_ptr = 0
        cls.segments_polylines = []
        cls.segments_info = []
        cls.available_verticals = []
        cls._alignment = None
        cls.cant_polylines = []
        cls.cant_info = []
        cls.available_cants = []
        cls.has_cant = False
        cls.elev_ref = 0.0
        cls.elev_zone_bot = 0.0
        cls.elev_zone_top = 1.0
        cls.cant_zone_bot = -0.4
        cls.cant_zone_top = -0.04
        cls._e_display_min = 0.0
        cls._e_display_max = 1.0
        cls._c_display_min = 0.0
        cls._c_display_max = 0.3

        # Find and close the profile area by its stable C pointer.
        # We search screen.areas fresh rather than reusing the stored Python
        # wrapper, which may have drifted after redraws.
        if area_ptr != 0:
            try:
                target = next(
                    (a for a in bpy.context.screen.areas if a.as_pointer() == area_ptr),
                    None,
                )
                if target is not None:
                    with bpy.context.temp_override(
                        area=target,
                        window=bpy.context.window,
                        screen=bpy.context.screen,
                    ):
                        bpy.ops.screen.area_close()
            except Exception:
                pass

    @classmethod
    def tag_redraw(cls) -> None:
        """Force the profile area to redraw (e.g. when VE slider changes)."""
        if not cls.is_installed or cls.profile_area_ptr == 0:
            return
        try:
            cls.profile_area.tag_redraw()
        except Exception:
            pass

    @classmethod
    def _refit_zones(cls) -> None:
        """(Re)derive the fixed elevation/cant zone bounds from the data, the
        current vertical exaggeration, and the cant range.

        Unlike the old per-frame _recompute_zones this replaces, the result depends
        only on the data and ve -- never on the current view/zoom -- so it only
        needs to run when either of those changes (_compute_profile, fit_view, a
        resize, or the vertical_exaggeration property), not every frame.
        """
        try:
            cls.ve = bpy.context.scene.CivilAlignmentProperties.vertical_exaggeration
        except Exception:
            pass
        if not cls.ve or cls.ve <= 0:
            cls.ve = 10.0

        cls.elev_ref = (cls.elev_min + cls.elev_max) * 0.5

        # Elevation display range: at least 1 m visible so flat profiles show a usable axis.
        e_span = max(cls.elev_max - cls.elev_min, 0.0)
        e_pad = max(e_span * 0.10, 1.0)
        cls._e_display_min = cls.elev_min - e_pad * 0.05
        cls._e_display_max = cls._e_display_min + max(e_span, 0.0) + e_pad

        cls.elev_zone_bot = (cls._e_display_min - cls.elev_ref) * cls.ve
        cls.elev_zone_top = (cls._e_display_max - cls.elev_ref) * cls.ve

        if cls.has_cant:
            # Cant panel sits below the elevation panel, sized/gapped as fixed
            # fractions of the (now fixed) elevation zone height.
            elev_h = cls.elev_zone_top - cls.elev_zone_bot
            cant_h = elev_h * cls.CANT_HEIGHT_FRACTION
            gap_h = elev_h * cls.CANT_GAP_FRACTION
            cls.cant_zone_top = cls.elev_zone_bot - gap_h
            cls.cant_zone_bot = cls.cant_zone_top - cant_h

            # Cant display range with 5 % padding on each side
            c_span = max(cls.cant_max - cls.cant_min, 0.0)
            c_pad = max(c_span * 0.10, 0.001)
            cls._c_display_min = cls.cant_min - c_pad * 0.05
            cls._c_display_max = cls.cant_max + c_pad * 0.95

    @classmethod
    def fit_view(cls, space, area_width: int = 1920, area_height: int = 400) -> None:
        """Reposition the profile camera so the fixed data+VE layout is fully visible.

        Chooses view_distance as a "contain" fit of both axes -- whichever of the
        horizontal (distance) or vertical (elevation*ve, plus cant if present)
        extent needs more room at the given area's aspect ratio wins, so neither
        axis is cropped. This is only an initial estimate — draw_3d refines it
        against the real projection (and re-fits on resize).
        """
        cls._refit_zones()

        h_span = max(cls.dist_max - cls.dist_min, 1.0)
        z_bot = cls.cant_zone_bot if cls.has_cant else cls.elev_zone_bot
        z_span = max(cls.elev_zone_top - z_bot, 1.0)

        # An ortho VIEW_3D shows ~1.08x its view_distance in world height, so the
        # distance that frames h_span across ~86% of the pane width is
        # vd = h_span * (H/W) / (0.86 * 1.08); framing z_span across ~90% of the
        # pane height is vd = z_span / (0.90 * 1.08). Take whichever is larger so
        # both axes fit (one may end up with extra margin — expected/correct).
        ar = area_height / max(area_width, 1)
        vd_for_x = h_span * ar / (0.86 * 1.08)
        vd_for_z = z_span / (0.90 * 1.08)
        vd = max(vd_for_x, vd_for_z, 1.0)

        mid_d = (cls.dist_min + cls.dist_max) * 0.5
        mid_z = (cls.elev_zone_top + z_bot) * 0.5
        space.region_3d.view_location = mathutils.Vector((mid_d, 0.0, mid_z))
        space.region_3d.view_distance = vd
        cls._xfit_frames = 6
        cls._last_region_wh = (0, 0)

    # --------------------------------------------------------------- geometry

    @classmethod
    def _compute_profile(cls, alignment) -> None:
        cls.segments_polylines = []
        cls.segments_info = []
        cls.available_verticals = []
        cls.alignment_name = alignment.Name or "(unnamed)"
        cls.unit_symbol, cls.station_separator = _get_length_unit_info(tool.Ifc.get())
        cls._alignment = alignment

        all_dists: list[float] = []
        all_elevs: list[float] = []

        # Collect all IfcAlignmentVertical layouts: those directly nested under
        # the alignment AND those under child alignments (IFC CT 4.1.4.4.1.2).
        vertical_layouts = tool.Alignment.get_all_vertical_layouts(alignment)

        for layout_entity in vertical_layouts:
            v_id = layout_entity.id()
            v_label = layout_entity.Name or f"V{len(cls.available_verticals) + 1}"
            color_idx = len(cls.available_verticals)
            cls.available_verticals.append((v_id, v_label))

            real_segments = []  # entities, in order, for this vertical only

            for seg_rel in getattr(layout_entity, "IsNestedBy", []) or []:
                for seg in seg_rel.RelatedObjects or []:
                    if not seg.is_a("IfcAlignmentSegment"):
                        continue
                    dp = seg.DesignParameters
                    if not dp:
                        continue

                    dist = getattr(dp, "StartDistAlong", 0.0) or 0.0
                    height = getattr(dp, "StartHeight", 0.0) or 0.0
                    h_len = getattr(dp, "HorizontalLength", 0.0) or 0.0
                    g_start = getattr(dp, "StartGradient", 0.0) or 0.0
                    g_end = getattr(dp, "EndGradient", g_start) or g_start
                    seg_type = dp.PredefinedType or "UNKNOWN"

                    if h_len <= 0:
                        continue

                    real_segments.append(seg)
                    pts = cls._sample_segment(dist, height, h_len, g_start, g_end, seg_type)
                    cls.segments_polylines.append(pts)
                    cls.segments_info.append(
                        {
                            "dist": dist,
                            "height": height,
                            "h_len": h_len,
                            "g_start": g_start,
                            "g_end": g_end,
                            "type": seg_type,
                            "vertical_id": v_id,
                            "vertical_label": v_label,
                            "color_idx": color_idx,
                            "segment_id": seg.id(),
                        }
                    )
                    all_dists.extend(d for d, _ in pts)
                    all_elevs.extend(e for _, e in pts)

            # Key-point labels (P.V.C., P.V.I., P.V.T., V.C.C., V.P.O.B., V.P.O.E.) --
            # shares _get_segment_start_point_label with update_key_point_referents and
            # AlignmentSegmentDecorator's horizontal labeling, so these always agree with
            # the IfcReferents that function creates, including any jurisdiction-specific
            # naming registered via register_referent_name_callback().
            n = len(real_segments)
            start_index = len(cls.segments_info) - n
            for k, seg in enumerate(real_segments):
                prev_seg = real_segments[k - 1] if k > 0 else None
                next_seg = real_segments[k + 1] if k + 1 < n else None
                info = cls.segments_info[start_index + k]
                info["start_label"] = _get_segment_start_point_label(prev_seg, seg)
                info["end_label"] = _get_segment_start_point_label(seg, next_seg)

        if all_dists:
            cls.dist_min = min(all_dists)
            cls.dist_max = max(all_dists)
            cls.elev_min = min(all_elevs)
            cls.elev_max = max(all_elevs)
        else:
            # No vertical geometry yet — e.g. opening the profile view to draw
            # the first one. Frame the canvas to the horizontal alignment's
            # own length instead of leaving stale/default 0..1 bounds, so
            # there's a sensible drawing surface to click PIs onto.
            h_layout = ifcopenshell.api.alignment.get_horizontal_layout(alignment)
            h_length = tool.Alignment.get_horizontal_alignment_length(h_layout) if h_layout else 0.0
            cls.dist_min = 0.0
            cls.dist_max = max(h_length, 1.0)
            cls.elev_min = 0.0
            cls.elev_max = max(h_length * 0.1, 10.0)

        # Collect cant data (plotted below the elevation profile)
        cls._collect_cant_data(alignment)

        # Compute BVC / EVC / PVI geometry for each segment.
        # BVC = start, EVC = end (from sampled polyline for accuracy).
        # PVI = tangent intersection at dist + h_len/2 (parabolic arcs always have PVI at midpoint).
        for i, info in enumerate(cls.segments_info):
            pts = cls.segments_polylines[i] if i < len(cls.segments_polylines) else []
            bvc_d = info["dist"]
            bvc_e = info["height"]
            if pts:
                evc_d, evc_e = pts[-1]
            else:
                evc_d = bvc_d + info["h_len"]
                evc_e = bvc_e + info["g_start"] * info["h_len"]
            is_curve = info["type"] not in ("CONSTANTGRADIENT",)
            pvi = None
            if is_curve and abs(info["g_start"] - info["g_end"]) > 1e-10:
                pvi_d = bvc_d + info["h_len"] / 2.0
                pvi_e = bvc_e + info["g_start"] * info["h_len"] / 2.0
                pvi = (pvi_d, pvi_e)
            info["bvc"] = (bvc_d, bvc_e)
            info["evc"] = (evc_d, evc_e)
            info["pvi"] = pvi
            info["is_curve"] = is_curve

        # New data means the fixed elevation/cant zones (and the VE they're built
        # from) need recomputing -- see _refit_zones.
        cls._refit_zones()

    @classmethod
    def _collect_cant_data(cls, alignment) -> None:
        """Collect IfcAlignmentCant segments and build the cant profile arrays."""
        cls.cant_polylines = []
        cls.cant_info = []
        cls.available_cants = []
        cls.has_cant = False
        cls.cant_min = 0.0
        cls.cant_max = 0.005

        # Cant layouts directly nested under the alignment
        cant_layouts = []
        for rel in getattr(alignment, "IsNestedBy", []) or []:
            for obj in rel.RelatedObjects or []:
                if obj.is_a("IfcAlignmentCant"):
                    cant_layouts.append(obj)

        # Cant layouts on child alignments (IFC CT 4.1.4.4.1.2 pattern)
        for rel in getattr(alignment, "IsDecomposedBy", []) or []:
            for child in rel.RelatedObjects or []:
                if not child.is_a("IfcAlignment"):
                    continue
                for crel in getattr(child, "IsNestedBy", []) or []:
                    for obj in crel.RelatedObjects or []:
                        if obj.is_a("IfcAlignmentCant"):
                            cant_layouts.append(obj)

        if not cant_layouts:
            return

        all_vals: list[float] = []

        for cant_layout in cant_layouts:
            c_id = cant_layout.id()
            # Prefer the owning alignment name as the label
            c_label = cant_layout.Name or f"Cant #{c_id}"
            for rel in getattr(cant_layout, "Nests", []) or []:
                if rel.RelatingObject.is_a("IfcAlignment"):
                    c_label = rel.RelatingObject.Name or c_label
                    break
            color_idx = len(cls.available_cants)
            cls.available_cants.append((c_id, c_label))

            for seg_rel in getattr(cant_layout, "IsNestedBy", []) or []:
                for seg in seg_rel.RelatedObjects or []:
                    if not seg.is_a("IfcAlignmentSegment"):
                        continue
                    dp = seg.DesignParameters
                    if not dp:
                        continue

                    dist = getattr(dp, "StartDistAlong", 0.0) or 0.0
                    h_len = getattr(dp, "HorizontalLength", None)
                    if h_len is None:
                        h_len = getattr(dp, "Length", 0.0) or 0.0
                    seg_type = getattr(dp, "PredefinedType", "?") or "?"

                    if h_len <= 0:
                        continue

                    start_l = getattr(dp, "StartCantLeft", 0.0) or 0.0
                    start_r = getattr(dp, "StartCantRight", 0.0) or 0.0
                    end_l = getattr(dp, "EndCantLeft", None)
                    end_r = getattr(dp, "EndCantRight", None)
                    end_l = start_l if end_l is None else end_l
                    end_r = start_r if end_r is None else end_r

                    # Three curves: centreline deviating elevation and each
                    # railhead.  Railhead deviating elevation == the matching
                    # Start/EndCant{Left,Right}; centreline == their mean.  Every
                    # curve follows the segment's named transition shape.
                    rails = (
                        ("C", 0.5 * (start_l + start_r), 0.5 * (end_l + end_r)),
                        ("L", start_l, end_l),
                        ("R", start_r, end_r),
                    )
                    for rail, s_val, e_val in rails:
                        pts = cls._sample_cant_segment(dist, h_len, s_val, e_val, seg_type)
                        cls.cant_polylines.append(pts)
                        cls.cant_info.append({
                            "dist": dist,
                            "h_len": h_len,
                            "rail": rail,
                            "start_cant": s_val,
                            "end_cant": e_val,
                            "type": seg_type,
                            "cant_id": c_id,
                            "cant_label": c_label,
                            "color_idx": color_idx,
                            "segment_id": seg.id(),
                        })
                        all_vals.extend(v for _, v in pts)

        if not all_vals:
            return

        cls.has_cant = True
        cls.cant_min = min(all_vals)
        cls.cant_max = max(all_vals)
        # Enforce a minimum visible span of 5 mm so the profile never collapses to a line
        if cls.cant_max - cls.cant_min < 0.005:
            mid = (cls.cant_max + cls.cant_min) / 2
            cls.cant_min = mid - 0.0025
            cls.cant_max = mid + 0.0025

    @staticmethod
    def _cant_transition_factor(u: float, seg_type: str) -> float:
        """Fraction (0..1) of the cant change completed at normalised position u.

        Closed-form of each IfcAlignmentCantSegment transition shape — matches
        the parent-curve the IFC geometry mapping builds
        (ifcopenshell.api.alignment._map_alignment_cant_segment).
        """
        if u <= 0.0:
            return 0.0
        if u >= 1.0:
            return 1.0
        if seg_type in ("LINEARTRANSITION", "CONSTANTCANT"):
            return u
        if seg_type == "BLOSSCURVE":
            return 3.0 * u * u - 2.0 * u * u * u
        if seg_type == "COSINECURVE":
            return (1.0 - math.cos(math.pi * u)) * 0.5
        if seg_type == "SINECURVE":
            return u - math.sin(2.0 * math.pi * u) / (2.0 * math.pi)
        if seg_type == "HELMERTCURVE":
            return 2.0 * u * u if u <= 0.5 else 1.0 - 2.0 * (1.0 - u) ** 2
        # VIENNESEBEND (couples with the horizontal) and anything unknown —
        # a cubic S-curve is the closest single-segment approximation.
        return 3.0 * u * u - 2.0 * u * u * u

    @classmethod
    def _sample_cant_segment(
        cls,
        dist: float,
        h_len: float,
        cant_start: float,
        cant_end: float,
        seg_type: str,
        n: int | None = None,
    ) -> list[tuple[float, float]]:
        """Return a polyline of one rail's deviating elevation over a cant segment."""
        d = cant_end - cant_start
        if seg_type == "CONSTANTCANT" or abs(d) < 1e-12:
            return [(dist, cant_start), (dist + h_len, cant_start)]
        if n is None:
            n = 2 if seg_type == "LINEARTRANSITION" else 24
        return [
            (dist + (i / n) * h_len,
             cant_start + d * cls._cant_transition_factor(i / n, seg_type))
            for i in range(n + 1)
        ]

    @staticmethod
    def _sample_segment(
        dist: float,
        height: float,
        h_len: float,
        g_start: float,
        g_end: float,
        seg_type: str,
        n: int = 48,
    ) -> list[tuple[float, float]]:
        """Return a polyline approximation of one vertical segment."""
        if seg_type == "CONSTANTGRADIENT":
            return [(dist, height), (dist + h_len, height + h_len * g_start)]

        # Parabolic blending covers PARABOLICARC, CIRCULARARC, CLOTHOID, and
        # other transition types to a good visual approximation.
        # h(t) = h0 + g1·t + (g2−g1)/(2L)·t²
        pts = []
        dg_over_2L = (g_end - g_start) / (2.0 * h_len)
        for i in range(n + 1):
            t = h_len * i / n
            pts.append((dist + t, height + g_start * t + dg_over_2L * t * t))
        return pts

    @classmethod
    def _dist_to_station_str(cls, dist_along: float, interval: float = 1.0) -> str:
        """Convert a distance-along value to a formatted station string.

        Delegates to ifcopenshell.api.alignment.station_from_distance_along so that
        beginning station and any station equations are accounted for.
        """
        try:
            import ifcopenshell.api.alignment as _ali
            if cls._alignment is not None:
                station = _ali.station_from_distance_along(tool.Ifc.get(), cls._alignment, dist_along)
                return _fmt_station(station, interval, cls.station_separator)
        except Exception:
            pass
        return _fmt_station(dist_along, interval, cls.station_separator)

    @classmethod
    def _ez(cls, e: float) -> float:
        """Map an elevation data value to world-Z via the fixed vertical exaggeration."""
        return (e - cls.elev_ref) * cls.ve

    @classmethod
    def screen_to_data(
        cls, region: "bpy.types.Region", rv3d: "bpy.types.RegionView3D", mouse_x: float, mouse_y: float
    ) -> Optional[Tuple[float, float]]:
        """Convert a region-relative mouse position to (distance_along, elevation).

        ``region``/``rv3d`` must be looked up explicitly by the caller (e.g.
        by matching profile_area_ptr against context.screen.areas) rather
        than taken from context.region/context.region_data — during a modal
        operator's event handling, those don't reliably track wherever the
        mouse currently is when it's over an area *other than* the one the
        operator was invoked from, unlike draw handlers (which Blender calls
        per-area with correct context). Getting this wrong means every event
        looks like it's outside the profile area, so clicks silently do
        nothing — see ALIGN_OT_draw_vertical_alignment._locate_profile_view.

        Inverse of _ez (world X is distance-along directly; world Z is a fixed
        linear function of elevation, so no per-call zone resync is needed).

        Returns None if there's no valid region/view to project against.
        """
        if not region or not rv3d:
            return None

        ref = (cls.dist_min, 0.0, (cls.elev_zone_bot + cls.elev_zone_top) * 0.5)
        point = region_2d_to_location_3d(region, rv3d, (mouse_x, mouse_y), ref)
        if point is None:
            return None

        elevation = point.z / cls.ve + cls.elev_ref
        return point.x, elevation

    @classmethod
    def _cz2(cls, v: float) -> float:
        """Map a cant data value to world-Z within the cant zone."""
        c_span = max(cls._c_display_max - cls._c_display_min, 1e-10)
        t = (v - cls._c_display_min) / c_span
        return cls.cant_zone_bot + t * (cls.cant_zone_top - cls.cant_zone_bot)

    # ---------------------------------------------------------------- drawing

    def draw_3d(self, context) -> None:
        """Draw grid, profile polylines, and boundary ticks in 3D world space (POST_VIEW)."""
        try:
            if bpy.context.area is None or bpy.context.area.as_pointer() != self.__class__.profile_area_ptr:
                return
        except Exception:
            return

        cls = self.__class__
        region = bpy.context.region
        rv3d = bpy.context.region_data
        if not region or not rv3d:
            return

        try:
            props = bpy.context.scene.CivilAlignmentProperties
        except Exception:
            return

        # Visible vertical IDs (None = show all)
        visible_ids: set | None = None
        try:
            if props.vertical_items:
                visible_ids = {item.entity_id for item in props.vertical_items if item.is_visible}
        except Exception:
            pass

        # --- Visible world extents from screen corners -------------------------
        ref = (cls.dist_min, 0.0, (cls.elev_zone_bot + cls.elev_zone_top) * 0.5)
        bl = region_2d_to_location_3d(region, rv3d, (0, 0), ref)
        tr = region_2d_to_location_3d(region, rv3d, (region.width, region.height), ref)
        if bl is None or tr is None:
            return

        vis_d_min, vis_d_max = bl.x, tr.x
        vis_z_min, vis_z_max = bl.z, tr.z

        # --- Zoom self-correction (both axes) --------------------------------
        # fit_view can only estimate the ortho projection; nail the real framing
        # here so the whole alignment (and the fixed elevation/cant zones) are on
        # screen, and re-fit whenever the pane is resized. Zones themselves are
        # fixed (see _refit_zones) — only the camera's view_distance is corrected,
        # exactly like the main viewport doesn't restretch a scene as you zoom.
        wh = (region.width, region.height)
        if wh != cls._last_region_wh:
            cls._last_region_wh = wh
            cls._xfit_frames = 6
        if cls._xfit_frames > 0:
            cls._xfit_frames -= 1
            vis_span_x = vis_d_max - vis_d_min
            vis_span_z = vis_z_max - vis_z_min
            data_span_x = max(cls.dist_max - cls.dist_min, 1e-6)
            z_bot = cls.cant_zone_bot if cls.has_cant else cls.elev_zone_bot
            data_span_z = max(cls.elev_zone_top - z_bot, 1e-6)
            ratio_x = (data_span_x / 0.88) / vis_span_x if vis_span_x > 1e-6 else 1.0  # fills ~88% of width
            ratio_z = (data_span_z / 0.92) / vis_span_z if vis_span_z > 1e-6 else 1.0  # fills ~92% of height
            ratio = max(ratio_x, ratio_z)  # whichever axis needs more room wins (contain fit)
            if abs(ratio - 1.0) > 0.02:
                # Adjust and repaint next frame; this frame still draws
                # (one slightly-off frame reads better than a blank flash).
                try:
                    rv3d.view_distance = max(rv3d.view_distance * ratio, 1.0)
                    mid_z = (cls.elev_zone_top + z_bot) * 0.5
                    rv3d.view_location = mathutils.Vector(
                        ((cls.dist_min + cls.dist_max) * 0.5, 0.0, mid_z)
                    )
                    bpy.context.area.tag_redraw()
                except Exception:
                    pass
            else:
                cls._xfit_frames = 0

        # Small padding so grid lines fully cover the viewport edges
        d_pad = (vis_d_max - vis_d_min) * 0.02
        z_pad = (vis_z_max - vis_z_min) * 0.02

        d_interval = _nice_interval(vis_d_max - vis_d_min, 8)
        # Zone boundaries in world-Z (shortcuts used throughout draw_3d)
        z_elev_bot = cls.elev_zone_bot
        z_elev_top = cls.elev_zone_top
        # Elevation display range for grid intervals
        vis_e_min_clamp = cls._e_display_min
        vis_e_max_clamp = cls._e_display_max
        e_interval = _nice_interval(max(vis_e_max_clamp - vis_e_min_clamp, 1e-6), 6)

        # --- Solid background — covers the 3D scene objects that the split
        # VIEW_3D would otherwise show (horizontal alignment geometry, etc.).
        # Drawn with depth_test NONE so it always writes over scene content.
        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")
        bg_margin = max(abs(vis_d_max - vis_d_min), abs(vis_z_max - vis_z_min)) * 0.5 + 1e4
        bg_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        bg_shader.bind()
        bg_shader.uniform_float("color", (0.11, 0.11, 0.11, 1.0))
        bg_verts = [
            (vis_d_min - bg_margin, 0.0, vis_z_min - bg_margin),
            (vis_d_max + bg_margin, 0.0, vis_z_min - bg_margin),
            (vis_d_max + bg_margin, 0.0, vis_z_max + bg_margin),
            (vis_d_min - bg_margin, 0.0, vis_z_max + bg_margin),
        ]
        batch_for_shader(
            bg_shader, "TRIS", {"pos": bg_verts}, indices=[(0, 1, 2), (0, 2, 3)]
        ).draw(bg_shader)

        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("NONE")

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()
        shader.uniform_float("viewportSize", (region.width, region.height))

        # --- Grid lines (drawn first so profile renders on top) ---------------
        shader.uniform_float("lineWidth", cls.LINE_GRID)
        shader.uniform_float("color", cls.COLOR_GRID)

        # Vertical station grid lines
        for d in _frange(vis_d_min, vis_d_max, d_interval):
            batch = batch_for_shader(
                shader, "LINES",
                {"pos": [(d, 0.0, vis_z_min - z_pad), (d, 0.0, vis_z_max + z_pad)]},
                indices=[[0, 1]],
            )
            batch.draw(shader)

        # Horizontal elevation grid lines — clipped to the elevation zone only
        for e in _frange(vis_e_min_clamp, vis_e_max_clamp, e_interval):
            z = cls._ez(e)
            if z < z_elev_bot - 1e-6 or z > z_elev_top + 1e-6:
                continue
            batch = batch_for_shader(
                shader, "LINES",
                {"pos": [(vis_d_min - d_pad, 0.0, z), (vis_d_max + d_pad, 0.0, z)]},
                indices=[[0, 1]],
            )
            batch.draw(shader)

        # --- Profile segments -------------------------------------------------
        shader.uniform_float("lineWidth", cls.LINE_PROFILE)
        for pts, info in zip(cls.segments_polylines, cls.segments_info):
            if visible_ids is not None and info.get("vertical_id", -1) not in visible_ids:
                continue
            verts = [(d, 0.0, cls._ez(e)) for d, e in pts]
            if len(verts) < 2:
                continue
            color = cls.VERTICAL_COLORS[info.get("color_idx", 0) % len(cls.VERTICAL_COLORS)]
            shader.uniform_float("color", color)
            edges = [[i, i + 1] for i in range(len(verts) - 1)]
            batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=edges)
            batch.draw(shader)

        # --- Highlighted selected vertical segment (drawn on top) ------------
        selected_v_id = 0
        try:
            selected_v_id = props.selected_v_segment_id
        except Exception:
            pass

        if selected_v_id:
            shader.uniform_float("lineWidth", cls.LINE_PROFILE + 2.0)
            shader.uniform_float("color", (1.0, 0.55, 0.0, 1.0))  # Orange
            for pts, info in zip(cls.segments_polylines, cls.segments_info):
                if info.get("segment_id") != selected_v_id:
                    continue
                if visible_ids is not None and info.get("vertical_id", -1) not in visible_ids:
                    continue
                verts = [(d, 0.0, cls._ez(e)) for d, e in pts]
                if len(verts) < 2:
                    continue
                edges = [[i, i + 1] for i in range(len(verts) - 1)]
                batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=edges)
                batch.draw(shader)

        # --- Segment boundary dots --------------------------------------------
        # Sized in screen pixels (like lineWidth) rather than world units, so
        # the dot stays a fixed on-screen size — matching the profile line's
        # weight — instead of ballooning at zoomed-in scales.
        world_per_px = (vis_d_max - vis_d_min) / max(region.width, 1)
        dot_r = cls.LINE_PROFILE * world_per_px
        dot_centers = [
            (info["dist"], cls._ez(info["height"]))
            for info in cls.segments_info
            if visible_ids is None or info.get("vertical_id", -1) in visible_ids
        ]
        if dot_centers:
            dot_verts, dot_indices = _dot_tris(dot_centers, dot_r)
            dot_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
            dot_shader.bind()
            dot_shader.uniform_float("color", cls.COLOR_BOUNDARY)
            batch_for_shader(dot_shader, "TRIS", {"pos": dot_verts}, indices=dot_indices).draw(dot_shader)
            shader.bind()

        # --- Vertical curve tangent lines (BVC→PVI and EVC→PVI) --------------
        shader.uniform_float("lineWidth", cls.LINE_TANGENT_VERT)
        shader.uniform_float("color", cls.COLOR_TANGENT_VERT)
        for info in cls.segments_info:
            if visible_ids is not None and info.get("vertical_id", -1) not in visible_ids:
                continue
            if not info.get("is_curve") or info.get("pvi") is None:
                continue
            bvc_d, bvc_e = info["bvc"]
            evc_d, evc_e = info["evc"]
            pvi_d, pvi_e = info["pvi"]
            bvc_w = (bvc_d, 0.0, cls._ez(bvc_e))
            evc_w = (evc_d, 0.0, cls._ez(evc_e))
            pvi_w = (pvi_d, 0.0, cls._ez(pvi_e))
            for a_pt, b_pt in [(bvc_w, pvi_w), (evc_w, pvi_w)]:
                batch = batch_for_shader(
                    shader, "LINES", {"pos": [a_pt, b_pt]}, indices=[[0, 1]]
                )
                batch.draw(shader)

        # --- Elevation subplot — full 4-sided border box ----------------------
        AXIS_COLOR = (0.55, 0.55, 0.55, 1.0)
        shader.uniform_float("lineWidth", 1.5)
        shader.uniform_float("color", AXIS_COLOR)
        # Left Y-axis
        batch_for_shader(shader, "LINES",
            {"pos": [(cls.dist_min, 0.0, z_elev_bot),
                     (cls.dist_min, 0.0, z_elev_top)]},
            indices=[[0, 1]]).draw(shader)
        # Right border
        batch_for_shader(shader, "LINES",
            {"pos": [(cls.dist_max, 0.0, z_elev_bot),
                     (cls.dist_max, 0.0, z_elev_top)]},
            indices=[[0, 1]]).draw(shader)
        # Bottom border
        batch_for_shader(shader, "LINES",
            {"pos": [(cls.dist_min, 0.0, z_elev_bot),
                     (cls.dist_max, 0.0, z_elev_bot)]},
            indices=[[0, 1]]).draw(shader)
        # Top border
        batch_for_shader(shader, "LINES",
            {"pos": [(cls.dist_min, 0.0, z_elev_top),
                     (cls.dist_max, 0.0, z_elev_top)]},
            indices=[[0, 1]]).draw(shader)

        # ================================================================
        # --- Cant zone (plotted below elevation, separate Y axis) -----
        # ================================================================
        if cls.has_cant and cls.cant_polylines:
            visible_cant_ids: set | None = None
            try:
                if props.cant_items:
                    visible_cant_ids = {it.entity_id for it in props.cant_items if it.is_visible}
            except Exception:
                pass

            cant_z_top = cls.cant_zone_top
            cant_z_bot = cls.cant_zone_bot
            cant_h = cant_z_top - cant_z_bot
            _cz = cls._cz2

            # Background — slightly distinct shade so the cant zone reads as
            # a separate panel from the elevation zone above it.
            gpu.state.blend_set("NONE")
            gpu.state.depth_test_set("NONE")
            bg2 = gpu.shader.from_builtin("UNIFORM_COLOR")
            bg2.bind()
            bg2.uniform_float("color", (0.12, 0.12, 0.14, 1.0))
            bg2_verts = [
                (vis_d_min - d_pad, 0.0, cant_z_bot),
                (vis_d_max + d_pad, 0.0, cant_z_bot),
                (vis_d_max + d_pad, 0.0, cant_z_top),
                (vis_d_min - d_pad, 0.0, cant_z_top),
            ]
            batch_for_shader(bg2, "TRIS", {"pos": bg2_verts},
                             indices=[(0, 1, 2), (0, 2, 3)]).draw(bg2)

            gpu.state.blend_set("ALPHA")
            gpu.state.depth_test_set("NONE")

            # Re-bind the polyline shader — drawing the background quad above
            # left the UNIFORM_COLOR shader bound, so every subsequent
            # shader.uniform_float() call would target the wrong program and the
            # entire cant zone (zero line, grid, polylines, ticks, border) would
            # silently fail to render.
            shader.bind()
            shader.uniform_float("viewportSize", (region.width, region.height))

            # Zero-cant reference line
            zero_z = _cz(0.0)
            if cant_z_bot <= zero_z <= cant_z_top:
                shader.uniform_float("lineWidth", 1.2)
                shader.uniform_float("color", cls.COLOR_CANT_ZERO)
                batch_for_shader(shader, "LINES",
                    {"pos": [(vis_d_min - d_pad, 0.0, zero_z),
                             (vis_d_max + d_pad, 0.0, zero_z)]},
                    indices=[[0, 1]]).draw(shader)

            # Cant grid lines (4–5 horizontal lines covering the cant range)
            c_disp_span = max(cls._c_display_max - cls._c_display_min, 1e-10)
            cant_interval = _nice_interval(c_disp_span, 4)
            shader.uniform_float("lineWidth", cls.LINE_GRID)
            shader.uniform_float("color", cls.COLOR_CANT_GRID)
            for cv in _frange(cls._c_display_min, cls._c_display_max, cant_interval):
                gz = _cz(cv)
                if cant_z_bot - 1e-6 <= gz <= cant_z_top + 1e-6:
                    batch_for_shader(shader, "LINES",
                        {"pos": [(vis_d_min - d_pad, 0.0, gz),
                                 (vis_d_max + d_pad, 0.0, gz)]},
                        indices=[[0, 1]]).draw(shader)

            # Cant polylines — centreline + one per rail, coloured by role
            _rail_color = {
                "C": cls.CANT_COLOR_CENTER,
                "L": cls.CANT_COLOR_LEFT,
                "R": cls.CANT_COLOR_RIGHT,
            }
            for pts, info in zip(cls.cant_polylines, cls.cant_info):
                if visible_cant_ids is not None and info.get("cant_id", -1) not in visible_cant_ids:
                    continue
                verts = [(d, 0.0, _cz(v)) for d, v in pts]
                if len(verts) < 2:
                    continue
                rail = info.get("rail", "L")
                shader.uniform_float("lineWidth", 1.4 if rail == "C" else cls.LINE_PROFILE)
                shader.uniform_float("color", _rail_color.get(rail, cls.CANT_COLOR_LEFT))
                edges = [[i, i + 1] for i in range(len(verts) - 1)]
                batch_for_shader(shader, "LINES", {"pos": verts}, indices=edges).draw(shader)

            # Selected cant segment highlight (orange, thicker)
            selected_cant_id = 0
            try:
                selected_cant_id = props.selected_cant_segment_id
            except Exception:
                pass
            if selected_cant_id:
                shader.uniform_float("lineWidth", cls.LINE_PROFILE + 2.0)
                shader.uniform_float("color", (1.0, 0.55, 0.0, 1.0))
                for pts, info in zip(cls.cant_polylines, cls.cant_info):
                    if info.get("segment_id") != selected_cant_id:
                        continue
                    if visible_cant_ids is not None and info.get("cant_id", -1) not in visible_cant_ids:
                        continue
                    verts = [(d, 0.0, _cz(v)) for d, v in pts]
                    if len(verts) < 2:
                        continue
                    edges = [[i, i + 1] for i in range(len(verts) - 1)]
                    batch_for_shader(shader, "LINES", {"pos": verts}, indices=edges).draw(shader)

            # Cant segment boundary dots (same fixed screen-pixel sizing as the
            # elevation zone's — world_per_px is shared across the whole view).
            dot_r_c = cls.LINE_PROFILE * world_per_px
            cant_dot_centers = [
                (info["dist"], _cz(info["start_cant"]))
                for info in cls.cant_info
                if info.get("rail") != "C"
                and (visible_cant_ids is None or info.get("cant_id", -1) in visible_cant_ids)
            ]
            if cant_dot_centers:
                cant_dot_verts, cant_dot_indices = _dot_tris(cant_dot_centers, dot_r_c)
                cant_dot_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
                cant_dot_shader.bind()
                cant_dot_shader.uniform_float("color", cls.COLOR_BOUNDARY)
                batch_for_shader(
                    cant_dot_shader, "TRIS", {"pos": cant_dot_verts}, indices=cant_dot_indices
                ).draw(cant_dot_shader)
                shader.bind()

            # Cant subplot — full 4-sided border box (right side = cant Y-axis)
            shader.uniform_float("lineWidth", 1.5)
            shader.uniform_float("color", (0.55, 0.55, 0.55, 1.0))
            # Left border
            batch_for_shader(shader, "LINES",
                {"pos": [(cls.dist_min, 0.0, cant_z_bot),
                         (cls.dist_min, 0.0, cant_z_top)]},
                indices=[[0, 1]]).draw(shader)
            # Right border (cant Y-axis)
            batch_for_shader(shader, "LINES",
                {"pos": [(cls.dist_max, 0.0, cant_z_bot),
                         (cls.dist_max, 0.0, cant_z_top)]},
                indices=[[0, 1]]).draw(shader)
            # Bottom border
            batch_for_shader(shader, "LINES",
                {"pos": [(cls.dist_min, 0.0, cant_z_bot),
                         (cls.dist_max, 0.0, cant_z_bot)]},
                indices=[[0, 1]]).draw(shader)
            # Top border
            batch_for_shader(shader, "LINES",
                {"pos": [(cls.dist_min, 0.0, cant_z_top),
                         (cls.dist_max, 0.0, cant_z_top)]},
                indices=[[0, 1]]).draw(shader)

        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")

    def draw_labels(self, context) -> None:
        """Draw axis labels, grid tick labels, header, and segment callouts (POST_PIXEL)."""
        try:
            if bpy.context.area is None or bpy.context.area.as_pointer() != self.__class__.profile_area_ptr:
                return
        except Exception:
            return

        cls = self.__class__
        region = bpy.context.region
        rv3d = bpy.context.region_data
        if not region or not rv3d:
            return

        try:
            props = bpy.context.scene.CivilAlignmentProperties
        except Exception:
            return

        # Visible vertical IDs (None = show all)
        visible_ids: set | None = None
        try:
            if props.vertical_items:
                visible_ids = {item.entity_id for item in props.vertical_items if item.is_visible}
        except Exception:
            pass

        # Show the vertical name as a label prefix when >1 vertical is visible
        n_visible = len(visible_ids) if visible_ids is not None else len(cls.available_verticals)
        show_vertical_prefix = n_visible > 1

        # Recompute visible world extents (same calculation as draw_3d).
        ref = (cls.dist_min, 0.0, (cls.elev_zone_bot + cls.elev_zone_top) * 0.5)
        bl = region_2d_to_location_3d(region, rv3d, (0, 0), ref)
        tr = region_2d_to_location_3d(region, rv3d, (region.width, region.height), ref)
        if bl is None or tr is None:
            return

        vis_d_min, vis_d_max = bl.x, tr.x
        vis_z_min, vis_z_max = bl.z, tr.z

        d_interval = _nice_interval(vis_d_max - vis_d_min, 8)
        vis_e_min_clamp = cls._e_display_min
        vis_e_max_clamp = cls._e_display_max
        e_interval = _nice_interval(max(vis_e_max_clamp - vis_e_min_clamp, 1e-6), 6)

        font_id = 0
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 5, 0, 0, 0, 1)

        # --- Window header ----------------------------------------------------
        blf.size(font_id, tool.Blender.scale_font_size(13))
        blf.color(font_id, *cls.COLOR_HEADER)
        blf.position(font_id, 16, region.height - 28, 0)
        blf.draw(font_id, f"Vertical Profile — {cls.alignment_name}")

        # --- Station axis labels (horizontal, along the bottom) --------------
        BOTTOM_MARGIN = 28   # px from bottom for label baseline
        ELEV_MARGIN = 72     # px from left where elevation labels end; station zone starts here

        blf.size(font_id, tool.Blender.scale_font_size(10))
        blf.color(font_id, *cls.COLOR_LABEL)

        prev_sx = -9999
        for d in _frange(vis_d_min, vis_d_max, d_interval):
            screen = location_3d_to_region_2d(region, rv3d, (d, 0.0, vis_z_min))
            if screen is None:
                continue
            sx = screen.x
            label = cls._dist_to_station_str(d, d_interval)
            w, _ = blf.dimensions(font_id, label)
            # Skip labels too close to the viewport edge or the previous label
            if sx - w * 0.5 < ELEV_MARGIN or sx + w * 0.5 > region.width - 8:
                continue
            if sx - prev_sx < w + 10:
                continue
            blf.position(font_id, sx - w * 0.5, BOTTOM_MARGIN, 0)
            blf.draw(font_id, label)
            prev_sx = sx

        # Axis title "Station (unit)" centred at the bottom
        blf.size(font_id, tool.Blender.scale_font_size(10))
        blf.color(font_id, *cls.COLOR_AXIS_TITLE)
        title = f"Station ({cls.unit_symbol})"
        tw, _ = blf.dimensions(font_id, title)
        blf.position(font_id, (region.width - tw) * 0.5, 8, 0)
        blf.draw(font_id, title)

        # --- Elevation axis labels (vertical axis, left side) ----------------
        blf.size(font_id, tool.Blender.scale_font_size(10))
        blf.color(font_id, *cls.COLOR_LABEL)

        # When cant is present, stop elevation labels at the top of the cant zone.
        elev_label_sy_min = BOTTOM_MARGIN + 14
        if cls.has_cant:
            sc_sep = location_3d_to_region_2d(region, rv3d, (vis_d_min, 0.0, cls.cant_zone_top))
            if sc_sep:
                elev_label_sy_min = max(BOTTOM_MARGIN + 14, sc_sep.y + 6)

        prev_sy = -9999
        for e in _frange(vis_e_min_clamp, vis_e_max_clamp, e_interval):
            screen = location_3d_to_region_2d(region, rv3d, (vis_d_min, 0.0, cls._ez(e)))
            if screen is None:
                continue
            sy = screen.y
            if sy < elev_label_sy_min or sy > region.height - 40:
                continue
            if sy - prev_sy < 14:
                continue
            label = _fmt_elev(e, e_interval)
            w, h = blf.dimensions(font_id, label)
            blf.position(font_id, ELEV_MARGIN - w - 4, sy - h * 0.5, 0)
            blf.draw(font_id, label)
            prev_sy = sy

        # Axis title "Elev (unit)" at the top of the elevation column
        blf.size(font_id, tool.Blender.scale_font_size(10))
        blf.color(font_id, *cls.COLOR_AXIS_TITLE)
        blf.position(font_id, 4, region.height - 44, 0)
        blf.draw(font_id, f"Elev ({cls.unit_symbol})")

        # --- BVC / PVI / EVC callouts and gradient endpoint labels -----------
        # Build per-vertical label-enabled lookup from the vertical_items collection.
        # Defaults to True when a vertical isn't in the list (profile not yet open).
        v_label_enabled: dict = {}
        try:
            for item in props.vertical_items:
                v_label_enabled[item.entity_id] = item.show_labels
        except Exception:
            pass

        pt_font_size = tool.Blender.scale_font_size(10)
        blf.size(font_id, pt_font_size)
        pt_line_h = pt_font_size + 3
        n_segs = len(cls.segments_info)
        labeled_stations: set = set()

        def _draw_vp_label(world_pos, stacked_lines, color, draw_cross=False):
            screen = location_3d_to_region_2d(region, rv3d, world_pos)
            if not screen:
                return
            sx, sy = screen.x, screen.y
            if sx < -80 or sx > region.width + 80 or sy < -20 or sy > region.height + 20:
                return
            if draw_cross:
                r = 7
                shader_x = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
                shader_x.bind()
                shader_x.uniform_float("viewportSize", (region.width, region.height))
                shader_x.uniform_float("lineWidth", 1.8)
                shader_x.uniform_float("color", color)
                xv = [(sx - r, sy, 0), (sx + r, sy, 0), (sx, sy - r, 0), (sx, sy + r, 0)]
                gpu.state.blend_set("ALPHA")
                batch_for_shader(shader_x, "LINES", {"pos": xv}, indices=[[0, 1], [2, 3]]).draw(shader_x)
                gpu.state.blend_set("NONE")
            blf.size(font_id, pt_font_size)
            blf.color(font_id, *color)
            # Stack upward from the point by default; flip downward near the top
            # edge so a multi-line label can't run off-screen -- a point can end
            # up arbitrarily close to any edge once you zoom in far enough.
            total_h = len(stacked_lines) * pt_line_h
            if sy > region.height - total_h - 8:
                for j, line in enumerate(stacked_lines):
                    blf.position(font_id, sx + 12, sy - 4 - (j + 1) * pt_line_h, 0)
                    blf.draw(font_id, line)
            else:
                for j, line in enumerate(reversed(stacked_lines)):
                    blf.position(font_id, sx + 12, sy + 4 + j * pt_line_h, 0)
                    blf.draw(font_id, line)

        # Track labeled stations per vertical so duplicate-suppression stays
        # within one vertical (different verticals can share the same station).
        labeled_by_vertical: dict = {}  # vertical_id → set of rounded station keys

        n_segs = len(cls.segments_info)
        for i, info in enumerate(cls.segments_info):
            if visible_ids is not None and info.get("vertical_id", -1) not in visible_ids:
                continue

            v_id = info.get("vertical_id", -1)
            if not v_label_enabled.get(v_id, True):
                continue

            v_label = info.get("vertical_label", "")
            if v_id not in labeled_by_vertical:
                labeled_by_vertical[v_id] = set()
            labeled = labeled_by_vertical[v_id]

            is_curve = info.get("is_curve", False)
            bvc_d, bvc_e = info.get("bvc", (info["dist"], info["height"]))
            evc_d, evc_e = info.get("evc", (
                info["dist"] + info["h_len"],
                info["height"] + info["g_start"] * info["h_len"],
            ))
            pvi_data = info.get("pvi")

            bvc_w = (bvc_d, 0.0, cls._ez(bvc_e))
            evc_w = (evc_d, 0.0, cls._ez(evc_e))
            bvc_key = round(bvc_d, 3)
            evc_key = round(evc_d, 3)

            sta_bvc = cls._dist_to_station_str(bvc_d)
            sta_evc = cls._dist_to_station_str(evc_d)

            # When multiple verticals are visible, prefix point names with the vertical label
            pfx = f" [{v_label}]" if show_vertical_prefix and v_label else ""

            # start_label/end_label come from _get_segment_start_point_label (set in
            # _compute_profile) -- e.g. "P.V.C."/"P.V.T." for a real curve, "P.V.I."
            # for a sharp break, "V.P.O.B."/"V.P.O.E." at the alignment's true ends.
            start_label = info.get("start_label", "")
            end_label = info.get("end_label", "")

            if is_curve:
                if bvc_key not in labeled:
                    _draw_vp_label(
                        bvc_w,
                        [f"{start_label}{pfx}", f"Sta {sta_bvc}", f"Elev {_fmt_elev(bvc_e, e_interval)}"],
                        cls.COLOR_BVC,
                    )
                    labeled.add(bvc_key)
                if pvi_data:
                    pvi_d, pvi_e = pvi_data
                    pvi_w = (pvi_d, 0.0, cls._ez(pvi_e))
                    sta_pvi = cls._dist_to_station_str(pvi_d)
                    _draw_vp_label(
                        pvi_w,
                        [f"P.V.I.{pfx}", f"Sta {sta_pvi}", f"Elev {_fmt_elev(pvi_e, e_interval)}"],
                        cls.COLOR_PVI_VERT,
                        draw_cross=True,
                    )
                if evc_key not in labeled:
                    _draw_vp_label(
                        evc_w,
                        [f"{end_label}{pfx}", f"Sta {sta_evc}", f"Elev {_fmt_elev(evc_e, e_interval)}"],
                        cls.COLOR_EVC,
                    )
                    labeled.add(evc_key)
            else:
                g_pct = info["g_start"] * 100.0
                if bvc_key not in labeled:
                    lines = [f"{start_label}{pfx}", f"Sta {sta_bvc}", f"Elev {_fmt_elev(bvc_e, e_interval)}", f"{g_pct:+.2f}%"]
                    if show_vertical_prefix and v_label:
                        lines.append(f"[{v_label}]")
                    _draw_vp_label(bvc_w, lines, cls.COLOR_GRAD)
                    labeled.add(bvc_key)
                # Always label the end of the last segment for each vertical
                is_last_for_vertical = (
                    i == n_segs - 1
                    or cls.segments_info[i + 1].get("vertical_id", -1) != v_id
                )
                if is_last_for_vertical and evc_key not in labeled:
                    _draw_vp_label(
                        evc_w,
                        [f"{end_label}{pfx}", f"Sta {sta_evc}", f"Elev {_fmt_elev(evc_e, e_interval)}"],
                        cls.COLOR_GRAD,
                    )
                    labeled.add(evc_key)

        # ================================================================
        # --- Cant axis labels and callouts ---------------------------
        # ================================================================
        if cls.has_cant and cls.cant_polylines:
            visible_cant_ids_l: set | None = None
            try:
                if props.cant_items:
                    visible_cant_ids_l = {it.entity_id for it in props.cant_items if it.is_visible}
            except Exception:
                pass

            cant_z_top = cls.cant_zone_top
            cant_z_bot = cls.cant_zone_bot
            _cz_l = cls._cz2

            def _fmt_cant(v: float) -> str:
                if cls.unit_symbol in ("ft", "'"):
                    return f'{v * 12:.3f}"'
                return f"{v * 1000:.1f} mm"

            # "Cant" header + axis unit — just above the cant graph top border, right-aligned
            top_screen = location_3d_to_region_2d(region, rv3d, (vis_d_min, 0.0, cant_z_top))
            if top_screen:
                blf.size(font_id, tool.Blender.scale_font_size(11))
                blf.color(font_id, *cls.COLOR_CANT_HDR)
                hw, _ = blf.dimensions(font_id, "Cant")
                blf.position(font_id, region.width - hw - 8, top_screen.y + 4, 0)
                blf.draw(font_id, "Cant")
                blf.size(font_id, tool.Blender.scale_font_size(10))
                blf.color(font_id, *cls.COLOR_AXIS_TITLE)
                cant_unit = "mm" if cls.unit_symbol not in ("ft", "'") else "in"
                uw, _ = blf.dimensions(font_id, cant_unit)
                blf.position(font_id, region.width - uw - 8, top_screen.y - 10, 0)
                blf.draw(font_id, cant_unit)

            # Cant Y-axis tick values — right side (cant has its own right Y-axis)
            c_disp_span_l = max(cls._c_display_max - cls._c_display_min, 1e-10)
            cant_interval = _nice_interval(c_disp_span_l, 4)
            blf.size(font_id, tool.Blender.scale_font_size(10))
            blf.color(font_id, *cls.COLOR_LABEL)
            prev_csy = -9999
            for cv in _frange(cls._c_display_min, cls._c_display_max, cant_interval):
                gz = _cz_l(cv)
                sc = location_3d_to_region_2d(region, rv3d, (vis_d_min, 0.0, gz))
                if sc is None:
                    continue
                sy = sc.y
                if sy < BOTTOM_MARGIN + 8 or sy > region.height - 40:
                    continue
                if sy - prev_csy < 12:
                    continue
                lbl = _fmt_cant(cv)
                lw, lh = blf.dimensions(font_id, lbl)
                blf.position(font_id, region.width - lw - 4, sy - lh * 0.5, 0)
                blf.draw(font_id, lbl)
                prev_csy = sy

            # Zero-cant reference label (right side near the zero line)
            zero_z = _cz_l(0.0)
            zero_s = location_3d_to_region_2d(region, rv3d, (vis_d_min, 0.0, zero_z))
            if zero_s and cant_z_bot < zero_z < cant_z_top:
                blf.size(font_id, tool.Blender.scale_font_size(9))
                blf.color(font_id, *cls.COLOR_CANT_ZERO)
                blf.position(font_id, region.width - 20, zero_s.y + 2, 0)
                blf.draw(font_id, "0")

            # Centreline / left / right legend, under the "Cant" header
            if top_screen:
                blf.size(font_id, tool.Blender.scale_font_size(9))
                for lbl, col, dy in (
                    ("L rail", cls.CANT_COLOR_LEFT, -22),
                    ("R rail", cls.CANT_COLOR_RIGHT, -32),
                    ("CL", cls.CANT_COLOR_CENTER, -42),
                ):
                    blf.color(font_id, *col)
                    lw, _ = blf.dimensions(font_id, lbl)
                    blf.position(font_id, region.width - lw - 8, top_screen.y + dy, 0)
                    blf.draw(font_id, lbl)

            # Cant segment start/end callouts — per rail
            if getattr(props, "show_cant_segment_labels", True):
                blf.size(font_id, tool.Blender.scale_font_size(10))
                last_dist_by_cant: dict = {}
                for info in cls.cant_info:
                    cid = info.get("cant_id", -1)
                    last_dist_by_cant[cid] = max(last_dist_by_cant.get(cid, info["dist"]), info["dist"])
                labeled_cant: set = set()
                for info in cls.cant_info:
                    cid = info.get("cant_id", -1)
                    if visible_cant_ids_l is not None and cid not in visible_cant_ids_l:
                        continue
                    rail = info.get("rail", "L")
                    if rail == "C":
                        continue  # numeric callouts only on the railheads
                    d = info["dist"]
                    seg_color = cls.CANT_COLOR_RIGHT if rail == "R" else cls.CANT_COLOR_LEFT

                    s_key = (round(d, 3), rail)
                    if s_key not in labeled_cant:
                        sp = location_3d_to_region_2d(region, rv3d, (d, 0.0, _cz_l(info["start_cant"])))
                        if sp:
                            blf.color(font_id, *seg_color)
                            blf.position(font_id, sp.x + 6, sp.y + 4, 0)
                            blf.draw(font_id, _fmt_cant(info["start_cant"]))
                        labeled_cant.add(s_key)

                    if abs(d - last_dist_by_cant.get(cid, d)) < 1e-6:
                        e_d = d + info["h_len"]
                        e_key = (round(e_d, 3), rail)
                        if e_key not in labeled_cant:
                            ep = location_3d_to_region_2d(region, rv3d, (e_d, 0.0, _cz_l(info["end_cant"])))
                            if ep:
                                blf.color(font_id, *seg_color)
                                blf.position(font_id, ep.x + 6, ep.y + 4, 0)
                                blf.draw(font_id, _fmt_cant(info["end_cant"]))
                            labeled_cant.add(e_key)

        blf.disable(font_id, blf.SHADOW)


class VerticalDrawDecorator:
    """Live preview while ALIGN_OT_draw_vertical_alignment is running.

    Draws the in-progress PI polyline and a rubber-band line to the mouse
    cursor, using the exact same (dist_along, elevation) -> world-Z mapping
    VerticalProfileDecorator._ez uses, so the preview lines up with the
    profile grid/curve drawn underneath it by that decorator (which stays
    installed and keeps drawing its own grid/background throughout).
    """

    is_installed: bool = False
    handlers: list = []
    points: list = []                    # shared reference to the operator's [(dist, elev), ...] list
    mouse_data: Optional[Tuple[float, float]] = None  # (dist_along, elevation) under the cursor, or None

    COLOR_LINE = (1.0, 0.9, 0.2, 1.0)
    COLOR_RUBBER = (1.0, 0.9, 0.2, 0.5)
    COLOR_HUD_TEXT = (1.0, 1.0, 1.0, 1.0)
    LINE_WIDTH = 2.0

    @classmethod
    def install(cls, context, points: list) -> None:
        if cls.is_installed:
            cls.uninstall()
        cls.points = points
        cls.mouse_data = None
        handler = cls()
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_3d, (context,), "WINDOW", "POST_VIEW"))
        cls.handlers.append(SpaceView3D.draw_handler_add(handler.draw_hud, (context,), "WINDOW", "POST_PIXEL"))
        cls.is_installed = True

    @classmethod
    def uninstall(cls) -> None:
        for handler in cls.handlers:
            try:
                SpaceView3D.draw_handler_remove(handler, "WINDOW")
            except ValueError:
                pass
        cls.handlers = []
        cls.is_installed = False
        cls.points = []
        cls.mouse_data = None

    @classmethod
    def tag_redraw(cls) -> None:
        VerticalProfileDecorator.tag_redraw()

    @classmethod
    def update_mouse(cls, point: Optional[Tuple[float, float]]) -> None:
        """Set the (dist_along, elevation) the preview/rubber-band should show.

        Takes an already-resolved point rather than raw mouse coordinates —
        the caller (ALIGN_OT_draw_vertical_alignment) is what knows about the
        station-range clamp and left-to-right PI ordering constraints, so it
        computes the constrained point before handing it here. Pass None to
        hide the preview (e.g. the mouse left the profile area).
        """
        cls.mouse_data = point
        cls.tag_redraw()

    def _in_profile_area(self) -> bool:
        try:
            return (
                bpy.context.area is not None
                and bpy.context.area.as_pointer() == VerticalProfileDecorator.profile_area_ptr
            )
        except Exception:
            return False

    def draw_3d(self, context) -> None:
        cls = self.__class__
        if not self._in_profile_area():
            return
        if not cls.points and cls.mouse_data is None:
            return

        ez = VerticalProfileDecorator._ez
        verts = [(d, 0.0, ez(e)) for d, e in cls.points]

        region = bpy.context.region
        if not region:
            return

        gpu.state.blend_set("ALPHA")
        gpu.state.depth_test_set("NONE")
        gpu.state.depth_mask_set(False)

        shader = gpu.shader.from_builtin("POLYLINE_UNIFORM_COLOR")
        shader.bind()
        shader.uniform_float("viewportSize", (region.width, region.height))
        shader.uniform_float("lineWidth", self.LINE_WIDTH)

        if len(verts) >= 2:
            indices = [[i, i + 1] for i in range(len(verts) - 1)]
            batch = batch_for_shader(shader, "LINES", {"pos": verts}, indices=indices)
            shader.uniform_float("color", self.COLOR_LINE)
            batch.draw(shader)

        if verts and cls.mouse_data is not None:
            rubber_end = (cls.mouse_data[0], 0.0, ez(cls.mouse_data[1]))
            batch = batch_for_shader(shader, "LINES", {"pos": [verts[-1], rubber_end]}, indices=[[0, 1]])
            shader.uniform_float("color", self.COLOR_RUBBER)
            batch.draw(shader)

        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")
        gpu.state.depth_mask_set(True)

    def draw_hud(self, context) -> None:
        cls = self.__class__
        if not self._in_profile_area():
            return
        if cls.mouse_data is None:
            return

        region = context.region
        rv3d = context.region_data
        if not region:
            return

        dist_along, elevation = cls.mouse_data

        # Crosshair at the candidate-PI position — the only visual feedback
        # for the first PI (anchored to the start station) before anything
        # has actually been placed yet, since the rubber-band line itself
        # needs a previous point to draw from.
        if rv3d is not None:
            cursor_2d = location_3d_to_region_2d(
                region, rv3d, (dist_along, 0.0, VerticalProfileDecorator._ez(elevation))
            )
            if cursor_2d is not None:
                size = 6
                shader2d = gpu.shader.from_builtin("UNIFORM_COLOR")
                shader2d.bind()
                shader2d.uniform_float("color", self.COLOR_RUBBER)
                batch = batch_for_shader(
                    shader2d,
                    "LINES",
                    {
                        "pos": [
                            (cursor_2d.x - size, cursor_2d.y),
                            (cursor_2d.x + size, cursor_2d.y),
                            (cursor_2d.x, cursor_2d.y - size),
                            (cursor_2d.x, cursor_2d.y + size),
                        ]
                    },
                )
                batch.draw(shader2d)
        lines = [
            f"Dist Along: {dist_along:.2f}",
            f"Elevation: {elevation:.3f}",
        ]
        if cls.points:
            prev_d, prev_e = cls.points[-1]
            dd = dist_along - prev_d
            if abs(dd) > 1e-6:
                grade = (elevation - prev_e) / dd * 100.0
                lines.append(f"Grade: {grade:.2f}%")

        font_id = 0
        font_size = tool.Blender.scale_font_size(14)
        blf.size(font_id, font_size)
        blf.enable(font_id, blf.SHADOW)
        blf.shadow(font_id, 6, 0, 0, 0, 1)
        blf.color(font_id, *self.COLOR_HUD_TEXT)

        margin = 20
        line_height = font_size * 1.4
        y = region.height - margin
        for i, line in enumerate(lines):
            blf.position(font_id, margin, y - i * line_height, 0)
            blf.draw(font_id, line)
        blf.disable(font_id, blf.SHADOW)
