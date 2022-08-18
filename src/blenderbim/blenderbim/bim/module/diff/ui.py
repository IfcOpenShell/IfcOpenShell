# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.diff.data import DiffData
import blenderbim.tool as tool
import json


class BIM_PT_diff(Panel):
    bl_label = "IFC Diff"
    bl_idname = "BIM_PT_diff"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_quality_control"

    def draw(self, context):
        if not DiffData.is_loaded:
            DiffData.load()

        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.DiffProperties

        layout.label(text="IFC Diff Setup:")

        row = layout.row(align=True)
        row.prop(props, "old_file")
        row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "new_file")
        row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "diff_relationships")
        row.context_pointer_set("bim_prop_group", props)
        add = row.operator("bim.edit_blender_collection", icon="ADD", text="")
        add.option = "add"
        add.collection = "diff_relationships"

        for index, r in enumerate(props.diff_relationships):
            row = layout.row(align=True)
            row.context_pointer_set("bim_prop_group", props)
            row.prop(r, "relationship", text=" ")
            remove = row.operator("bim.edit_blender_collection", icon="REMOVE", text="")
            remove.option = "remove"
            remove.collection = "diff_relationships"
            remove.index = index

        row = layout.row(align=True)
        row.prop(props, "diff_filter_elements")
        row.operator("bim.ifc_selector", icon="FILTER", text="")

        row = layout.row()
        row.operator("bim.execute_ifc_diff")

        row = layout.row(align=True)
        row.prop(props, "diff_json_file")
        row.operator("bim.select_diff_json_file", icon="FILE_FOLDER", text="")
        row.operator("bim.visualise_diff", icon="HIDE_OFF", text="")

        if DiffData.data["diff_json"]:
            row = layout.row()
            row.alignment = "CENTER"
            row.label(text=f"{DiffData.data['total_added']} added")
            row.label(text=f"{DiffData.data['total_deleted']} deleted")
            row.label(text=f"{DiffData.data['total_changed']} changed")

        if DiffData.data["changes"]:
            box = layout.box()
            row = box.row()
            row.label(text="Active Object Changes:")
            for key, value in DiffData.data["changes"].items():
                row = box.row()
                if key == "Added":
                    icon = "ADD"
                elif key == "Deleted":
                    icon = "X"
                else:
                    icon = "GREASEPENCIL"
                row.label(text=key, icon=icon)
