# IfcFM - IFC for facility management
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcFM.
#
# IfcFM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcFM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcFM.  If not, see <http://www.gnu.org/licenses/>.

import csv

try:
    from xlsxwriter import Workbook
except:
    pass  # No XLSX support

try:
    from odf.opendocument import OpenDocumentSpreadsheet
    from odf.style import Style, TableCellProperties
    from odf.table import Table, TableRow, TableCell
    from odf.text import P
except:
    pass  # No ODF support


# https://stackoverflow.com/questions/1143671/how-to-sort-objects-by-multiple-keys-in-python

from operator import itemgetter as i
from functools import cmp_to_key


def cmp(x, y):
    """
    Replacement for built-in function cmp that was removed in Python 3

    Compare the two objects x and y and return an integer according to
    the outcome. The return value is negative if x < y, zero if x == y
    and strictly positive if x > y.

    https://portingguide.readthedocs.io/en/latest/comparisons.html#the-cmp-function
    """

    try:
        return (x > y) - (x < y)
    except:
        return 0


def multikeysort(items, columns):
    comparers = [((i(col[1:].strip()), -1) if col.startswith("-") else (i(col.strip()), 1)) for col in columns]

    def comparer(left, right):
        comparer_iter = (cmp(fn(left), fn(right)) * mult for fn, mult in comparers)
        return next((result for result in comparer_iter if result), 0)

    return sorted(items, key=cmp_to_key(comparer))


class Writer:
    def __init__(self, parser, filename=None):
        self.filename = filename
        self.parser = parser
        self.sheet_data = {}
        self.colours = {
            "r": "fdff8e",  # Required
            "i": "fdcd94",  # Internal reference
            "e": "cd95ff",  # External reference
            "o": "cdffc8",  # Optional
            "s": "c0c0c0",  # Secondary information
            "p": "9ccaff",  # Project specific
            "n": "000000",  # Not used
        }
        self.colours = {
            "r": "dc8774",  # Required
            "i": "eda786",  # Internal reference
            "e": "96c7d0",  # External reference
            "o": "ddb873",  # Optional or edd889
            "s": "dddddd",  # Secondary information
            "p": "b8dd73",  # Project specific
            "n": "000000",  # Not used
        }
        self.sheets = {
            "Actor": {
                "data": self.parser.actors,
                "fields": [
                    "Name",
                    "Category",
                    "Email",
                    "Phone",
                    "CompanyURL",
                    "Department",
                    "Address1",
                    "Address2",
                    "StateRegion",
                    "PostalCode",
                    "Country",
                ],
                "colours": "rirrrrrrrrr",
                "order": ["Name"],
            },
            "Facility": {
                "data": self.parser.facilities,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "ProjectName",
                    "SiteName",
                    "LinearUnits",
                    "AreaUnits",
                    "AreaMeasurement",
                    "Phase",
                    "ModelSoftware",
                    "ModelProjectID",
                    "ModelSiteID",
                    "ModelBuildingID",
                ],
                "colours": "ririrrrrrreeee",
                "order": ["Name"],
            },
            "Floor": {
                "data": self.parser.floors,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "ModelSoftware",
                    "ModelObject",
                    "ModelID",
                    "Elevation",
                ],
                "colours": "ririeeer",
                "order": ["Elevation"],
            },
            "Space": {
                "data": self.parser.spaces,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "LevelName",
                    "Description",
                    "ModelSoftware",
                    "ModelID",
                    "BuildingRoomNumber",
                    "UsableHeight",
                    "AreaGross",
                    "AreaNet",
                ],
                "colours": "ririireerrrr",
                "order": ["LevelName", "Name"],
            },
            "Zone": {
                "data": self.parser.zones,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "SpaceName",
                    "ModelSoftware",
                    "ModelID",
                    "ParentZoneName",
                ],
                "colours": "ririieei",
                "order": ["Name", "SpaceName"],
            },
            "Type": {
                "data": self.parser.types,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "Description",
                    "ModelSoftware",
                    "ModelObject",
                    "ModelID",
                ],
                "colours": "ririreee",
                "order": ["ModelObject", "Name"],
            },
            "Component": {
                "data": self.parser.components,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "TypeName",
                    "SpaceName",
                    "SystemName",
                    "ModelSoftware",
                    "ModelObject",
                    "ModelID",
                ],
                "colours": "ririiieee",
                "order": ["ModelObject", "Name"],
            },
            "System": {
                "data": self.parser.systems,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "ModelSoftware",
                    "ModelID",
                    "ParentSystemName",
                ],
                "colours": "ririeei",
                "order": ["Name"],
            },
            "Document": {
                "data": self.parser.documents,
                "fields": [
                    "Name",
                    "AuthorOrganizationName",
                    "AuthorDate",
                    "Category",
                    "WorksheetName",
                    "WorksheetRow",
                    "Revision",
                    "Location",
                    "Description",
                    "SpecificationSection",
                    "SubmittalID",
                    "SourceURL",
                ],
                "colours": "ririiirrrrer",
                "order": ["Name"],
            },
        }

    def write(self):
        for category, spec in self.sheets.items():
            self.write_data(category, spec["data"], spec["fields"], spec["colours"], spec["order"])

    def write_data(self, sheet, data, fieldnames, colours, sort_fields):
        self.sheet_data[sheet] = {"headers": fieldnames, "colours": colours, "rows": []}
        for row in multikeysort(list(data.values()), sort_fields):
            values = []
            for fieldname in fieldnames:
                values.append(row[fieldname])
            self.sheet_data[sheet]["rows"].append(values)


class CsvWriter(Writer):
    def write(self):
        super().write()
        for sheet, data in self.sheet_data.items():
            with open(os.path.join(self.filename, "{}.csv".format(sheet)), "w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(data["headers"])
                for row in data["rows"]:
                    writer.writerow(row)


class XlsWriter(Writer):
    def write(self):
        super().write()
        self.workbook = Workbook(self.filename + ".xlsx")

        self.cell_formats = {}
        for key, value in self.colours.items():
            self.cell_formats[key] = self.workbook.add_format()
            self.cell_formats[key].set_bg_color(value)

        for sheet in self.sheets.keys():
            self.write_worksheet(sheet)
        self.workbook.close()

    def write_worksheet(self, name):
        worksheet = self.workbook.add_worksheet(name)
        r = 0
        c = 0
        for header in self.sheet_data[name]["headers"]:
            cell = worksheet.write(r, c, header, self.cell_formats["s"])
            c += 1
        c = 0
        r += 1
        for row in self.sheet_data[name]["rows"]:
            c = 0
            for col in row:
                if c >= len(self.sheet_data[name]["colours"]):
                    cell_format = "p"
                else:
                    cell_format = self.sheet_data[name]["colours"][c]
                cell = worksheet.write(r, c, col, self.cell_formats[cell_format])
                c += 1
            r += 1


class OdsWriter(Writer):
    def write(self):
        super().write()
        self.doc = OpenDocumentSpreadsheet()

        self.cell_formats = {}
        for key, value in self.colours.items():
            style = Style(name=key, family="table-cell")
            style.addElement(TableCellProperties(backgroundcolor="#" + value))
            self.doc.automaticstyles.addElement(style)
            self.cell_formats[key] = style

        for sheet in self.sheets.keys():
            self.write_table(sheet)
        self.doc.save(self.filename, True)

    def write_table(self, name):
        table = Table(name=name)
        tr = TableRow()
        for header in self.sheet_data[name]["headers"]:
            tc = TableCell(valuetype="string", stylename="s")
            tc.addElement(P(text=header))
            tr.addElement(tc)
        table.addElement(tr)
        for row in self.sheet_data[name]["rows"]:
            tr = TableRow()
            c = 0
            for col in row:
                if c >= len(self.sheet_data[name]["colours"]):
                    cell_format = "p"
                else:
                    cell_format = self.sheet_data[name]["colours"][c]
                tc = TableCell(valuetype="string", stylename=cell_format)
                if col is None:
                    col = "NULL"
                tc.addElement(P(text=col))
                tr.addElement(tc)
                c += 1
            table.addElement(tr)
        self.doc.spreadsheet.addElement(table)
