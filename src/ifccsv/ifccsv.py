#!/usr/bin/env python3
# This can be packaged with `pyinstaller --onefile --clean --icon=icon.ico ifccsv.py`

import ifcopenshell
import csv
import lark
import argparse

class IfcSelectorParser():
    def __init__(self):
        self.ifc = ''
        self.file = None
        self.query = ''
        self.results = []

    def parse(self):
        self.file = ifcopenshell.open(self.ifc)
        l = lark.Lark('''start: query (lfunction query)*
                    query: selector | group
                    group: "(" query (lfunction query)* ")"
                    selector: (inverse_relationship)? guid_selector | (inverse_relationship)? class_selector
                    guid_selector: "#" /[0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$]{22}/
                    class_selector: "." WORD filter ?
                    filter: "[" filter_key (comparison filter_value)? "]"
                    filter_key: WORD | pset_or_qto
                    filter_value: ESCAPED_STRING
                    pset_or_qto: /[A-Za-z0-9_]+/ "." /[A-Za-z0-9_]+/
                    lfunction: and | or
                    inverse_relationship: types | contains_elements
                    types: "*"
                    contains_elements: "@"
                    and: "&"
                    or: "|"
                    comparison: contains | morethanequalto | lessthanequalto | equal | morethan | lessthan
                    contains: "*="
                    morethanequalto: ">="
                    lessthanequalto: "<"
                    equal: "="
                    morethan: ">"
                    lessthan: "<"

                    // Embed common.lark for packaging
                    DIGIT: "0".."9"
                    HEXDIGIT: "a".."f"|"A".."F"|DIGIT
                    INT: DIGIT+
                    SIGNED_INT: ["+"|"-"] INT
                    DECIMAL: INT "." INT? | "." INT
                    _EXP: ("e"|"E") SIGNED_INT
                    FLOAT: INT _EXP | DECIMAL _EXP?
                    SIGNED_FLOAT: ["+"|"-"] FLOAT
                    NUMBER: FLOAT | INT
                    SIGNED_NUMBER: ["+"|"-"] NUMBER
                    _STRING_INNER: /.*?/
                    _STRING_ESC_INNER: _STRING_INNER /(?<!\\\\)(\\\\\\\\)*?/
                    ESCAPED_STRING : "\\"" _STRING_ESC_INNER "\\""
                    LCASE_LETTER: "a".."z"
                    UCASE_LETTER: "A".."Z"
                    LETTER: UCASE_LETTER | LCASE_LETTER
                    WORD: LETTER+
                    CNAME: ("_"|LETTER) ("_"|LETTER|DIGIT)*
                    WS_INLINE: (" "|/\\t/)+
                    WS: /[ \\t\\f\\r\\n]/+
                    CR : /\\r/
                    LF : /\\n/
                    NEWLINE: (CR? LF)+

                    %ignore WS // Disregard spaces in text
                 ''')

        start = l.parse(self.query)
        self.results = self.get_group(start)

    def get_group(self, group):
        lfunction = None
        for child in group.children:
            if child.data == 'query':
                new_results = self.get_query(child)
                if not lfunction:
                    results = new_results
                elif lfunction == 'or':
                    results.extend(new_results)
                elif lfunction == 'and':
                    results = list(set(results).intersection(new_results))
                results = list(set(results))
            elif child.data == 'lfunction':
                lfunction = child.children[0].data
        return results

    def get_query(self, query):
        for child in query.children:
            if child.data == 'selector':
                return self.get_selector(child)
            elif child.data == 'group':
                return self.get_group(child)

    def get_selector(self, selector):
        if len(selector.children) == 1:
            inverse_relationship = None
            class_or_guid_selector = selector.children[0]
        else:
            inverse_relationship = selector.children[0]
            class_or_guid_selector = selector.children[1]

        if class_or_guid_selector.data == 'class_selector':
            results = self.get_class_selector(class_or_guid_selector)
        elif class_or_guid_selector.data == 'guid_selector':
            results = self.get_guid_selector(class_or_guid_selector)

        if not inverse_relationship:
            return results
        return self.parse_inverse_relationship(results, inverse_relationship.children[0].data)

    def parse_inverse_relationship(self, elements, inverse_relationship):
        results = []
        for element in elements:
            if inverse_relationship == 'types':
                if hasattr(element, 'Types') and element.Types:
                    results.extend(element.Types[0].RelatedObjects)
                elif hasattr(element, 'ObjectTypeOf') and element.ObjectTypeOf:
                    results.extend(element.ObjectTypeOf[0].RelatedObjects)
            elif inverse_relationship == 'contains_elements' \
                    and hasattr(element, 'ContainsElements'):
                for relationship in element.ContainsElements:
                    results.extend(relationship.RelatedElements)
        return results

    def get_class_selector(self, class_selector):
        elements = self.file.by_type(class_selector.children[0])
        if len(class_selector.children) > 1 \
                and class_selector.children[1].data == 'filter':
            return self.filter_elements(elements, class_selector.children[1])
        return elements

    def filter_elements(self, elements, filter_rule):
        results = []
        key = filter_rule.children[0].children[0]
        if not isinstance(key, str):
            key = key.children[0] + '.' + key.children[1]
        comparison = value = None
        if len(filter_rule.children) > 1:
            comparison = filter_rule.children[1].children[0].data
            value = filter_rule.children[2].children[0][1:-1]
        for element in elements:
            element_value = IfcAttributeExtractor.get_element_key(element, key)
            if not element_value:
                continue
            if not comparison \
                    or self.filter_element(element, element_value, comparison, value):
                results.append(element)
        return results

    def filter_element(self, element, element_value, comparison, value):
        if comparison == 'equal':
            return str(element_value) == value
        elif comparison == 'contains':
            return value in str(element_value)
        elif comparison == 'morethan':
            return element_value > float(value)
        elif comparison == 'lessthan':
            return element_value < float(value)
        elif comparison == 'morethanequalto':
            return element_value >= float(value)
        elif comparison == 'lessthanequalto':
            return element_value <= float(value)
        return False

    def get_guid_selector(self, guid_selector):
        return [self.file.by_id(guid_selector.children[0])]


class IfcAttributeExtractor():
    @staticmethod
    def get_element_key(element, key):
        if key == 'IfcClass':
            return element.is_a()
        elif hasattr(element, key):
            return getattr(element, key)
        elif '.' not in key:
            return None
        pset_name, prop = key.split('.', 1)
        pset = IfcAttributeExtractor.get_element_pset(element, pset_name)
        if pset:
            return IfcAttributeExtractor.get_pset_property(pset, prop)
        qto = IfcAttributeExtractor.get_element_qto(element, pset_name)
        if qto:
            return IfcAttributeExtractor.get_qto_property(qto, prop)
        return None

    @staticmethod
    def set_element_key(element, key, value):
        if hasattr(element, key):
            return setattr(element, key, value)
        if '.' not in key:
            return
        if key[0:3] == 'Qto':
            qto, prop = key.split('.', 1)
            qto = IfcAttributeExtractor.get_element_qto(element, qto_name)
            if qto:
                return IfcAttributeExtractor.set_qto_property(qto, prop, value)
        pset_name, prop = key.split('.', 1)
        pset = IfcAttributeExtractor.get_element_pset(element, pset_name)
        if pset:
            return IfcAttributeExtractor.set_pset_property(pset, prop, value)

    @staticmethod
    def get_element_qto(element, name):
        for relationship in element.IsDefinedBy:
            if relationship.is_a('IfcRelDefinesByProperties') \
                    and relationship.RelatingPropertyDefinition.is_a('IfcElementQuantity') \
                    and relationship.RelatingPropertyDefinition.Name == name:
                return relationship.RelatingPropertyDefinition

    @staticmethod
    def get_qto_property(qto, name):
        for prop in qto.Quantities:
            if prop.Name != name:
                continue
            return getattr(prop, prop.is_a()[len('IfcQuantity'):] + 'Value')

    @staticmethod
    def set_qto_property(qto, name, value):
        for prop in qto.Quantities:
            if prop.Name != name:
                continue
            setattr(prop, prop.is_a()[len('IfcQuantity'):] + 'Value', value)

    @staticmethod
    def get_element_pset(element, name):
        if element.is_a('IfcTypeObject'):
            if element.HasPropertySets:
                for pset in element.HasPropertySets:
                    if pset.is_a('IfcPropertySet') \
                        and pset.Name == name:
                        return pset
        else:
            for relationship in element.IsDefinedBy:
                if relationship.is_a('IfcRelDefinesByProperties') \
                    and relationship.RelatingPropertyDefinition.is_a('IfcPropertySet') \
                    and relationship.RelatingPropertyDefinition.Name == name:
                    return relationship.RelatingPropertyDefinition

    @staticmethod
    def get_pset_property(pset, name):
        for property in pset.HasProperties:
            if property.Name == name:
                return property.NominalValue.wrappedValue

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
                            property.NominalValue.wrappedValue = True if value.lower() in ['1', 't', 'true', 'yes', 'y', 'uh-huh'] else False


class IfcCsv():
    def __init__(self):
        self.results = []
        self.attributes = []
        self.output = ''

    def export(self, ifc_file, elements):
        self.ifc_file = ifc_file
        for element in elements:
            result = []
            if hasattr(element, 'GlobalId'):
                result.append(element.GlobalId)
            else:
                result.append(None)

            for index, attribute in enumerate(self.attributes):
                if '*' in attribute:
                    self.attributes.extend(self.get_wildcard_attributes(attribute))
                    del(self.attributes[index])

            for attribute in self.attributes:
                result.append(IfcAttributeExtractor.get_element_key(element, attribute))
            self.results.append(result)

        with open(self.output, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            header = ['GlobalId']
            header.extend(self.attributes)
            writer.writerow(header)
            for row in self.results:
                writer.writerow(row)

    def get_wildcard_attributes(self, attribute):
        results = set()
        pset_qto_name = attribute.split('.', 1)[0]
        for element in self.ifc_file.by_type('IfcPropertySet') + self.ifc_file.by_type('IfcElementQuantity'):
            print(element)
            if element.Name != pset_qto_name:
                continue
            if element.is_a('IfcPropertySet'):
                results.update([p.Name for p in element.HasProperties])
            else:
                results.update([p.Name for p in element.Quantities])
        return ['{}.{}'.format(pset_qto_name, n) for n in results]

    def Import(self, ifc):
        ifc_file = ifcopenshell.open(ifc)
        with open(self.output, newline='', encoding='utf-8') as f:
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
                        continue # Skip GlobalId
                    IfcAttributeExtractor.set_element_key(element, headers[i], value)
        ifc_file.write(ifc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Exports IFC data to and from CSV')
    parser.add_argument(
        '-i',
        '--ifc',
        type=str,
        required=True,
        help='The IFC file')
    parser.add_argument(
        '-c',
        '--csv',
        type=str,
        default='data.csv',
        help='The CSV file to import from or export to')
    parser.add_argument(
        '-q',
        '--query',
        type=str,
        default='',
        help='Specify a IFC query selector, such as ".IfcWall"')
    parser.add_argument(
        '-a',
        '--arguments',
        nargs='+',
        help='Specify attributes that are part of the extract')
    parser.add_argument(
        '--export',
        action='store_true',
        help='Export from IFC to CSV')
    parser.add_argument(
        '--import',
        action='store_true',
        help='Import from CSV to IFC')
    args = parser.parse_args()

    if args.export:
        ifc_selector_parser = IfcSelectorParser()
        ifc_selector_parser.ifc = args.ifc
        ifc_selector_parser.query = args.query
        ifc_selector_parser.parse()
        ifc_csv = IfcCsv()
        ifc_csv.output = args.csv
        ifc_csv.attributes = args.arguments if args.arguments else []
        ifc_csv.export(ifc_selector_parser.file, ifc_selector_parser.results)
    elif getattr(args, 'import'):
        ifc_csv = IfcCsv()
        ifc_csv.output = args.csv
        ifc_csv.Import(args.ifc)
