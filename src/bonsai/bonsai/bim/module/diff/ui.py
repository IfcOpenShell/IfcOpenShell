# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

from bpy.types import Panel
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.diff.data import DiffData
import bonsai.bim.helper
import bonsai.tool as tool


class BIM_PT_diff(Panel):
    bl_label = "Diff"
    bl_idname = "BIM_PT_diff"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_quality_control"

    def draw(self, context):
        if not DiffData.is_loaded:
            DiffData.load()

        layout = self.layout
        layout.use_property_split = True

        scene = context.scene
        props = scene.DiffProperties

        layout.label(text="IFC Diff Setup:")

        if tool.Ifc.get():
            row = layout.row()
            row.prop(props, "active_file")

            if props.active_file == "NONE":
                row = layout.row(align=True)
                row.prop(props, "old_file")
                row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")

                row = layout.row(align=True)
                row.prop(props, "new_file")
                row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")
            elif props.active_file == "NEW":
                row = layout.row(align=True)
                row.prop(props, "old_file")
                row.operator("bim.select_diff_old_file", icon="FILE_FOLDER", text="")
            elif props.active_file == "OLD":
                row = layout.row(align=True)
                row.prop(props, "new_file")
                row.operator("bim.select_diff_new_file", icon="FILE_FOLDER", text="")

            if props.active_file != "NONE":
                row = layout.row()
                row.prop(props, "should_load_changed_elements")
        else:
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

        bonsai.bim.helper.draw_filter(self.layout, props.filter_groups, DiffData, "diff")

        row = layout.row()
        row.operator("bim.execute_ifc_diff")

        if props.active_file == "NONE":
            return

        row = layout.row(align=True)
        row.prop(props, "diff_json_file")
        row.operator("bim.select_diff_json_file", icon="FILE_FOLDER", text="")
        row.operator("bim.visualise_diff", icon="HIDE_OFF", text="")

        if DiffData.data["diff_json"]:
            row = layout.row()
            col = row.column(align=True)
            col.operator(
                "bim.select_diff_objects",
                icon="RESTRICT_SELECT_OFF",
                text=f"Select {DiffData.data['total_added']} Added",
            ).mode = "ADDED"
            col.operator(
                "bim.select_diff_objects",
                icon="RESTRICT_SELECT_OFF",
                text=f"Select {DiffData.data['total_deleted']} Deleted",
            ).mode = "DELETED"
            col.operator(
                "bim.select_diff_objects",
                icon="RESTRICT_SELECT_OFF",
                text=f"Select {DiffData.data['total_changed']} Changed",
            ).mode = "CHANGED"

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
