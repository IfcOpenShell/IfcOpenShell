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

from __future__ import annotations

from bpy.types import Menu, Panel, UIList

import bonsai.tool as tool

# Per-kind icon for the source-picker menu. Picked from Blender's built-in
# icon set; semantically close to the kind so users can scan the menu visually.
_SOURCE_MENU_ENTRIES: tuple[tuple[str, str, str], ...] = (
    ("SPATIAL", "Clip Spatial Element", "OUTLINER_COLLECTION"),
    ("CLASS", "Clip by Class", "BLANK1"),
    ("TYPE", "Clip Type", "FILE_3D"),
    ("MATERIAL", "Clip Material", "MATERIAL"),
    ("PROFILE", "Clip Profile", "MESH_CIRCLE"),
    ("DRAWING", "Clip Drawing Extents", "CAMERA_DATA"),
    ("STATUS", "Clip by Status", "INFO"),
    ("SYSTEM", "Clip by System", "MOD_FLUID"),
    ("GROUP", "Clip by Group", "OUTLINER_OB_GROUP_INSTANCE"),
    ("ZONE", "Clip by Zone", "MOD_LATTICE"),
)


class BIM_MT_clip_box_add_for_source(Menu):
    bl_idname = "BIM_MT_clip_box_add_for_source"
    bl_label = "Add Clip Box From Source"

    def draw(self, context):
        layout = self.layout
        for kind, label, icon in _SOURCE_MENU_ENTRIES:
            op = layout.operator("bim.add_clip_box_for_source", text=label, icon=icon)
            op.source_kind = kind


class BIM_MT_clip_box_settings(Menu):
    bl_idname = "BIM_MT_clip_box_settings"
    bl_label = "Clip Box Settings"

    def draw(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)
        self.layout.prop(scene_props, "clip_only_ifc_products")
        self.layout.prop(scene_props, "include_linked_ifc")
        self.layout.prop(scene_props, "enable_gizmos")


class BIM_MT_clip_box_info(Menu):
    bl_idname = "BIM_MT_clip_box_info"
    bl_label = "Clip Box Face Handles"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Face Handles", icon="INFO")
        layout.separator()
        layout.label(text="Drag a face to resize the clip box on that axis.")
        layout.label(text="The opposite face stays fixed (one-sided resize).")
        layout.label(text="Ctrl+Click a face to align the viewport to it.")
        layout.separator()
        layout.label(text="Toggle handles from the Settings (gear) menu.")


class BIM_UL_clip_box(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        obj = item.obj
        row = layout.row(align=True)
        if obj is None:
            # Host empty was deleted from outliner; still expose the
            # remove button so the orphan entry isn't permanent.
            row.label(text="(missing)", icon="ERROR")
            row.operator("bim.remove_clip_box", text="", icon="X", emboss=False).index = index
            return
        row.prop(obj, "name", text="", emboss=False, icon="MESH_CUBE")
        row.operator("bim.duplicate_clip_box", text="", icon="DUPLICATE", emboss=False).index = index
        row.operator("bim.remove_clip_box", text="", icon="X", emboss=False).index = index


class BIM_PT_clip_box(Panel):
    bl_idname = "BIM_PT_clip_box"
    bl_label = "Clip Box"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_sandbox"

    def draw(self, context):
        layout = self.layout
        scene_props = tool.ClipBox.get_scene_props(context.scene)

        toggles = layout.row(align=True)
        toggles.scale_y = 2.0
        toggles.prop(
            scene_props,
            "enabled",
            text="Enable Clipping",
            icon="HIDE_OFF" if scene_props.enabled else "HIDE_ON",
            toggle=True,
        )
        toggles.prop(scene_props, "show_caps", text="Show Caps", icon="MOD_SOLIDIFY", toggle=True)
        toggles.menu("BIM_MT_clip_box_settings", icon="PREFERENCES", text="")
        toggles.menu("BIM_MT_clip_box_info", icon="INFO", text="")

        layout.separator()
        row = layout.row(align=True)
        row.operator("bim.add_clip_box", icon="ADD", text="Add Clip Box")
        row.menu("BIM_MT_clip_box_add_for_source", icon="DOWNARROW_HLT", text="")

        layout.template_list(
            "BIM_UL_clip_box",
            "",
            scene_props,
            "clip_boxes",
            scene_props,
            "active_clip_box_index",
            rows=3,
        )

        obj = tool.ClipBox.get_active_clip_box(context.scene)
        if obj is None:
            layout.label(text="No active clip box", icon="INFO")
            return

        col = layout.column(align=True)
        col.label(text="Edit the empty with G / R / S to move / rotate / resize")
        col.prop(obj, "location")
        col.prop(obj, "rotation_euler")
        col.prop(obj, "scale")
