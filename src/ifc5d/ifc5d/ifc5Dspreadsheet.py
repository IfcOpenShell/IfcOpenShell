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

import argparse
import datetime
import json
import logging
import os
import time
from collections import Counter
from typing import Optional, Union

import ifcopenshell
import ifcopenshell.util.cost
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.unit
from typing_extensions import TypedDict


class CostItem(TypedDict, extra_items=float):
    # Exported columns.
    Index: int
    Hierarchy: str
    ItemIsASum: int
    Id: int
    Identification: Union[str, None]
    Name: Union[str, None]
    Description: Union[str, None]
    Unit: str
    Quantities: str
    Quantity: Union[float, None]
    RateSubtotal: float
    TotalPrice: float

    # Internal.
    cost_categories: dict[str, float]


class CostItemQuantity(TypedDict):
    quantity: Union[float, None]
    unit: str


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
    def cost_item_is_a_sum(cost_item: ifcopenshell.entity_instance) -> bool:
        for cost_value in cost_item.CostValues or []:
            if cost_value.Category == "*":
                return True
        return False

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

        # Guess IfcCostItem unit.
        unit = ""
        if cost_values_data:
            unit = cost_values_data[0]["unit"]
        if not unit:
            unit = quantity_data["unit"]

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
            "ItemIsASum": IfcDataGetter.cost_item_is_a_sum(cost_item),
            "Hierarchy": hierarchy,
            "Id": cost_item.id(),
            "Identification": cost_item.Identification,
            "Name": cost_item.Name,
            "Description": cost_item.Description,
            "Unit": unit,
            "Quantities": IfcDataGetter.serialise_cost_quantities(file, cost_item),
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
        index = 1
        for cost_item in IfcDataGetter.get_root_costs(schedule):
            cost_items_data.extend(
                IfcDataGetter.get_cost_items_data(file=file, cost_item=cost_item, hierarchy=str(index))
            )
            index += 1
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

        unit = ""
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

            ifc_unit = ifcopenshell.util.unit.get_property_unit(cost_item_quantities[0], file)
            if ifc_unit:
                unit = ifcopenshell.util.unit.get_unit_symbol(ifc_unit)
        else:
            total_cost_quantity = None

        return {
            "quantity": total_cost_quantity,
            "unit": unit,
        }

    @staticmethod
    def serialise_cost_quantities(file: ifcopenshell.file, cost_item: ifcopenshell.entity_instance) -> str:
        if not cost_item.is_a("IfcCostItem"):
            return ""
        if cost_item.CostQuantities is None:
            return ""
        result = []
        for quantity in cost_item.CostQuantities:
            prefix = ""
            for rel in file.get_inverse(quantity):
                if rel.is_a("IfcPropertySet") or rel.is_a("IfcElementQuantity"):
                    # Find elements that have this property set
                    for prop_rel in file.get_inverse(rel):
                        if prop_rel.is_a("IfcRelDefinesByProperties"):
                            for obj in prop_rel.RelatedObjects:
                                if obj.is_a("IfcElement"):
                                    prefix += (obj.Name or "") + " - "
            name = prefix + (quantity.Name or "")
            # Formula is an optional IfcLabel on IfcQuantity* in IFC4+; absent in
            # IFC2X3, hence the schema-safe getattr.
            formula = getattr(quantity, "Formula", None) or ""
            if quantity.is_a("IfcPhysicalSimpleQuantity"):
                value = quantity[3]
                try:
                    value = float(value) if value is not None else 0.0
                except (TypeError, ValueError):
                    value = 0.0
                result.append([name, value, formula])
            else:
                result.append([name + " ERROR: Only IfcPhysicalSimpleQuantity is supported", 0.0, formula])
        return json.dumps(result, ensure_ascii=False)


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
        :param file: IFC file to export cost schedules from.
        :param output: Output directory.
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
                "ItemIsASum",
                "Hierarchy",
                "Index",
                "Identification",
                "Name",
                "Description",
                "Unit",
            ]
            if cost_schedule.PredefinedType != "SCHEDULEOFRATES":
                headers.insert(-1, "Quantities")
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

    # Presentation formats (.ods / .xlsx) mirror exactly what the Bonsai cost
    # panel shows for a cost item: ID (Identification), Name, Quantity,
    # Value (RateSubtotal) and the calculated Total Cost. Everything else
    # (internal bookkeeping columns, Description, Unit, per-category cost
    # breakdowns) is bonsai/csv2ifc round-trip plumbing and stays out of the
    # presentation formats. The .csv format keeps the full column set since
    # csv2ifc reads those extra columns back in on import.
    PRESENTATION_COLUMNS = ("Identification", "Name", "Quantity", "RateSubtotal", "TotalPrice")

    # Header text as shown in presentation formats, matching the Bonsai cost
    # panel's own column labels (see BIM_UL_cost_items_trait.draw_header).
    PRESENTATION_LABELS = {
        "Identification": "ID",
        "RateSubtotal": "Value",
        "TotalPrice": "Total Cost",
    }

    def multiply_cells(self, cell1, cell2):
        return "={}*{}".format(cell1, cell2)

    def sum_cells(self, list_of_cells):
        return "=SUM({})".format(",".join(list_of_cells))

    def get_visible_headers(self, schedule_id: int) -> list[str]:
        """Internal column keys shown in presentation formats, in panel order."""
        headers = self.sheet_data[schedule_id]["headers"]
        return [h for h in self.PRESENTATION_COLUMNS if h in headers]

    def get_display_label(self, column: str) -> str:
        """Header text to write for a column in presentation formats."""
        return self.PRESENTATION_LABELS.get(column, column)

    def is_numeric_column(self, column: str) -> bool:
        return column in ("Quantity", "RateSubtotal", "TotalPrice") or column.endswith(" Cost")

    def get_total_price_formula(self, schedule_id: int, cost_item_index: int, first_data_row: int) -> Union[str, None]:
        """Spreadsheet formula for the TotalPrice cell of a cost item, or None for a plain value.

        Sum items get ``=SUM(...)`` over the TotalPrice cells of their direct
        children, leaf items with a quantity and a rate get ``=Quantity*RateSubtotal``.
        Assumes one cost item per row, in ``cost_items`` order, starting at
        ``first_data_row`` (1-based).
        """
        items = self.sheet_data[schedule_id]["cost_items"]
        headers = self.get_visible_headers(schedule_id)
        if "TotalPrice" not in headers:
            return None
        item = items[cost_item_index]
        col = lambda name: self.column_indexes[headers.index(name)]
        if item["ItemIsASum"]:
            prefix = item["Hierarchy"] + "."
            child_rows = [
                first_data_row + i
                for i, other in enumerate(items)
                if other["Hierarchy"].startswith(prefix) and "." not in other["Hierarchy"][len(prefix) :]
            ]
            if child_rows:
                total_col = col("TotalPrice")
                return self.sum_cells(["{}{}".format(total_col, r) for r in child_rows])
            return None
        if "Quantity" in headers and "RateSubtotal" in headers and item.get("Quantity") and item.get("RateSubtotal"):
            row = first_data_row + cost_item_index
            return self.multiply_cells("{}{}".format(col("Quantity"), row), "{}{}".format(col("RateSubtotal"), row))
        return None

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
        os.makedirs(self.output, exist_ok=True)
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
        from odf.number import CurrencyStyle, CurrencySymbol, Number
        from odf.opendocument import OpenDocumentSpreadsheet
        from odf.style import Style, TableCellProperties

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

        os.makedirs(self.output, exist_ok=True)
        file_name = ""
        for cost_schedule in self.cost_schedules:
            if file_name:
                file_name += "_" + cost_schedule.Name or ""
            else:
                file_name += cost_schedule.Name or ""
            self.write_table(cost_schedule)
        self.doc.save(os.path.join(self.output, file_name), True)

    def write_table(self, cost_schedule):
        from odf.number import CurrencySymbol, Number
        from odf.table import Table, TableCell, TableRow
        from odf.text import P

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
            else:
                assert False, type
            row.addElement(cell)

        first_data_row = 6  # 3 metadata rows, 1 blank row, 1 header row.

        def add_cost_item_rows(table, cost_data, cost_item_index):
            row = TableRow()
            self.row_count += 1
            style = self.colours.get(cost_data["Index"])

            for column in self.get_visible_headers(cost_schedule.id()):
                value = cost_data.get(column, "")
                formula = None
                if column == "TotalPrice":
                    formula = self.get_total_price_formula(cost_schedule.id(), cost_item_index, first_data_row)
                if formula:
                    cell = TableCell(formula=formula, stylename=style)
                elif self.is_numeric_column(column) and isinstance(value, (int, float)):
                    cell = TableCell(valuetype="float", value=value, stylename=style)
                else:
                    cell = TableCell(valuetype="string", stylename=style)
                    cell.addElement(P(text=value))
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
        for header in self.get_visible_headers(cost_schedule.id()):
            add_cell(type="text", value=self.get_display_label(header), row=header_row, style="fed8b1")
        table.addElement(header_row)

        self.row_count = 5
        for i, cost_item_data in enumerate(self.sheet_data[cost_schedule.id()]["cost_items"]):
            add_cost_item_rows(table, cost_item_data, i)

        self.doc.spreadsheet.addElement(table)


class Ifc5DXlsxWriter(Ifc5Dwriter):
    def write(self) -> None:
        # openpyxl rather than xlsxwriter: it is what ifccsv already uses and
        # what ships with Bonsai, so XLSX export works out of the box there.
        import openpyxl

        super().write()
        os.makedirs(self.output, exist_ok=True)
        file_name = ""
        for cost_schedule in self.cost_schedules:
            if file_name:
                file_name += "_" + cost_schedule.Name or ""
            else:
                file_name += cost_schedule.Name or ""
        self.file_path = os.path.join(self.output, "{}.xlsx".format(file_name))
        self.workbook = openpyxl.Workbook()
        self.workbook.remove(self.workbook.active)
        for cost_schedule in self.cost_schedules:
            self.write_table(cost_schedule)
        self.workbook.save(self.file_path)

    def write_table(self, cost_schedule):
        import re

        sheet_id = cost_schedule.id()
        title = re.sub(r"[\[\]:*?/\\]", "_", self.sheet_data[sheet_id]["Name"])[:31]
        worksheet = self.workbook.create_sheet(title)
        headers = self.get_visible_headers(sheet_id)
        worksheet.append([self.get_display_label(h) for h in headers])

        first_data_row = 2  # Row 1 is the header.
        for i, cost_item_data in enumerate(self.sheet_data[sheet_id]["cost_items"]):
            row = []
            for header in headers:
                formula = None
                if header == "TotalPrice":
                    formula = self.get_total_price_formula(sheet_id, i, first_data_row)
                # openpyxl treats strings starting with "=" as formulas.
                row.append(formula if formula else cost_item_data.get(header, None))
            worksheet.append(row)


class Ifc5DPdfWriter(Ifc5Dwriter):
    def __init__(
        self,
        file: Union[str, ifcopenshell.file],
        output: str,
        options: dict,
        cost_schedule: ifcopenshell.entity_instance,
        force_schedule_type: Optional[str] = None,
    ):
        """
        PDF Writer is based on typst library, be sure it is available.
        :param file: IFC file to exprot cost schedules from.
        :param output: Output file path including name and .pdf extension.
        :param cost_schedule: exported cost schedule. Output will be different accoding to Cost Schedule PredefinedType.
        :param force_schedule_type: optional parameter to force the output to a specific Schedule Type (suports "PRICEDBILLOFQUANTITIES", "UNPRICEDBILLOFQUANTITIES", "SCHEDULEOFRATES",).
        """
        self.output = output
        if isinstance(file, str):
            self.file = ifcopenshell.open(file)
        else:
            self.file = file
        self.cost_schedule = cost_schedule
        self.force_schedule_type = force_schedule_type
        self.options = options

    def write(self) -> None:
        import os
        import shutil
        import tempfile

        import typst

        import ifc5d

        DEFAULT_OPTIONS = {
            "nested_structure_depth": 0,
            "parent_to_new_page_up_to_depth": 0,
            "show_only_parents": False,
            "should_print_cover": False,
            "should_print_cost_ids": True,
            "should_print_description": False,
            "should_print_each_quantity": True,
            "should_print_each_cost_value": False,
            "should_print_rates": True,
            "should_print_summary": True,
        }

        HANDLED_COST_SCHEDULE_TYPES = (
            # Commented predefined types are not handled at the moment
            # "BUDGET",
            # "COSTPLAN",
            # "ESTIMATE",
            # "TENDER",
            "PRICEDBILLOFQUANTITIES",
            "UNPRICEDBILLOFQUANTITIES",
            "SCHEDULEOFRATES",
            # "USERDEFINED",
            # "NOTDEFINED"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            cost_schedule_name = self.cost_schedule.Name or "Unnamed"
            if self.force_schedule_type in ("PRICEDBILLOFQUANTITIES", "SCHEDULEOFRATES"):
                schedule_type = self.force_schedule_type
            elif self.force_schedule_type is None or self.force_schedule_type == "AUTO":
                schedule_type = self.cost_schedule.PredefinedType
                if schedule_type not in HANDLED_COST_SCHEDULE_TYPES:
                    schedule_type = "PRICEDBILLOFQUANTITIES"
            else:
                raise ValueError(
                    "force_schedule_type can be set to AUTO, PRICEDBILLOFQUANTITIES, SCHEDULEOFRATES values only."
                )
            project_monetary_unit = self.file.by_type("IfcMonetaryUnit")
            if project_monetary_unit:
                project_currency = project_monetary_unit[0].Currency
            else:
                project_currency = ""

            # export csv file
            csv_file_writer = Ifc5DCsvWriter(file=self.file, output=temp_dir, cost_schedule=self.cost_schedule)
            csv_file_writer.write()
            csv_file_name = cost_schedule_name + ".csv"

            # locate typst template file
            typst_template_file_path = os.path.join(
                os.path.dirname(ifc5d.__file__), "typst_template_ifc_cost_schedule.typ"
            )
            shutil.copy(typst_template_file_path, temp_dir)

            # generate typst main file content and write it
            typst_main_content = ""
            typst_main_content += '#import "{}": *\n'.format("typst_template_ifc_cost_schedule.typ")
            typst_main_content += "#show: project.with(\n"
            typst_main_content += '  schedule_path: "{}",\n'.format(csv_file_name)
            typst_main_content += '  title: "{}",\n'.format(self.file.by_type("IfcProject")[0].Name)
            typst_main_content += '  schedule_name: "{}",\n'.format(cost_schedule_name)
            typst_main_content += '  schedule_description: "{}",\n'.format(self.cost_schedule.Description or "")
            typst_main_content += '  schedule_type: "{}",\n'.format(schedule_type)
            typst_main_content += '  project_currency: "{}",\n'.format(project_currency)
            for option_name, default_value in DEFAULT_OPTIONS.items():
                value = self.options.get(option_name, default_value)
                if isinstance(value, bool):
                    formatted_value = str(value).lower()
                else:
                    formatted_value = str(value)
                typst_main_content += f"  {option_name}: {formatted_value},\n"

            typst_main_content += ")"
            typst_main_path = os.path.join(temp_dir, "main.typ")
            with open(typst_main_path, "w") as typ_file:
                typ_file.write(typst_main_content)

            # compile pdf file and write it
            pdf_bytes = typst.compile(typst_main_path)
            with open(self.output, "wb") as f:
                f.write(pdf_bytes)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="Specify an IFC file to process")
    parser.add_argument("output", help="The output directory")
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
    else:
        assert False, args
    writer.write()

    logger.info("Finished conversion in %ss", time.time() - start)
    logger.info("Conversion and report generation complete")
