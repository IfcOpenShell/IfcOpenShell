# IfcResources - IFC resources utility
# Copyright (C) 2021,2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
#
# This file is part of IfcResources.
#
# IfcResources is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcResources is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcResources.  If not, see <http://www.gnu.org/licenses/>.

import csv
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.unit
import datetime
from typing import Any, Optional, Union


class Csv2Ifc:
    """Class to import resources from a CSV file into an IFC file.

    See resource_spreadsheet.csv for example of the format.
    Notes about format:
    - empty rows are skipped.
    - 'HIERARCHY' must be the first column.
    - See SUPPORTED_COLUMNS below for the list of supported columns.

    Example:

    .. code:: python

        csv2ifc = Csv2Ifc("resource_spreadsheet.csv", ifc_file)
        csv2ifc.execute()
    """

    SUPPORTED_COLUMNS = (
        "HIERARCHY",
        "TYPE",  # CREW, LABOR, EQUIPMENT, SUBCONTRACTOR, MATERIAL, PRODUCT.
        "ACTIVITY/RESOURCE NAME",
        "DESCRIPTION",
        "COST",
        "QUANTITY NAME",
        "LABOR OUTPUT",
        "EQUIPMENT OUTPUT",
    )

    def __init__(self, csv: str, ifc_file: Optional[ifcopenshell.file] = None):
        """
        :param csv: CSV filepath to load resources from.
        :param ifc_file: IFC file to load imported resources to. If not provided,
            a simple empty IFC file will be created.
        """
        self.csv = csv
        self.file = ifc_file
        self.resources: list[dict[str, Any]] = []
        self.units = {}  # TODO: never used
        self.resource_map = {
            "CREW": "IfcCrewResource",
            "LABOR": "IfcLaborResource",
            "EQUIPMENT": "IfcConstructionEquipmentResource",
            "SUBCONTRACTOR": "IfcSubContractResource",
            "MATERIAL": "IfcConstructionMaterialResource",
            "PRODUCT": "IfcConstructionProductResource",
        }

    def execute(self) -> None:
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self) -> None:
        self.parents = {}
        self.headers: dict[str, int] = {}
        with open(self.csv, "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                # Skip empty rows.
                if not row[0]:
                    continue
                if row[0] == "HIERARCHY":
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        self.headers[col] = i
                    continue

                resource_data = self.get_row_resource_data(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.resources.append(resource_data)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(resource_data)
                self.parents[hierarchy_key] = resource_data

    def get_row_resource_data(self, row: list[str]) -> dict[str, Any]:
        name = row[self.headers["ACTIVITY/RESOURCE NAME"]]
        resource_class = self.resource_map[row[self.headers["TYPE"]]]
        base_cost_value = row[self.headers["COST"]]
        productivity = {}

        if resource_class in ["IfcConstructionEquipmentResource", "IfcLaborResource"]:
            output_ratio = row[self.headers["LABOR OUTPUT"]]
            if not output_ratio:
                output_ratio = row[self.headers["EQUIPMENT OUTPUT"]]
            if output_ratio:
                time_consumed = datetime.timedelta(minutes=float(output_ratio) * 60)
                time_consumed = ifcopenshell.util.date.datetime2ifc(time_consumed, "IfcDuration")

                productivity = {
                    "BaseQuantityConsumed": time_consumed,
                    "BaseQuantityProducedName": row[self.headers["QUANTITY NAME"]],
                    "BaseQuantityProducedValue": 1,
                }

        return {
            "Name": str(name).strip() if name else None,
            "Description": row[self.headers["DESCRIPTION"]],
            "class": resource_class,
            "BaseCostValue": float(base_cost_value) if base_cost_value else None,
            "Productivity": productivity,
            "children": [],
        }

    def create_ifc(self) -> None:
        if not self.file:
            self.create_boilerplate_ifc()
        self.create_resources(self.resources)

    def create_resources(
        self, resources: list[dict[str, Any]], parent: Optional[ifcopenshell.entity_instance] = None
    ) -> None:
        for resource in resources:
            self.create_resource(resource, parent)

    def create_resource(self, resource: dict[str, Any], parent: Union[ifcopenshell.entity_instance, None]) -> None:
        assert self.file
        if parent is None:
            resource["ifc"] = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class=resource["class"])
        else:
            resource["ifc"] = ifcopenshell.api.run(
                "resource.add_resource", self.file, parent_resource=parent, ifc_class=resource["class"]
            )
        resource["ifc"].Name = resource["Name"]
        if resource.get("Description", None):
            resource["ifc"].Description = resource.get("Description")
        if resource["Productivity"]:
            pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource["ifc"], name="EPset_Productivity")
            ifcopenshell.api.run(
                "pset.edit_pset",
                self.file,
                pset=pset,
                properties=resource["Productivity"],
            )
        if resource["BaseCostValue"]:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=resource["ifc"])
            cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(resource["BaseCostValue"])
        self.create_resources(resource["children"], resource["ifc"])

    # TODO: never used.
    def create_unit(self, symbol, unit_type):
        assert self.file
        unit = self.units.get(symbol, None)
        if unit:
            return unit
        else:
            unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type=unit_type)
        # unit = self.file.createIfcContextDependentUnit(
        #     self.file.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0), "USERDEFINED", symbol
        # )
        self.units[symbol] = unit
        return unit

    def create_boilerplate_ifc(self) -> None:
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
