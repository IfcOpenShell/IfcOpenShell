#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifccsv.py`

import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import ifcopenshell.util.schema
import csv
import lark
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
            qto, prop = key.split(".", 1)
            qto = IfcAttributeSetter.get_element_qto(element, qto_name)
            if qto:
                IfcAttributeSetter.set_qto_property(qto, prop, value)
                return element
        pset_name, prop = key.split(".", 1)
        pset = IfcAttributeSetter.get_element_pset(element, pset_name)
        if pset:
            IfcAttributeSetter.set_pset_property(pset, prop, value)
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
    def set_pset_property(pset, name, value):
        for property in pset.HasProperties:
            if property.Name == name:
                # In lieu of loading a map for data casting, we only have four
                # options, which this ugly method will determine.
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
                                True if value.lower() in ["1", "t", "true", "yes", "y", "uh-huh"] else False
                            )


class IfcCsv:
    def __init__(self):
        self.results = []
        self.attributes = []
        self.output = ""
        self.selector = None
        self.delimiter = ";"

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
            writer = csv.writer(f)
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

    def Import(self, ifc):
        ifc_file = ifcopenshell.open(ifc)
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
        ifc_file.write(ifc)


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
        ifc_csv.Import(args.ifc)
