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
                    selector: guid_selector | class_selector
                    guid_selector: "#" /[0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$]{22}/
                    class_selector: "." WORD filter ?
                    filter: "[" filter_key (comparison filter_value)? "]"
                    filter_key: WORD | pset_or_qto
                    filter_value: ESCAPED_STRING
                    pset_or_qto: /[A-Za-z0-9_]+/ "." /[A-Za-z0-9_]+/
                    lfunction: and | or
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
        for child in selector.children:
            if child.data == 'class_selector':
                return self.get_class_selector(child)
            elif child.data == 'guid_selector':
                return self.get_guid_selector(child)

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
        if hasattr(element, key):
            return getattr(element, key)
        elif '.' not in key:
            return None
        elif key[0:3] == 'Qto':
            qto_name, prop = key.split('.')
            qto = IfcAttributeExtractor.get_element_qto(element, qto_name)
            if qto:
                return IfcAttributeExtractor.get_qto_property(qto, prop)
        else:
            pset_name, prop = key.split('.')
            pset = IfcAttributeExtractor.get_element_pset(element, pset_name)
            if pset:
                return IfcAttributeExtractor.get_pset_property(pset, prop)
        return None

    @staticmethod
    def set_element_key(element, key, value):
        if '.' not in key \
                and hasattr(element, key):
            setattr(element, key, value)
        elif key[0:3] == 'Qto':
            qto, prop = key.split('.')
            qto = IfcAttributeExtractor.get_element_qto(element, qto_name)
            if qto:
                IfcAttributeExtractor.set_qto_property(qto, prop, value)
        else:
            pset_name, prop = key.split('.')
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
    def set_qto_property(qto, name, avlue):
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
                property.NominalValue.wrappedValue = value


class IfcCsv():
    def __init__(self):
        self.results = []
        self.attributes = []
        self.output = ''

    def export(self, elements):
        for element in elements:
            result = []
            if hasattr(element, 'GlobalId'):
                result.append(element.GlobalId)
            else:
                result.append(None)
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
    ifc_csv.export(ifc_selector_parser.results)
elif getattr(args, 'import'):
    ifc_csv = IfcCsv()
    ifc_csv.output = args.csv
    ifc_csv.Import(args.ifc)
