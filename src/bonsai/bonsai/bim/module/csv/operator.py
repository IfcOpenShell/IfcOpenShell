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
import subprocess
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bonsai.bim.handler import refresh_ui_data
from typing import TYPE_CHECKING
from collections import Counter
from fractions import Fraction

import pandas as pd
import subprocess
import time
import re



class AddCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.add_csv_attribute"
    bl_label = "Add CSV Attribute"
    bl_description = "Add a new IFC Attribute to the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        props.csv_attributes.add()
        return {"FINISHED"}


class RemoveCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.remove_csv_attribute"
    bl_label = "Remove CSV Attribute"
    bl_options = {"REGISTER", "UNDO"}
    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        props.csv_attributes.remove(self.index)
        return {"FINISHED"}


class RemoveAllCsvAttributes(bpy.types.Operator):
    bl_idname = "bim.remove_all_csv_attributes"
    bl_label = "Remove all CSV Attributes"
    bl_description = "Remove all IFC Attributes from the CSV export"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        props.csv_attributes.clear()
        return {"FINISHED"}


class ReorderCsvAttribute(bpy.types.Operator):
    bl_idname = "bim.reorder_csv_attribute"
    bl_label = "Reorder CSV Attribute"
    bl_options = {"REGISTER", "UNDO"}
    old_index: bpy.props.IntProperty()
    new_index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        old = props.csv_attributes[self.old_index]
        new = props.csv_attributes[self.new_index]
        props = ["name", "header", "sort", "group", "varies_value", "summary", "formatting"]
        for prop in props:
            value = getattr(new, prop)
            setattr(new, prop, getattr(old, prop))
            setattr(old, prop, value)
        return {"FINISHED"}


class ImportCsvAttributes(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.import_csv_attributes"
    bl_label = "Load CSV Settings"
    bl_description = "Import a json template for CSV export"
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})
    filename_ext = ".json"

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        data = json.load(open(self.filepath))
        tool.Search.import_filter_query(data["query"], props.filter_groups)

        for prop in [
            "should_generate_svg",
            "should_preserve_existing",
            "include_filename_and_global_id",
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
            for prop in ["name", "header", "sort", "group", "summary", "formatting", "data_type"]:
                if prop in attribute:
                    setattr(new, prop, attribute[prop])

        props.output_filter_groups.clear()
        for group_data in data.get("output_filter_groups", []):
            group = props.output_filter_groups.add()
            group.active_output_filter = group_data.get("active_output_filter", -1)
            for filter_data in group_data.get("filters", []):
                f = group.filters.add()
                f.name = filter_data.get("name", "")
                f.column = filter_data.get("column", "")
                f.comparison = filter_data.get("comparison", "=")
                f.value = filter_data.get("value", "")

        if "ifc_files" in data and data["ifc_files"]:
            ifc_props = tool.Blender.get_ifc_props()
            ifc_props.ifc_files.clear()
            for file_data in data.get("ifc_files", []):
                node = ifc_props.ifc_files.add()
                node.file_path = file_data.get("file_path", "")
                node.is_selected = file_data.get("is_selected", False)

        return {"FINISHED"}


class ExportCsvAttributes(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_csv_attributes"
    bl_label = "Save CSV Settings"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Save a json template for CSV export"
    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_csv_props()

        settings = {}
        for prop in [
            "should_generate_svg",
            "should_preserve_existing",
            "include_filename_and_global_id",
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
                    "data_type": getattr(a, "data_type", "string"),
                }
                for a in props.csv_attributes
            ],
            "settings": settings,
            "output_filter_groups": [
                {
                    "active_output_filter": group.active_output_filter,
                    "filters": [
                        {
                            "name": f.name,
                            "column": f.column,
                            "comparison": f.comparison,
                            "value": f.value,
                        }
                        for f in group.filters
                    ],
                }
                for group in props.output_filter_groups
            ],
            "ifc_files": [
                {
                    "file_path": node.file_path,
                    "is_selected": node.is_selected,
                }
                for node in tool.Blender.get_ifc_props().ifc_files
            ],
        }

        filepath = getattr(self, 'filepath', None)
        if not filepath:
            filepath = self.filepath if hasattr(self, 'filepath') else ''
        with open(filepath, "w") as outfile:
            json.dump(data, outfile)

        return {"FINISHED"}


class AddOutputFilterGroup(bpy.types.Operator):
    bl_idname = "bim.add_output_filter_group"
    bl_label = "Add Output Filter Group"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        props = context.scene.CsvProperties
        props.output_filter_groups.add()
        return {"FINISHED"}


class RemoveOutputFilterGroup(bpy.types.Operator):
    bl_idname = "bim.remove_output_filter_group"
    bl_label = "Remove Output Filter Group"
    bl_options = {"REGISTER", "UNDO"}
    group_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.CsvProperties
        props.output_filter_groups.remove(self.group_index)
        return {"FINISHED"}


class AddOutputFilter(bpy.types.Operator):
    bl_idname = "bim.add_output_filter"
    bl_label = "Add Output Filter"
    bl_options = {"REGISTER", "UNDO"}
    group_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.CsvProperties
        # Create group if it doesn't exist (for chain_filter_with_set_operations mode)
        while len(props.output_filter_groups) <= self.group_index:
            props.output_filter_groups.add()
        group = props.output_filter_groups[self.group_index]
        group.filters.add()
        group.active_output_filter = len(group.filters) - 1
        return {"FINISHED"}


class RemoveOutputFilter(bpy.types.Operator):
    bl_idname = "bim.remove_output_filter"
    bl_label = "Remove Output Filter"
    bl_options = {"REGISTER", "UNDO"}

    group_index: bpy.props.IntProperty()
    filter_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.CsvProperties
        group = props.output_filter_groups[self.group_index]
        group.filters.remove(self.filter_index)
        if group.active_output_filter >= len(group.filters):
            group.active_output_filter = len(group.filters) - 1
        return {"FINISHED"}


class ToggleOutputFilterInclusion(bpy.types.Operator):
    bl_idname = "bim.toggle_output_filter_inclusion"
    bl_label = "Toggle Output Filter Mode"
    bl_description = "Cycle between Add (+), Subtract (-), and Filter modes for this output filter"
    bl_options = {"REGISTER", "UNDO"}

    group_index: bpy.props.IntProperty()
    filter_index: bpy.props.IntProperty()

    def execute(self, context):
        props = context.scene.CsvProperties
        group = props.output_filter_groups[self.group_index]
        output_filter = group.filters[self.filter_index]

        if output_filter.filter_mode == "ADD":
            output_filter.filter_mode = "SUBTRACT"
        elif output_filter.filter_mode == "SUBTRACT":
            output_filter.filter_mode = "FILTER"
        else:
            output_filter.filter_mode = "ADD"

        return {"FINISHED"}


class ExportIfcCsv(bpy.types.Operator, ExportHelper):
    bl_idname = "bim.export_ifccsv"
    bl_label = "Export IFC"
    bl_description = "Export IFC data as a spreadsheet."
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_csv_props()
        propsIfc = tool.Blender.get_ifc_props()
        something_selected = any(node.is_selected for node in propsIfc.ifc_files)
        if not props.should_load_from_memory and not something_selected:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    @classmethod
    def description(cls, context, properties):
        props = tool.Blender.get_csv_props()
        if props.format == "web":
            return "Open Web UI for spreadsheet data export."
        return f"Export IFC data as a spreadsheet by the provided filepath in '{props.format}' format ."

    def invoke(self, context, event):
        props = tool.Blender.get_csv_props()
        if props.format == "web":
            return self.execute(context)
        self.filter_glob = f"*.{props.format}"
        self.filename_ext = f".{props.format}"
        propsIfc = tool.Blender.get_ifc_props()
        selected_basenames = [os.path.splitext(os.path.basename(node.file_path))[0]
                              for node in propsIfc.ifc_files if node.is_selected]
        if selected_basenames:
            suggested_name = "_".join(selected_basenames) + self.filename_ext
            self.filepath = os.path.join(os.path.dirname(bpy.data.filepath), suggested_name)
        return ExportHelper.invoke(self, context, event)

    def get_unique_column_names(self, dataframe: pd.DataFrame) -> list[str]:
        count = Counter()
        return [
            f"{col}.{i:03d}" if duped and not count.update([col]) and (i := count[col]) else col
            for col, duped in zip(dataframe.columns, dataframe.columns.duplicated())
        ]

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        propsIfc = tool.Blender.get_ifc_props()
        
        if props:
            props.progress = 0.01
            props.import_phase = "Starting export..."
        
        self.ifccsv = ifccsv
        self.filepath = bpy.path.ensure_ext(self.filepath, f".{props.format}")
        
        if props.should_load_from_memory:
            ifc_file_path = bpy.context.scene.BIMProperties.ifc_file
            for node in propsIfc.ifc_files:
                node.is_selected = False
            for node in propsIfc.ifc_files:
                if tool.Ifc.resolve_uri(node.file_path) == ifc_file_path:
                    node.is_selected = True
                    break
            if not any(node.is_selected for node in propsIfc.ifc_files):
                new_file = propsIfc.ifc_files.add()
                new_file.file_path = ifc_file_path
                new_file.is_selected = True
        
        self._selected_files = [node for node in propsIfc.ifc_files if node.is_selected]
        self._total_files = len(self._selected_files)
        
        self._file_index = 0
        self._file_substep = 0
        self._current_ifc_file = None
        self._current_results = None
        self._current_df = None
        self._current_ifc_csv = None
        self._current_export_generator = None
        self._current_element_count = 0
        self._current_elements_processed = 0
        self._dataframes = []
        self._timer_interval = 0.05
        self._total_rows_extracted = 0
        self._timer = context.window_manager.event_timer_add(self._timer_interval, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            csv_props = tool.Blender.get_csv_props()
            if csv_props:
                csv_props.progress = 0.0
                csv_props.import_phase = ""
            wm = getattr(context, 'window_manager', None)
            if wm:
                wm.event_timer_remove(self._timer)
            self.report({'INFO'}, 'Export cancelled.')
            return {'CANCELLED'}
        
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}
        
        wm = getattr(context, 'window_manager', None)
        if wm:
            for window in wm.windows:
                for area in window.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()

        props = tool.Blender.get_csv_props()
        start_time = time.perf_counter()
        
        while self._file_index < self._total_files:
                node = self._selected_files[self._file_index]
                file_name = os.path.basename(node.file_path)
                
                if self._file_substep == 0:
                    props.csv_ifc_file = tool.Ifc.resolve_uri(node.file_path)
                    file_num = self._file_index + 1
                    props.import_phase = f"Processing ({file_name}) opening... {file_num}/{self._total_files}"
                    props.progress = (self._file_index / self._total_files) if self._total_files > 0 else 0.0
                    
                    try:
                        self._current_ifc_file = ifcopenshell.open(props.csv_ifc_file)
                    except Exception as e:
                        self.report({"INFO"}, f"An error occurred while opening {props.csv_ifc_file}: {e}")
                        self._file_index += 1
                        self._file_substep = 0
                        if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                            return {'PASS_THROUGH'}
                        continue
                    
                    self._file_substep = 1
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        return {'PASS_THROUGH'}
                
                if self._file_substep == 1:
                    file_num = self._file_index + 1
                    props.import_phase = f"Processing ({file_name}) filtering... {file_num}/{self._total_files}"
                    
                    self._current_results = ifcopenshell.util.selector.filter_elements(
                        self._current_ifc_file, tool.Search.export_filter_query(props.filter_groups)
                    )
                    
                    self._file_substep = 2
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        return {'PASS_THROUGH'}
                
                if self._file_substep == 2:
                    if self._current_export_generator is None:
                        file_num = self._file_index + 1
                        props.import_phase = f"Processing ({file_name}) extracting... {file_num}/{self._total_files}"
                        
                        self._current_ifc_csv = self.ifccsv.IfcCsv()
                        attributes = [a.name for a in props.csv_attributes]
                        headers = [a.header for a in props.csv_attributes]
                        sep = props.csv_custom_delimiter if props.csv_delimiter == "CUSTOM" else props.csv_delimiter
                        
                        self._current_element_count = len(self._current_results)
                        self._current_elements_processed = 0
                        
                        self._current_export_generator = self._current_ifc_csv.Export(
                            self._current_ifc_file,
                            self._current_results,
                            attributes,
                            headers=headers,
                            output="",
                            include_global_id=props.include_filename_and_global_id,
                            delimiter=sep,
                            null=props.null_value,
                            empty=props.empty_value,
                            bool_true=props.true_value,
                            bool_false=props.false_value,
                            concat=props.concat_value,
                        )
                    
                    start_substep_time = time.perf_counter()
                    while True:
                        try:
                            element = next(self._current_export_generator)
                            self._current_elements_processed += 1
                            
                            file_num = self._file_index + 1
                            file_start_progress = (self._file_index / self._total_files) if self._total_files > 0 else 0.0
                            file_progress_range = (1.0 / self._total_files) if self._total_files > 0 else 1.0
                            element_progress = (self._current_elements_processed / self._current_element_count) if self._current_element_count > 0 else 0.0
                            props.progress = file_start_progress + (element_progress * file_progress_range)
                            props.import_phase = f"Processing ({file_name}) {self._current_elements_processed}/{self._current_element_count} {file_num}/{self._total_files}"
                        except StopIteration:
                            self._file_substep = 3
                            break
                        
                        if (time.perf_counter() - start_substep_time) >= getattr(self, '_timer_interval', 0.05):
                            return {'PASS_THROUGH'}
                    
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        return {'PASS_THROUGH'}
                
                if self._file_substep == 3:
                    attributes = [a.name for a in props.csv_attributes]
                    
                    sort = []
                    groups = []
                    summaries = []
                    formatting = []
                    for attribute in props.csv_attributes:
                        if attribute.sort != "NONE":
                            sort.append({"name": attribute.name, "order": attribute.sort})
                        if attribute.group != "NONE":
                            groups.append(
                                {"name": attribute.name, "type": attribute.group, "varies_value": attribute.varies_value}
                            )
                        if attribute.summary != "NONE":
                            summaries.append({"name": attribute.name, "type": attribute.summary})
                        if attribute.formatting != "{{value}}" and "{{value}}" in attribute.formatting:
                            formatting.append({"name": attribute.name, "format": attribute.formatting})
                    
                    self._current_ifc_csv.group_results(groups, attributes)
                    self._current_ifc_csv.summarise_results(summaries, attributes)
                    self._current_ifc_csv.sort_results(sort, attributes, props.include_filename_and_global_id)
                    self._current_ifc_csv.format_results(formatting, attributes, props.null_value)
                    
                    self._current_df = self._current_ifc_csv.export_pd()
                    
                    if self._current_df is not None:
                        if props.include_filename_and_global_id:
                            file_name = os.path.basename(node.file_path)
                            if "FileName" in self._current_df.columns:
                                self._current_df["FileName"] = file_name
                            else:
                                self._current_df.insert(0, "FileName", file_name)
                        
                        self._dataframes.append(self._current_df)
                        self._total_rows_extracted += len(self._current_df)
                        
                        current_file_rows = len(self._current_df)
                        file_num = self._file_index + 1
                        props.progress = ((self._file_index + 1) / self._total_files) if self._total_files > 0 else 1.0
                        props.import_phase = f"Processing ({file_name}) {current_file_rows} rows {file_num}/{self._total_files}"
                    
                    self._current_ifc_file = None
                    self._current_results = None
                    self._current_df = None
                    self._current_ifc_csv = None
                    self._current_export_generator = None
                    self._current_element_count = 0
                    self._current_elements_processed = 0
                    self._file_index += 1
                    self._file_substep = 0
                    
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        return {'PASS_THROUGH'}
        
        wm = getattr(context, 'window_manager', None)
        
        if not self._dataframes:
            props.progress = 0.0
            props.import_phase = ""
            if wm:
                wm.event_timer_remove(self._timer)
            self.report({"ERROR"}, "No data was generated for selected files.")
            return {"CANCELLED"}
        
        combined_df = pd.concat(self._dataframes, ignore_index=True)
        combined_df.columns = self.get_unique_column_names(combined_df)
        
        preferences = tool.Blender.get_addon_preferences()
        final_df = self.apply_filters(combined_df, props, preferences)
        
        try:
            self.format_and_write_output(final_df, props)
            props.progress = 1.0
            props.import_phase = ""
        except Exception as e:
            props.progress = 0.0
            props.import_phase = ""
            if wm:
                wm.event_timer_remove(self._timer)
            self.report({"ERROR"}, f"Failed to write output: {str(e)}")
            return {'CANCELLED'}
        
        props.progress = 0.0
        props.import_phase = ""
        if wm:
            wm.event_timer_remove(self._timer)
        return {'FINISHED'}
    
    def apply_filters(self, combined_df, props, preferences):
        if preferences.chain_filter_with_set_operations:
            result_df = None
            if len(props.output_filter_groups) > 0:
                for filter_idx, filter in enumerate(props.output_filter_groups[0].filters):
                    df = combined_df.copy()
                    column_name = filter.column
                    comparison_operator = filter.comparison
                    comparison_value = filter.value
                    if not comparison_value:
                        continue
                    if comparison_operator == "regex":
                        try:
                            pattern = re.compile(comparison_value)
                            if column_name == "__ALL__":
                                mask = df.astype(str).apply(lambda x: x.str.contains(pattern, na=False)).any(axis=1)
                                df = df[mask]
                            else:
                                mask = df[column_name].astype(str).str.contains(pattern, na=False)
                                df = df[mask]
                        except Exception as e:
                            self.report({"ERROR"}, f"Invalid regular expression pattern: {str(e)}")
                            continue
                    else:
                        if not column_name:
                            self.report({"WARNING"}, "Column must be specified for non-regex comparisons")
                            continue
                        col_match = next((col for col in df.columns if col.lower() == column_name.lower()), None)
                        if not col_match:
                            self.report({"WARNING"}, f"Column '{column_name}' not found in dataframe.")
                            continue
                        try:
                            column = df[col_match]
                            value = comparison_value
                            attr = next((a for a in props.csv_attributes if a.header == column_name), None)
                            data_type = getattr(attr, 'data_type', 'string') if attr else 'string'
                            def parse_imperial(val):
                                """
                                Parse an imperial measurement string and return meters.
                                Supported formats:
                                - 9' 2"
                                - 29' 2''
                                - 8' 10 3/16"
                                - 8.5 (decimal feet)
                                - 10 3/16" (inches only)
                                """
                                if val is None or (isinstance(val, str) and not val.strip()):
                                    return None

                                s = str(val).strip()

                                feet = 0.0
                                inches = 0.0

                                if re.fullmatch(r"\d+(\.\d+)?", s):
                                    feet = float(s)
                                else:
                                    feet_match = re.search(r"(\d+(?:\.\d+)?)\s*'(?!')", s)
                                    if feet_match:
                                        feet = float(feet_match.group(1))

                                    s_no_feet = re.sub(r"\d+(?:\.\d+)?\s*'(?!')", "", s)

                                    inch_match = re.search(
                                        r"(\d+)?\s*(\d+/\d+)?\s*(?:\"|''|$)",
                                        s_no_feet
                                    )

                                    if inch_match:
                                        whole = inch_match.group(1)
                                        frac = inch_match.group(2)

                                        if whole:
                                            inches += float(whole)
                                        if frac:
                                            inches += float(Fraction(frac))

                                total_inches = feet * 12.0 + inches
                                meters = total_inches * 0.0254
                                return meters
                            try:
                                if data_type == 'imperial_string':
                                    column_converted = column.apply(parse_imperial)
                                    val_m = parse_imperial(value)
                                    column = column_converted
                                    value = val_m
                                elif data_type == 'float':
                                    column = pd.to_numeric(column, errors='coerce')
                                    try:
                                        value = float(value)
                                    except Exception:
                                        pass
                                elif data_type == 'int':
                                    column = pd.to_numeric(column, errors='coerce').astype('Int64')
                                    try:
                                        value = int(value)
                                    except Exception:
                                        pass
                                elif data_type == 'bool':
                                    column = column.astype(bool)
                                    value = bool(value)
                            except (ValueError, TypeError) as e:
                                self.report({"WARNING"}, f"Could not interpret value '{value}' as {data_type}. Error: {str(e)}")
                            if comparison_operator == "=":
                                if data_type == "imperial_string":
                                    try:
                                        mask = column.notna() & pd.notna(value) & (abs(column - value) < 1e-3)
                                    except Exception:
                                        mask = column == value
                                elif data_type == "float":
                                    try:
                                        col_float = pd.to_numeric(column, errors='coerce')
                                        val_float = float(value)
                                        mask = col_float.notna() & (abs(col_float - val_float) < 1e-3)
                                    except Exception:
                                        mask = column == value
                                else:
                                    mask = column == value
                            elif comparison_operator == "!=":
                                mask = column != value
                            elif comparison_operator == ">":
                                mask = column > value
                            elif comparison_operator == ">=":
                                mask = column >= value
                            elif comparison_operator == "<":
                                mask = column < value
                            elif comparison_operator == "*=":
                                mask = column.astype(str).str.contains(str(value), na=False)
                            elif comparison_operator == "!*=":
                                mask = ~column.astype(str).str.contains(str(value), na=False)
                            else:
                                self.report({"WARNING"}, f"Unknown operator '{comparison_operator}'.")
                                continue
                            filtered_rows = df[mask]
                            df = filtered_rows
                        except Exception as e:
                            self.report({"ERROR"}, f"Comparison filter error: {str(e)}")
                    
                    if filter_idx == 0:
                        result_df = df
                    else:
                        filter_mode = filter.filter_mode
                        if filter_mode == "ADD":
                            result_df = pd.concat([result_df, df]).drop_duplicates().reset_index(drop=True)
                        elif filter_mode == "SUBTRACT":
                            result_df = result_df.merge(df, indicator=True, how='left').query('_merge == "left_only"').drop('_merge', axis=1).reset_index(drop=True)
                        elif filter_mode == "FILTER":
                            result_df = pd.merge(result_df, df, how='inner').reset_index(drop=True)
            
            return result_df if result_df is not None else combined_df
        else:
            group_results = []
            for group_idx, group in enumerate(props.output_filter_groups):
                df = combined_df.copy()
                for filter_idx, filter in enumerate(group.filters):
                    column_name = filter.column
                    comparison_operator = filter.comparison
                    comparison_value = filter.value
                    if not comparison_value:
                        continue
                    if comparison_operator == "regex":
                        try:
                            pattern = re.compile(comparison_value)
                            if column_name == "__ALL__":
                                mask = df.astype(str).apply(lambda x: x.str.contains(pattern, na=False)).any(axis=1)
                                df = df[mask]
                            else:
                                mask = df[column_name].astype(str).str.contains(pattern, na=False)
                                df = df[mask]
                        except Exception as e:
                            self.report({"ERROR"}, f"Invalid regular expression pattern: {str(e)}")
                            continue
                    else:
                        if not column_name:
                            self.report({"WARNING"}, "Column must be specified for non-regex comparisons")
                            continue
                        col_match = next((col for col in df.columns if col.lower() == column_name.lower()), None)
                        if not col_match:
                            self.report({"WARNING"}, f"Column '{column_name}' not found in dataframe.")
                            continue
                        try:
                            column = df[col_match]
                            value = comparison_value
                            attr = next((a for a in props.csv_attributes if a.header == column_name), None)
                            data_type = getattr(attr, 'data_type', 'string') if attr else 'string'
                            def parse_imperial(val):
                                """
                                Parse an imperial measurement string and return meters.
                                Supported formats:
                                - 9' 2"
                                - 29' 2''
                                - 8' 10 3/16"
                                - 8.5 (decimal feet)
                                - 10 3/16" (inches only)
                                """
                                if val is None or (isinstance(val, str) and not val.strip()):
                                    return None

                                s = str(val).strip()

                                feet = 0.0
                                inches = 0.0

                                if re.fullmatch(r"\d+(\.\d+)?", s):
                                    feet = float(s)
                                else:
                                    feet_match = re.search(r"(\d+(?:\.\d+)?)\s*'(?!')", s)
                                    if feet_match:
                                        feet = float(feet_match.group(1))

                                    s_no_feet = re.sub(r"\d+(?:\.\d+)?\s*'(?!')", "", s)

                                    inch_match = re.search(
                                        r"(\d+)?\s*(\d+/\d+)?\s*(?:\"|''|$)",
                                        s_no_feet
                                    )

                                    if inch_match:
                                        whole = inch_match.group(1)
                                        frac = inch_match.group(2)

                                        if whole:
                                            inches += float(whole)
                                        if frac:
                                            inches += float(Fraction(frac))

                                total_inches = feet * 12.0 + inches
                                meters = total_inches * 0.0254
                                return meters
                            try:
                                if data_type == 'imperial_string':
                                    column_converted = column.apply(parse_imperial)
                                    val_m = parse_imperial(value)
                                    column = column_converted
                                    value = val_m
                                elif data_type == 'float':
                                    column = pd.to_numeric(column, errors='coerce')
                                    try:
                                        value = float(value)
                                    except Exception:
                                        pass
                                elif data_type == 'int':
                                    column = pd.to_numeric(column, errors='coerce').astype('Int64')
                                    try:
                                        value = int(value)
                                    except Exception:
                                        pass
                                elif data_type == 'bool':
                                    column = column.astype(bool)
                                    value = bool(value)
                            except (ValueError, TypeError) as e:
                                self.report({"WARNING"}, f"Could not interpret value '{value}' as {data_type}. Error: {str(e)}")
                            if comparison_operator == "=":
                                if data_type == "imperial_string":
                                    try:
                                        mask = column.notna() & pd.notna(value) & (abs(column - value) < 1e-3)
                                    except Exception:
                                        mask = column == value
                                elif data_type == "float":
                                    try:
                                        col_float = pd.to_numeric(column, errors='coerce')
                                        val_float = float(value)
                                        mask = col_float.notna() & (abs(col_float - val_float) < 1e-3)
                                    except Exception:
                                        mask = column == value
                                else:
                                    mask = column == value
                            elif comparison_operator == "!=":
                                mask = column != value
                            elif comparison_operator == ">":
                                mask = column > value
                            elif comparison_operator == ">=":
                                mask = column >= value
                            elif comparison_operator == "<":
                                mask = column < value
                            elif comparison_operator == "*=":
                                mask = column.astype(str).str.contains(str(value), na=False)
                            elif comparison_operator == "!*=":
                                mask = ~column.astype(str).str.contains(str(value), na=False)
                            else:
                                self.report({"WARNING"}, f"Unknown operator '{comparison_operator}'.")
                                continue
                            filtered_rows = df[mask]
                            df = filtered_rows
                        except Exception as e:
                            self.report({"ERROR"}, f"Comparison filter error: {str(e)}")
                group_results.append(df)

            if group_results:
                return pd.concat(group_results).drop_duplicates().reset_index(drop=True)
            else:
                return combined_df
    
    def format_and_write_output(self, final_df, props):
        def value_to_imperial_string(value, unit_name):
            if unit_name == 'METER':
                meters = float(value)
            elif unit_name == 'FOOT':
                meters = float(value) * 0.3048
            elif unit_name == 'INCH':
                meters = float(value) * 0.0254
            else:
                meters = float(value)
            if unit_name == 'METER':
                return f"{meters:.3f} m"
            elif unit_name == 'INCH':
                inches = meters / 0.0254
                return f"{inches:.2f} in"
            total_inches = meters / 0.0254
            feet = int(total_inches // 12)
            inches = int(total_inches % 12)
            frac = total_inches - (feet * 12 + inches)
            sixteenths = round(frac * 16)
            if sixteenths == 16:
                inches += 1
                sixteenths = 0
            if inches == 12:
                feet += 1
                inches = 0
            if sixteenths > 0:
                return f"{feet}' {inches} {sixteenths}/16\""
            else:
                return f"{feet}' {inches}\""

        scene = getattr(bpy.context, 'scene', None)
        unit_name = 'FOOT'
        if scene and hasattr(scene, 'BIMProperties'):
            unit_name = getattr(scene.BIMProperties, 'length_unit', 'FOOT').upper()

        for attr in props.csv_attributes:
            if getattr(attr, 'data_type', None) == 'imperial_string':
                col = attr.header
                if col in final_df.columns:
                    def _format_val(val):
                        try:
                            return value_to_imperial_string(val, unit_name)
                        except Exception:
                            return val
                    final_df[col] = final_df[col].apply(_format_val)

        if props.format == "web":
            if not tool.Web.get_web_props().is_connected:
                bpy.ops.bim.connect_websocket_server()
            tool.Web.send_webui_data(data=final_df.to_csv(index=False), data_key="csv_data", event="csv_data")
            self.report({"INFO"}, "Data is exported to WEB (web).")
        else:
            if props.format == "csv":
                final_df.to_csv(self.filepath, index=False)
            elif props.format == "ods":
                final_df.to_excel(self.filepath, engine="odf", index=False)
            elif props.format == "xlsx":
                final_df.to_excel(self.filepath, engine="openpyxl", index=False)
            self.report({"INFO"}, f"Combined data exported to {self.filepath}.")
        return {"FINISHED"}


class ImportIfcCsv(bpy.types.Operator, tool.Ifc.Operator, ImportHelper):
    bl_idname = "bim.import_ifccsv"
    bl_label = "Import to IFC"
    bl_description = "Import IFC data from a spreadsheet."
    bl_options = {"REGISTER", "UNDO"}
    filter_glob: bpy.props.StringProperty(default="*.csv;*.ods;*.xlsx", options={"HIDDEN"})

    @classmethod
    def poll(cls, context):
        props = tool.Blender.get_csv_props()
        propsIfc = tool.Blender.get_ifc_props()
        something_selected = any(node.is_selected for node in propsIfc.ifc_files)
        if not props.should_load_from_memory and not something_selected:
            cls.poll_message_set("Select an IFC file or use 'load from memory' if it's loaded in Bonsai.")
            return False
        return True

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".csv")
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        csv_props = tool.Blender.get_csv_props()
        if csv_props:
            csv_props.progress = 0.01
            csv_props.import_phase = "Starting import..."
        self._import_generator = None
        self._import_file_generator = None
        self._timer_interval = 0.05
        self._timer = context.window_manager.event_timer_add(self._timer_interval, window=context.window)
        context.window_manager.modal_handler_add(self)
        self._step = 0
        self._row_index = 0
        self._df = None
        self._import_rows = None
        self._import_total = 0
        self._import_mode = None
        self._import_file_groups = None
        self._import_file_group_index = 0
        self._import_file_group_row = 0
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        if event.type == 'ESC':
            csv_props = tool.Blender.get_csv_props()
            if csv_props:
                csv_props.progress = 0.0
            if getattr(self, '_import_mode', None) == 'file':
                current_filename = None
                header_to_name = {a.header: a.name for a in csv_props.csv_attributes}
                if self._df is not None:
                    import_headers = [col for col in self._df.columns if col not in ["FileName", "GlobalId"] and col in header_to_name]
                    import_names = [header_to_name[col] for col in import_headers]
                else:
                    import_headers = []
                    import_names = []
                if self._import_mode == 'memory':
                    if not hasattr(self, '_import_generator') or self._import_generator is None:
                        group_df = self._import_rows
                        ifc_file = tool.Ifc.get()
                        ifc_csv = ifccsv.IfcCsv()
                        self._import_generator = ifc_csv.Import(
                            ifc_file,
                            group_df,
                            attributes=import_names,
                            delimiter=sep,
                            null=csv_props.null_value,
                            empty=csv_props.empty_value,
                            bool_true=csv_props.true_value,
                            bool_false=csv_props.false_value,
                            concat=csv_props.concat_value,
                        )
                        self._row_index = 0
                last_file = None
                last_row = None
                if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups):
                    last_file, _ = self._import_file_groups[self._import_file_group_index]
                    last_row = self._import_file_group_row
                msg = f"Import cancelled. Last processed file: {last_file}, row: {last_row}"
                self.report({'INFO'}, msg)
            wm = getattr(context, 'window_manager', None)
            if wm:
                wm.event_timer_remove(self._timer)
            return {'CANCELLED'}
        if event.type != 'TIMER':
            return {'PASS_THROUGH'}
        wm = getattr(context, 'window_manager', None)
        if wm:
            for window in wm.windows:
                for area in window.screen.areas:
                    if area.type == 'PROPERTIES':
                        area.tag_redraw()
        csv_props = tool.Blender.get_csv_props()
        if csv_props is None:
            self.report({'ERROR'}, 'CSV Properties not registered on scene.')
            wm = getattr(context, 'window_manager', None)
            if wm:
                wm.event_timer_remove(self._timer)
            return {'CANCELLED'}
        sep = csv_props.csv_custom_delimiter if csv_props.csv_delimiter == "CUSTOM" else csv_props.csv_delimiter

        if self._step == 0:
            self._step += 1
            csv_props.import_phase = "Loading File..."
            csv_props.progress = 0.02
            return {'PASS_THROUGH'}

        if self._step == 1:
            self._step += 1
            if self.filepath.endswith(".csv"):
                self._df = pd.read_csv(self.filepath, delimiter=sep)
            elif self.filepath.endswith(".xlsx"):
                self._df = pd.read_excel(self.filepath)
            elif self.filepath.endswith(".ods"):
                self._df = pd.read_excel(self.filepath, engine="odf")
            else:
                self.report({'ERROR'}, f"Unsupported file format: {self.filepath}")
                csv_props.progress = 0.0
                wm = getattr(context, 'window_manager', None)
                if wm:
                    wm.event_timer_remove(self._timer)
                return {'CANCELLED'}
            
            if self._df is not None:
                missing_columns = []
                if "FileName" not in self._df.columns:
                    missing_columns.append("FileName")
                if "GlobalId" not in self._df.columns:
                    missing_columns.append("GlobalId")
                
                if missing_columns:
                    self.report({'ERROR'}, f"Missing required columns: {', '.join(missing_columns)}. Import file must have FileName and GlobalId as the first two columns.")
                    csv_props.progress = 0.0
                    csv_props.import_phase = ""
                    wm = getattr(context, 'window_manager', None)
                    if wm:
                        wm.event_timer_remove(self._timer)
                    return {'CANCELLED'}
            
            header_to_name = {a.header: a.name for a in csv_props.csv_attributes}
            if self._df is not None:
                import_headers = [col for col in self._df.columns if col not in ["FileName", "GlobalId"] and col in header_to_name]
                import_names = [header_to_name[col] for col in import_headers]
            else:
                import_headers = []
                import_names = []
            self._import_mode = 'memory' if csv_props.should_load_from_memory else 'file'
            if self._import_mode == 'memory':
                scene = getattr(bpy.context, 'scene', None)
                current_ifc_path = getattr(getattr(scene, 'BIMProperties', None), 'ifc_file', None)
                current_ifc_basename = os.path.basename(current_ifc_path) if current_ifc_path else None
                group_df = self._df[self._df["FileName"] == current_ifc_basename] if self._df is not None and current_ifc_basename else None
                self._import_rows = group_df
                self._import_total = len(group_df) if group_df is not None else 0
                ifc_file = tool.Ifc.get()
                ifc_csv = ifccsv.IfcCsv()
                self._import_generator = ifc_csv.Import(
                    ifc_file,
                    group_df,
                    attributes=import_names,
                    delimiter=sep,
                    null=csv_props.null_value,
                    empty=csv_props.empty_value,
                    bool_true=csv_props.true_value,
                    bool_false=csv_props.false_value,
                    concat=csv_props.concat_value,
                )
                self._row_index = 0
            else:
                self._import_file_groups = list(self._df.groupby("FileName")) if self._df is not None else []
                self._import_file_group_index = 0
                self._import_file_group_row = 0
                self._import_total = len(self._df) if self._df is not None else 0
                if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups):
                    file_name, group_df = self._import_file_groups[self._import_file_group_index]
                    file_path = None
                    ifc_props = tool.Blender.get_ifc_props()
                    if ifc_props and hasattr(ifc_props, 'ifc_files'):
                        for node in ifc_props.ifc_files:
                            if os.path.basename(node.file_path) == file_name:
                                file_path = tool.Ifc.resolve_uri(node.file_path)
                                break
                    if file_path:
                        try:
                            ifc_file = ifcopenshell.open(file_path)
                            ifc_file.path = file_path
                        except Exception as e:
                            self.report({"ERROR"}, f"Failed to open IFC file '{file_name}': {e}")
                            file_path = None
                        if file_path:
                            header_to_name = {a.header: a.name for a in csv_props.csv_attributes}
                            import_headers = [col for col in group_df.columns if col not in ["FileName", "GlobalId"] and col in header_to_name]
                            import_names = [header_to_name[col] for col in import_headers]
                            ifc_csv = ifccsv.IfcCsv()
                            self._import_file_generator = ifc_csv.Import(
                                ifc_file,
                                group_df,
                                attributes=import_names,
                                delimiter=sep,
                                null=csv_props.null_value,
                                empty=csv_props.empty_value,
                                bool_true=csv_props.true_value,
                                bool_false=csv_props.false_value,
                                concat=csv_props.concat_value,
                            )
                            self._import_file_group_row = 0
                            self._current_ifc_file = ifc_file
                            self._current_file_path = file_path
            self._step = 2
            return {'PASS_THROUGH'}

        if self._step == 2:
            if self._import_mode == 'memory':
                start_time = time.perf_counter()
                while True:
                    try:
                        result = next(self._import_generator)
                        self._row_index += 1
                    except StopIteration:
                        self._step = 3
                        self._import_generator = None
                        break
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        break
                percent = int(100 * self._row_index / self._import_total) if self._import_total else 0
                csv_props.progress = self._row_index / self._import_total if self._import_total else 0.0
                csv_props.import_phase = f"Processing rows... {self._row_index}/{self._import_total} ({percent}%)"
                return {'PASS_THROUGH'}
            else:
                start_time = time.perf_counter()
                while True:
                    try:
                        result = next(self._import_file_generator)
                        self._import_file_group_row += 1
                    except StopIteration:
                        if not csv_props.should_load_from_memory and self._import_file_groups:
                            if hasattr(self, '_current_ifc_file') and hasattr(self, '_current_file_path'):
                                try:
                                    self._current_ifc_file.write(self._current_file_path)
                                except Exception as e:
                                    pass
                        self._import_file_group_index += 1
                        self._import_file_group_row = 0
                        self._import_file_generator = None
                        self._current_ifc_file = None
                        self._current_file_path = None
                        if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups):
                            file_name, group_df = self._import_file_groups[self._import_file_group_index]
                            file_path = None
                            ifc_props = tool.Blender.get_ifc_props()
                            if ifc_props and hasattr(ifc_props, 'ifc_files'):
                                for node in ifc_props.ifc_files:
                                    if os.path.basename(node.file_path) == file_name:
                                        file_path = tool.Ifc.resolve_uri(node.file_path)
                                        break
                            if file_path:
                                try:
                                    ifc_file = ifcopenshell.open(file_path)
                                    ifc_file.path = file_path
                                except Exception as e:
                                    self.report({"ERROR"}, f"Failed to open IFC file '{file_name}': {e}")
                                    file_path = None
                            if file_path:
                                header_to_name = {a.header: a.name for a in csv_props.csv_attributes}
                                import_headers = [col for col in group_df.columns if col not in ["FileName", "GlobalId"] and col in header_to_name]
                                import_names = [header_to_name[col] for col in import_headers]
                                ifc_csv = ifccsv.IfcCsv()
                                self._import_file_generator = ifc_csv.Import(
                                    ifc_file,
                                    group_df,
                                    attributes=import_names,
                                    delimiter=sep,
                                    null=csv_props.null_value,
                                    empty=csv_props.empty_value,
                                    bool_true=csv_props.true_value,
                                    bool_false=csv_props.false_value,
                                    concat=csv_props.concat_value,
                                )
                                self._import_file_group_row = 0
                                self._current_ifc_file = ifc_file
                                self._current_file_path = file_path
                        break
                    if (time.perf_counter() - start_time) >= getattr(self, '_timer_interval', 0.05):
                        break
                completed = self._import_file_group_row + sum(len(g[1]) for g in self._import_file_groups[:self._import_file_group_index]) if self._import_file_groups else 0
                percent = int(100 * completed / self._import_total) if self._import_total else 0
                csv_props.progress = completed / self._import_total if self._import_total else 0.0
                current_group_len = len(self._import_file_groups[self._import_file_group_index][1]) if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups) else 0
                current_filename = None
                if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups):
                    current_filename = self._import_file_groups[self._import_file_group_index][0]
                if current_filename:
                    csv_props.import_phase = f"Processing ({current_filename}) {self._import_file_group_row}/{current_group_len} ({percent}%)"
                else:
                    csv_props.import_phase = f"Processing rows... {self._import_file_group_row}/{current_group_len} ({percent}%)"
                if self._import_file_groups and self._import_file_group_index < len(self._import_file_groups):
                    return {'PASS_THROUGH'}
                elif self._step != 3:
                    self._step = 3
                    return {'PASS_THROUGH'}

        if self._step == 3:
            csv_props.import_phase = "Finishing..."
            csv_props.progress = 1.0
            wm = getattr(context, 'window_manager', None)
            if wm:
                wm.event_timer_remove(self._timer)
            refresh_ui_data()
            self.report({'INFO'}, 'Data is imported to IFC files.')
            return {'FINISHED'}
        return {'PASS_THROUGH'}



class SelectCsvIfcFile(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.select_csv_ifc_file"
    bl_label = "Select CSV IFC File"
    bl_description = "Select IFC file for spreadsheet import/export."
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".ifc"
    filter_glob: bpy.props.StringProperty(default="*.ifc;*.ifczip;*.ifcxml", options={"HIDDEN"})

    def execute(self, context):
        props = tool.Blender.get_csv_props()
        props.csv_ifc_file = self.filepath
        return {"FINISHED"}


class AddIfcFiles(bpy.types.Operator, ImportHelper):
    bl_idname = "bim.add_ifc_files"
    bl_label = "Add IFC Files"
    bl_description = "Select IFC files to add to the list"
    bl_options = {"REGISTER", "UNDO"}

    files: bpy.props.CollectionProperty(name="Files", type=bpy.types.OperatorFileListElement)
    directory: bpy.props.StringProperty(subtype="DIR_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    use_relative_path: bpy.props.BoolProperty(
        name="Use Relative Path",
        description="Whether to store linked model path relative to the currently opened IFC file.",
        default=True,
    )
    use_cache: bpy.props.BoolProperty(name="Use Cache", default=False)

    def execute(self, context):
        propsIfc = tool.Blender.get_ifc_props()

        for file in self.files:
            new_file = propsIfc.ifc_files.add()
            new_file.file_path = tool.Ifc.get_uri(
                os.path.join(self.directory, file.name), use_relative_path=self.use_relative_path
            )
            new_file.is_selected = True

        return {"FINISHED"}


class RemoveIfcFile(bpy.types.Operator):
    bl_idname = "bim.remove_ifc_file"
    bl_label = "Remove IFC File"

    index: bpy.props.IntProperty()

    def execute(self, context):
        props = tool.Blender.get_ifc_props()
        props.ifc_files.remove(self.index)
        return {"FINISHED"}


class AddlinkedFiles(bpy.types.Operator):
    bl_idname = "bim.add_linked_files"
    bl_label = "Add Linked Files"
    bl_description = "Add linked files from the project to the IFC file list"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        propsIfc = tool.Blender.get_ifc_props()
        project_props = tool.Project.get_project_props()

        for link in project_props.links:
            linked_file_path = link.name

            if not any(node.file_path == linked_file_path for node in propsIfc.ifc_files):
                new_file = propsIfc.ifc_files.add()
                new_file.file_path = linked_file_path
                new_file.is_selected = True

        self.report({"INFO"}, "Linked files added to the IFC file list.")
        return {"FINISHED"}


class OpenIfcFile(bpy.types.Operator):
    bl_idname = "bim.open_ifc_file"
    bl_label = "Open IFC File"
    bl_description = "Open the selected IFC file in a new Blender instance and load the project"
    bl_options = {"REGISTER", "UNDO"}

    file_path: bpy.props.StringProperty(name="File Path")

    def execute(self, context):
        try:
            subprocess.Popen(
                [
                    "blender",
                    "--python-expr",
                    f"import bpy; bpy.ops.bim.load_project(filepath='{tool.Ifc.resolve_uri(self.file_path)}', should_start_fresh_session=True)",
                ]
            )
            self.report({"INFO"}, f"Opening file: {tool.Ifc.resolve_uri(self.file_path)} in a new Blender instance.")
        except Exception as e:
            self.report({"ERROR"}, f"Failed to open file: {e}")
        return {"FINISHED"}
