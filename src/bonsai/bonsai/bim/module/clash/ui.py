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

import bpy
import bonsai.bim.helper
from bpy.types import Panel
from bonsai.bim.module.clash.data import ClashData


class BIM_PT_ifcclash(Panel):
    bl_label = "Clash Sets"
    bl_idname = "BIM_PT_ifcclash"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_clash_detection"

    def draw(self, context):
        if not ClashData.is_loaded:
            ClashData.load()

        layout = self.layout

        scene = context.scene
        props = scene.BIMClashProperties

        row = layout.row(align=True)
        row.operator("bim.add_clash_set")
        row.operator("bim.import_clash_sets", text="", icon="IMPORT")
        row.operator("bim.export_clash_sets", text="", icon="EXPORT")

        if not props.clash_sets:
            return

        layout.template_list("BIM_UL_clash_sets", "", props, "clash_sets", props, "active_clash_set_index")

        if not props.active_clash_set:
            return

        clash_set = props.active_clash_set

        row = layout.row(align=True)
        row.prop(clash_set, "name")
        row.operator("bim.remove_clash_set", icon="X", text="").index = props.active_clash_set_index

        row = layout.row()
        row.prop(clash_set, "mode")

        if clash_set.mode == "intersection":
            row = layout.row()
            row.prop(clash_set, "tolerance")
            row = layout.row()
            row.prop(clash_set, "check_all")
        elif clash_set.mode == "collision":
            row = layout.row()
            row.prop(clash_set, "allow_touching")
        elif clash_set.mode == "clearance":
            row = layout.row()
            row.prop(clash_set, "clearance")
            row = layout.row()
            row.prop(clash_set, "check_all")

        row = layout.row(align=True)
        row.label(text="Group A:", icon="OUTLINER_OB_POINTCLOUD")
        row.operator("bim.add_clash_source", icon="ADD", text="").group = "a"

        for index, source in enumerate(clash_set.a):
            row = layout.row(align=True)
            row.prop(source, "name", text="")
            row.prop(source, "mode", text="")
            op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
            op.index = index
            op.group = "a"
            op = row.operator("bim.remove_clash_source", icon="X", text="")
            op.index = index
            op.group = "a"

            if source.mode != "a":
                bonsai.bim.helper.draw_filter(
                    layout, source.filter_groups, ClashData, f"clash_{props.active_clash_set_index}_a_{index}"
                )

        row = layout.row(align=True)
        row.label(text="Group B:", icon="OUTLINER_OB_POINTCLOUD")
        row.operator("bim.add_clash_source", icon="ADD", text="").group = "b"

        for index, source in enumerate(clash_set.b):
            row = layout.row(align=True)
            row.prop(source, "name", text="")
            row.prop(source, "mode", text="")
            op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
            op.index = index
            op.group = "b"
            op = row.operator("bim.remove_clash_source", icon="X", text="")
            op.index = index
            op.group = "b"

            if source.mode != "a":
                bonsai.bim.helper.draw_filter(
                    layout, source.filter_groups, ClashData, f"clash_{props.active_clash_set_index}_b_{index}"
                )

        row = layout.row()
        row.prop(props, "should_create_clash_snapshots")

        layout.prop(props, "export_path")

        row = layout.row()
        op = row.operator("bim.execute_ifc_clash")
        op.filepath = props.export_path

        row = layout.row()
        row.label(text=f"{len(clash_set.clashes)} Clashes Found", icon="PIVOT_CURSOR")

        layout.template_list("BIM_UL_clashes", "", props.active_clash_set, "clashes", props, "active_clash_index")
        row = layout.row()
        row.operator("bim.select_clash")


class BIM_PT_clash_manager(Panel):
    bl_idname = "BIM_PT_clash_manager"
    bl_label = "Clash Manager"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_clash_detection"

    def draw(self, context):
        pass


class BIM_PT_smart_clash_manager(Panel):
    bl_idname = "BIM_PT_smart_clash_manager"
    bl_label = "Smart Clash Manager"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_clash_manager"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMClashProperties

        row = layout.row()
        layout.label(text="Select clash results to group:")

        row = layout.row(align=True)
        row.prop(props, "clash_results_path", text="")
        op = row.operator("bim.select_clash_results", icon="FILE_FOLDER", text="")

        row = layout.row()
        layout.label(text="Select output path for smart-grouped clashes:")

        row = layout.row(align=True)
        row.prop(props, "smart_grouped_clashes_path", text="")
        op = row.operator("bim.select_smart_grouped_clashes_path", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "smart_clash_grouping_max_distance")

        row = layout.row(align=True)
        row.operator("bim.smart_clash_group")

        row = layout.row(align=True)
        row.operator("bim.load_smart_groups_for_active_clash_set")

        layout.template_list("BIM_UL_smart_groups", "", props, "smart_clash_groups", props, "active_smart_group_index")

        row = layout.row(align=True)
        row.operator("bim.select_smart_group")


class BIM_UL_clash_sets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.prop(item, "name", text="", emboss=False)
        else:
            layout.label(text="", translate=False)


class BIM_UL_smart_groups(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        ob = data
        if item:
            layout.label(text=str(item.number), translate=False, icon="NONE", icon_value=0)
        else:
            layout.label(text="", translate=False)


class BIM_UL_clashes(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=str(item.a_name), translate=False, icon="NONE", icon_value=0)
            row.label(text=str(item.b_name), translate=False, icon="NONE", icon_value=0)
            row.prop(item, "status", text="")
        else:
            layout.label(text="", translate=False)
