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
from . import ui, prop, operator, decorator, workspace

_last_active_ptr: int = 0
_last_profile_alignment_id: int = 0  # tracks which alignment the profile was last built for


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
        from bonsai.bim.module.alignment.prop import _alignment_enum_items

        props = scene.CivilAlignmentProperties
        alignment = tool.Alignment.get_active_alignment()
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
                    ve = props.vertical_exaggeration
                    for window in ctx.window_manager.windows:
                        for a in window.screen.areas:
                            if a.as_pointer() == dec.profile_area_ptr:
                                space = next(
                                    (s for s in a.spaces if s.type == "VIEW_3D"), None
                                )
                                if space:
                                    dec.fit_view(space, ve, area_width=a.width, area_height=a.height)
                    dec.tag_redraw()

        for window in ctx.window_manager.windows:
            for area in window.screen.areas:
                if area.type == "PROPERTIES":
                    area.tag_redraw()
    except Exception:
        pass


classes = (
    # Property groups (must be registered before classes that use them)
    prop.AlignmentPI,
    prop.AlignmentDisplayRow,
    prop.VerticalAlignmentItem,
    prop.CantAlignmentItem,
    prop.CivilAlignmentProperties,
    prop.PICurveMarkerProperties,
    # UILists and section-toggle operators
    ui.ALIGN_UL_alignment_pis,
    ui.ALIGN_OT_toggle_h_segments,
    ui.ALIGN_OT_toggle_v_segments,
    ui.ALIGN_OT_toggle_cant_segments,
    operator.ImportAlignmentCSV,
    # Operators - PI Management
    operator.ALIGN_OT_add_pi,
    operator.ALIGN_OT_remove_pi,
    operator.ALIGN_OT_pick_pi_from_viewport,
    operator.ALIGN_OT_recalculate_pis,
    operator.ALIGN_OT_clear_pis,
    # Operators - Creation
    operator.ALIGN_OT_create_alignment_by_pis,
    operator.ALIGN_OT_create_alignment_by_pi,
    # Operators - Stationing
    operator.ALIGN_OT_add_stationing_referent,
    operator.ALIGN_OT_name_segments,
    # Operators - Vertical Profile Window
    operator.ALIGN_OT_show_vertical_profile,
    # Operators - Segment Selection
    operator.ALIGN_OT_select_h_segment,
    operator.ALIGN_OT_select_v_segment,
    operator.ALIGN_OT_select_cant_segment,
    # Operators - PI Edit Mode
    operator.ALIGN_OT_enter_pi_edit_mode,
    # Operators - Alignments tab authoring workflow (Add Element + interactive draw)
    operator.ALIGN_OT_add_alignment,
    operator.ALIGN_OT_remove_alignment,
    operator.ALIGN_OT_set_start_station,
    operator.ALIGN_OT_add_station_equation,
    operator.ALIGN_OT_edit_station_equation,
    operator.ALIGN_OT_remove_station_equation,
    operator.ALIGN_OT_apply_pi_curve,
    operator.ALIGN_OT_clear_pi_markers,
    operator.ALIGN_OT_draw_horizontal_alignment,
    # UI Panels (appear in Properties sidebar under CIVIL tab)
    ui.ALIGN_PT_alignment_creation,
    ui.ALIGN_PT_pi_editor,
    ui.ALIGN_PT_alignment_stationing,
    # UI Panels (appear in Properties sidebar under ALIGNMENTS tab)
    ui.ALIGN_PT_alignment_authoring,
    ui.ALIGN_PT_alignment_stationing_authoring,
    ui.ALIGN_PT_alignment_segments,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportAlignmentCSV.bl_idname, text="Alignment (.csv)")


def register():
    if not bpy.app.background:
        bpy.utils.register_tool(
            workspace.AlignmentTool,
            separator=True,
            group=False,
        )
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
    if not bpy.app.background:
        bpy.utils.unregister_tool(workspace.AlignmentTool)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
    del bpy.types.Scene.CivilAlignmentProperties
    del bpy.types.Object.bonsai_pi_curve_marker
