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

import csv
import argparse
import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.schema

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.style import Style, TableCellProperties
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
except:
    pass  # No ODF support


try:
    from xlsxwriter import Workbook
except:
    pass  # No XLSX support


try:
    import pandas as pd
except:
    pass  # No Pandas support


class IfcAttributeSetter:
    @staticmethod
    def set_element_key(ifc_file, element, key, value):
        if key == "class" and element.is_a() != value:
            return ifcopenshell.util.schema.reassign_class(ifc_file, element, value)
        if hasattr(element, key):
            setattr(element, key, value)
            return element
        if "." not in key:
            return element
        if key[0:3] == "Qto":
            qto_name, prop = key.split(".", 1)
            qto = IfcAttributeSetter.get_element_qto(element, qto_name)
            if qto:
                IfcAttributeSetter.set_qto_property(qto, prop, value)
                return element
        pset_name, prop = key.split(".", 1)
        pset = IfcAttributeSetter.get_element_pset(element, pset_name)
        if pset:
            IfcAttributeSetter.set_pset_property(ifc_file, pset, prop, value)
            return element
        return element

    @staticmethod
    def get_element_qto(element, name):
        for relationship in element.IsDefinedBy:
            if (
                relationship.is_a("IfcRelDefinesByProperties")
                and relationship.RelatingPropertyDefinition.is_a("IfcElementQuantity")
                and relationship.RelatingPropertyDefinition.Name == name
            ):
                return relationship.RelatingPropertyDefinition

    @staticmethod
    def set_qto_property(qto, name, value):
        for prop in qto.Quantities:
            if prop.Name != name:
                continue
            setattr(prop, prop.is_a()[len("IfcQuantity") :] + "Value", value)

    @staticmethod
    def get_element_pset(element, name):
        if element.is_a("IfcTypeObject"):
            if element.HasPropertySets:
                for pset in element.HasPropertySets:
                    if pset.is_a("IfcPropertySet") and pset.Name == name:
                        return pset
        else:
            for relationship in element.IsDefinedBy:
                if (
                    relationship.is_a("IfcRelDefinesByProperties")
                    and relationship.RelatingPropertyDefinition.is_a("IfcPropertySet")
                    and relationship.RelatingPropertyDefinition.Name == name
                ):
                    return relationship.RelatingPropertyDefinition

    @staticmethod
    def set_pset_property(ifc_file, pset, name, value):
        for property in pset.HasProperties:
            if property.Name != name:
                continue

            if value.lower() in ["null", "none"]:
                property.NominalValue = None
                continue

            # In lieu of loading a map for data casting, we only have four
            # options, which this ugly method will determine.
            if property.NominalValue is None:
                if value.isnumeric():
                    property.NominalValue = ifc_file.createIfcInteger(int(value))
                elif value.lower() in ["1", "true", "yes", "uh-huh"]:
                    property.NominalValue = ifc_file.createIfcBoolean(True)
                elif value.lower() in ["0", "false", "no", "nope"]:
                    property.NominalValue = ifc_file.createIfcBoolean(False)
                else:
                    try:
                        value = float(value)
                        property.NominalValue = ifc_file.createIfcReal(value)
                    except:
                        property.NominalValue = ifc_file.createIfcLabel(str(value))
            else:
                try:
                    property.NominalValue.wrappedValue = str(value)
                except:
                    try:
                        property.NominalValue.wrappedValue = float(value)
                    except:
                        try:
                            property.NominalValue.wrappedValue = int(value)
                        except:
                            property.NominalValue.wrappedValue = (
                                True if value.lower() in ["1", "true", "yes", "uh-huh"] else False
                            )


class IfcCsv:
    def __init__(self, output="", delimiter=","):
        self.headers = []
        self.results = []
        self.dataframe = None

    def export(self, ifc_file, elements, attributes, output=None, format=None, delimiter=","):
        self.ifc_file = ifc_file
        self.results = []
        for element in elements:
            result = []
            if hasattr(element, "GlobalId"):
                result.append(element.GlobalId)
            else:
                result.append(None)

            for index, attribute in enumerate(attributes or []):
                if "*" in attribute:
                    attributes.extend(self.get_wildcard_attributes(attribute))
                    del attributes[index]

            for attribute in attributes:
                result.append(ifcopenshell.util.selector.get_element_value(element, attribute))
            self.results.append(result)

        self.headers = ["GlobalId"]
        self.headers.extend(attributes or [])

        if format == "csv":
            self.export_csv(output, delimiter=delimiter)
        elif format == "ods":
            self.export_ods(output)
        elif format == "xlsx":
            self.export_xlsx(output)
        elif format == "pd":
            return self.export_pd()

    def export_csv(self, output, delimiter=None):
        with open(output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(self.headers)
            for row in self.results:
                writer.writerow(row)

    def export_ods(self, output):
        self.doc = OpenDocumentSpreadsheet()

        self.colours = {
            "h": "dc8774",  # Header
            "g": "eda786",  # GlobalId
            "a": "96c7d0",  # Other Attribute
        }

        self.cell_formats = {}
        for key, value in self.colours.items():
            style = Style(name=key, family="table-cell")
            style.addElement(TableCellProperties(backgroundcolor="#" + value))
            self.doc.automaticstyles.addElement(style)
            self.cell_formats[key] = style

        table = Table(name="IfcCSV")
        tr = TableRow()
        for header in self.headers:
            tc = TableCell(valuetype="string", stylename="h")
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)
        for row in self.results:
            tr = TableRow()
            c = 0
            for i, col in enumerate(row):
                cell_format = "g" if i == 0 else "a"
                tc = TableCell(valuetype="string", stylename=cell_format)
                if col is None:
                    col = "NULL"
                tc.addElement(P(text=col))
                tr.addElement(tc)
                c += 1
            table.addElement(tr)
        self.doc.spreadsheet.addElement(table)

        if output[-4:].lower() == ".ods":
           output = output[0:-4]
        self.doc.save(output, True)

    def export_xlsx(self, output):
        self.workbook = Workbook(output)

        self.colours = {
            "h": "dc8774",  # Header
            "g": "eda786",  # GlobalId
            "a": "96c7d0",  # Other Attribute
        }

        self.cell_formats = {}
        for key, value in self.colours.items():
            self.cell_formats[key] = self.workbook.add_format()
            self.cell_formats[key].set_bg_color(value)

        worksheet = self.workbook.add_worksheet("IfcCSV")
        r = 0
        c = 0
        for header in self.headers:
            cell = worksheet.write(r, c, header, self.cell_formats["h"])
            c += 1
        c = 0
        r += 1
        for row in self.results:
            c = 0
            for i, col in enumerate(row):
                cell_format = "g" if i == 0 else "a"
                cell = worksheet.write(r, c, col, self.cell_formats[cell_format])
                c += 1
            r += 1

        self.workbook.close()

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

    def Import(self, ifc_file, table, delimiter=","):
        # Currently only supports CSV.
        with open(table, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=delimiter)
            headers = []
            for row in reader:
                if not headers:
                    headers = row
                    continue
                try:
                    element = ifc_file.by_guid(row[0])
                except:
                    print("The element with GUID {} was not found".format(row[0]))
                    continue
                for i, value in enumerate(row):
                    if i == 0:
                        continue  # Skip GlobalId
                    element = IfcAttributeSetter.set_element_key(ifc_file, element, headers[i], value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports IFC data to and from CSV")
    parser.add_argument("-i", "--ifc", type=str, required=True, help="The IFC file")
    parser.add_argument("-s", "--spreadsheet", type=str, default="data.csv", help="The spreadsheet file")
    parser.add_argument("-f", "--format", type=str, default="csv", help="The format, chosen from csv, ods, or xlsx")
    parser.add_argument("-q", "--query", type=str, default="", help='Specify a IFC query selector, such as ".IfcWall"')
    parser.add_argument(
        "-a",
        "--arguments",
        nargs="+",
        help="Specify attributes that are part of the extract, using the IfcQuery syntax such as 'type', 'Name' or 'Pset_Foo.Bar'",
    )
    parser.add_argument("--export", action="store_true", help="Export from IFC to CSV")
    parser.add_argument("--import", action="store_true", help="Import from CSV to IFC")
    args = parser.parse_args()

    if args.export:
        ifc_file = ifcopenshell.open(args.ifc)
        results = ifcopenshell.util.selector.Selector.parse(ifc_file, args.query)
        ifc_csv = IfcCsv()
        ifc_csv.export(ifc_file, results, args.arguments or [], output=args.spreadsheet, format=args.format)
    elif getattr(args, "import"):
        ifc_csv = IfcCsv()
        ifc_file = ifcopenshell.open(args.ifc)
        ifc_csv.Import(ifc_file, args.spreadsheet)
        ifc_file.write(args.ifc)
