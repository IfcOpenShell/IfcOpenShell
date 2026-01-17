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
import bonsai.tool as tool
from bpy.types import Panel
from bonsai.bim.module.search.data import SearchData


class BIM_UL_ifc_files(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {"DEFAULT", "COMPACT"}:
            row = layout.row(align=True)
            row.prop(item, "file_path", text="")
            row.prop(item, "is_selected", text="")
            op = row.operator("bim.open_ifc_file", icon="HIDE_OFF", text="")
            op.file_path = item.file_path
            row.operator("bim.remove_ifc_file", icon="X", text="").index = index
        elif self.layout_type in {"GRID"}:
            layout.label(text=item.file_path)


class BIM_PT_ifccsv(Panel):
    bl_label = "Spreadsheet Import/Export"
    bl_idname = "BIM_PT_ifccsv"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):
        assert self.layout
        layout = self.layout
        props = tool.Blender.get_csv_props()
        ifcprops = tool.Blender.get_ifc_props()

        if tool.Ifc.get():
            row = layout.row(align=True)
            row.prop(props, "should_load_from_memory")
            row.operator("bim.import_csv_attributes", icon="IMPORT", text="")
            row.operator("bim.export_csv_attributes", icon="EXPORT", text="")
        else:
            row = layout.row(align=True)
            row.alignment = "RIGHT"
            row.operator("bim.import_csv_attributes", icon="IMPORT", text="")
            row.operator("bim.export_csv_attributes", icon="EXPORT", text="")
        row.prop(props, "should_show_settings", icon="PREFERENCES", text="")

        if not tool.Ifc.get() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.operator("bim.add_ifc_files", icon="FILE_FOLDER", text="Add IFC Files")
            row.operator("bim.add_linked_files", icon="LINKED", text="Add Linked Files")

            layout.template_list(
                "BIM_UL_ifc_files",
                "",
                ifcprops,
                "ifc_files",
                ifcprops,
                "active_ifc_file_index",
            )

        if props.should_show_settings:
            layout.use_property_split = True
            row = layout.row(align=True)
            row.prop(props, "format")

            if props.format == "csv":
                row = layout.row(align=True)
                row.prop(props, "csv_delimiter")

                if props.csv_delimiter == "CUSTOM":
                    row = layout.row(align=True)
                    row.prop(props, "csv_custom_delimiter")

            row = layout.row()
            row.prop(props, "should_generate_svg")
            row = layout.row()
            row.prop(props, "should_preserve_existing")
            row = layout.row()
            row.prop(props, "include_filename_and_global_id")
            row = layout.row()
            row.prop(props, "null_value")
            row = layout.row()
            row.prop(props, "empty_value")
            row = layout.row()
            row.prop(props, "true_value")
            row = layout.row()
            row.prop(props, "false_value")
            row = layout.row()
            row.prop(props, "concat_value")
            layout.use_property_split = False

        bonsai.bim.helper.draw_filter(self.layout, props.filter_groups, SearchData, "csv")

        row = layout.row(align=True)
        op = row.operator("bim.search", text="Select", icon="VIEWZOOM")
        op.property_group = "CsvProperties"
        layout.separator()

        row = layout.row(align=True)
        row.operator("bim.add_csv_attribute", icon="ADD")
        row.prop(props, "should_show_sort", icon="SORTSIZE", text="")
        row.prop(props, "should_show_group", icon="OUTLINER_COLLECTION", text="")
        row.prop(props, "should_show_summary", icon="SYNTAX_ON", text="")
        row.prop(props, "should_show_formatting", icon="CON_TRANSLIKE", text="")

        total = len(props.csv_attributes)
        for index, attribute in enumerate(props.csv_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.prop(attribute, "header", text="")
            row.prop(attribute, "data_type", text="Type")
            if props.should_show_sort:
                row.prop(attribute, "sort", text="")
            if props.should_show_group:
                row.prop(attribute, "group", text="")
                if attribute.group == "VARIES":
                    row.prop(attribute, "varies_value", text="")
            if props.should_show_summary:
                row.prop(attribute, "summary", text="")
            if props.should_show_formatting:
                row.prop(attribute, "formatting", text="")
            if total > 1:
                if index != 0:
                    op = row.operator(f"bim.reorder_csv_attribute", icon="TRIA_UP", text="")
                    op.old_index = index
                    op.new_index = index - 1
                if index + 1 != total:
                    op = row.operator(f"bim.reorder_csv_attribute", icon="TRIA_DOWN", text="")
                    op.old_index = index
                    op.new_index = index + 1
            row.operator("bim.remove_csv_attribute", icon="X", text="").index = index

        box = layout.box()
        row = box.row(align=True)
        
        preferences = tool.Blender.get_addon_preferences()
        if not preferences.chain_filter_with_set_operations:
            row.operator("bim.add_output_filter_group", icon="ADD", text="Add Output Filter Group")
        else:
            op = row.operator("bim.edit_filter_query", text="", icon="FILTER")
            row = box.row(align=True)
            add_op = row.operator("bim.add_output_filter", text="Add Output Filter", icon="ADD")
            add_op.group_index = 0


        if preferences.chain_filter_with_set_operations:
            if len(props.output_filter_groups) > 0 and len(props.output_filter_groups[0].filters) > 0:
                for i, filter in enumerate(props.output_filter_groups[0].filters):
                    row = box.row(align=True)
                    if i > 0:
                        mode_icons = {"ADD": "ADD", "SUBTRACT": "REMOVE", "FILTER": "FILTER"}
                        op = row.operator(
                            "bim.toggle_output_filter_inclusion",
                            icon=mode_icons.get(filter.filter_mode, "ADD"),
                            text="",
                            depress=filter.filter_mode != "ADD",
                        )
                        op.group_index = 0
                        op.filter_index = i
                    row.prop(filter, "column", text="")
                    row.prop(filter, "comparison", text="")
                    row.prop(filter, "value", text="")
                    op = row.operator("bim.remove_output_filter", icon="X", text="")
                    op.group_index = 0
                    op.filter_index = i
        elif len(props.output_filter_groups) > 0:
            for group_idx, group in enumerate(props.output_filter_groups):
                group_box = box.box()
                group_row = group_box.row(align=True)
                group_row.label(text="")
                add = group_row.operator("bim.add_output_filter", text="Add Output Filter")
                add.group_index = group_idx
                if not preferences.chain_filter_with_set_operations:
                    remove = group_row.operator("bim.remove_output_filter_group", icon="X", text="")
                    remove.group_index = group_idx
                if len(group.filters) > 0:
                    for i, filter in enumerate(group.filters):
                        row = group_box.row(align=True)
                        if preferences.chain_filter_with_set_operations and i > 0:
                            mode_icons = {"ADD": "ADD", "SUBTRACT": "REMOVE", "FILTER": "FILTER"}
                            op = row.operator(
                                "bim.toggle_output_filter_inclusion",
                                icon=mode_icons.get(filter.filter_mode, "ADD"),
                                text="",
                                depress=filter.filter_mode != "ADD",
                            )
                            op.group_index = group_idx
                            op.filter_index = i
                        row.prop(filter, "column", text="")
                        row.prop(filter, "comparison", text="")
                        row.prop(filter, "value", text="")
                        op = row.operator("bim.remove_output_filter", icon="X", text="")
                        op.group_index = group_idx
                        op.filter_index = i
                else:
                    group_box.label(text="No filters in this group")
        else:
            box.label(text="No filter groups added")

        row = layout.row(align=True)
        if props.format == "web":
            row.operator("bim.export_ifccsv", icon="EXPORT", text="Open Web UI")
        else:
            row.operator("bim.export_ifccsv", icon="EXPORT", text="Export IFC to " + props.format.upper())
        row.operator("bim.import_ifccsv", icon="IMPORT")

        csv_props = tool.Blender.get_csv_props()
        if csv_props and 0.0 < csv_props.progress < 1.0:
            progress_row = layout.row()
            phase_text = csv_props.import_phase or "Importing..."
            progress_row.progress(
                factor=csv_props.progress,
                type="BAR",
                text=phase_text
            )
            progress_row.scale_x = 2
