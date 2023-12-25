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

import bpy
from bpy.types import Panel


class BIM_PT_ifcclash(Panel):
    bl_label = "Clash Sets"
    bl_idname = "BIM_PT_ifcclash"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_clash_detection"

    def draw(self, context):
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

        if props.active_clash_set_index < len(props.clash_sets):
            clash_set = props.active_clash_set

            row = layout.row(align=True)
            row.prop(clash_set, "name")
            row.operator("bim.remove_clash_set", icon="X", text="").index = props.active_clash_set_index

            row = layout.row(align=True)
            row.prop(clash_set, "tolerance")

            layout.label(text="Group A:")
            row = layout.row()
            row.operator("bim.add_clash_source").group = "a"

            for index, source in enumerate(clash_set.a):
                row = layout.row(align=True)
                row.prop(source, "name", text="")
                op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
                op.index = index
                op.group = "a"
                op = row.operator("bim.remove_clash_source", icon="X", text="")
                op.index = index
                op.group = "a"

                row = layout.row(align=True)
                row.prop(source, "mode", text="")
                row.prop(source, "selector", text="")

            layout.label(text="Group B:")
            row = layout.row()
            row.operator("bim.add_clash_source").group = "b"

            for index, source in enumerate(clash_set.b):
                row = layout.row(align=True)
                row.prop(source, "name", text="")
                op = row.operator("bim.select_clash_source", icon="FILE_FOLDER", text="")
                op.index = index
                op.group = "b"
                op = row.operator("bim.remove_clash_source", icon="X", text="")
                op.index = index
                op.group = "b"

                row = layout.row(align=True)
                row.prop(source, "mode", text="")
                row.prop(source, "selector", text="")

            row = layout.row()
            row.prop(props, "should_create_clash_snapshots")
            row = layout.row(align=True)
            row.operator("bim.execute_ifc_clash")
            row.operator("bim.select_ifc_clash_results")


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


class BIM_PT_dumb_clash_manager(Panel):
    bl_idname = "BIM_PT_dumb_clash_manager"
    bl_label = "Dumb Manager"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_clash_manager"

    def draw(self, context):
        layout = self.layout
        props = context.scene.BIMClashProperties

        row = layout.row(align=True)
        row.operator("bim.load_ifc_clashes", text="LOAD IFC CLASHES", icon="IMPORT")
        row.operator("bim.save_ifc_clashes", text="SAVE CLASH RESULTS", icon="EXPORT")
        layout.template_list("BIM_UL_clashes", "", props.active_clash_set, "clashes", props, "active_clash_index")
        # bim.select_clash
        row = layout.row(align=True)
        row.operator("bim.select_clash", text="SELECT CLASH", icon="IMPORT")
        row.prop(props, "sould_focus_on_clash", icon="RESTRICT_VIEW_OFF")


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
