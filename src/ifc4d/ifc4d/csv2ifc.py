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
import ifcopenshell.util.unit


class Csv2Ifc:
    def __init__(self):
        self.csv = None
        self.file = None
        self.resources = []
        self.units = {}

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
                    for i, col in enumerate(row):
                        if not col:
                            continue
                        self.headers[col] = i
                    continue
                cost_data = self.get_row_resource_data(row)
                hierarchy_key = int(row[0])
                if hierarchy_key == 1:
                    self.resources.append(cost_data)
                else:
                    self.parents[hierarchy_key - 1]["children"].append(cost_data)
                self.parents[hierarchy_key] = cost_data

    def get_row_resource_data(self, row):
        name = row[self.headers["Name"]]
        identification = row[self.headers["Identification"]] if "Identification" in self.headers else None

        type = row[self.headers["Type"]]
        base_cost_value = row[self.headers["BaseCostValue"]]
        base_cost_quantity = row[self.headers["BaseCostQuantity"]]
        base_cost_unit = row[self.headers["QuantityUnit"]]

        productivity = {
            "BaseQuantityConsumed": row[self.headers["BaseQuantityConsumed"]],
            "BaseQuantityProducedName": row[self.headers["BaseQuantityProducedName"]],
            "BaseQuantityProducedValue": row[self.headers["BaseQuantityProducedValue"]],
        }

        return {
            "Identification": str(identification).strip() if identification else None,
            "Name": str(name).strip() if name else None,
            "Type": type,
            "BaseCostValue": float(base_cost_value) if base_cost_value else None,
            "BaseCostQuantity": float(base_cost_quantity) if base_cost_quantity else None,
            "Unit": str(base_cost_unit).strip() if base_cost_unit else None,
            "Productivity": productivity if productivity["BaseQuantityProducedName"] else None,
            "children": [],
        }

    def create_ifc(self):
        if not self.file:
            self.create_boilerplate_ifc()
        self.create_resources(self.resources)

    def create_resources(self, resources, parent=None):
        for resource in resources:
            self.create_resource(resource, parent)

    def create_resource(self, resource, parent):
        if parent is None:
            resource["ifc"] = ifcopenshell.api.run("resource.add_resource", self.file, ifc_class=resource["Type"])
        else:
            resource["ifc"] = ifcopenshell.api.run(
                "resource.add_resource", self.file, parent_resource=parent, ifc_class=resource["Type"]
            )
        resource["ifc"].Name = resource["Name"]
        resource["ifc"].Identification = resource["Identification"]
        productivity = resource["Productivity"]
        if productivity:
            pset = ifcopenshell.api.run("pset.add_pset", self.file, product=resource["ifc"], name="EPset_Productivity")
            ifcopenshell.api.run(
                "pset.edit_pset",
                self.file,
                pset=pset,
                properties=productivity,
            )
        if resource["BaseCostValue"]:
            cost_value = ifcopenshell.api.run("cost.add_cost_value", self.file, parent=resource["ifc"])
            cost_value.AppliedValue = self.file.createIfcMonetaryMeasure(resource["BaseCostValue"])
        if resource["Unit"]:
            measure_class = ifcopenshell.util.unit.get_symbol_measure_class(resource["Unit"])
            print(measure_class)
            value_component = self.file.create_entity(measure_class, resource["BaseCostQuantity"])
            print(value_component)
            unit_component = None
            if measure_class == "IfcNumericMeasure":
                unit_component = self.create_unit(resource["Unit"])
            else:
                unit_type = ifcopenshell.util.unit.get_measure_unit_type(measure_class)
                print(unit_type)
                unit_assignment = ifcopenshell.util.unit.get_unit_assignment(self.file)
                if unit_assignment:
                    units = [u for u in unit_assignment.Units if getattr(u, "UnitType", None) == unit_type]
                    if units:
                        unit_component = units[0]
                if not unit_component:
                    unit_component = self.create_unit(resource["Unit"], unit_type)
                    print(unit_component)
            cost_value.UnitBasis = self.file.createIfcMeasureWithUnit(value_component, unit_component)
        self.create_resources(resource["children"], resource["ifc"])

    def create_unit(self, symbol, unit_type):
        unit = self.units.get(symbol, None)
        if unit:
            return unit
        else:
            unit = ifcopenshell.api.run("unit.add_si_unit", self.file, unit_type=unit_type, name=ifcopenshell.util.unit.si_type_names.get(unit_type, None))
        # unit = self.file.createIfcContextDependentUnit(
        #     self.file.createIfcDimensionalExponents(0, 0, 0, 0, 0, 0, 0), "USERDEFINED", symbol
        # )
        self.units[symbol] = unit
        return unit

    def create_boilerplate_ifc(self):
        self.file = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        ifcopenshell.api.run("unit.assign_unit", self.file)
