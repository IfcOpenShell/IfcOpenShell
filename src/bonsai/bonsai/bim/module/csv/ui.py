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

import bonsai.bim.helper
from bpy.types import Panel
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.search.data import SearchData


class BIM_PT_ifccsv(Panel):
    bl_label = "Spreadsheet Import/Export"
    bl_idname = "BIM_PT_ifccsv"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_collaboration"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        props = scene.CsvProperties

        if IfcStore.get_file():
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

        if not IfcStore.get_file() or not props.should_load_from_memory:
            row = layout.row(align=True)
            row.prop(props, "csv_ifc_file")
            row.operator("bim.select_csv_ifc_file", icon="FILE_FOLDER", text="")

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
            row.prop(props, "include_global_id")
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

        row = layout.row(align=True)
        row.operator("bim.export_ifccsv", icon="EXPORT", text="Export IFC to " + props.format.upper())
        row.operator("bim.import_ifccsv", icon="IMPORT")
