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
import csv
import argparse
import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.schema

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


class IfcCsv:
    def __init__(self):
        self.headers = []
        self.results = []
        self.dataframe = None

    def export(
        self,
        ifc_file,
        elements,
        attributes,
        headers=None,
        output=None,
        format=None,
        should_preserve_existing=False,
        include_global_id=True,
        delimiter=",",
        null="-",
        bool_true="YES",
        bool_false="NO",
    ):
        self.ifc_file = ifc_file
        self.results = []
        if not headers:
            headers = [None] * len(attributes)
        for element in elements:
            result = []
            if include_global_id:
                if hasattr(element, "GlobalId"):
                    result.append(element.GlobalId)
                else:
                    result.append(None)

            for index, attribute in enumerate(attributes or []):
                if "*" in attribute:
                    attributes.extend(self.get_wildcard_attributes(attribute))
                    del attributes[index]

            for attribute in attributes:
                value = ifcopenshell.util.selector.get_element_value(element, attribute)
                if value is None:
                    value = null
                elif value is True:
                    value = bool_true
                elif value is False:
                    value = bool_false
                result.append(value)
            self.results.append(result)

        self.headers = ["GlobalId"] if include_global_id else []
        for i, attribute in enumerate(attributes or []):
            if headers[i]:
                self.headers.append(headers[i])
            else:
                self.headers.append(attribute)

        if format == "csv":
            self.export_csv(output, delimiter=delimiter)
        elif format == "ods":
            self.export_ods(output, should_preserve_existing=should_preserve_existing)
        elif format == "xlsx":
            self.export_xlsx(output, should_preserve_existing=should_preserve_existing)
        elif format == "pd":
            return self.export_pd()

    def export_csv(self, output, delimiter=None):
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.headers)
            for row in self.results:
                writer.writerow(row)

    def export_ods(self, output, should_preserve_existing=False):
        if os.path.exists(output) and should_preserve_existing:
            ods_document = load(output)
            first_table = ods_document.spreadsheet.getElementsByType(Table)[0]

            df = self.export_pd()
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
            df = self.export_pd()
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
        if os.path.exists(output):
            book = openpyxl.load_workbook(output)
            with pd.ExcelWriter(
                output,
                engine="openpyxl",
                mode="a",
                if_sheet_exists="overlay" if should_preserve_existing else "replace",
            ) as writer:
                df = self.export_pd()
                df.to_excel(writer, sheet_name=book.sheetnames[0], index=False)
        else:
            df = self.export_pd()
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

    def Import(self, ifc_file, table, attributes=None, delimiter=",", null="-", bool_true="YES", bool_false="NO"):
        ext = table.split(".")[-1].lower()

        if ext == "csv":
            self.import_csv(ifc_file, table, attributes, delimiter, null, bool_true, bool_false)
        elif ext == "ods":
            self.import_ods(ifc_file, table, attributes, null, bool_true, bool_false)
        elif ext == "xlsx":
            self.import_xlsx(ifc_file, table, attributes, null, bool_true, bool_false)

    def import_csv(self, ifc_file, table, attributes=None, delimiter=",", null="-", bool_true="YES", bool_false="NO"):
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
                self.process_row(ifc_file, row, headers, attributes, null, bool_true, bool_false)

    def import_xlsx(self, ifc_file, table, attributes, null, bool_true, bool_false):
        workbook = openpyxl.load_workbook(filename=table, read_only=True)
        worksheet = workbook.active  # Assuming data is on the first sheet
        headers = None

        for row in worksheet.iter_rows(values_only=True):
            if not headers:
                headers = list(row)
                if not attributes:
                    attributes = [None] * len(headers)
                elif len(attributes) == len(headers) - 1:
                    attributes.insert(0, "")  # The GlobalId column
                continue
            self.process_row(ifc_file, row, headers, attributes, null, bool_true, bool_false)

    def import_ods(self, ifc_file, table, attributes, null, bool_true, bool_false):
        doc = load(table)
        first_sheet = doc.spreadsheet.getElementsByType(Table)[0]
        rows = first_sheet.getElementsByType(TableRow)
        headers = None

        for row in rows:
            values = [cell.getElementsByType(P)[0].childNodes[0].data for cell in row.getElementsByType(TableCell)]
            if not headers:
                headers = values
                if not attributes:
                    attributes = [None] * len(headers)
                elif len(attributes) == len(headers) - 1:
                    attributes.insert(0, "")  # The GlobalId column
                continue
            self.process_row(ifc_file, values, headers, attributes, null, bool_true, bool_false)

    def import_pd(self, ifc_file, df, attributes=None, null="-", bool_true="YES", bool_false="NO"):
        headers = df.columns.tolist()

        if not attributes:
            attributes = [None] * len(headers)
        elif len(attributes) == len(headers) - 1:
            attributes.insert(0, "")  # The GlobalId column

        for _, row in df.iterrows():
            self.process_row(ifc_file, row.tolist(), headers, attributes, null, bool_true, bool_false)

    def process_row(self, ifc_file, row, headers, attributes, null, bool_true, bool_false):
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
    parser.add_argument(
        "-n", "--null", type=str, default="-", help="How to represent null values. Defaults to a hyphen."
    )
    parser.add_argument("--bool_true", type=str, default="YES", help="How to represent true values. Defaults to YES.")
    parser.add_argument("--bool_false", type=str, default="NO", help="How to represent false values. Defaults to NO.")
    parser.add_argument("-q", "--query", type=str, default="", help='Specify a IFC query selector, such as "IfcWall"')
    parser.add_argument(
        "-a",
        "--attributes",
        nargs="+",
        help="Specify attributes that are part of the extract, using the IfcQuery syntax such as 'class', 'Name' or 'Pset_Foo.Bar'",
    )
    parser.add_argument(
        "-h",
        "--headers",
        nargs="+",
        help="Specify human readable headers that correlate to each attribute.",
    )
    parser.add_argument("--export", action="store_true", help="Export from IFC to CSV")
    parser.add_argument("--import", action="store_true", help="Import from CSV to IFC")
    args = parser.parse_args()

    if args.export:
        ifc_file = ifcopenshell.open(args.ifc)
        results = ifcopenshell.util.selector.filter_elements(ifc_file, args.query)
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
            bool_true=args.bool_true,
            bool_false=args.bool_false,
        )
    elif getattr(args, "import"):
        ifc_csv = IfcCsv()
        ifc_file = ifcopenshell.open(args.ifc)
        ifc_csv.Import(
            ifc_file, args.spreadsheet, attributes=args.attributes or [], delimiter=args.delimiter, null=args.null
        )
        ifc_file.write(args.ifc)
