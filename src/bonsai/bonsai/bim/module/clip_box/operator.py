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

import bpy

import bonsai.tool as tool

CLIP_BOX_NAME = "ClipBox"
CLIP_BOX_COLLECTION = "BBIM_ClipBoxes"


class BIM_OT_add_clip_box(bpy.types.Operator):
    bl_idname = "bim.add_clip_box"
    bl_label = "Add Clip Box"
    bl_description = (
        "Create a clip box empty at the 3D cursor. The empty's location, rotation, and scale "
        "drive the viewport clip planes; resize with S, move with G, rotate with R"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)

        obj = bpy.data.objects.new(CLIP_BOX_NAME, None)
        obj.empty_display_type = "CUBE"
        obj.empty_display_size = 1.0
        obj.location = context.scene.cursor.location.copy()
        # Default to a 20m cube (scale 10 around [-1, +1] local cube) so
        # the volume covers a typical building storey or two rather than
        # the meaningless 2m unit cube. The user resizes with S.
        obj.scale = (10.0, 10.0, 10.0)
        obj.show_in_front = True

        collection = tool.Blender.get_or_create_collection(context.scene, CLIP_BOX_COLLECTION)
        collection.objects.link(obj)

        obj_props = tool.ClipBox.get_object_props(obj)
        obj_props.is_clip_box = True

        entry = scene_props.clip_boxes.add()
        entry.obj = obj
        scene_props.active_clip_box_index = len(scene_props.clip_boxes) - 1

        # Adding a new clip box arms clipping so the user sees the cut
        # immediately. Without this they'd have to find the panel
        # toggle to discover the feature actually works.
        scene_props.enabled = True

        tool.Blender.set_active_object(obj)
        tool.ClipBox.refresh(context.scene)
        # Persist to the project pset so the box round-trips through IFC
        # save/load. A project-level pset avoids the IfcRoot scale lock /
        # strip that a per-entity placement would trigger on export.
        tool.ClipBox.save_to_project_pset(context.scene)
        return {"FINISHED"}


class BIM_OT_remove_clip_box(bpy.types.Operator):
    bl_idname = "bim.remove_clip_box"
    bl_label = "Remove Clip Box"
    bl_description = "Remove this clip box and its host empty"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})
    delete_object: bpy.props.BoolProperty(default=True, name="Delete Host Object")

    def execute(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)
        index = self.index if self.index >= 0 else scene_props.active_clip_box_index
        if index < 0 or index >= len(scene_props.clip_boxes):
            return {"CANCELLED"}

        entry = scene_props.clip_boxes[index]
        obj = entry.obj
        scene_props.clip_boxes.remove(index)
        if scene_props.active_clip_box_index >= len(scene_props.clip_boxes):
            scene_props.active_clip_box_index = max(0, len(scene_props.clip_boxes) - 1)

        if self.delete_object and obj is not None:
            bpy.data.objects.remove(obj, do_unlink=True)

        tool.ClipBox.refresh(context.scene)
        tool.ClipBox.save_to_project_pset(context.scene)
        return {"FINISHED"}


class BIM_OT_set_active_clip_box(bpy.types.Operator):
    bl_idname = "bim.set_active_clip_box"
    bl_label = "Set Active Clip Box"
    bl_description = "Set this clip box as the active one driving the viewport clip"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})

    def execute(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)
        if self.index < 0 or self.index >= len(scene_props.clip_boxes):
            return {"CANCELLED"}
        scene_props.active_clip_box_index = self.index
        return {"FINISHED"}


class BIM_OT_toggle_clip_box_enabled(bpy.types.Operator):
    bl_idname = "bim.toggle_clip_box_enabled"
    bl_label = "Toggle Clip Box"
    bl_description = "Toggle whether the active clip box is driving the viewport clip planes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)
        scene_props.enabled = not scene_props.enabled
        return {"FINISHED"}


class BIM_OT_duplicate_clip_box(bpy.types.Operator):
    bl_idname = "bim.duplicate_clip_box"
    bl_label = "Duplicate Clip Box"
    bl_description = "Duplicate this clip box: copy its empty + matrix into a new entry"
    bl_options = {"REGISTER", "UNDO"}

    index: bpy.props.IntProperty(default=-1, options={"SKIP_SAVE"})

    def execute(self, context):
        scene_props = tool.ClipBox.get_scene_props(context.scene)
        source_index = self.index if self.index >= 0 else scene_props.active_clip_box_index
        if source_index < 0 or source_index >= len(scene_props.clip_boxes):
            return {"CANCELLED"}
        source = scene_props.clip_boxes[source_index].obj
        if source is None:
            return {"CANCELLED"}

        copy = bpy.data.objects.new(source.name, None)
        copy.empty_display_type = source.empty_display_type
        copy.empty_display_size = source.empty_display_size
        copy.show_in_front = source.show_in_front
        copy.matrix_world = source.matrix_world.copy()

        collection = tool.Blender.get_or_create_collection(context.scene, CLIP_BOX_COLLECTION)
        collection.objects.link(copy)

        tool.ClipBox.get_object_props(copy).is_clip_box = True

        entry = scene_props.clip_boxes.add()
        entry.obj = copy
        scene_props.active_clip_box_index = len(scene_props.clip_boxes) - 1
        scene_props.enabled = True

        tool.Blender.set_active_object(copy)
        tool.ClipBox.refresh(context.scene)
        tool.ClipBox.save_to_project_pset(context.scene)
        return {"FINISHED"}
