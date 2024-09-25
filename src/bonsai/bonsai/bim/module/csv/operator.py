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

from __future__ import annotations
import os
import bpy
import json
import ifccsv
import logging
import tempfile
import ifcopenshell
import ifcopenshell.util.selector
import bonsai.tool as tool
import bonsai.bim.module.drawing.scheduler as scheduler
from bonsai.bim.ifc import IfcStore
from bonsai.bim.handler import refresh_ui_data
from typing import TYPE_CHECKING
from collections import Counter

if TYPE_CHECKING:
    import pandas as pd


class AddCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.add_csv_attribute"
    bl_label = "Add CSV Attribute"
    bl_description = "Add a new IFC Attribute to the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        attribute = context.scene.CsvProperties.csv_attributes.add()
        return {"FINISHED"}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.CsvProperties.csv_attributes.remove(self.index)
        return {"FINISHED"}


class RemoveAllCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.remove_all_csv_attributes"
    bl_label = "Remove all CSV Attributes"
    bl_description = "Remove all IFC Attributes from the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.CsvProperties.csv_attributes.clear()
        return {"FINISHED"}


class ReorderCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.reorder_csv_attribute"
    bl_label = "Reorder CSV Attribute"
    bl_options = {"REGISTER", "UNDO"}
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()

    def execute(self, context):
        old = context.scene.CsvProperties.csv_attributes[self.old_index]
        new = context.scene.CsvProperties.csv_attributes[self.new_index]
        props = ["name", "header", "sort", "group", "varies_value", "summary", "formatting"]
        for prop in props:
            value = getattr(new, prop)
            setattr(new, prop, getattr(old, prop))
            setattr(old, prop, value)
        return {"FINISHED"}


class ImportCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.import_csv_attributes"
    bl_label = "Load CSV Settings"
    bl_description = "Import a json template for CSV export"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        props = context.scene.CsvProperties
        data = json.load(open(self.filepath))
        tool.Search.import_filter_query(data["query"], props.filter_groups)

        for prop in [
            "should_generate_svg",
            "should_preserve_existing",
            "include_global_id",
            "null_value",
            "empty_value",
            "true_value",
            "false_value",
            "concat_value",
            "csv_delimiter",
            "format",
            "csv_custom_delimiter",
        ]:
            setattr(props, prop, data["settings"][prop])

        props.csv_attributes.clear()
        for attribute in data["attributes"]:
            new = props.csv_attributes.add()
            for prop in ["name", "header", "sort", "group", "summary", "formatting"]:
                setattr(new, prop, attribute[prop])
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.export_csv_attributes"
    bl_label = "Save CSV Settings"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save a json template for CSV export"
    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        props = context.scene.CsvProperties

        settings = {}
        for prop in [
            "should_generate_svg",
            "should_preserve_existing",
            "include_global_id",
            "null_value",
            "empty_value",
            "true_value",
            "false_value",
            "concat_value",
            "csv_delimiter",
            "format",
            "csv_custom_delimiter",
        ]:
            settings[prop] = getattr(props, prop)

        data = {
            "query": tool.Search.export_filter_query(props.filter_groups),
            "attributes": [
                {
                    "name": a.name,
                    "header": a.header,
                    "sort": a.sort,
                    "group": a.group,
                    "summary": a.summary,
                    "formatting": a.formatting,
                }
                for a in props.csv_attributes
            ],
            "settings": settings,
        }

        with open(self.filepath, "w") as outfile:
            json.dump(data, outfile)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportIfcCsv(bpy.types.Operator):
    bl_idname = "bim.export_ifccsv"
    bl_label = "Export IFC"
    filename_ext = ".csv"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        props = context.scene.CsvProperties
        if not props.should_load_from_memory and not props.csv_ifc_file:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    def invoke(self, context, event):
        props = context.scene.CsvProperties
        if props.format == "web":
            return self.execute(context)
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, f".{props.format}")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifccsv

        props = context.scene.CsvProperties
        self.filepath = bpy.path.ensure_ext(self.filepath, f".{props.format}")
        if props.should_load_from_memory:
            ifc_file = IfcStore.get_file()
        else:
            ifc_file = ifcopenshell.open(props.csv_ifc_file)
        results = ifcopenshell.util.selector.filter_elements(
            ifc_file, tool.Search.export_filter_query(props.filter_groups)
        )

        ifc_csv = ifccsv.IfcCsv()
        attributes = [a.name for a in props.csv_attributes]
        headers = [a.header for a in props.csv_attributes]

        sort = []
        groups = []
        summaries = []
        formatting = []
        for attribute in props.csv_attributes:
            if attribute.sort != "NONE":
                sort.append({"name": attribute.name, "order": attribute.sort})
            if attribute.group != "NONE":
                groups.append({"name": attribute.name, "type": attribute.group, "varies_value": attribute.varies_value})
            if attribute.summary != "NONE":
                summaries.append({"name": attribute.name, "type": attribute.summary})

            if attribute.formatting != "{{value}}" and "{{value}}" in attribute.formatting:
                formatting.append({"name": attribute.name, "format": attribute.formatting})

        file_format = props.format
        if props.format == "web":
            file_format = "pd"

        sep = props.csv_custom_delimiter if props.csv_delimiter == "CUSTOM" else props.csv_delimiter
        ifc_csv.export(
            ifc_file,
            results,
            attributes,
            headers=headers,
            output=self.filepath,
            format=file_format,
            should_preserve_existing=props.should_preserve_existing,
            delimiter=sep,
            include_global_id=props.include_global_id,
            null=props.null_value,
            empty=props.empty_value,
            bool_true=props.true_value,
            bool_false=props.false_value,
            concat=props.concat_value,
            sort=sort,
            groups=groups,
            summaries=summaries,
            formatting=formatting,
        )

        if props.format != "csv" and props.should_generate_svg:
            schedule_creator = scheduler.Scheduler()
            schedule_creator.schedule(self.filepath, tool.Drawing.get_path_with_ext(self.filepath, "svg"))
        if props.format == "web":
            if not context.scene.WebProperties.is_connected:
                bpy.ops.bim.connect_websocket_server()
            df = ifc_csv.dataframe
            assert df is not None
            # Tabulator seems to be ignoring columns non-unique columns,
            # so we ensure they are unique at input.
            df.columns = self.get_unique_column_names(df)
            tool.Web.send_webui_data(data=df.to_csv(index=False), data_key="csv_data", event="csv_data")

        self.report({"INFO"}, f"Data is exported to {props.format.upper()}.")
        return {"FINISHED"}

    def get_unique_column_names(self, dataframe: pd.DataFrame) -> list[str]:
        count = Counter()
        return [
            f"{col}.{i:03d}" if duped and not count.update([col]) and (i := count[col]) else col
            for col, duped in zip(dataframe.columns, dataframe.columns.duplicated())
        ]


class ImportIfcCsv(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.import_ifccsv"
    bl_label = "Import to IFC"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.csv;*.ods;*.xlsx", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        props = context.scene.CsvProperties
        if not props.should_load_from_memory and not props.csv_ifc_file:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def _execute(self, context):
        import ifccsv

        props = context.scene.CsvProperties
        if props.should_load_from_memory:
            ifc_file = IfcStore.get_file()
        else:
            ifc_file = ifcopenshell.open(props.csv_ifc_file)
        ifc_csv = ifccsv.IfcCsv()
        sep = props.csv_custom_delimiter if props.csv_delimiter == "CUSTOM" else props.csv_delimiter
        attributes = [a.name for a in props.csv_attributes]
        ifc_csv.Import(
            ifc_file,
            self.filepath,
            attributes=attributes,
            delimiter=sep,
            null=props.null_value,
            empty=props.empty_value,
            bool_true=props.true_value,
            bool_false=props.false_value,
        )
        if not props.should_load_from_memory:
            ifc_file.write(props.csv_ifc_file)
        refresh_ui_data()
        self.report({"INFO"}, "Data is imported to IFC.")
        return {"FINISHED"}


class SelectCsvIfcFile(bpy.types.Operator):
    bl_idname = "bim.select_csv_ifc_file"
    bl_label = "Select CSV IFC File"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.CsvProperties.csv_ifc_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}
