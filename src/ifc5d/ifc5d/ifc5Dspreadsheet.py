# Ifc5D - Extract Cost Data from IFC to spreadsheets
# Copyright (C) 2019, 2020, 2021 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of Ifc5D.
#
# Ifc5D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc5D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc5D.  If not, see <http://www.gnu.org/licenses/>.


import os
import time
import argparse
import datetime
import logging
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.cost
import ifcopenshell.util.date


class IfcDataGetter:
    @staticmethod
    def get_schedules(file):
        if not file:
            return None
        return file.by_type("IfcCostSchedule")

    @staticmethod
    def canonicalise_time(time):
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")

    @staticmethod
    def get_root_costs(cost_schedule):
        return [obj for rel in cost_schedule.Controls or [] for obj in rel.RelatedObjects or []]

    @staticmethod
    def get_cost_item_values(cost_item=None):
        if not cost_item:
            return None
        values = []
        for cost_value in cost_item.CostValues or []:
            name = cost_value.Name
            applied_value = ifcopenshell.util.cost.calculate_applied_value(cost_item, cost_value)
            unit = IfcDataGetter.get_cost_value_unit(cost_value)
            values.append(
                {
                    "id": cost_value.id(),
                    "name": name,
                    "applied_value": float(applied_value) if applied_value else 0.0,
                    "unit": unit if unit else "",
                    "category": cost_value.Category or "General",
                }
            )
        return values

    @staticmethod
    def process_categories(cost_item, categories):
        for cost_value in cost_item.CostValues or []:
            if cost_value.Category:
                categories.add("{}{}".format(cost_value.Category, " Cost"))
        return categories

    @staticmethod
    def process_cost_item_categories(cost_item, categories):
        IfcDataGetter.process_categories(cost_item, categories)
        for rel in cost_item.IsNestedBy or []:
            for child in rel.RelatedObjects or []:
                IfcDataGetter.process_cost_item_categories(child, categories)
        return categories

    @staticmethod
    def get_cost_rates_categories(schedule):
        categories = set()
        for cost_item in IfcDataGetter.get_root_costs(schedule):
            IfcDataGetter.process_cost_item_categories(cost_item, categories)
        return categories

    @staticmethod
    def process_cost_data(file, cost_item, cost_items_data, index, hierarchy="1"):
        def listToString(s):
            return ", ".join([str(i) for i in s])

        quantity_data = IfcDataGetter.get_cost_item_quantity(file, cost_item)
        cost_values_data = IfcDataGetter.get_cost_item_values(cost_item)

        data = {
            "Index": index,
            "Hierarchy": hierarchy,
            "Id": cost_item.id(),
            "Identification": cost_item.Identification,
            "Description": cost_item.Name,
            "Unit": cost_values_data[0]["unit"] if cost_values_data else "",
            "Quantity": quantity_data["quantity"]["total_quantity"],
            "ChildrenData": [],
        }
        for cost_value in cost_values_data or []:
            cost_category = "{}{}".format(cost_value["category"], " Cost")
            data[cost_category] = cost_value["applied_value"]
        if data.get("* Cost", None):
            data["Total Price"] = data["* Cost"]
            data["* Cost"] = ""
        rate_subtotal = 0
        for key, value in data.items():
            if "Cost" in key and not "*" in key:
                rate_subtotal += value

        data["Rate Subtotal"] = rate_subtotal

        cost_items_data.append(data)

        index += 1
        child_hierarchy = hierarchy + ".1"
        for nested_cost in [obj for rel in cost_item.IsNestedBy or [] for obj in rel.RelatedObjects or []]:
            IfcDataGetter.process_cost_data(file, nested_cost, cost_items_data, index, child_hierarchy)
            child_hierarchy = (
                ".".join(child_hierarchy.split(".")[:-1]) + "." + str(int(child_hierarchy.split(".")[-1]) + 1)
            )

    @staticmethod
    def get_cost_items_data(file, schedule):
        cost_items_data = []
        index = 0
        for cost_item in IfcDataGetter.get_root_costs(schedule):
            IfcDataGetter.process_cost_data(file, cost_item, cost_items_data, index)
        return cost_items_data

    @staticmethod
    def format_unit(unit):
        if unit.is_a("IfcContextDependentUnit"):
            return f"{unit.UnitType} / {unit.Name}"
        else:
            name = unit.Name
            if unit.get_info().get("Prefix", None):
                name = f"{unit.Prefix} {name}"
            return f"{unit.UnitType} / {name}"

    @staticmethod
    def get_cost_value_unit(cost_value=None):
        if not cost_value:
            return None
        unit = cost_value.UnitBasis
        if not unit:
            return None
        return IfcDataGetter.format_unit(unit.UnitComponent)

    @staticmethod
    def get_cost_item_quantity(file, cost_item=None):
        # TODO: handle multiple quantities, THOSE WHHICH ARE JUYST ASSIGNED TO THE COST ITEM DIRECTLY, NOT THROUGH OBJECTS.
        def add_quantity(quantity, take_off_name):
            accounted_for.append(quantity)
            if take_off_name == "":
                take_off_name = quantity[0]
                if quantity[0] != take_off_name:
                    take_off_name = "mixed-takeoff-quantities"
            return quantity[3]

        if not cost_item:
            return None
        take_off_name = ""
        has_changed_name = False
        total_cost_quantity = 0
        accounted_for = []
        for rel in cost_item.Controls or []:
            for related_object in rel.RelatedObjects:
                qtos = ifcopenshell.util.element.get_psets(related_object, qtos_only=True)
                for quantities in qtos.values() or []:
                    qto = file.by_id(quantities["id"])
                    for quantity in qto.Quantities:
                        if not quantity in cost_item.CostQuantities:
                            continue
                        total_cost_quantity += add_quantity(quantity, take_off_name)
                        accounted_for.append(quantity)

        for quantity in cost_item.CostQuantities or []:
            if not quantity in accounted_for:
                total_cost_quantity += add_quantity(quantity, take_off_name)

        return {
            "id": cost_item.id(),
            "name": cost_item.Name,
            "quantity": {"take_off_name": take_off_name, "total_quantity": total_cost_quantity},
        }


class Ifc5Dwriter:
    def __init__(self, file=None, output=None, cost_schedule=None):
        self.output = output
        if isinstance(file, str):
            self.file = ifcopenshell.open(file)
        else:
            self.file = file
        self.cost_schedule = cost_schedule
        self.cost_schedules = []
        self.sheet_data = {}
        self.column_indexes = []
        self.colours = {
            0: "0839C2",  # 1st Row - Dark Blue
            1: "266EF6",  # Internal reference
            2: "47C9FF",  # External reference
            3: "82E9FF",  # Optional
            4: "B8F2FF",  # Secondary information
            5: "DAECF5",  # Project specific
            6: "000000",  # Not used
            7: "fed8b1",  # 2nd Row - Light Orange
        }

    def parse(self):
        self.column_indexes = []
        self.used_names = []
        for i in range(26):
            self.column_indexes.append("ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i % 26])
        if self.cost_schedule:
            for cost_schedule in self.cost_schedules:
                if cost_schedule.id() != self.cost_schedule.id():
                    self.cost_schedules.remove(cost_schedule)
        for cost_schedule in self.cost_schedules:
            sheet_id = cost_schedule.id()
            self.sheet_data[sheet_id] = {}
            self.sheet_data[sheet_id]["headers"] = [
                "Id",
                "Hierarchy",
                "Index",
                "Identification",
                "Description",
                "Quantity",
                "Unit",
            ]
            cost_rate_categories = IfcDataGetter.get_cost_rates_categories(cost_schedule)
            self.sheet_data[sheet_id]["headers"].extend(list(cost_rate_categories))
            self.sheet_data[sheet_id]["headers"].extend(["Rate Subtotal", "Total Price", "Children"])
            self.sheet_data[sheet_id]["cost_items"] = IfcDataGetter.get_cost_items_data(self.file, cost_schedule)
            self.sheet_data[sheet_id]["UpdateDate"] = IfcDataGetter.canonicalise_time(
                ifcopenshell.util.date.ifc2datetime(cost_schedule.UpdateDate)
            )
            self.sheet_data[sheet_id]["PredefinedType"] = cost_schedule.PredefinedType
            schedule_name = cost_schedule.Name or "Unnamed"
            if schedule_name in self.used_names:
                schedule_name = "{}_{}".format(schedule_name, self.used_names.count(schedule_name))
            self.sheet_data[sheet_id]["Name"] = schedule_name
            self.used_names.append(schedule_name)

    def multiply_cells(self, cell1, cell2):
        return "={}*{}".format(cell1, cell2)

    def sum_cells(self, list_of_cells):
        return "=SUM({})".format(",".join(list_of_cells))

    def get_cell_position(self, schedule_id, attribute):
        def get_position_in_list(item, item_list):
            try:
                return item_list.index(item)
            except ValueError:
                return -1

        if self.sheet_data and self.sheet_data[schedule_id]:
            attribute = get_position_in_list(attribute, self.sheet_data[schedule_id]["headers"])
            return "{}{}".format(self.column_indexes[attribute], self.row_count)

    def write(self):
        self.cost_schedules = IfcDataGetter.get_schedules(self.file)
        self.sheet_data = {}
        self.parse()


class Ifc5DCsvWriter(Ifc5Dwriter):
    def write(self):
        import csv

        super().write()
        for sheet, data in self.sheet_data.items():
            with open(
                os.path.join(self.output, "{}.csv".format(data["Name"])), "w", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(data["headers"])
                row = []
                for cost_item_data in data["cost_items"]:
                    writer.writerow([cost_item_data.get(column, "") for column in data["headers"]])


class Ifc5DOdsWriter(Ifc5Dwriter):
    def write(self):
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.style import Style, TableCellProperties
        from odf.number import NumberStyle, CurrencyStyle, CurrencySymbol, Number, Text

        super().write()

        self.doc = OpenDocumentSpreadsheet()

        for value in self.colours.values():
            style = Style(name=value, family="table-cell")
            bg_color = TableCellProperties(backgroundcolor="#" + value)
            style.addElement(bg_color)
            self.doc.styles.addElement(style)

        ns1 = CurrencyStyle(name="positive-AUD", volatile="true")
        ns1.addElement(CurrencySymbol(language="en", country="AU", text="$"))
        ns1.addElement(Number(decimalplaces="2", minintegerdigits="1", grouping="true"))
        self.doc.styles.addElement(ns1)

        for cost_schedule in self.cost_schedules:
            self.write_table(cost_schedule)

        self.doc.save(self.output, True)

    def write_table(self, cost_schedule):
        from odf.table import Table, TableRow, TableCell
        from odf.text import P
        from odf.number import NumberStyle, CurrencyStyle, CurrencySymbol, Number, Text

        def row():
            return TableRow()

        def add_cell(type, value=None, row=None, style=None):
            if type == "currency":
                cell = TableCell(valuetype="currency", stylename=style)
                cell.addElement(Number(numberstyle="Currency", value=value))
                cell.addElement(CurrencySymbol(currency="USD"))
                cell.setAttribute("number:currency-style", "USD")
            elif type == "number":
                cell = TableCell(valuetype="float", stylename=style)
                cell.addElement(Number(numberstyle="Number", value=value))
            elif type == "text":
                cell = TableCell(valuetype="string", stylename=style)
                cell.addElement(P(text=value))
            elif type == "formula":
                cell = TableCell(formula=value, stylename=style)
            row.addElement(cell)

        def add_cost_item_rows(table, cost_data):
            row = TableRow()
            self.row_count += 1

            for i, column in enumerate(self.sheet_data[cost_schedule.id()]["headers"]):
                if column == "Total Price" and cost_data["Quantity"] != 0 and cost_data["Rate Subtotal"]:
                    cell_quantity = self.get_cell_position(cost_schedule.id(), "Quantity")
                    cell_subtotal_rate = self.get_cell_position(cost_schedule.id(), "Rate Subtotal")
                    value = self.multiply_cells(cell_quantity, cell_subtotal_rate)
                    cell = TableCell(formula=value, stylename=self.colours.get(cost_data["Index"]))
                else:
                    value = cost_data.get(column, "")
                    cell = TableCell(valuetype="string", stylename=self.colours.get(cost_data["Index"]))
                    cell.addElement(P(text=value))
                # TODO:FIX QUANTITY AND COST TO SHOW AS NUMBERS AND CURRENCIES
                # elif "Cost" in column or "Rate" in column:
                #     value = cost_data.get(column, "")
                #     cell = TableCell(valuetype="string", stylename=self.colours.get(cost_data["Index"]))
                #     cell.addElement(P(text=value))
                #     # cell.addElement(P(text=u"${}".format(value))) # The current displayed value
                #     print("Should add rate ", "${}".format(value))
                # elif "Quantity" in column:
                #     value = cost_data.get(column, "")
                #     cell = TableCell(valuetype="float", stylename=self.colours.get(cost_data["Index"]))
                #     print("Should add quantity",value)
                #     cell.addElement(P(text=value))
                row.addElement(cell)
            table.addElement(row)

        table = Table(name=self.sheet_data[cost_schedule.id()].get("Name", ""))

        new = row()
        add_cell(type="text", value="Predefined Type:", row=new, style="fed8b1")
        add_cell(
            type="text", value=self.sheet_data[cost_schedule.id()].get("PredefinedType", ""), row=new, style="fed8b1"
        )
        table.addElement(new)

        new = row()
        add_cell(type="text", value="Cost Schedule:", row=new, style="fed8b1")
        add_cell(type="text", value=self.sheet_data[cost_schedule.id()]["Name"], row=new, style="fed8b1")
        table.addElement(new)

        new = row()
        add_cell(type="text", value="Update Date:", row=new, style="fed8b1")
        add_cell(type="text", value=self.sheet_data[cost_schedule.id()].get("UpdateDate", ""), row=new, style="fed8b1")
        table.addElement(new)

        new = row()
        table.addElement(new)

        header_row = TableRow()
        for header in self.sheet_data[cost_schedule.id()]["headers"]:
            add_cell(type="text", value=header, row=header_row, style="fed8b1")
        table.addElement(header_row)

        self.row_count = 5
        for cost_item_data in self.sheet_data[cost_schedule.id()]["cost_items"]:
            add_cost_item_rows(table, cost_item_data)

        self.doc.spreadsheet.addElement(table)


class Ifc5DXlsxWriter(Ifc5Dwriter):
    def write(self):
        import xlsxwriter

        super().write()

        self.workbook = xlsxwriter.Workbook(self.output + ".xlsx")
        self.used_names = []
        for cost_schedule in self.cost_schedules:
            self.write_table(cost_schedule)
        self.workbook.close()

    def write_table(self, cost_schedule):
        worksheet = self.workbook.add_worksheet(self.sheet_data[cost_schedule.id()]["Name"])
        headers = self.sheet_data[cost_schedule.id()]["headers"]
        for i, header in enumerate(headers):
            worksheet.write(0, i, header)

        row = 1
        for cost_item_data in self.sheet_data[cost_schedule.id()]["cost_items"]:
            col = 0
            for header in headers:
                worksheet.write(row, col, cost_item_data.get(header, ""))
                col += 1
            row += 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Specify an IFC file to process")
    parser.add_argument("output", help="The output directory for CSV or filename for other formats")
    parser.add_argument("-l", "--log", type=str, help="Specify where errors should be logged", default="process.log")
    parser.add_argument(
        "-f", "--format", type=str, help="Choose which format to export in (CSV/ODS/XLSX)", default="CSV"
    )
    args = vars(parser.parse_args())

    print("Processing IFC file...")
    start = time.time()
    logging.basicConfig(filename=args["log"], filemode="a", level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Starting conversion and Generating report")
    if args["format"] == "CSV":
        writer = Ifc5DCsvWriter(args["input"], args["output"])
    elif args["format"] == "ODS":
        writer = Ifc5DOdsWriter(args["input"], args["output"])
    elif args["format"] == "XLSX":
        writer = Ifc5DXlsxWriter(args["input"], args["output"])
    writer.write()

    logger.info("Finished conversion in %ss", time.time() - start)
    logger.info("Conversion and report generation complete")
