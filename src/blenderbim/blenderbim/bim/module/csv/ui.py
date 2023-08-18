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

import blenderbim.bim.helper
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.search.data import SearchData


class BIM_PT_ifccsv(Panel):
    bl_label = "CSV Import/Export"
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
            row.prop(props, "should_show_settings", icon="PREFERENCES", text="")
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
            row = layout.row(align=True)
            row.prop(props, "format")

            if props.format == "csv":
                row = layout.row(align=True)
                row.prop(props, "csv_delimiter")

                if props.csv_delimiter == "CUSTOM":
                    row = layout.row(align=True)
                    row.prop(props, "csv_custom_delimiter")

            row = layout.row(align=True)
            row.prop(props, "null_value")

        blenderbim.bim.helper.draw_filter(self.layout, props, SearchData, "csv")

        row = layout.row(align=True)
        row.operator("bim.add_csv_attribute", icon="ADD")

        for index, attribute in enumerate(props.csv_attributes):
            row = layout.row(align=True)
            row.prop(attribute, "name", text="")
            row.operator("bim.remove_csv_attribute", icon="X", text="").index = index

        row = layout.row(align=True)
        row.operator("bim.export_ifccsv", icon="EXPORT", text="Export IFC to " + props.format.upper())
        row.operator("bim.import_ifccsv", icon="IMPORT")
