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

from __future__ import annotations
import csv
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.api.cost
import ifcopenshell.api.root
import ifcopenshell.util.unit
import ifcopenshell.util.selector
import ifcopenshell.util.element
import locale
from typing import Any, Union, Optional, TypedDict, NotRequired


class CsvHeader(TypedDict):
    Index: int
    Name: int
    Unit: int
    Identification: NotRequired[int]
    Value: NotRequired[int]

    # Not schedule of rates:
    Quantity: NotRequired[int]
    Property: NotRequired[int]
    Query: NotRequired[int]


class CostItem(TypedDict):
    children: list[CostItem]
    ifc: NotRequired[ifcopenshell.entity_instance]

    Identification: Union[str, None]
    Name: Union[str, None]
    Unit: Union[str, None]
    CostValues: Union[dict[str, float], float, None]

    # Only might be available in non-SOR.
    Quantity: Union[float, None]
    Property: Union[str, None]
    Query: Union[str, None]


class Csv2Ifc:
    # Inputs.
    csv: str
    file: Union[ifcopenshell.file, None] = None
    cost_schedule: Union[ifcopenshell.entity_instance, None] = None
    is_schedule_of_rates: bool = False

    # Output.
    cost_items: list[CostItem]

    # Private.
    headers: CsvHeader
    units: dict[str, ifcopenshell.entity_instance]

    def __init__(
        self,
        csv: str = None,
        ifc_file: Union[ifcopenshell.file, None] = None,
        cost_schedule: Union[ifcopenshell.entity_instance, None] = None,
        *,
        is_schedule_of_rates: bool = False,
    ):
        """
        :param csv: CSV filepath to import.
        :param ifc_file: IFC file to import to. If not provided, boilerplate file will be created.
        :param cost_schedule: Cost schedule to load cost items to. If not provided, new one will be created.
        :param is_schedule_of_rates: Whether imported schedule is a schedule of rates.
        """
        # TODO: Arguments added only at 25.04.14
        # `csv` argument is actually not optional, it's only optional for backwards compatibility.
        # And will be deprecated later.
        if csv is None:
            print("WARNING. `csv` argument is not optional and should be provided to the constructor.")
        self.csv = csv
        self.file = ifc_file
        self.cost_schedule = cost_schedule
        self.is_schedule_of_rates = is_schedule_of_rates
        self.units = {}

    def execute(self) -> None:
        assert self.csv
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self) -> None:
        """Fill ``headers`` and ``cost_items`` based on data from csv file."""
        self.cost_items = []
        self.headers = {}

        parents: dict[int, CostItem] = {}
        locale.setlocale(locale.LC_ALL, "")  # set the system locale
        non_sor_fields = {"Property", "Query"}

        # TODO: 25-04-17 Deprecated 0 indices, should fully remove later.
        min_index = None

        with open(self.csv, "r", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if not row[0]:
                    continue
                # parse header
                if not self.headers:
                    self.has_categories = True
                    self.headers = {col: i for i, col in enumerate(row) if col}
                    if "Value" in self.headers:
                        self.has_categories = False

                    # validate header
                    mandatory_fields = {"Name", "Quantity", "Unit"}
                    if not self.is_schedule_of_rates:
                        mandatory_fields.update(non_sor_fields)
                    available_fields = set(self.headers.keys())
                    missing_fields = mandatory_fields - available_fields

                    # TODO: 25-04-17 Deprecated 'Description' argument, should fully remove later.
                    if missing_fields and "Name" in missing_fields and "Description" in available_fields:
                        print(
                            "WARNING. 'Description' column is deprecated and should be renamed to 'Name'. It will be deprecated soon completely."
                        )
                        self.headers["Name"] = self.headers["Description"]
                        del self.headers["Description"]
                        missing_fields.remove("Name")

                    if missing_fields:
                        if missing_fields == non_sor_fields and not self.is_schedule_of_rates:
                            self.is_schedule_of_rates = True
                            print(
                                "WARNING. Assumed the imported cost schedule is a schedule of rates "
                                f"because the following fields are missing: {', '.join(non_sor_fields)}."
                            )
                        else:
                            raise Exception(f"Missing mandatory fields in CSV header: {', '.join(missing_fields)}")

                    continue
                cost_data = self.get_row_cost_data(row)
                index = int(row[self.headers["Index"]])
                if min_index is None and index in (0, 1):
                    if index == 0:
                        print(
                            "WARNING. Indices in csv table start from 0, they should start from 1. It will be deprecated soon completely."
                        )
                    min_index = index
                if index == min_index:
                    self.cost_items.append(cost_data)
                else:
                    parents[index - 1]["children"].append(cost_data)
                parents[index] = cost_data

    def get_row_cost_data(self, row: list[str]) -> CostItem:
        name = row[self.headers["Name"]]
        identification = row[self.headers["Identification"]] if "Identification" in self.headers else None
        quantity = row[(self.headers["Quantity"])] if "Quantity" in self.headers else None
        unit = row[self.headers["Unit"]]
        if self.is_schedule_of_rates:
            property_name, query = None, None
        else:
            property_name = row[(self.headers["Property"])] if "Property" in self.headers else None
            query = row[(self.headers["Query"])] if "Query" in self.headers else None

        if self.has_categories:
            cost_values = {
                k: locale.atof(row[v])
                for k, v in self.headers.items()
                if k not in ["Hierarchy", "Identification", "Name", "Quantity", "Unit", "Subtotal", "Property", "Query"]
                and row[v]
            }
        else:
            assert "Value" in self.headers
            cost_values = row[self.headers["Value"]]
            cost_values = float(cost_values) if cost_values else None
        return {
            "Identification": str(identification) if identification else None,
            "Name": str(name) if name else None,
            "Unit": str(unit) if unit else None,
            "CostValues": cost_values,
            "Quantity": float(quantity) if quantity else None,
            "Property": property_name,
            "Query": query,
            "children": [],
        }

    def create_ifc(self) -> None:
        if not self.file:
            self.create_boilerplate_ifc()
        assert self.file
        if not self.cost_schedule:
            self.cost_schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="CSV Import")
            if self.is_schedule_of_rates:
                self.cost_schedule.PredefinedType = "SCHEDULEOFRATES"
        self.create_cost_items(self.cost_items)

    def create_cost_items(
        self, cost_items: list[CostItem], parent: Optional[ifcopenshell.entity_instance] = None
    ) -> None:
        # Not using `self.cost_items` directly to allow recursion.
        for cost_item in cost_items:
            self.create_cost_item(cost_item, parent)

    def create_cost_item(self, cost_item: CostItem, parent: Optional[ifcopenshell.entity_instance] = None) -> None:
        assert self.file
        if parent is None:
            cost_item["ifc"] = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=self.cost_schedule)
        else:
            cost_item["ifc"] = ifcopenshell.api.cost.add_cost_item(self.file, cost_item=parent)

        cost_item["ifc"].Name = cost_item["Name"]
        cost_item["ifc"].Identification = cost_item["Identification"]

        cost_values = cost_item["CostValues"]
        if ((isinstance(cost_values, dict) and len(cost_values) == 0) or (cost_values is None)) and cost_item[
            "children"
        ]:
            if not self.is_schedule_of_rates:
                cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=cost_item["ifc"])
                cost_value.Category = "*"
        elif self.has_categories:
            assert isinstance(cost_values, dict)
            for category, value in cost_values.items():
                cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=cost_item["ifc"])
                cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(value)
                if category != "Rate" or category != "Price":
                    if "Rate" in category or "Price" in category:
                        category = category.replace("Rate", "")
                        category = category.strip()
                    cost_value.Category = category
        elif cost_values:
            cost_value = ifcopenshell.api.cost.add_cost_value(self.file, parent=cost_item["ifc"])
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
        prop_name = cost_item["Property"]
        if not prop_name or prop_name.upper() == "COUNT":
            prop_name = ""

        if not self.is_schedule_of_rates and cost_item["Quantity"] is not None:
            quantity = ifcopenshell.api.cost.add_cost_item_quantity(
                self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
            )
            # 3 IfcPhysicalSimpleQuantity Value
            quantity[3] = int(cost_item["Quantity"]) if quantity_class == "IfcQuantityCount" else cost_item["Quantity"]
            if prop_name:
                quantity.Name = prop_name

        if cost_item["Query"]:
            results = ifcopenshell.util.selector.filter_elements(self.file, cost_item["Query"])
            results = [r for r in results if has_property(self.file, r, prop_name)]
            # NOTE: currently we do not support count quantities that have
            # both defined quantity in .csv "Quantity" column
            # and some query in "Query" column.
            # If query is provided it will override the defined value
            # due current behaviour in cost.assign_cost_item_quantity.
            if results:
                ifcopenshell.api.cost.assign_cost_item_quantity(
                    self.file,
                    cost_item=cost_item["ifc"],
                    products=results,
                    prop_name=prop_name,
                )
            elif not quantity:
                quantity = ifcopenshell.api.cost.add_cost_item_quantity(
                    self.file, cost_item=cost_item["ifc"], ifc_class=quantity_class
                )

        self.create_cost_items(cost_item["children"], cost_item["ifc"])

    def create_unit(self, symbol: str) -> ifcopenshell.entity_instance:
        unit = self.units.get(symbol, None)
        if unit:
            return unit
        assert self.file
        unit = self.file.create_entity(
            "IfcContextDependentUnit",
            self.file.create_entity("IfcDimensionalExponents", 0, 0, 0, 0, 0, 0, 0),
            "USERDEFINED",
            symbol,
        )
        self.units[symbol] = unit
        return unit

    def create_boilerplate_ifc(self) -> None:
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")


def has_property(self, product: ifcopenshell.entity_instance, property_name: str) -> bool:
    if not property_name:
        return True
    qtos = ifcopenshell.util.element.get_psets(product, qtos_only=True)
    for qset, quantities in qtos.items():
        for quantity, value in quantities.items():
            if quantity == property_name:
                return True
    return False
