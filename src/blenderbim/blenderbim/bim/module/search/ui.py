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
import blenderbim.bim.helper
from bpy.types import Panel
from blenderbim.bim.module.search.data import SearchData, ColourByPropertyData, SelectSimilarData


class BIM_PT_search(Panel):
    bl_label = "Search"
    bl_idname = "BIM_PT_search"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_grouping_and_filtering"

    def draw(self, context):
        if not SearchData.is_loaded:
            SearchData.load()

        props = context.scene.BIMSearchProperties

        blenderbim.bim.helper.draw_filter(self.layout, props.filter_groups, SearchData, "search")

        if len(props.filter_groups):
            row = self.layout.row(align=True)
            row.operator("bim.search", text="Search", icon="VIEWZOOM")

        return


class BIM_PT_filter(Panel):
    bl_label = "Filter Selection"
    bl_idname = "BIM_PT_filter"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_grouping_and_filtering"

    def draw(self, context):
        row = self.layout.row(align=True)
        row.operator("bim.activate_ifc_class_filter", icon="FILTER")
        row.operator("bim.activate_ifc_container_filter", icon="FILTER")


class BIM_PT_colour_by_property(Panel):
    bl_label = "Colour By Property"
    bl_idname = "BIM_PT_colour_by_property"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_grouping_and_filtering"

    def draw(self, context):
        if not ColourByPropertyData.is_loaded:
            ColourByPropertyData.load()

        props = context.scene.BIMSearchProperties

        row = self.layout.row(align=True)
        row.label(text=f"{len(ColourByPropertyData.data['saved_colourschemes'])} Saved Colourschemes")

        if ColourByPropertyData.data["saved_colourschemes"]:
            row.operator("bim.load_colourscheme", text="", icon="IMPORT")
        row.operator("bim.save_colourscheme", text="", icon="EXPORT")

        row = self.layout.row()
        row.prop(props, "colourscheme_query", text="Query")

        row = self.layout.row(align=True)
        row.operator("bim.colour_by_property", icon="BRUSH_DATA")
        row.operator("bim.reset_object_colours")
        row.operator("bim.select_by_property", icon="RESTRICT_SELECT_OFF", text="")

        if len(props.colourscheme):
            self.layout.template_list(
                "BIM_UL_colourscheme", "", props, "colourscheme", props, "active_colourscheme_index"
            )


class BIM_PT_select_similar(Panel):
    bl_label = "Select Similar"
    bl_idname = "BIM_PT_select_similar"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_options = {"DEFAULT_CLOSED"}
    bl_parent_id = "BIM_PT_tab_grouping_and_filtering"

    def draw(self, context):
        if not SelectSimilarData.is_loaded:
            SelectSimilarData.load()

        props = context.scene.BIMSearchProperties

        if SelectSimilarData.data["element_key"]:
            row = self.layout.row(align=True)
            row.prop(props, "element_key", text="")
            op = row.operator("bim.select_similar", text="", icon="RESTRICT_SELECT_OFF")
            op.key = props.element_key
        else:
            row = self.layout.row()
            row.label(text=f"No Active Element")


class BIM_UL_colourscheme(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMWorkScheduleProperties
        if not item:
            return
        row = layout.row(align=True)
        row.label(text=f"{item.name} ({item.total})")
        row.prop(item, "colour", text="")


class BIM_UL_ifc_class_filter(bpy.types.UIList):
    use_filter_linked: bpy.props.BoolProperty(name="Included", default=True, options=set(), description="Filter")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout
        split.use_property_split = True
        split.use_property_decorate = False
        split.prop(
            item, "is_selected", text="", emboss=False, icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
        )
        split.prop(item, "name", text="", emboss=False, slider=True)
        split = split.column()
        split.scale_x = 0.5
        split.label(text=str(item.total))


class BIM_UL_ifc_building_storey_filter(bpy.types.UIList):
    use_filter_linked: bpy.props.BoolProperty(name="Included", default=True, options=set(), description="Filter")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        split = layout
        split.use_property_split = True
        split.use_property_decorate = False
        split.prop(
            item, "is_selected", text="", emboss=False, icon="CHECKBOX_HLT" if item.is_selected else "CHECKBOX_DEHLT"
        )
        split.prop(item, "name", text="", emboss=False, slider=True)
        split = split.column()
        split.scale_x = 0.5
        split.label(text=str(item.total))
