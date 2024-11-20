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

from __future__ import annotations
import csv
import _csv
import ifcopenshell.api.resource
import isodate
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.date
import ifcopenshell.util.element
import ifcopenshell.util.resource
import ifcopenshell.util.unit
import datetime
from typing import Any, Optional, Union, Literal, get_args, NamedTuple, cast


SUPPORTED_COLUMN = Literal[
    "HIERARCHY",
    "TYPE",  # CREW, LABOR, EQUIPMENT, SUBCONTRACTOR, MATERIAL, PRODUCT.
    "ACTIVITY/RESOURCE NAME",
    "DESCRIPTION",
    "COST",
    "USAGE",  # ScheduleUsage.
    "QUANTITY NAME",  # EPset_Productivity.BaseQuantityProducedName.
    # OUTPUT = EPset_Productivity.BaseQuantityConsumed / EPset_Productivity.BaseQuantityProducedValue.
    # In hours per quantity.
    "LABOR OUTPUT",  # OUTPUT for LABOR TYPE.
    "EQUIPMENT OUTPUT",  # OUTPUT for EQUIPMENT TYPE.
]

RESOURCE_MAP = {
    "CREW": "IfcCrewResource",
    "LABOR": "IfcLaborResource",
    "EQUIPMENT": "IfcConstructionEquipmentResource",
    "SUBCONTRACTOR": "IfcSubContractResource",
    "MATERIAL": "IfcConstructionMaterialResource",
    "PRODUCT": "IfcConstructionProductResource",
}


class Csv2Ifc:
    """Class to import resources from a CSV file into an IFC file.

    See resource_spreadsheet.csv for example of the format.
    Note that columns UNIT and PRODUCTIVITY UNIT are not actually used during import.
    Notes about format:
    - empty rows are skipped.
    - 'HIERARCHY' must be the first column.
    - See SUPPORTED_COLUMN above for the list of supported columns.

    Example:

    .. code:: python

        csv2ifc = Csv2Ifc("resource_spreadsheet.csv", ifc_file)
        csv2ifc.execute()
    """

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

    def execute(self) -> None:
        self.parse_csv()
        self.create_ifc()

    def parse_csv(self) -> None:
        self.parents = {}
        self.headers: dict[SUPPORTED_COLUMN, int] = {}
        with open(self.csv, "r") as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                # Skip empty rows.
                if not row[0]:
                    continue
                if row[0] == "HIERARCHY":
                    missing_columns = set(get_args(SUPPORTED_COLUMN)) - set(row)
                    if missing_columns:
                        raise Exception(
                            f"Header is missing some of the required columns: {', '.join(missing_columns)}."
                        )

                    for i, col in enumerate(row):
                        if not col:
                            continue
                        self.headers[col] = i
                    continue

                if not self.headers:
                    raise Exception(
                        f"No header found in CSV file before data row: '{row}'. Note that header should start with 'HIERARCHY' column."
                    )

                resource_data = self.get_row_resource_data(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.resources.append(resource_data)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(resource_data)
                self.parents[hierarchy_key] = resource_data

    def get_row_resource_data(self, row: list[str]) -> dict[str, Any]:
        name = row[self.headers["ACTIVITY/RESOURCE NAME"]]
        resource_class = RESOURCE_MAP[row[self.headers["TYPE"]]]
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
            "usage": row[self.headers["USAGE"]],
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
        if usage_value := resource["usage"]:
            usage = ifcopenshell.api.resource.add_resource_time(self.file, resource=resource["ifc"])
            ifcopenshell.api.resource.edit_resource_time(self.file, usage, {"ScheduleUsage": float(usage_value)})
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


class Ifc2CsvRow(NamedTuple):
    hierarchy: int
    resource_type: str
    name: str
    description: str
    cost: Union[float, None]
    usage: Union[float, None]
    quantity_name: Union[str, None]
    labor_output: Union[float, None]
    equipment_output: Union[float, None]
    guid: str


class Ifc2Csv:
    """Class to export resources from an IFC file to csv file."""

    HEADER = (
        "HIERARCHY",
        "TYPE",
        "ACTIVITY/RESOURCE NAME",
        "DESCRIPTION",
        "COST",
        "USAGE",
        "QUANTITY NAME",
        "LABOR OUTPUT",
        "EQUIPMENT OUTPUT",
        "GUID",
    )
    assert len(HEADER) == len(Ifc2CsvRow._fields)

    def __init__(self, filepath: str, ifc_file: ifcopenshell.file):
        self.filepath = filepath
        self.file = ifc_file
        self.inverse_resource_map = {value: key for key, value in RESOURCE_MAP.items()}

    def execute(self) -> None:
        with open(self.filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(self.HEADER)
            for resource in self.file.by_type("IfcConstructionResource"):
                if resource.Nests:
                    continue
                self.process_recourse(writer, resource, 1)

    def process_recourse(
        self, writer: _csv._writer, resource: ifcopenshell.entity_instance, hierarchy_level: int
    ) -> None:
        row = self.get_row(resource, hierarchy_level)
        writer.writerow(row)
        resources = ifcopenshell.util.resource.get_nested_resources(resource)
        for resource in resources:
            self.process_recourse(writer, resource, hierarchy_level + 1)
        if resources:
            writer.writerow((None,) * len(self.HEADER))

    def get_row(self, resource: ifcopenshell.entity_instance, hierarchy_level: int) -> Ifc2CsvRow:
        resource_class = resource.is_a()
        cost, unit = ifcopenshell.util.resource.get_cost(resource)

        quantity_name = None
        labor_output, equipment_output = None, None
        if resource_class in ("IfcConstructionEquipmentResource", "IfcLaborResource"):
            pset: dict[str, Any] = ifcopenshell.util.element.get_pset(resource, "EPset_Productivity")
            if pset:
                quantity_name = cast(str, pset["BaseQuantityProducedName"])
                time_consumed: float = isodate.parse_duration(pset["BaseQuantityConsumed"]).total_seconds() / 3600
                produced: float = pset["BaseQuantityProducedValue"]
                output = time_consumed / produced
                if resource_class == "IfcLaborResource":
                    labor_output = output
                else:
                    equipment_output, labor_output = None, output

        # Get usage_value.
        usage_value = None
        if usage := resource.Usage:
            usage_value: Union[float, None] = usage.ScheduleUsage

        return Ifc2CsvRow(
            hierarchy=hierarchy_level,
            resource_type=self.inverse_resource_map[resource.is_a()],
            name=resource.Name,
            description=resource.Description,
            cost=cost,
            usage=usage_value,
            quantity_name=quantity_name,
            labor_output=labor_output,
            equipment_output=equipment_output,
            guid=resource.GlobalId,
        )
