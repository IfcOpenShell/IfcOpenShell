#!/usr/bin/env python3

# IfcCSV - A utility to interact with IFC data through CSV.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcCSV.
#
# IfcCSV is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcCSV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcCSV.  If not, see <http://www.gnu.org/licenses/>.

# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifccsv.py`

import os
import re
import csv
import argparse
import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.schema
from statistics import mean
from typing import Optional, Union, Literal, Iterable

try:
    from odf.namespaces import OFFICENS
    from odf.opendocument import OpenDocumentSpreadsheet, load
    from odf.style import Style, TableCellProperties
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
except:
    pass  # No ODF support


try:
    import openpyxl
except:
    pass  # No XLSX support


try:
    import pandas as pd
except:
    pass  # No Pandas support


__version__ = version = "0.0.0"


FILE_FORMAT = Literal[
    "csv",
    "ods",
    "xlsx",
    "pd",
]


class IfcCsv:
    attributes: list[str]
    headers: list[str]

    def __init__(self):
        self.headers = []
        self.results = []
        self.dataframe = None

    def export(
        self,
        ifc_file: ifcopenshell.file,
        elements: Iterable[ifcopenshell.entity_instance],
        attributes: Union[list[str], None],
        headers: Optional[list[str]] = None,
        output=None,
        format: FILE_FORMAT = None,
        should_preserve_existing: bool = False,
        include_global_id: bool = True,
        delimiter: str = ",",
        null: str = "-",
        empty: str = "",
        bool_true: str = "YES",
        bool_false: str = "NO",
        concat: str = ", ",
        sort=None,
        groups=None,
        summaries=None,
        formatting=None,
    ):
        self.ifc_file = ifc_file
        self.results = []
        self.headers = []
        attributes = attributes or []

        if not headers:
            headers = [None] * len(attributes)

        if include_global_id:
            attributes.insert(0, "GlobalId")
            headers.insert(0, "GlobalId")

        for element in elements:
            result = []

            for attribute in attributes:
                value = ifcopenshell.util.selector.get_element_value(element, attribute)
                if value is None:
                    value = null
                elif value == "":
                    value = empty
                elif value is True:
                    value = bool_true
                elif value is False:
                    value = bool_false
                elif isinstance(value, (list, tuple)) and concat is not None:
                    value = concat.join(map(str, value))
                result.append(value)
            self.results.append(result)

        self.headers = []
        for i, attribute in enumerate(attributes):
            if headers[i]:
                self.headers.append(headers[i])
            else:
                self.headers.append(attribute)

        self.group_results(groups, attributes)
        self.summarise_results(summaries, attributes)
        self.sort_results(sort, attributes, include_global_id)
        self.format_results(formatting, attributes, null)

        if format == "csv":
            self.export_csv(output, delimiter=delimiter)
        elif format == "ods":
            self.export_ods(output, should_preserve_existing=should_preserve_existing)
        elif format == "xlsx":
            self.export_xlsx(output, should_preserve_existing=should_preserve_existing)
        elif format == "pd":
            return self.export_pd()

    def group_results(self, groups, attributes):
        if not groups:
            return

        group_results = {}
        group_indices = {}
        group_values = {}
        group_varies_values = {}

        for group in groups:
            index = attributes.index(group["name"])
            group_indices.setdefault(group["type"], [])
            group_indices[group["type"]].append(index)
            if group["type"] == "VARIES":
                group_varies_values[index] = group["varies_value"]

        for row in self.results:
            key = "-".join([str(row[gi]) for gi in group_indices.get("GROUP", [])])
            for group_type, gis in group_indices.items():
                if group_type in ("CONCAT", "VARIES"):
                    for gi in gis:
                        group_values.setdefault(key, {}).setdefault(gi, set())
                        group_values[key][gi].add(str(row[gi]))
                elif group_type in ("SUM", "AVERAGE", "MIN", "MAX"):
                    for gi in gis:
                        group_values.setdefault(key, {}).setdefault(gi, [])
                        try:
                            value = float(row[gi])
                        except:
                            continue
                        group_values[key][gi].append(value)
            group_results[key] = row

        for group_type, gis in group_indices.items():
            if group_type == "CONCAT":
                for key, result in group_results.items():
                    for gi in gis:
                        result[gi] = ", ".join(group_values[key][gi])
            elif group_type == "VARIES":
                for key, result in group_results.items():
                    for gi in gis:
                        if len(group_values[key][gi]) > 1:
                            result[gi] = group_varies_values[gi]
            elif group_type == "SUM":
                for key, result in group_results.items():
                    for gi in gis:
                        result[gi] = sum(group_values[key][gi])
            elif group_type == "AVERAGE":
                for key, result in group_results.items():
                    for gi in gis:
                        result[gi] = mean(group_values[key][gi])
            elif group_type == "MIN":
                for key, result in group_results.items():
                    for gi in gis:
                        result[gi] = min(group_values[key][gi])
            elif group_type == "MAX":
                for key, result in group_results.items():
                    for gi in gis:
                        result[gi] = max(group_values[key][gi])

        self.results = group_results.values()

    def summarise_results(self, summaries, attributes):
        self.summaries = [None] * len(attributes)

        if not summaries:
            return

        summary_indices = {}
        summary_values = {}

        for summary in summaries:
            index = attributes.index(summary["name"])
            summary_indices.setdefault(summary["type"], [])
            summary_indices[summary["type"]].append(index)

        for row in self.results:
            for summary_type, sis in summary_indices.items():
                if summary_type in ("SUM", "AVERAGE", "MIN", "MAX"):
                    for si in sis:
                        summary_values.setdefault(si, [])
                        try:
                            value = float(row[si])
                        except:
                            continue
                        summary_values[si].append(value)

        for summary_type, sis in summary_indices.items():
            for si in sis:
                if summary_type == "SUM":
                    self.summaries[si] = sum(summary_values[si])
                elif summary_type == "AVERAGE":
                    self.summaries[si] = mean(summary_values[si])
                elif summary_type == "MIN":
                    self.summaries[si] = min(summary_values[si])
                elif summary_type == "MAX":
                    self.summaries[si] = max(summary_values[si])
                self.summaries[si] = summary_type.title() + ": " + str(self.summaries[si])

    def format_results(self, formatting, attributes, null):
        if not formatting:
            return

        formatting_indices = {}

        for data in formatting:
            index = attributes.index(data["name"])
            formatting_indices[index] = data["format"]

        for index, format_query in formatting_indices.items():
            for row in self.results:
                if row[index] == null:
                    continue
                row[index] = '"' + str(row[index]).replace('"', '\\"') + '"'
                row[index] = ifcopenshell.util.selector.format(format_query.replace("{{value}}", row[index]))

            if self.summaries[index] is not None:
                summary_label, summary_value = self.summaries[index].split(": ")
                summary_value = '"' + str(summary_value).replace('"', '\\"') + '"'
                summary_value = ifcopenshell.util.selector.format(format_query.replace("{{value}}", summary_value))
                self.summaries[index] = summary_label + ": " + str(summary_value)

    def sort_results(self, sort, attributes, include_global_id):
        if not self.results:
            return
        if sort:

            def natural_sort(value):
                if isinstance(value, str):
                    convert = lambda text: int(text) if text.isdigit() else text.lower()
                    return [convert(c) for c in re.split("([0-9]+)", value)]
                return value

            # Sort least important keys first, then more important keys.
            # https://stackoverflow.com/questions/11476371/sort-by-multiple-keys-using-different-orderings
            for sort_data in reversed(sort):
                i = attributes.index(sort_data["name"])
                reverse = sort_data["order"] == "DESC"
                self.results = sorted(self.results, key=lambda x: natural_sort(x[i]), reverse=reverse)
        else:
            if include_global_id and len(list(self.results)[0]) > 1:
                self.results = sorted(self.results, key=lambda x: x[1])
            elif not include_global_id:
                self.results = sorted(self.results, key=lambda x: x[0])

    def export_csv(self, output: str, delimiter: Optional[str] = None) -> None:
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.headers)
            for row in self.results:
                writer.writerow(row)
            if any([s for s in self.summaries if s is not None]):
                writer.writerow(self.summaries)

    def export_ods(self, output, should_preserve_existing=False):
        df = self.export_pd()
        if self.summaries:
            df.loc[df.shape[0]] = self.summaries

        if os.path.exists(output) and should_preserve_existing:
            ods_document = load(output)
            first_table = ods_document.spreadsheet.getElementsByType(Table)[0]

            for col_index, col in enumerate(df.columns):
                # Assuming the first row of the table contains headers
                header_cell = self.get_col(first_table.getElementsByType(TableRow)[0], col_index)
                self.set_cell_value(header_cell, col)

            # Replace existing table data with data from DataFrame
            for row_index, (_, row) in enumerate(df.iterrows()):
                table_row = self.get_row(first_table, row_index + 1)  # + 1 for header

                for col_index, value in enumerate(row):
                    cell = self.get_col(table_row, col_index)
                    self.set_cell_value(cell, value)

            # If the DataFrame has fewer rows than the table, blank out the extra rows
            num_rows_table = len(first_table.getElementsByType(TableRow)) - 1  # Exclude header row
            if len(df) < num_rows_table:
                for i in range(len(df) + 1, num_rows_table + 1):  # +1 to account for header
                    for cell in first_table.getElementsByType(TableRow)[i].getElementsByType(TableCell):
                        for item in cell.childNodes:
                            cell.removeChild(item)

            ods_document.save(output)
        else:
            df.to_excel(output, index=False, engine="odf")

    def set_cell_value(self, cell, value):
        for item in cell.childNodes:
            cell.removeChild(item)

        if isinstance(value, (int, float)):
            cell.setAttrNS(OFFICENS, "value-type", "float")
            cell.setAttrNS(OFFICENS, "value", value)
        else:
            cell.setAttrNS(OFFICENS, "value-type", "string")
            cell.setAttrNS(OFFICENS, "value", str(value))
        p_element = P(text=str(value))
        cell.addElement(p_element)

    def get_row(self, table, row_index):
        rows = table.getElementsByType(TableRow)
        if row_index < len(rows):
            return rows[row_index]
        new_row = TableRow()
        table.addElement(new_row)
        return new_row

    def get_col(self, row, col_index):
        cells = row.getElementsByType(TableCell)
        if col_index < len(cells):
            return cells[col_index]
        new_cell = TableCell()
        row.addElement(new_cell)
        return new_cell

    def export_xlsx(self, output, should_preserve_existing=False):
        df = self.export_pd()
        if self.summaries:
            df.loc[df.shape[0]] = self.summaries

        if os.path.exists(output):
            book = openpyxl.load_workbook(output)
            with pd.ExcelWriter(
                output,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="overlay" if should_preserve_existing else "replace",
            ) as writer:
                df.to_excel(writer, sheet_name=book.sheetnames[0], index=False)
        else:
            df.to_excel(output, index=False, engine="openpyxl")

    def export_pd(self):
        self.dataframe = pd.DataFrame(self.results, columns=self.headers)
        return self.dataframe

    def get_wildcard_attributes(self, attribute):
        results = set()
        pset_qto_name = attribute.split(".", 1)[0]
        for element in self.ifc_file.by_type("IfcPropertySet") + self.ifc_file.by_type("IfcElementQuantity"):
            if element.Name != pset_qto_name:
                continue
            if element.is_a("IfcPropertySet"):
                results.update([p.Name for p in element.HasProperties])
            else:
                results.update([p.Name for p in element.Quantities])
        return ["{}.{}".format(pset_qto_name, n) for n in results]

    def Import(
        self,
        ifc_file: ifcopenshell.file,
        table: str,
        attributes: Optional[list[Union[str, None]]] = None,
        delimiter: str = ",",
        null: str = "-",
        empty: str = "",
        bool_true: str = "YES",
        bool_false: str = "NO",
    ) -> None:
        """
        Args:
            table: filepath to the table.
        """
        ext: FILE_FORMAT = table.split(".")[-1].lower()

        if ext == "csv":
            self.import_csv(ifc_file, table, attributes, delimiter, null, empty, bool_true, bool_false)
        elif ext == "ods":
            self.import_ods(ifc_file, table, attributes, null, empty, bool_true, bool_false)
        elif ext == "xlsx":
            self.import_xlsx(ifc_file, table, attributes, null, empty, bool_true, bool_false)

    def import_csv(
        self,
        ifc_file: ifcopenshell.file,
        table: str,
        attributes: Optional[list[Union[str, None]]] = None,
        delimiter: str = ",",
        null: str = "-",
        empty: str = "",
        bool_true: str = "YES",
        bool_false: str = "NO",
    ) -> None:
        with open(table, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            headers = []
            for row in reader:
                if not headers:
                    headers = row
                    if not attributes:
                        attributes = [None] * len(headers)
                    elif len(attributes) == len(headers) - 1:
                        attributes.insert(0, "")  # The GlobalId column
                    continue
                self.process_row(ifc_file, row, headers, attributes, null, empty, bool_true, bool_false)

    def import_xlsx(self, ifc_file, table, attributes, null, empty, bool_true, bool_false):
        df = pd.read_excel(table)
        self.import_pd(ifc_file, df, attributes, null, empty, bool_true, bool_false)

    def import_ods(self, ifc_file, table, attributes, null, empty, bool_true, bool_false):
        df = pd.read_excel(table, engine="odf")
        self.import_pd(ifc_file, df, attributes, null, empty, bool_true, bool_false)

    def import_pd(self, ifc_file, df, attributes=None, null="-", empty="", bool_true="YES", bool_false="NO"):
        headers = df.columns.tolist()

        if not attributes:
            attributes = [None] * len(headers)
        elif len(attributes) == len(headers) - 1:
            attributes.insert(0, "")  # The GlobalId column

        for _, row in df.iterrows():
            self.process_row(ifc_file, row.tolist(), headers, attributes, null, empty, bool_true, bool_false)

    def process_row(
        self,
        ifc_file: ifcopenshell.file,
        row: list[str],
        headers: list[str],
        attributes: list[Union[str, None]],
        null: str,
        empty: str,
        bool_true: str,
        bool_false: str,
    ) -> None:
        try:
            element = ifc_file.by_guid(row[0])
        except:
            print("The element with GUID {} was not found".format(row[0]))
            return
        for i, value in enumerate(row):
            if i == 0:
                continue  # Skip GlobalId
            if value == null:
                value = None
            elif value == empty:
                value = ""
            elif value == bool_true:
                value = True
            elif value == bool_false:
                value = False
            key = attributes[i] or headers[i]
            ifcopenshell.util.selector.set_element_value(ifc_file, element, key, value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports IFC data to and from CSV")
    parser.add_argument("-i", "--ifc", type=str, required=True, help="The IFC file")
    parser.add_argument("-s", "--spreadsheet", type=str, default="data.csv", help="The spreadsheet file")
    parser.add_argument("-f", "--format", type=str, default="csv", help="The format, chosen from csv, ods, or xlsx")
    parser.add_argument("-d", "--delimiter", type=str, default=",", help="The delimiter in CSV. Defaults to a comma.")
    parser.add_argument("-n", "--null", type=str, default="N/A", help="How to represent null values. Defaults to N/A.")
    parser.add_argument(
        "-e", "--empty", type=str, default="-", help="How to represent empty strings. Defaults to a hyphen."
    )
    parser.add_argument("--bool_true", type=str, default="YES", help="How to represent true values. Defaults to YES.")
    parser.add_argument("--bool_false", type=str, default="NO", help="How to represent false values. Defaults to NO.")
    parser.add_argument("--concat", type=str, default=", ", help="How to concatenate lists. Defaults to ', '.")
    parser.add_argument("-q", "--query", type=str, default="", help='Specify a IFC query selector, such as "IfcWall"')
    parser.add_argument(
        "-a",
        "--attributes",
        nargs="+",
        help="Specify attributes that are part of the extract, using the IfcQuery syntax such as 'class', 'Name' or 'Pset_Foo.Bar'",
    )
    parser.add_argument("--headers", nargs="+", help="Specify human readable headers that correlate to each attribute.")
    parser.add_argument("--sort", nargs="+", help="Specify one or more attributes to sort by.")
    parser.add_argument("--order", nargs="+", help="Choose the sort order from ASC or DESC for each sorted attribute.")
    parser.add_argument("--export", action="store_true", help="Export from IFC to the desired format.")
    parser.add_argument("--import", action="store_true", help="Import from the autodetected format to IFC.")
    args = parser.parse_args()

    if args.export:
        ifc_file = ifcopenshell.open(args.ifc)
        results = ifcopenshell.util.selector.filter_elements(ifc_file, args.query)
        sort = None
        if args.sort and len(args.sort) == len(args.order):
            sort = [{"name": s, "order": args.order[i]} for i, s in enumerate(args.sort)]
        ifc_csv = IfcCsv()
        ifc_csv.export(
            ifc_file,
            results,
            args.attributes or [],
            headers=args.headers or [],
            output=args.spreadsheet,
            format=args.format,
            delimiter=args.delimiter,
            null=args.null,
            empty=args.empty,
            bool_true=args.bool_true,
            bool_false=args.bool_false,
            concat=args.concat,
            sort=sort,
        )
    elif getattr(args, "import"):
        ifc_csv = IfcCsv()
        ifc_file = ifcopenshell.open(args.ifc)
        ifc_csv.Import(
            ifc_file,
            args.spreadsheet,
            attributes=args.attributes or [],
            delimiter=args.delimiter,
            null=args.null,
            empty=args.empty,
        )
        ifc_file.write(args.ifc)
