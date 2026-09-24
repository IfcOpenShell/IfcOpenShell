# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>, 2026 Michael Yoder <myoder@desertspringscivil.com>
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

import bpy
from . import ui, prop, operator, decorator

_last_active_ptr: int = 0
_last_profile_alignment_id: int = 0  # tracks which alignment the profile was last built for


def _auto_finish_unrelated_pi_markers(active, alignment) -> None:
    """Delete PI marker empties left over from any alignment other than the
    one ``alignment`` (the alignment tool.Alignment.get_active_alignment()
    now resolves for the just-changed active object) represents.

    PI markers are meant to be temporary, only-during-editing scaffolding
    (see ALIGN_OT_finish_pi_editing): once focus moves elsewhere -- most
    visibly by creating a new IFC element/type via one of Bonsai's many
    bim.add_* operators, but equally by picking a different existing element
    to work on -- there's no good reason for them to keep sitting
    half-resolved in the scene. Called from _on_active_object_changed rather
    than hooking "Add" specifically: there is no single choke point for
    that (dozens of bim.add_* operators exist scattered across modules),
    whereas every one of them ends by making the new object active, which
    that handler already watches.

    Deliberately does nothing when ``active`` is None (a plain deselect) --
    that's not "moving on to something else," and clearing markers on every
    empty-space click would be far too eager. Also does nothing to
    ``alignment``'s own markers: if the active object is one of them (or the
    alignment itself), that PI edit is still the one in progress.
    """
    if active is None:
        return

    marker_alignment_ids = {
        obj.bonsai_pi_curve_marker.alignment_id
        for obj in bpy.data.objects
        if obj.bonsai_pi_curve_marker.is_pi_marker
    }
    if not marker_alignment_ids:
        return

    active_alignment_id = alignment.id() if alignment else None
    if marker_alignment_ids == {active_alignment_id}:
        return  # only the still-in-progress alignment has markers -- nothing to finish

    finished_any = False
    for alignment_id in marker_alignment_ids:
        if alignment_id == active_alignment_id:
            continue
        for m in operator._find_pi_markers(alignment_id):
            bpy.data.objects.remove(m, do_unlink=True)
        decorator.PIMarkerDecorator.uninstall()
        finished_any = True

    if finished_any:
        operator._refresh_pi_marker_visuals(bpy.context, active_alignment_id or 0)


@bpy.app.handlers.persistent
def _on_active_object_changed(scene, depsgraph):
    """Sync the alignment dropdown, vertical profile, and Properties panel on selection change.

    Scene-context panels don't auto-redraw on selection changes.  We watch the
    active-object pointer and, when it changes, sync the dropdown and — if the
    alignment itself changed — recompute the vertical profile.

    The profile recompute uses its own tracker (_last_profile_alignment_id) rather
    than comparing the dropdown value.  This is necessary because the dropdown is
    updated by _on_active_alignment_update *before* the depsgraph fires, so the
    two values would always match and the recompute would never run.
    """
    global _last_active_ptr, _last_profile_alignment_id
    try:
        ctx = bpy.context
        vl = ctx.view_layer
        active = vl.objects.active if vl else None
        ptr = active.as_pointer() if active else 0
        if ptr == _last_active_ptr:
            return
        _last_active_ptr = ptr

        import bonsai.tool as tool
        from bonsai.bim.module.alignment.prop import _alignment_enum_items, _clamp_alignment_enum

        props = scene.CivilAlignmentProperties
        _clamp_alignment_enum(props)
        alignment = tool.Alignment.get_active_alignment()
        _auto_finish_unrelated_pi_markers(active, alignment)
        new_val = str(alignment.id()) if alignment else "0"

        # Sync dropdown (only needed when selection came from 3D view / outliner)
        if props.active_alignment_id_str != new_val:
            for idx, (ident, _, _) in enumerate(_alignment_enum_items(props, None)):
                if ident == new_val:
                    props["active_alignment_id_str"] = idx
                    break

        # Recompute vertical profile when the alignment changes — use an independent
        # tracker so this fires even when the dropdown already shows the new alignment
        # (i.e. the change came from the dropdown, not from a viewport/outliner click).
        new_aid = alignment.id() if alignment else 0
        if new_aid != _last_profile_alignment_id:
            _last_profile_alignment_id = new_aid
            if alignment:
                from bonsai.bim.module.alignment.decorator import VerticalProfileDecorator
                dec = VerticalProfileDecorator
                if dec.is_installed:
                    dec._compute_profile(alignment)
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
                    # Refit the camera to the new alignment's extent
                    for window in ctx.window_manager.windows:
                        for a in window.screen.areas:
                            if a.as_pointer() == dec.profile_area_ptr:
                                space = next(
                                    (s for s in a.spaces if s.type == "VIEW_3D"), None
                                )
                                if space:
                                    dec.fit_view(space, area_width=a.width, area_height=a.height)
                    dec.tag_redraw()

        for window in ctx.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "PROPERTIES":
                    area.tag_redraw()
    except Exception:
        pass


classes = (
    # Property groups (must be registered before classes that use them)
    prop.VerticalAlignmentItem,
    prop.CantAlignmentItem,
    prop.VerticalPIMarker,
    prop.PolylinePointRow,
    prop.HorizontalPIMarker,
    prop.HorizontalSegmentRow,
    prop.VerticalSegmentRow,
    prop.CantSegmentRow,
    prop.CivilAlignmentProperties,
    prop.PICurveMarkerProperties,
    # UILists and section-toggle operators
    ui.ALIGN_OT_toggle_h_segments,
    ui.ALIGN_OT_toggle_v_segments,
    ui.ALIGN_OT_toggle_cant_segments,
    ui.ALIGN_UL_vertical_pi_markers,
    ui.ALIGN_UL_polyline_points,
    ui.ALIGN_UL_horizontal_pi_markers,
    ui.ALIGN_UL_h_segments,
    ui.ALIGN_UL_v_segments,
    ui.ALIGN_UL_cant_segments,
    operator.ImportAlignmentCSV,
    # Operators - Vertical Profile Window
    operator.ALIGN_OT_show_vertical_profile,
    operator.ALIGN_OT_pan_vertical_profile,
    operator.ALIGN_OT_reset_vertical_profile_view,
    # Operators - Segment Selection
    operator.ALIGN_OT_select_h_segment,
    operator.ALIGN_OT_select_v_segment,
    operator.ALIGN_OT_select_cant_segment,
    # Operators - Alignments tab authoring workflow (Add Element + interactive draw)
    operator.ALIGN_OT_add_alignment,
    operator.ALIGN_OT_remove_alignment,
    operator.ALIGN_OT_set_start_station,
    operator.ALIGN_OT_add_station_equation,
    operator.ALIGN_OT_edit_station_equation,
    operator.ALIGN_OT_remove_station_equation,
    operator.ALIGN_OT_generate_key_points,
    operator.ALIGN_OT_remove_key_points,
    operator.ALIGN_OT_edit_horizontal_pis,
    operator.ALIGN_OT_apply_pi_curve,
    operator.ALIGN_OT_finish_pi_editing,
    operator.ALIGN_OT_load_horizontal_pi_table,
    operator.ALIGN_OT_apply_horizontal_pi_table,
    operator.ALIGN_OT_finish_horizontal_pi_table,
    operator.ALIGN_OT_draw_horizontal_alignment,
    # Operators - Vertical alignment authoring (draw-by-PI in the profile view)
    operator.ALIGN_OT_draw_vertical_alignment,
    operator.ALIGN_OT_load_vertical_pis,
    operator.ALIGN_OT_apply_vertical_pi_curve,
    operator.ALIGN_OT_drag_vertical_pis,
    operator.ALIGN_OT_move_pi_marker,
    operator.ALIGN_OT_draw_polyline_alignment,
    operator.ALIGN_OT_edit_polyline_points,
    operator.ALIGN_OT_load_polyline_table,
    operator.ALIGN_OT_add_polyline_point_row,
    operator.ALIGN_OT_remove_polyline_point_row,
    operator.ALIGN_OT_apply_polyline_table,
    operator.ALIGN_OT_finish_polyline_table,
    operator.ALIGN_OT_finish_vertical_pi_editing,
    # Operators - Segment table editing (stage edits, then Apply)
    operator.ALIGN_OT_add_segment_row,
    operator.ALIGN_OT_remove_segment_row,
    operator.ALIGN_OT_move_segment_row,
    operator.ALIGN_OT_enable_editing_h_segments,
    operator.ALIGN_OT_disable_editing_h_segments,
    operator.ALIGN_OT_apply_h_segments,
    operator.ALIGN_OT_enable_editing_v_segments,
    operator.ALIGN_OT_disable_editing_v_segments,
    operator.ALIGN_OT_apply_v_segments,
    operator.ALIGN_OT_generate_cant_layout,
    operator.ALIGN_OT_remove_cant_layout,
    operator.ALIGN_OT_rename_vertical,
    operator.ALIGN_OT_remove_vertical_layout,
    operator.ALIGN_OT_remove_horizontal_layout,
    operator.ALIGN_OT_enable_editing_cant_segments,
    operator.ALIGN_OT_disable_editing_cant_segments,
    operator.ALIGN_OT_apply_cant_segments,
    # UI Panels (appear in Properties sidebar under ALIGNMENTS tab)
    ui.ALIGN_PT_alignment_authoring,
    ui.ALIGN_PT_vertical_alignment_authoring,
    ui.ALIGN_PT_alignment_stationing_authoring,
    ui.ALIGN_PT_alignment_segments,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportAlignmentCSV.bl_idname, text="Alignment (.csv)")


addon_keymaps = []


def register():
    bpy.types.Scene.CivilAlignmentProperties = bpy.props.PointerProperty(type=prop.CivilAlignmentProperties)
    bpy.types.Object.bonsai_pi_curve_marker = bpy.props.PointerProperty(type=prop.PICurveMarkerProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
    if _on_active_object_changed not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_active_object_changed)
    # Reset decorator state so a module hot-reload never leaves is_installed=True
    # with stale handlers that prevent the first button press from opening the profile.
    from .decorator import VerticalProfileDecorator
    VerticalProfileDecorator.is_installed = False
    VerticalProfileDecorator.handlers = []
    VerticalProfileDecorator.profile_area = None
    VerticalProfileDecorator.profile_area_ptr = 0

    # Shift+wheel pans and Home resets the vertical profile view. Registered on
    # the generic "3D View" keymap since it needs to fire in any VIEW_3D area,
    # but the operators' poll() only allows them in the docked profile area
    # (falling through to Blender's defaults, e.g. view3d.view_all on Home,
    # everywhere else).
    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(operator.ALIGN_OT_pan_vertical_profile.bl_idname, "WHEELUPMOUSE", "PRESS", shift=True)
        kmi.properties.direction = -1
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(operator.ALIGN_OT_pan_vertical_profile.bl_idname, "WHEELDOWNMOUSE", "PRESS", shift=True)
        kmi.properties.direction = 1
        addon_keymaps.append((km, kmi))
        kmi = km.keymap_items.new(operator.ALIGN_OT_reset_vertical_profile_view.bl_idname, "HOME", "PRESS")
        addon_keymaps.append((km, kmi))


def unregister():
    if _on_active_object_changed in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_active_object_changed)
    # Clean up any open profile window so re-registration starts from a clean state.
    from .decorator import VerticalProfileDecorator
    if VerticalProfileDecorator.is_installed:
        try:
            VerticalProfileDecorator.uninstall()
        except Exception:
            pass
    VerticalProfileDecorator.is_installed = False
    VerticalProfileDecorator.handlers = []
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del bpy.types.Scene.CivilAlignmentProperties
    del bpy.types.Object.bonsai_pi_curve_marker

    wm = bpy.context.window_manager
    if wm.keyconfigs.addon:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
