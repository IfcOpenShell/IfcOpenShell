# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import bpy
from bpy.app.handlers import persistent

import bonsai.tool as tool

from . import face_quad, gizmos, operator, prop, ui

classes = (
    operator.BIM_OT_add_clip_box,
    operator.BIM_OT_add_clip_box_for_source,
    operator.BIM_OT_align_view_to_clip_face,
    operator.BIM_OT_duplicate_clip_box,
    operator.BIM_OT_remove_clip_box,
    operator.BIM_OT_set_active_clip_box,
    operator.BIM_OT_toggle_clip_box_enabled,
    prop.BIMClipBoxProperties,
    prop.BIMSceneClipBoxProperties,
    face_quad.BIM_GT_box_face_quad,
    face_quad.BIM_GT_box_face_outline,
    gizmos.OBJECT_GGT_bim_clip_box,
    ui.BIM_MT_clip_box_add_for_source,
    ui.BIM_MT_clip_box_info,
    ui.BIM_MT_clip_box_settings,
    ui.BIM_UL_clip_box,
    ui.BIM_PT_clip_box,
)


@persistent
def _on_depsgraph_update(scene, depsgraph):
    tool.ClipBox.on_depsgraph_update(scene, depsgraph)
    tool.ClipBox.on_depsgraph_update_caps(scene, depsgraph)


@persistent
def _on_load_pre(filepath):
    # Tear down any in-flight clip-box timers before Blender frees the
    # WM / screens / areas / regions for the loading file. A refresh timer
    # that survives the teardown fires against the new file's freshly-
    # allocated regions before their GPU state is wired, CTD-ing inside
    # GPU_matrix_ortho_set. The gate also blocks the depsgraph IFC-reload
    # branch and is held closed until on_pre_view fires for the first time
    # on the new file (first paint = GPU contexts wired).
    tool.ClipBox._file_loading = True
    tool.ClipBox._post_load_paint_pending = True
    tool.ClipBox._cancel_pending_refresh()
    tool.ClipBox._cancel_pending_cap_rebuild()


@persistent
def _on_load_post(filepath):
    # The _file_loading gate is NOT cleared here: load_post fires before
    # the new file's first paint, so GPU contexts may still be uninitialised.
    # on_pre_view consumes _post_load_paint_pending to open the gate at the
    # safe moment and kick the post-load re-arm.
    # Restore the per-scene clip-box list from the project's BBIM_ClipBoxes
    # pset. Runs after the standard load_post that creates Blender objects.
    tool.ClipBox._last_seen_object_matrices.clear()
    tool.ClipBox.load_from_project_pset()


_draw_handler_pre = None
_draw_handler_post = None


def register():
    global _draw_handler_pre, _draw_handler_post
    bpy.types.Object.BIMClipBoxProperties = bpy.props.PointerProperty(type=prop.BIMClipBoxProperties)
    bpy.types.Scene.BIMSceneClipBoxProperties = bpy.props.PointerProperty(type=prop.BIMSceneClipBoxProperties)
    tool.ClipBox.reset_ownership()
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)
    if _on_load_pre not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(_on_load_pre)
    if _on_load_post not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_on_load_post)
    if _draw_handler_pre is None:
        _draw_handler_pre = bpy.types.SpaceView3D.draw_handler_add(tool.ClipBox.on_pre_view, (), "WINDOW", "PRE_VIEW")
    if _draw_handler_post is None:
        _draw_handler_post = bpy.types.SpaceView3D.draw_handler_add(
            tool.ClipBox.on_post_view_caps, (), "WINDOW", "POST_VIEW"
        )


def unregister():
    global _draw_handler_pre, _draw_handler_post
    if _draw_handler_post is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handler_post, "WINDOW")
        except ValueError:
            pass
        _draw_handler_post = None
    if _draw_handler_pre is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(_draw_handler_pre, "WINDOW")
        except ValueError:
            pass
        _draw_handler_pre = None
    if _on_load_post in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_on_load_post)
    if _on_load_pre in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(_on_load_pre)
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    tool.ClipBox._cancel_pending_refresh()
    tool.ClipBox._cancel_pending_cap_rebuild()
    tool.ClipBox._last_seen_object_matrices.clear()
    tool.ClipBox.clear_clip_planes()
    del bpy.types.Object.BIMClipBoxProperties
    del bpy.types.Scene.BIMSceneClipBoxProperties
