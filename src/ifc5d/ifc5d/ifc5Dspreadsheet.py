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


from __future__ import annotations
import os
import time
import argparse
import datetime
import logging
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.cost
import ifcopenshell.util.date
from collections import Counter
from typing import Union, Optional, Any, TypedDict, NotRequired


class CostItem(TypedDict):
    # Exported columns.
    Index: int
    Hierarchy: str
    Id: int
    Identification: Union[str, None]
    Name: Union[str, None]
    Unit: str
    Quantity: Union[float, None]
    RateSubtotal: float
    TotalPrice: float

    # Internal.
    cost_categories: dict[str, float]


class CostItemQuantity(TypedDict):
    quantity: Union[float, None]


class CostValue(TypedDict):
    id: int
    """Cost Value id."""
    name: Union[str, None]
    applied_value: float
    unit: str
    category: str


class IfcDataGetter:
    @staticmethod
    def get_schedules(
        file: ifcopenshell.file, filter_by_schedule: Optional[ifcopenshell.entity_instance] = None
    ) -> list[ifcopenshell.entity_instance]:
        if filter_by_schedule:
            return [filter_by_schedule]
        return file.by_type("IfcCostSchedule")

    @staticmethod
    def canonicalise_time(time: Union[datetime.datetime, None]) -> str:
        if not time:
            return "-"
        return time.strftime("%d/%m/%y")

    @staticmethod
    def get_root_costs(cost_schedule: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.cost.get_root_cost_items(cost_schedule)

    @staticmethod
    def get_cost_item_values(cost_item: Union[ifcopenshell.entity_instance, None]) -> Union[list[CostValue], None]:
        if not cost_item:
            return None
        values: list[CostValue] = []
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
    def get_cost_items_data(
        file: ifcopenshell.file,
        cost_item: ifcopenshell.entity_instance,
        index: int = 1,
        hierarchy: str = "1",
    ) -> list[CostItem]:
        """
        :param cost_items_data: A list to fill with cost items.
        :param index: Current hierarchy depth.
        """
        cost_items_data: list[CostItem] = []

        quantity_data = IfcDataGetter.get_cost_item_quantity(file, cost_item)
        cost_values_data = IfcDataGetter.get_cost_item_values(cost_item)

        rate_subtotal = 0.0
        total_price = 0.0
        cost_categories: dict[str, float] = {}
        for cost_value in cost_values_data or []:
            category = cost_value["category"]
            if cost_value["category"] == "*":  # A sum.
                total_price = cost_value["applied_value"]
            else:
                cost_category = "{}{}".format(category, " Cost")
                cost_categories[cost_category] = cost_value["applied_value"]
                rate_subtotal += cost_value["applied_value"]

        data: CostItem = {
            "Index": index,
            "Hierarchy": hierarchy,
            "Id": cost_item.id(),
            "Identification": cost_item.Identification,
            "Name": cost_item.Name,
            "Unit": cost_values_data[0]["unit"] if cost_values_data else "",
            "Quantity": quantity_data["quantity"],
            "RateSubtotal": rate_subtotal,
            "TotalPrice": total_price,
            "cost_categories": cost_categories,
        }
        cost_items_data.append(data)

        index += 1
        child_hierarchy = hierarchy + ".1"
        for i, nested_cost in enumerate(ifcopenshell.util.cost.get_nested_cost_items(cost_item), 1):
            child_hierarchy = f"{hierarchy}.{i}"
            cost_items_data.extend(IfcDataGetter.get_cost_items_data(file, nested_cost, index, child_hierarchy))
        return cost_items_data

    @staticmethod
    def get_schedule_cost_items_data(file: ifcopenshell.file, schedule: ifcopenshell.entity_instance) -> list[CostItem]:
        cost_items_data: list[CostItem] = []
        for cost_item in IfcDataGetter.get_root_costs(schedule):
            cost_items_data.extend(IfcDataGetter.get_cost_items_data(file, cost_item))
        return cost_items_data

    @staticmethod
    def format_unit(unit: ifcopenshell.entity_instance) -> str:
        if unit.is_a("IfcContextDependentUnit"):
            return f"{unit.UnitType} / {unit.Name}"
        else:
            name = unit.Name
            if unit.get_info().get("Prefix", None):
                name = f"{unit.Prefix} {name}"
            return f"{unit.UnitType} / {name}"

    @staticmethod
    def get_cost_value_unit(cost_value: Optional[ifcopenshell.entity_instance] = None) -> Union[str, None]:
        if not cost_value:
            return None
        unit = cost_value.UnitBasis
        if not unit:
            return None
        return IfcDataGetter.format_unit(unit.UnitComponent)

    @staticmethod
    def get_cost_item_quantity(file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance) -> CostItemQuantity:
        accounted_for: set[ifcopenshell.entity_instance] = set()

        # NOTE: take_off_name is not used anywhere.
        take_off_name: str = ""

        # TODO: handle multiple quantities, THOSE WHHICH ARE JUYST ASSIGNED TO THE COST ITEM DIRECTLY, NOT THROUGH OBJECTS.
        def add_quantity(quantity: ifcopenshell.entity_instance, take_off_name: str) -> float:
            accounted_for.add(quantity)
            if take_off_name == "":
                # 0 IfcPhysicalSimpleQuantity.Name
                take_off_name = quantity[0]
            if quantity[0] != take_off_name:
                take_off_name = "mixed-takeoff-quantities"
            # 3 IfcPhysicalSimpleQuantity.Value
            return quantity[3]

        cost_item_quantities: list[ifcopenshell.entity_instance] = cost_item.CostQuantities
        if cost_item_quantities:
            total_cost_quantity = 0.0
            # Add quantities from cost assignments.
            for related_object in ifcopenshell.util.cost.get_cost_assignments_by_type(cost_item):
                qtos = ifcopenshell.util.element.get_psets(related_object, qtos_only=True)
                for quantities in qtos.values() or []:
                    qto = file.by_id(quantities["id"])
                    for quantity in qto.Quantities:
                        if quantity not in cost_item_quantities:
                            continue
                        total_cost_quantity += add_quantity(quantity, take_off_name)

            # Add cost item quantities assigned to the cost item directly.
            for quantity in cost_item_quantities:
                if quantity not in accounted_for:
                    total_cost_quantity += add_quantity(quantity, take_off_name)
        else:
            total_cost_quantity = None

        return {
            "quantity": total_cost_quantity,
        }


class SheetData(TypedDict):
    headers: list[str]
    cost_items: list[CostItem]
    # IFC attributes.
    UpdateDate: str
    PredefinedType: Union[str, None]
    Name: str
    """Name should be unique as it's going to be used as a filename"""


class Ifc5Dwriter:
    # Inputs.
    file: ifcopenshell.file
    output: str
    cost_schedule: Union[ifcopenshell.entity_instance, None]
    colors: dict[int, str]
    """Colors to use for hierarchy indices."""

    # Outputs.
    sheet_data: dict[int, SheetData]

    # Private.
    cost_schedules: list[ifcopenshell.entity_instance]
    """List of cost schedules to export."""
    column_indexes: list[str] = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    default_colors: dict[int, str] = {
        0: "0839C2",  # 1st Row - Dark Blue
        1: "266EF6",  # Internal reference
        2: "47C9FF",  # External reference
        3: "82E9FF",  # Optional
        4: "B8F2FF",  # Secondary information
        5: "DAECF5",  # Project specific
        6: "000000",  # Not used
        7: "fed8b1",  # 2nd Row - Light Orange
    }

    def __init__(
        self,
        file: Union[str, ifcopenshell.file],
        output: str,
        cost_schedule: Optional[ifcopenshell.entity_instance] = None,
    ):
        """
        :param file: IFC file to exprot cost schedules from.
        :param output: Output directory for csv files.
        :param cost_schedule: exported cost schedule. If not provided, will export all available schedules.
        """
        self.output = output
        if isinstance(file, str):
            self.file = ifcopenshell.open(file)
        else:
            self.file = file
        self.cost_schedule = cost_schedule
        self.colours = self.default_colors.copy()

    def parse(self) -> None:
        """Fill ``sheet_data`` from ``cost_schedules``."""
        self.sheet_data = {}
        counter: Counter[str] = Counter()
        for cost_schedule in self.cost_schedules:
            sheet_id = cost_schedule.id()
            cost_items = IfcDataGetter.get_schedule_cost_items_data(self.file, cost_schedule)
            headers: list[str] = [
                "Id",
                "Hierarchy",
                "Index",
                "Identification",
                "Name",
                "Unit",
            ]
            if cost_schedule.PredefinedType != "SCHEDULEOFRATES":
                headers.insert(-1, "Quantity")
            headers.extend(["RateSubtotal", "TotalPrice"])

            # Handle cost categories.
            categories: set[str] = set()
            for cost_item in cost_items:
                for category, value in cost_item["cost_categories"].items():
                    categories.add(category)
                    cost_item[category] = value
            assert not (intersection := categories.intersection(headers)), intersection
            headers.extend(categories)

            schedule_name = cost_schedule.Name or "Unnamed"
            counter[schedule_name] += 1
            if (count := counter[schedule_name]) > 1:
                schedule_name = f"{schedule_name}_{count - 1}"

            self.sheet_data[sheet_id] = {
                "Name": schedule_name,
                "headers": headers,
                "cost_items": cost_items,
                "UpdateDate": IfcDataGetter.canonicalise_time(
                    ifcopenshell.util.date.ifc2datetime(cost_schedule.UpdateDate)
                ),
                "PredefinedType": cost_schedule.PredefinedType,
            }

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

    def write(self) -> None:
        self.cost_schedules = IfcDataGetter.get_schedules(self.file, self.cost_schedule)
        self.parse()


class Ifc5DCsvWriter(Ifc5Dwriter):
    def write(self) -> None:
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
    def write(self) -> None:
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

        file_name = ""
        for cost_schedule in self.cost_schedules:
            if file_name:
                file_name += "_" + cost_schedule.Name or ""
            else:
                file_name += cost_schedule.Name or ""
            self.write_table(cost_schedule)
        self.doc.save(os.path.join(self.output, file_name), True)

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
    def write(self) -> None:
        import xlsxwriter

        super().write()
        file_name = ""
        for cost_schedule in self.cost_schedules:
            if file_name:
                file_name += "_" + cost_schedule.Name or ""
            else:
                file_name += cost_schedule.Name or ""
        self.file_path = os.path.join(self.output, "{}.xlsx".format(file_name))
        self.workbook = xlsxwriter.Workbook(self.file_path)
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
