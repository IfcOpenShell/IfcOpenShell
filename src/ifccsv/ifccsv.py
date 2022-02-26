#!/usr/bin/env python3

# IfcCSV - A utility to interact with IFC data through CSV.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcCSV.
#
# IfcCSV is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcCSV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcCSV.  If not, see <http://www.gnu.org/licenses/>.

# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifccsv.py`

import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.schema
import csv
import argparse


class IfcAttributeSetter:
    @staticmethod
    def set_element_key(ifc_file, element, key, value):
        if key == "type" and element.is_a() != value:
            return ifcopenshell.util.schema.reassign_class(ifc_file, element, value)
        if hasattr(element, key):
            setattr(element, key, value)
            return element
        if "." not in key:
            return element
        if key[0:3] == "Qto":
            qto_name, prop = key.split(".", 1)
            qto = IfcAttributeSetter.get_element_qto(element, qto_name)
            if qto:
                IfcAttributeSetter.set_qto_property(qto, prop, value)
                return element
        pset_name, prop = key.split(".", 1)
        pset = IfcAttributeSetter.get_element_pset(element, pset_name)
        if pset:
            IfcAttributeSetter.set_pset_property(ifc_file, pset, prop, value)
            return element
        return element

    @staticmethod
    def get_element_qto(element, name):
        for relationship in element.IsDefinedBy:
            if (
                relationship.is_a("IfcRelDefinesByProperties")
                and relationship.RelatingPropertyDefinition.is_a("IfcElementQuantity")
                and relationship.RelatingPropertyDefinition.Name == name
            ):
                return relationship.RelatingPropertyDefinition

    @staticmethod
    def set_qto_property(qto, name, value):
        for prop in qto.Quantities:
            if prop.Name != name:
                continue
            setattr(prop, prop.is_a()[len("IfcQuantity") :] + "Value", value)

    @staticmethod
    def get_element_pset(element, name):
        if element.is_a("IfcTypeObject"):
            if element.HasPropertySets:
                for pset in element.HasPropertySets:
                    if pset.is_a("IfcPropertySet") and pset.Name == name:
                        return pset
        else:
            for relationship in element.IsDefinedBy:
                if (
                    relationship.is_a("IfcRelDefinesByProperties")
                    and relationship.RelatingPropertyDefinition.is_a("IfcPropertySet")
                    and relationship.RelatingPropertyDefinition.Name == name
                ):
                    return relationship.RelatingPropertyDefinition

    @staticmethod
    def set_pset_property(ifc_file, pset, name, value):
        for property in pset.HasProperties:
            if property.Name != name:
                continue

            if value.lower() in ["null", "none"]:
                property.NominalValue = None
                continue

            # In lieu of loading a map for data casting, we only have four
            # options, which this ugly method will determine.
            if property.NominalValue is None:
                if value.isnumeric():
                    property.NominalValue = ifc_file.createIfcInteger(int(value))
                elif value.lower() in ["1", "true", "yes", "uh-huh"]:
                    property.NominalValue = ifc_file.createIfcBoolean(True)
                elif value.lower() in ["0", "false", "no", "nope"]:
                    property.NominalValue = ifc_file.createIfcBoolean(False)
                else:
                    try:
                        value = float(value)
                        property.NominalValue = ifc_file.createIfcReal(value)
                    except:
                        property.NominalValue = ifc_file.createIfcLabel(str(value))
            else:
                try:
                    property.NominalValue.wrappedValue = str(value)
                except:
                    try:
                        property.NominalValue.wrappedValue = float(value)
                    except:
                        try:
                            property.NominalValue.wrappedValue = int(value)
                        except:
                            property.NominalValue.wrappedValue = (
                                True if value.lower() in ["1", "true", "yes", "uh-huh"] else False
                            )


class IfcCsv:
    def __init__(self):
        self.results = []
        self.attributes = []
        self.output = ""
        self.selector = ifcopenshell.util.selector.Selector()
        self.delimiter = ","

    def export(self, ifc_file, elements):
        self.ifc_file = ifc_file
        for element in elements:
            result = []
            if hasattr(element, "GlobalId"):
                result.append(element.GlobalId)
            else:
                result.append(None)

            for index, attribute in enumerate(self.attributes):
                if "*" in attribute:
                    self.attributes.extend(self.get_wildcard_attributes(attribute))
                    del self.attributes[index]

            for attribute in self.attributes:
                result.append(self.selector.get_element_value(element, attribute))
            self.results.append(result)

        with open(self.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=self.delimiter)
            header = ["GlobalId"]
            header.extend(self.attributes)
            writer.writerow(header)
            for row in self.results:
                writer.writerow(row)

    def get_wildcard_attributes(self, attribute):
        results = set()
        pset_qto_name = attribute.split(".", 1)[0]
        for element in self.ifc_file.by_type("IfcPropertySet") + self.ifc_file.by_type("IfcElementQuantity"):
            if element.Name != pset_qto_name:
                continue
            if element.is_a("IfcPropertySet"):
                results.update([p.Name for p in element.HasProperties])
            else:
                results.update([p.Name for p in element.Quantities])
        return ["{}.{}".format(pset_qto_name, n) for n in results]

    def Import(self, ifc_file):
        with open(self.output, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            headers = []
            for row in reader:
                if not headers:
                    headers = row
                    continue
                try:
                    element = ifc_file.by_guid(row[0])
                except:
                    print("The element with GUID {} was not found".format(row[0]))
                    continue
                for i, value in enumerate(row):
                    if i == 0:
                        continue  # Skip GlobalId
                    element = IfcAttributeSetter.set_element_key(ifc_file, element, headers[i], value)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports IFC data to and from CSV")
    parser.add_argument("-i", "--ifc", type=str, required=True, help="The IFC file")
    parser.add_argument("-c", "--csv", type=str, default="data.csv", help="The CSV file to import from or export to")
    parser.add_argument("-q", "--query", type=str, default="", help='Specify a IFC query selector, such as ".IfcWall"')
    parser.add_argument("-a", "--arguments", nargs="+", help="Specify attributes that are part of the extract, using the IfcQuery syntax such as 'type', 'Name' or 'Pset_Foo.Bar'")
    parser.add_argument("--export", action="store_true", help="Export from IFC to CSV")
    parser.add_argument("--import", action="store_true", help="Import from CSV to IFC")
    args = parser.parse_args()

    if args.export:
        ifc_file = ifcopenshell.open(args.ifc)
        selector = ifcopenshell.util.selector.Selector()
        results = selector.parse(ifc_file, args.query)
        ifc_csv = IfcCsv()
        ifc_csv.output = args.csv
        ifc_csv.attributes = args.arguments if args.arguments else []
        ifc_csv.selector = selector
        ifc_csv.export(ifc_file, results)
    elif getattr(args, "import"):
        ifc_csv = IfcCsv()
        ifc_csv.output = args.csv
        ifc_file = ifcopenshell.open(args.ifc)
        ifc_csv.Import(ifc_file)
        ifc_file.write(args.ifc)
