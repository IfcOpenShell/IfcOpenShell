#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifccsv.py`

import ifcopenshell
import ifcopenshell.util.selector
import ifcopenshell.util.element
import csv
import lark
import argparse


class IfcAttributeExtractor:
    @staticmethod
    def set_element_key(ifc_file, element, key, value):
        if key == "type" and element.is_a() != value:
            return IfcAttributeExtractor.change_ifc_class(ifc_file, element, value)
        if hasattr(element, key):
            setattr(element, key, value)
            return element
        if "." not in key:
            return element
        if key[0:3] == "Qto":
            qto, prop = key.split(".", 1)
            qto = IfcAttributeExtractor.get_element_qto(element, qto_name)
            if qto:
                IfcAttributeExtractor.set_qto_property(qto, prop, value)
                return element
        pset_name, prop = key.split(".", 1)
        pset = IfcAttributeExtractor.get_element_pset(element, pset_name)
        if pset:
            IfcAttributeExtractor.set_pset_property(pset, prop, value)
            return element
        return element

    @staticmethod
    def change_ifc_class(ifc_file, element, new_class):
        try:
            new_element = ifc_file.create_entity(new_class)
        except:
            return
        new_attributes = [new_element.attribute_name(i) for i, attribute in enumerate(new_element)]
        for i, attribute in enumerate(element):
            try:
                new_element[new_attributes.index(element.attribute_name(i))] = attribute
            except:
                continue
        for inverse in ifc_file.get_inverse(element):
            ifcopenshell.util.element.replace_attribute(inverse, element, new_element)
        ifc_file.remove(element)
        return new_element

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
            reader = csv.reader(f)
            headers = []
            for row in reader:
                if not headers:
                    headers = row
                    continue
                element = ifc_file.by_guid(row[0])
                if not element:
                    continue
                for i, value in enumerate(row):
                    if i == 0:
                        continue  # Skip GlobalId
                    element = IfcAttributeExtractor.set_element_key(ifc_file, element, headers[i], value)
        ifc_file.write(ifc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Exports IFC data to and from CSV")
    parser.add_argument("-i", "--ifc", type=str, required=True, help="The IFC file")
    parser.add_argument("-c", "--csv", type=str, default="data.csv", help="The CSV file to import from or export to")
    parser.add_argument("-q", "--query", type=str, default="", help='Specify a IFC query selector, such as ".IfcWall"')
    parser.add_argument("-a", "--arguments", nargs="+", help="Specify attributes that are part of the extract")
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
