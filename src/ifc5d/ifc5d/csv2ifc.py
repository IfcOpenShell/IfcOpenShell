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


class Csv2Ifc:
    def __init__(self):
        self.csv = None
        self.file = None
        self.cost_items = []
        self.cost_schedule = None

    def execute(self):
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self):
        self.parents = {}
        self.headers = {}
        with open(self.csv, "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if not row[0]:
                    continue
                if row[0] == "Hierarchy":
                    self.has_categories = True
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        if col == "Value":
                            self.has_categories = False
                        self.headers[col] = i
                    continue
                cost_data = self.get_row_cost_data(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.cost_items.append(cost_data)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(cost_data)
                self.parents[hierarchy_key] = cost_data

    def get_row_cost_data(self, row):
        name = row[self.headers["Name"]]
        identification = row[self.headers["Identification"]] if "Identification" in self.headers else None
        cost_quantities = row[self.headers["Quantity"]]
        cost_quantities_unit = row[self.headers["Unit"]]
        if self.has_categories:
            cost_values = {
                k: float(row[v])
                for k, v in self.headers.items()
                if k not in ["Hierarchy", "Identification", "Name", "Quantity", "Unit", "Subtotal"] and row[v]
            }
        else:
            cost_values = row[self.headers["Value"]]
            cost_values = float(cost_values) if cost_values else None
        return {
            "Identification": str(identification) if identification else None,
            "Name": str(name) if name else None,
            "CostQuantities": float(cost_quantities) if cost_quantities else None,
            "CostQuantitiesUnit": str(cost_quantities_unit) if cost_quantities_unit else None,
            "CostValues": cost_values,
            "children": [],
        }

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.cost_schedule:
            self.cost_schedule = ifcopenshell.api.run("cost.add_cost_schedule", self.file, name="CSV Import")
        self.create_cost_items(self.cost_items)

    def create_cost_items(self, cost_items, parent=None):
        for cost_item in cost_items:
            self.create_cost_item(cost_item, parent)

    def create_cost_item(self, cost_item, parent):
        if parent is None:
            cost_item["ifc"] = ifcopenshell.api.run(
                "cost.add_cost_item", self.file, cost_schedule=self.cost_schedule
            )
        else:
            cost_item["ifc"] = ifcopenshell.api.run("cost.add_cost_item", self.file, cost_item=parent)

        cost_item["ifc"].Name = cost_item["Name"]
        cost_item["ifc"].Identification = cost_item["Identification"]

        if not cost_item["CostValues"]:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
            cost_value.Category = "*"
        elif self.has_categories:
            for category, value in cost_item["CostValues"].items():
                cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
                cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(value)
                cost_value.Category = category
        else:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=cost_item["ifc"])
            cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(cost_item["CostValues"])

        if cost_item["CostQuantities"]:
            quantity_class = ifcopenshell.util.unit.get_symbol_quantity_class(cost_item["CostQuantitiesUnit"])
            quantity = ifcopenshell.api.run(
                "cost.add_cost_item_quantity", self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
            )
            quantity[3] = cost_item["CostQuantities"]
        self.create_cost_items(cost_item["children"], cost_item["ifc"])

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
