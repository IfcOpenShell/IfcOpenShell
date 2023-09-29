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


class Csv2Ifc:
    def __init__(self):
        self.csv = None
        self.file = None
        self.cost_items = []
        self.cost_schedule = None
        self.is_schedule_of_rates = False
        self.units = {}

    def execute(self):
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self):
        self.parents = {}
        self.headers = {}
        locale.setlocale(locale.LC_ALL, "")  # set the system locale
        with open(self.csv, "r", encoding="ISO-8859-1") as csv_file:
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
                if k not in ["Hierarchy", "Identification", "Name", "Quantity", "Unit", "Subtotal", "Property", "Query"] and row[v]
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

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        if not self.cost_schedule:
            self.cost_schedule = ifcopenshell.api.run("cost.add_cost_schedule", self.file, name="CSV Import")
            if self.is_schedule_of_rates:
                self.cost_schedule.PredefinedType = "SCHEDULEOFRATES"
        self.create_cost_items(self.cost_items)

    def create_cost_items(self, cost_items, parent=None):
        for cost_item in cost_items:
            self.create_cost_item(cost_item, parent)

    def create_cost_item(self, cost_item, parent):
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
                    if "Rate" in category or"Price" in category:
                        category = category.replace("Rate","")
                        category = category.strip()
                    cost_value.Category = category
        else:
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

        if not self.is_schedule_of_rates and cost_item["Quantity"]:
            quantity_class = ifcopenshell.util.unit.get_symbol_quantity_class(cost_item["Unit"])
            quantity = ifcopenshell.api.run(
                "cost.add_cost_item_quantity", self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
            )
            quantity[3] = cost_item["Quantity"]
            
        if cost_item["assignments"]["PropertyName"] and cost_item["assignments"]["Query"]:
            print("for query",cost_item["assignments"]["Query"])
            results = ifcopenshell.util.selector.filter_elements(self.file, cost_item["assignments"]["Query"])
    
            results = [r for r in results if has_property(self.file, r, cost_item["assignments"]["PropertyName"])]
            if results:
                ifcopenshell.api.run("cost.assign_cost_item_quantity",  self.file, cost_item=cost_item["ifc"], products=results, prop_name=cost_item["assignments"]["PropertyName"])

        self.create_cost_items(cost_item["children"], cost_item["ifc"])

    def create_unit(self, symbol):
        unit = self.units.get(symbol, None)
        if unit:
            return unit
        unit = self.file.createIfcContextDependentUnit(
            self.file.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0), "USERDEFINED", symbol
        )
        self.units[symbol] = unit
        return unit

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")

def has_property(self, product, property_name):
    qtos = ifcopenshell.util.element.get_psets(product, qtos_only=True)
    for qset, quantities in qtos.items():
        for quantity, value in quantities.items():
            if quantity == property_name:
                return True
    return False