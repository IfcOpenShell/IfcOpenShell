# Ifc5D - IFC costing utility
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import csv
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.unit
import ifcopenshell.util.selector
import ifcopenshell.util.element
import locale
from typing import Any, Optional

CostItem = dict[str, Any]


class Csv2Ifc:
    def __init__(self):
        self.csv: str = None
        self.file: ifcopenshell.file = None
        self.cost_items: list[CostItem] = []
        self.cost_schedule: ifcopenshell.entity_instance = None
        self.is_schedule_of_rates: bool = False
        self.units: dict[str, ifcopenshell.entity_instance] = {}

    def execute(self) -> None:
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self) -> None:
        self.parents = {}
        self.headers = {}
        locale.setlocale(locale.LC_ALL, "")  # set the system locale
        with open(self.csv, "r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if not row[0]:
                    continue
                # parse header
                if row[0] == "Hierarchy":
                    self.has_categories = True
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        if col == "Value":
                            self.has_categories = False
                        self.headers[col] = i

                    # validate header
                    mandatory_fields = {"Name", "Quantity", "Unit"}
                    if not self.is_schedule_of_rates:
                        mandatory_fields.update({"Property", "Query"})
                    available_fields = set(self.headers.keys())
                    if not mandatory_fields.issubset(available_fields):
                        raise Exception(
                            f"Missing mandatory fields in CSV header: {', '.join(mandatory_fields-available_fields)}"
                        )

                    continue
                cost_data = self.get_row_cost_data(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.cost_items.append(cost_data)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(cost_data)
                self.parents[hierarchy_key] = cost_data

    def get_row_cost_data(self, row: list[str]) -> CostItem:
        name = row[self.headers["Name"]]
        identification = row[self.headers["Identification"]] if "Identification" in self.headers else None
        quantity = row[self.headers["Quantity"]]
        unit = row[self.headers["Unit"]]
        if not self.is_schedule_of_rates:
            assignments = {
                "PropertyName": row[self.headers["Property"]],
                "Query": row[self.headers["Query"]],
            }
        else:
            assignments = {
                "PropertyName": None,
                "Query": None,
            }
        if self.has_categories:
            cost_values = {
                k: locale.atof(row[v])
                for k, v in self.headers.items()
                if k not in ["Hierarchy", "Identification", "Name", "Quantity", "Unit", "Subtotal", "Property", "Query"]
                and row[v]
            }
        else:
            cost_values = row[self.headers["Value"]]
            cost_values = float(cost_values) if cost_values else None
        return {
            "Identification": str(identification) if identification else None,
            "Name": str(name) if name else None,
            "Quantity": float(quantity) if quantity else None,
            "Unit": str(unit) if unit else None,
            "CostValues": cost_values,
            "assignments": assignments,
            "children": [],
        }

    def create_ifc(self) -> None:
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.cost_schedule:
            self.cost_schedule = ifcopenshell.api.run("cost.add_cost_schedule", self.file, name="CSV Import")
            if self.is_schedule_of_rates:
                self.cost_schedule.PredefinedType = "SCHEDULEOFRATES"
        self.create_cost_items(self.cost_items)

    def create_cost_items(
        self, cost_items: list[CostItem], parent: Optional[ifcopenshell.entity_instance] = None
    ) -> None:
        for cost_item in cost_items:
            self.create_cost_item(cost_item, parent)

    def create_cost_item(self, cost_item: CostItem, parent: Optional[ifcopenshell.entity_instance] = None) -> None:
        if parent is None:
            cost_item["ifc"] = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_schedule=self.cost_schedule)
        else:
            cost_item["ifc"] = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_item=parent)

        cost_item["ifc"].Name = cost_item["Name"]
        cost_item["ifc"].Identification = cost_item["Identification"]

        if not cost_item["CostValues"] and cost_item["children"]:
            if not self.is_schedule_of_rates:
                cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
                cost_value.Category = "*"
        elif self.has_categories:
            for category, value in cost_item["CostValues"].items():
                cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
                cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(value)
                if category != "Rate" or category != "Price":
                    if "Rate" in category or "Price" in category:
                        category = category.replace("Rate", "")
                        category = category.strip()
                    cost_value.Category = category
        elif cost_item["CostValues"]:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
            cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(cost_item["CostValues"])
            if self.is_schedule_of_rates:
                measure_class = ifcopenshell.util.unit.get_symbol_measure_class(cost_item["Unit"])
                value_component = self.file.create_entity(measure_class, cost_item["Quantity"])
                unit_component = None

                if measure_class == "IfcNumericMeasure":
                    unit_component = self.create_unit(cost_item["Unit"])
                else:
                    unit_type = ifcopenshell.util.unit.get_measure_unit_type(measure_class)
                    unit_assignment = ifcopenshell.util.unit.get_unit_assignment(self.file)
                    if unit_assignment:
                        units = [u for u in unit_assignment.Units if getattr(u, "UnitType", None) == unit_type]
                        if units:
                            unit_component = units[0]
                    if not unit_component:
                        unit_component = self.create_unit(cost_item["Unit"])

                cost_value.UnitBasis = self.file.createIfcMeasureWithUnit(value_component, unit_component)

        quantity = None
        quantity_class = ifcopenshell.util.unit.get_symbol_quantity_class(cost_item["Unit"])
        if not cost_item["assignments"]["PropertyName"] or cost_item["assignments"]["PropertyName"].upper() == "COUNT":
            prop_name = ""
        else:
            prop_name = cost_item["assignments"]["PropertyName"]

        if not self.is_schedule_of_rates and cost_item["Quantity"] is not None:
            quantity = ifcopenshell.api.run(
                "cost.add_cost_item_quantity", self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
            )
            # 3 IfcPhysicalSimpleQuantity Value
            quantity[3] = int(cost_item["Quantity"]) if quantity_class == "IfcQuantityCount" else cost_item["Quantity"]
            if prop_name:
                quantity.Name = prop_name

        if cost_item["assignments"]["Query"]:
            results = ifcopenshell.util.selector.filter_elements(self.file, cost_item["assignments"]["Query"])
            results = [r for r in results if has_property(self.file, r, prop_name)]
            # NOTE: currently we do not support count quantities that have
            # both defined quantity in .csv "Quantity" column
            # and some query in "Query" column.
            # If query is provided it will override the defined value
            # due current behaviour in cost.assign_cost_item_quantity.
            if results:
                ifcopenshell.api.run(
                    "cost.assign_cost_item_quantity",
                    self.file,
                    cost_item=cost_item["ifc"],
                    products=results,
                    prop_name=prop_name,
                )
            elif not quantity:
                quantity = ifcopenshell.api.run(
                    "cost.add_cost_item_quantity", self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
                )

        self.create_cost_items(cost_item["children"], cost_item["ifc"])

    def create_unit(self, symbol: str) -> ifcopenshell.entity_instance:
        unit = self.units.get(symbol, None)
        if unit:
            return unit
        unit = self.file.createIfcContextDependentUnit(
            self.file.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0), "USERDEFINED", symbol
        )
        self.units[symbol] = unit
        return unit

    def create_boilerplate_ifc(self) -> None:
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")


def has_property(self, product: ifcopenshell.entity_instance, property_name: str) -> bool:
    if not property_name:
        return True
    qtos = ifcopenshell.util.element.get_psets(product, qtos_only=True)
    for qset, quantities in qtos.items():
        for quantity, value in quantities.items():
            if quantity == property_name:
                return True
    return False
