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
from mathutils import Matrix, Vector

import bonsai.tool as tool
from bonsai.bim.helper import prop_with_search

from . import data

# NOTE: do NOT add ``from __future__ import annotations`` to this module.
# PEP 563 stringifies the operator's EnumProperty class annotations, which
# breaks any introspection that reads ``cls.__annotations__[name].keywords``
# — including the enum-search helper that draws the search-button icon.

CLIP_BOX_NAME = "ClipBox"

# Display labels for the source-based picker, used for the menu entries and
# the dialog title. The dict keys are the canonical source-kind identifiers.
SOURCE_KIND_LABELS: dict[str, str] = {
    "SPATIAL": "Spatial Element",
    "CLASS": "Class",
    "TYPE": "Type",
    "MATERIAL": "Material",
    "PROFILE": "Profile",
    "DRAWING": "Drawing",
    "STATUS": "Status",
    "SYSTEM": "System",
    "GROUP": "Group",
    "ZONE": "Zone",
}


_SOURCE_ID_DISPATCH = {
    "SPATIAL": data.spatial_items,
    "CLASS": data.class_items,
    "TYPE": data.type_items,
    "MATERIAL": data.material_items,
    "PROFILE": data.profile_items,
    "DRAWING": data.drawing_items,
    "STATUS": data.status_items,
    "SYSTEM": data.system_items,
    "GROUP": data.group_items,
    "ZONE": data.zone_items,
}


def _source_id_items(self, context):
    """Dispatch the ``source_id`` enum items based on the picked ``source_kind``."""
    fn = _SOURCE_ID_DISPATCH.get(self.source_kind)
    if fn is None:
        return [(data.NO_OPTIONS_ID, "No options", "")]
    return fn(self, context)


def _source_display_name(kind, source_id):
    """Human-readable name of the picked source, used in the clip-box name."""
    if kind == "STATUS":
        return next((label for value, label in data.STATUS_LABELS if value == source_id), source_id)
    if kind == "CLASS":
        # source_id IS the human-readable IFC class name.
        return source_id
    ifc = tool.Ifc.get()
    if ifc is None:
        return source_id
    try:
        entity = ifc.by_id(int(source_id))
    except (TypeError, ValueError, RuntimeError):
        return source_id
    return (getattr(entity, "Name", None) or "Unnamed").strip() or "Unnamed"


class BIM_OT_align_view_to_clip_face(bpy.types.Operator):
    bl_idname = "bim.align_view_to_clip_face"
    bl_label = "Align View to Clip Box Face"
    bl_description = "Orient the 3D viewport to look directly at the picked clip-box face"
    bl_options = {"REGISTER"}

    axis: bpy.props.IntProperty(default=0, options={"SKIP_SAVE"})
    is_max: bpy.props.BoolProperty(default=True, options={"SKIP_SAVE"})

    def execute(self, context):
        rv3d = getattr(context, "region_data", None)
        if rv3d is None:
            return {"CANCELLED"}
        clip_box = tool.ClipBox.get_active_clip_box(context.scene)
        if clip_box is None:
            return {"CANCELLED"}
        rot_mat = clip_box.matrix_world.to_quaternion().to_matrix()
        outward_local = Vector((0.0, 0.0, 0.0))
        outward_local[self.axis] = 1.0 if self.is_max else -1.0
        outward = (rot_mat @ outward_local).normalized()
        if outward.length == 0.0:
            return {"CANCELLED"}
        up_world = (rot_mat @ _local_up_for_face(self.axis, self.is_max)).normalized()
        rv3d.view_rotation = _view_rotation_from_forward_and_up(-outward, up_world)
        return {"FINISHED"}


def _local_up_for_face(axis: int, is_max: bool) -> Vector:
    """Box-local up direction for a face, following Blender numpad conventions.

    Side faces (local ±X / ±Y normal) → local +Z is up. Top face (local +Z
    normal) → local +Y is up; bottom face (local -Z normal) → local -Y is
    up. The caller rotates this through the empty's matrix so the
    resulting world up axis tracks the box's orientation.
    """
    if axis == 2:
        return Vector((0.0, 1.0, 0.0)) if is_max else Vector((0.0, -1.0, 0.0))
    return Vector((0.0, 0.0, 1.0))


def _view_rotation_from_forward_and_up(forward: Vector, up_hint: Vector) -> "bpy.types.Quaternion":
    """Build a camera ``view_rotation`` that looks along ``forward`` with
    ``up_hint`` projected to the camera's local +Y."""
    back = -forward.normalized()
    right = up_hint.cross(back)
    if right.length < 1e-6:
        right = Vector((1.0, 0.0, 0.0))
    right.normalize()
    up = back.cross(right).normalized()
    return Matrix(
        (
            (right.x, up.x, back.x),
            (right.y, up.y, back.y),
            (right.z, up.z, back.z),
        )
    ).to_quaternion()


class BIM_OT_add_clip_box(bpy.types.Operator):
    bl_idname = "bim.add_clip_box"
    bl_label = "Add Clip Box"
    bl_description = (
        "Create a clip box empty at the 3D cursor. The empty's location, rotation, and scale "
        "drive the viewport clip planes; resize with S, move with G, rotate with R"
    )
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        # Default to a 20m cube (scale 10 around [-1, +1] local cube) so
        # the volume covers a typical building storey or two rather than
        # the meaningless 2m unit cube. The user resizes with S.
        matrix = Matrix.Translation(context.scene.cursor.location.copy()) @ Matrix.Diagonal((10.0, 10.0, 10.0, 1.0))
        tool.ClipBox.create_clip_box_empty(context, matrix, name=CLIP_BOX_NAME)
        return {"FINISHED"}


class BIM_OT_add_clip_box_for_source(bpy.types.Operator):
    bl_idname = "bim.add_clip_box_for_source"
    bl_label = "Add Clip Box From Source"
    bl_description = (
        "Create a clip box sized to a chosen source: a spatial container, IFC type, material, "
        "profile, drawing camera frustum, element status, system, group, or zone"
    )
    bl_options = {"REGISTER", "UNDO"}

    source_kind: bpy.props.EnumProperty(
        name="Source Kind",
        items=[(kind, label, "") for kind, label in SOURCE_KIND_LABELS.items()],
        default="SPATIAL",
        options={"SKIP_SAVE"},
    )
    source_id: bpy.props.EnumProperty(
        name="Source",
        items=_source_id_items,
        options={"SKIP_SAVE"},
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        label = f"Clip {SOURCE_KIND_LABELS.get(self.source_kind, 'Source')}"
        # Search button appears once the enum exceeds the helper's threshold,
        # giving the user a popup picker instead of a plain dropdown.
        prop_with_search(layout, self, "source_id", text=label)

    def execute(self, context):
        if not self.source_id or self.source_id == data.NO_OPTIONS_ID:
            self.report({"ERROR"}, "No source selected.")
            return {"CANCELLED"}
        matrix = tool.ClipBox.compute_matrix_for_source(self.source_kind, self.source_id)
        if matrix is None:
            kind_label = SOURCE_KIND_LABELS.get(self.source_kind, self.source_kind)
            self.report(
                {"ERROR"},
                f"No elements found for {kind_label} '{_source_display_name(self.source_kind, self.source_id)}'.",
            )
            return {"CANCELLED"}
        name = f"ClipBox.{SOURCE_KIND_LABELS.get(self.source_kind, self.source_kind)}.{_source_display_name(self.source_kind, self.source_id)}"
        tool.ClipBox.create_clip_box_empty(context, matrix, name=name)
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

        copy = tool.ClipBox.create_clip_box_empty(context, source.matrix_world.copy(), name=source.name)
        # Preserve the source's display attrs so the duplicate matches.
        copy.empty_display_type = source.empty_display_type
        copy.empty_display_size = source.empty_display_size
        copy.show_in_front = source.show_in_front
        return {"FINISHED"}
