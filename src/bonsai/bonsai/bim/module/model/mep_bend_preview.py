# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

"""Bend-preview lifecycle for MEP segment joins.

Holds the four lifecycle operators (Enable / Finish / Cancel /
EnableFromBend) and the ``GizmoBendPreview`` group that surfaces the
tunable dimensions and validate/cancel icons during preview. Draft state
lives at ``Scene.BIMPreviewProperties.bend`` per CLAUDE.md §2.9 (Scene
for cross-element previews).

The geometry math (``compute_bend_preview_polylines``,
``_bend_profile_cross_section``, ``_sweep_profile_along_polyline``)
stays in ``mep.py`` because the commit operator ``MEPAddBend`` reuses
it; this module imports the polyline helper for per-frame gizmo
positioning. The GPU lines themselves are drawn by
``decorator.BendPreviewDecorator``, kept in ``decorator.py`` with its
sibling decorators."""

from typing import ClassVar

import bpy
import ifcopenshell.util.element
import ifcopenshell.util.unit
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing import gizmos as gizmo
from bonsai.bim.module.model import preview_base
from bonsai.bim.module.model.mep import (
    _is_bend_fitting,
    _n_mep_selected,
    cached_compute_bend_preview_polylines,
    segments_are_parallel,
    validate_bend_preconditions,
)


class EnableBendPreview(bpy.types.Operator):
    """Enter bend-preview mode for two selected MEP segments. Populates
    scene.BIMPreviewProperties.bend with segment IFC ids and default
    start_length / end_length / radius; no IFC mutation until finish."""

    bl_idname = "bim.enable_bend_preview"
    bl_label = "Enter Bend Preview"
    bl_description = "Begin tuning bend parameters before committing the bend"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _n_mep_selected(2):
            cls.poll_message_set("Select exactly 2 MEP segments to bend.")
            return False
        return True

    def execute(self, context):
        selected = tool.Blender.get_selected_objects()
        active = context.active_object
        if active is None or active not in selected:
            self.report({"ERROR"}, "Active object must be one of the selected MEP segments.")
            return {"CANCELLED"}
        other = next((o for o in selected if o is not active), None)
        if other is None:
            self.report({"ERROR"}, "Two MEP segments must be selected.")
            return {"CANCELLED"}
        active_element = tool.Ifc.get_entity(active)
        other_element = tool.Ifc.get_entity(other)
        if active_element is None or other_element is None:
            self.report({"ERROR"}, "Both selected objects must be IFC elements.")
            return {"CANCELLED"}
        if segments_are_parallel(active, other):
            self.report({"ERROR"}, "Bend preview is for non-parallel segments only.")
            return {"CANCELLED"}

        # Pre-check the same preconditions MEPAddBend enforces so the user
        # sees the rejection here rather than after tuning a doomed preview.
        precondition_error = validate_bend_preconditions(active_element, other_element)
        if precondition_error is not None:
            self.report({"ERROR"}, precondition_error)
            return {"CANCELLED"}

        preview_base.sync_uncommitted_moves([active, other])

        props = preview_base.get_preview_props(context, "bend")
        # Auto-cancel any prior preview so re-clicking join on a different
        # pair doesn't silently commit the previous tuning.
        if props is not None and props.is_active:
            bpy.ops.bim.cancel_bend_preview()

        props.start_segment_id = active_element.id()
        props.end_segment_id = other_element.id()
        props.start_length = 0.1
        props.end_length = 0.1
        props.radius = 0.2
        props.is_active = True
        return {"FINISHED"}


class FinishBendPreview(bpy.types.Operator):
    """Commit the previewed bend with the tuned parameters and exit preview.

    Preview state survives a failed commit so the user can re-tune without
    re-selecting."""

    bl_idname = "bim.finish_bend_preview"
    bl_label = "Apply Bend"
    bl_description = "Commit the bend with the previewed parameters"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        return preview_base.commit_preview(
            self,
            context,
            "bend",
            "mep_add_bend",
            ("start_segment_id", "end_segment_id", "start_length", "end_length", "radius", "editing_bend_id"),
        )


class CancelBendPreview(bpy.types.Operator):
    """Exit bend preview without committing."""

    bl_idname = "bim.cancel_bend_preview"
    bl_label = "Cancel Bend"
    bl_description = "Discard the previewed bend"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if context.screen is None:
            return {"CANCELLED"}
        props = preview_base.get_preview_props(context, "bend")
        if props is None or not props.is_active:
            return {"CANCELLED"}
        preview_base.clear_preview_state(props)
        return {"FINISHED"}


class EnableBendPreviewFromBend(bpy.types.Operator):
    """Re-open the bend preview on an existing bend fitting.

    Resolves the two connected segments via the bend's ports +
    ``IfcRelConnectsPorts``, reads parametric values back from the bend's
    ``BBIM_Fitting`` pset, and flags the preview so committing replaces
    the existing bend in place."""

    bl_idname = "bim.enable_bend_preview_from_bend"
    bl_label = "Edit Bend"
    bl_description = "Re-open the bend preview to retune an existing bend"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        active = context.active_object
        if active is None:
            cls.poll_message_set("No active object.")
            return False
        element = tool.Ifc.get_entity(active)
        if element is None or not _is_bend_fitting(element):
            cls.poll_message_set("Active object must be a bend fitting.")
            return False
        return True

    def execute(self, context):
        active = context.active_object
        bend_element = tool.Ifc.get_entity(active)
        if bend_element is None or not _is_bend_fitting(bend_element):
            self.report({"ERROR"}, "Active object is not a bend fitting.")
            return {"CANCELLED"}

        connected_segments: list = []
        for port in tool.System.get_ports(bend_element):
            connected_port = tool.System.get_connected_port(port)
            if connected_port is None:
                continue
            related = tool.System.get_port_relating_element(connected_port)
            if related is not None and related.is_a("IfcFlowSegment") and related not in connected_segments:
                connected_segments.append(related)

        if len(connected_segments) != 2:
            self.report(
                {"ERROR"},
                f"Bend has {len(connected_segments)} connected segments; need exactly 2 to re-edit.",
            )
            return {"CANCELLED"}

        # Read parametric values from the bend type's BBIM_Fitting pset. The
        # type carries the canonical parameters; querying the occurrence
        # would force a get_type round-trip and miss user-edited types.
        bend_type = ifcopenshell.util.element.get_type(bend_element)
        if bend_type is None:
            self.report({"ERROR"}, "Bend fitting has no type to read parameters from.")
            return {"CANCELLED"}
        bend_type_obj = tool.Ifc.get_object(bend_type)
        if bend_type_obj is None:
            self.report({"ERROR"}, "Bend type has no Blender object — cannot read pset.")
            return {"CANCELLED"}
        bbim = tool.Model.get_modeling_bbim_pset_data(bend_type_obj, "BBIM_Fitting")
        if bbim is None:
            self.report({"ERROR"}, "Bend fitting has no BBIM_Fitting pset — not a parametric bend.")
            return {"CANCELLED"}
        data = bbim.get("data_dict", {})

        props = preview_base.get_preview_props(context, "bend")
        if props is not None and props.is_active:
            bpy.ops.bim.cancel_bend_preview()

        # Segment order is load-bearing: the bend's lateral sign and z-axis
        # flip are derived from which segment is "start" vs "end". Re-edit
        # must reuse the same pairing as the original create so the recreate
        # lands at the same orientation.
        start_segment, end_segment = connected_segments
        props.start_segment_id = start_segment.id()
        props.end_segment_id = end_segment.id()
        # Pset values are in IFC native units; scene units come from si_conversion.
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.start_length = float(data.get("start_length", 0.1)) * si_conversion
        props.end_length = float(data.get("end_length", 0.1)) * si_conversion
        props.radius = float(data.get("radius", 0.2)) * si_conversion
        props.editing_bend_id = bend_element.id()
        props.is_active = True
        return {"FINISHED"}


def _bend_preview_segments(context):
    """Resolve the two segment objects from the scene-level preview props.

    Re-resolves by IFC id each frame so undo / file reload during preview
    never dangles a stale bpy reference."""
    props = context.scene.BIMPreviewProperties.bend
    ifc_file = tool.Ifc.get()
    if ifc_file is None or not props.is_active:
        return None, None
    try:
        start_element = ifc_file.by_id(props.start_segment_id)
        end_element = ifc_file.by_id(props.end_segment_id)
    except Exception:
        return None, None
    start_obj = tool.Ifc.get_object(start_element) if start_element else None
    end_obj = tool.Ifc.get_object(end_element) if end_element else None
    return start_obj, end_obj


def _gizmo_x_matrix(location: Vector, x_direction: Vector) -> Matrix:
    """Build a 4x4 matrix placing a gizmo at ``location`` with its local +X
    axis aligned to ``x_direction`` in world space. ``BIM_GT_gizmo_dimension``
    draws + drags along local +X by convention."""
    x = x_direction.normalized()
    seed = Vector((0, 0, 1)) if abs(x.z) < 0.9 else Vector((1, 0, 0))
    y = (seed - x * seed.dot(x)).normalized()
    z = x.cross(y)
    mat = Matrix.Identity(4)
    mat[0][:3] = (x.x, y.x, z.x)
    mat[1][:3] = (x.y, y.y, z.y)
    mat[2][:3] = (x.z, y.z, z.z)
    mat.translation = location
    return mat


class GizmoBendPreview(bpy.types.GizmoGroup):
    """Interactive gizmo group for the bend preview flow.

    Three dimension widgets drag start_length / end_length / radius; two
    icon gizmos commit or cancel. When the geometry is degenerate the
    dimensions and validate hide but cancel stays visible so the user
    always has an exit."""

    bl_idname = "OBJECT_GGT_bim_bend_preview"
    bl_label = "Bend Preview Gizmos"
    bl_space_type = "VIEW_3D"
    bl_region_type = "WINDOW"
    bl_options = {"3D", "PERSISTENT"}

    ICON_SCALE: ClassVar[float] = 0.375
    ICON_SPACING_X: ClassVar[float] = 0.4
    ICON_Z_OFFSET: ClassVar[float] = 1.5

    @classmethod
    def poll(cls, context):
        preview = getattr(context.scene, "BIMPreviewProperties", None)
        props = preview.bend if preview is not None else None
        if props is None or not props.is_active:
            return False
        if not tool.Blender.are_viewport_gizmos_enabled():
            return False
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            return False
        try:
            ifc_file.by_id(props.start_segment_id)
            ifc_file.by_id(props.end_segment_id)
        except (RuntimeError, KeyError):
            return False
        return True

    def setup(self, context):
        prefs = tool.Blender.get_addon_preferences()
        default_color = tuple(prefs.decorations_colour[:3])
        highlight_color = tuple(prefs.decorator_color_selected[:3])

        _props = preview_base.make_props_callback("bend")

        def setup_dimension(attr: str, prop_name: str, invert_delta: bool = False) -> bpy.types.Gizmo:
            gz = self.gizmos.new("BIM_GT_gizmo_dimension")
            gz.move_get_cb = preview_base.make_dim_getter(_props, attr)
            gz.move_set_cb = preview_base.make_dim_setter(_props, attr)
            gz.axis = Vector((1, 0, 0))
            gz.invert_delta = invert_delta
            gz.delta_scale = 1.0
            gz.prop_name = prop_name
            gz.gizmo_group = self
            gz.color = default_color
            gz.color_highlight = highlight_color
            gz.alpha = 1.0
            gz.use_draw_modal = True
            gz.use_draw_scale = False
            gz.text_offset_sign = 1
            gz.text_alignment = gizmo.TextAlignment.CENTER
            gz.show_start_arrow = False
            gz.show_end_arrow = True
            gz.show_extension_lines = False
            gz.text_formatter = None
            return gz

        self.start_dim = setup_dimension("start_length", "Start Length")
        self.end_dim = setup_dimension("end_length", "End Length")
        self.radius_dim = setup_dimension("radius", "Radius")

        from bonsai.bim.module.drawing.gizmos import BaseParametricGizmoGroup

        self.validate_icon = self.gizmos.new("VIEW3D_GT_validate")
        self.validate_icon.use_draw_scale = False
        self.validate_icon.color = BaseParametricGizmoGroup.COLOR_GREEN
        self.validate_icon.color_highlight = highlight_color
        self.validate_icon.target_set_operator("bim.finish_bend_preview")

        self.cancel_icon = self.gizmos.new("VIEW3D_GT_cancel")
        self.cancel_icon.use_draw_scale = False
        self.cancel_icon.color = BaseParametricGizmoGroup.COLOR_RED
        self.cancel_icon.color_highlight = highlight_color
        self.cancel_icon.target_set_operator("bim.cancel_bend_preview")

    def refresh(self, context):
        self._position_gizmos(context)

    def draw_prepare(self, context):
        self._position_gizmos(context)

    def _position_gizmos(self, context):
        """Place gizmos at the bend intersection using the current scene
        props. Cancel stays visible on degenerate geometry so the user
        always has an exit; the other widgets hide when there's no defined
        tangent / arc to anchor them on."""
        start_obj, end_obj = _bend_preview_segments(context)
        if start_obj is None or end_obj is None:
            for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon, self.cancel_icon):
                gz.hide = True
            return

        props = context.scene.BIMPreviewProperties.bend
        preview = cached_compute_bend_preview_polylines(
            start_obj, end_obj, props.start_length, props.end_length, props.radius
        )
        if not preview["valid"]:
            for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon):
                gz.hide = True
            self.cancel_icon.hide = False
            axes = preview.get("invalid_axes") or []
            if axes:
                intersection_point = axes[0][1]
                billboard_rot = gizmo.get_billboard_rotation(context)
                anchor = intersection_point + Vector((0, 0, self.ICON_Z_OFFSET))
                self.cancel_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot, scale=self.ICON_SCALE)
            return

        for gz in (self.start_dim, self.end_dim, self.radius_dim, self.validate_icon, self.cancel_icon):
            gz.hide = False

        leg_a_far, leg_a_end = preview["leg_a"]
        leg_b_far, leg_b_end = preview["leg_b"]
        toward_bend_a = (
            (leg_a_end - leg_a_far).normalized() if (leg_a_end - leg_a_far).length > 1e-6 else Vector((0, 0, 1))
        )
        toward_bend_b = (
            (leg_b_end - leg_b_far).normalized() if (leg_b_end - leg_b_far).length > 1e-6 else Vector((0, 0, 1))
        )
        leg_a_tangent = leg_a_end + toward_bend_a * props.start_length
        leg_b_tangent = leg_b_end + toward_bend_b * props.end_length

        # axis is set in world space every frame so the drag projection
        # matches the visual regardless of either segment's matrix_world.
        self.start_dim.matrix_basis = _gizmo_x_matrix(leg_a_tangent, -toward_bend_a)
        self.start_dim.axis = -toward_bend_a
        self.start_dim.set_dimension_length(props.start_length)
        self.end_dim.matrix_basis = _gizmo_x_matrix(leg_b_tangent, -toward_bend_b)
        self.end_dim.axis = -toward_bend_b
        self.end_dim.set_dimension_length(props.end_length)

        arc = preview["arc"]
        if len(arc) >= 3:
            mid = len(arc) // 2
            chord_mid = (arc[0] + arc[-1]) * 0.5
            toward_mid = arc[mid] - chord_mid
            if toward_mid.length > 1e-6:
                toward_mid = toward_mid.normalized()
                half_chord = (arc[-1] - arc[0]).length * 0.5
                center_dist = max(0.0, props.radius * props.radius - half_chord * half_chord) ** 0.5
                arc_center = chord_mid - toward_mid * center_dist
                radial_out = arc[mid] - arc_center
                if radial_out.length > 1e-6:
                    radial_out.normalize()
                    inward = -radial_out
                    self.radius_dim.matrix_basis = _gizmo_x_matrix(arc[mid], inward)
                    self.radius_dim.axis = inward
                    self.radius_dim.set_dimension_length(props.radius)
                else:
                    self.radius_dim.hide = True
            else:
                self.radius_dim.hide = True
        else:
            self.radius_dim.hide = True

        billboard_rot = gizmo.get_billboard_rotation(context)
        anchor_base = arc[len(arc) // 2] if arc else (leg_a_end + leg_b_end) * 0.5
        anchor = anchor_base + Vector((0, 0, self.ICON_Z_OFFSET))
        offset_x = billboard_rot @ Vector((self.ICON_SPACING_X, 0.0, 0.0))
        self.validate_icon.matrix_basis = gizmo.billboarded_at(anchor, billboard_rot, scale=self.ICON_SCALE)
        self.cancel_icon.matrix_basis = gizmo.billboarded_at(anchor + offset_x, billboard_rot, scale=self.ICON_SCALE)
