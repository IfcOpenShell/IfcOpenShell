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
from blenderbim.bim.ifc import IfcStore


class BIM_PT_search(Panel):
    bl_label = "Search"
    bl_idname = "BIM_PT_search"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_selection"

    def draw(self, context):
        props = context.scene.BIMSearchProperties

        row = self.layout.row(align=True)
        row.operator("bim.add_filter_group", text="Add Search Group", icon="ADD")

        for i, filter_group in enumerate(props.filter_groups):
            box = self.layout.box()

            row = box.row(align=True)
            row.prop(props, "facet", text="")
            op = row.operator("bim.add_filter", text="Add Filter", icon="ADD")
            op.type = props.facet
            op.index = i

            for j, ifc_filter in enumerate(filter_group.filters):
                if ifc_filter.type == "entity":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "value", text="", icon="FILE_3D")
                elif ifc_filter.type == "attribute":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "name", text="", icon="COPY_ID")
                    row.prop(ifc_filter, "value", text="")
                elif ifc_filter.type == "type":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "value", text="", icon="FILE_VOLUME")
                elif ifc_filter.type == "material":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "value", text="", icon="MATERIAL")
                elif ifc_filter.type == "property":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "pset", text="", icon="PROPERTIES")
                    row.prop(ifc_filter, "name", text="")
                    row.prop(ifc_filter, "value", text="")
                elif ifc_filter.type == "classification":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "value", text="", icon="OUTLINER")
                elif ifc_filter.type == "location":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "name", text="", icon="PACKAGE")
                elif ifc_filter.type == "instance":
                    row = box.row(align=True)
                    row.prop(ifc_filter, "value", text="", icon="GRIP")
                op = row.operator("bim.remove_filter", text="", icon="X")
                op.group_index = i
                op.index = j

            row = box.row()
            row.operator("bim.remove_filter_group", icon="X").index = i

        if len(props.filter_groups):
            row = self.layout.row(align=True)
            row.operator("bim.search", text="Search", icon="VIEWZOOM")

        return  # Temporary for now whilst searching is being upgraded.

        row = self.layout.row()
        row.prop(props, "should_use_regex")
        row = self.layout.row()
        row.prop(props, "should_ignorecase")

        row = self.layout.row(align=True)
        row.operator("bim.reset_object_colours", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "global_id", text="", icon="TRACKER")
        row.operator("bim.select_global_id", text="", icon="VIEWZOOM").global_id = props.global_id

        row = self.layout.row(align=True)
        row.prop(props, "ifc_class", text="", icon="OBJECT_DATA")
        row.operator("bim.select_ifc_class", text="", icon="VIEWZOOM").ifc_class = props.ifc_class
        row.operator("bim.colour_by_class", text="", icon="BRUSH_DATA")

        row = self.layout.row(align=True)
        row.prop(props, "search_attribute_name", text="", icon="PROPERTIES")
        row.prop(props, "search_attribute_value", text="")
        op = row.operator("bim.select_attribute", text="", icon="VIEWZOOM")
        op.attribute_name = props.search_attribute_name
        op.attribute_value = props.search_attribute_value
        op = row.operator("bim.colour_by_attribute", text="", icon="BRUSH_DATA")
        op.attribute_name = props.search_attribute_name

        row = self.layout.row(align=True)
        row.prop(props, "search_pset_name", text="", icon="COPY_ID")
        row.prop(props, "search_prop_name", text="")
        row.prop(props, "search_pset_value", text="")
        op = row.operator("bim.select_pset", text="", icon="VIEWZOOM")
        op.pset_name = props.search_pset_name
        op.prop_name = props.search_prop_name
        op.pset_value = props.search_pset_value
        op = row.operator("bim.colour_by_pset", text="", icon="BRUSH_DATA")
        op.pset_name = props.search_pset_name
        op.prop_name = props.search_prop_name

        row = self.layout.row(align=True)
        row.operator("bim.activate_ifc_class_filter", icon="FILTER")
        row.operator("bim.activate_ifc_building_storey_filter", icon="FILTER")


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


class BIM_PT_IFCSelector(Panel):
    bl_label = "Selector"
    bl_idname = "BIM_PT_ifc_selector"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_selection"

    def draw(self, context):
        layout = self.layout
        layout.operator("bim.ifc_selector")


# this doesn't inherit from Panel since it's just a class to abstract away UI code from the IfcSelector Operator
class IfcSelectorUI:
    @classmethod
    def draw(self, context, layout):
        ifc_selector = context.scene.IfcSelectorProperties
        row = layout.row()

        row.context_pointer_set(name="bim_prop_group", data=ifc_selector)
        op = row.operator("bim.edit_blender_collection", text="Add selection group")
        op.option = "add"
        op.collection = "groups"
        layout.separator()

        self.draw_query_group_ui(self, ifc_selector, layout)

        if len(ifc_selector.groups) != 0:
            row = layout.row(align=True)
            row.prop(ifc_selector, "selector_query_syntax", text="Query Syntax")
            row.prop(ifc_selector, "manual_override", text="")

            select = row.operator("bim.filter_model_elements", text="", icon="RESTRICT_SELECT_OFF")
            select.option = "select"
            isolate = row.operator("bim.filter_model_elements", text="", icon="ZOOM_SELECTED")
            isolate.option = "isolate"
            hide = row.operator("bim.filter_model_elements", text="", icon="HIDE_ON")
            hide.option = "hide"
            unhide = row.operator("bim.filter_model_elements", text="", icon="HIDE_OFF")
            unhide.option = "unhide"

            row = layout.row(align=True)
            row.alignment = "CENTER"
            row.operator("bim.save_selector_query", text="Save Query")
            op = row.operator("bim.open_query_library", text="Load Query")
            row.operator("bim.add_to_ifc_group", text="Add to IFC Group")

            row = layout.row(align=True)
            row.operator("bim.show_scene_elements", text="Show All Elements", icon="HIDE_OFF")

    def draw_query_group_ui(self, ifc_selector, layout):
        for index, group in enumerate(ifc_selector.groups):
            row = layout.row()
            row.alignment = "CENTER"
            row.label(text="or") if index != 0 else None

            box = layout.box()
            row = box.row(align=True)
            row.alignment = "CENTER"
            row.label(text=f"Group #{str(index+1)}")
            row.context_pointer_set(name="bim_prop_group", data=group)
            op = row.operator("bim.edit_blender_collection", text="Add query", icon="PLUS")
            op.option = "add"
            op.collection = "queries"

            row.context_pointer_set(name="bim_prop_group", data=ifc_selector)
            op = row.operator("bim.edit_blender_collection", text="Remove selection group")
            op.option = "remove"
            op.collection = "groups"
            op.index = index

            self.draw_query_ui(self, group, box)

    def draw_query_ui(self, group, box):
        for index, query in enumerate(group.queries):
            row = box.row()
            row.alignment = "LEFT"

            row.prop(query, "and_or", text="") if index != 0 else None
            if query.and_or == "or":
                row = box.row()
                row.alignment = "LEFT"
            row.prop(query, "selector", text="")

            if query.selector in ["IFC Class", "IfcSpatialElement", "IfcElementType"]:
                row.label(text="Equals")
                row.prop_search(query, "active_option", query, "options", text="")
                row.prop_search(query, "active_sub_option", query, "sub_options", text="") if len(
                    query.sub_options
                ) != 0 else None
                self.draw_filter_ui(self, box, query)

            elif query.selector in ["GlobalId", "Attribute"]:
                row.prop(query, "negation", text="")
                row.prop(query, "comparison", text="")
                row.prop(query, "value", text="")

            row.context_pointer_set(name="bim_prop_group", data=group)
            op = row.operator("bim.edit_blender_collection", icon="REMOVE", text="")
            op.option = "remove"
            op.collection = "queries"
            op.index = index

            row.context_pointer_set(name="bim_prop_group", data=query)
            op = (
                row.operator("bim.edit_blender_collection", text="Add filter")
                if query.selector == "IFC Class"
                else None
            )
            if op:
                op.option = "add"
                op.collection = "filters"

    def draw_filter_ui(self, box, query):
        for filter_index, f in enumerate(query.filters):
            row = box.row()
            row.alignment = "LEFT"
            row.label(text="  ↪")
            row.prop(f, "and_or", text="") if filter_index != 0 else None
            if f.and_or == "or":
                row = box.row()
                row.alignment = "LEFT"
                row.label(text="  ↪")
            row.prop(f, "selector", text="")

            if f.selector == "Attribute":
                row.prop_search(f, "active_option", f, "options", text="", results_are_suggestions=True)
                row.prop(
                    f,
                    "negation",
                )
                row.prop(f, "comparison", text="")
                row.prop(f, "value", text="")

            elif f.selector == "IfcPropertySet":
                row.prop_search(f, "active_option", f, "options", text="")
                row.prop_search(f, "active_sub_option", f, "sub_options", text="")
                row.prop(f, "negation")
                row.prop(f, "comparison", text="")
                row.prop(f, "value", text="")

            row.context_pointer_set(name="bim_prop_group", data=query)
            op = row.operator("bim.edit_blender_collection", icon="REMOVE", text="")
            op.option = "remove"
            op.collection = "filters"
            op.index = filter_index
