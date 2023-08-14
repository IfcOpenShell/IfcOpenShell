# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import re
import lark
import ifcopenshell.util
import ifcopenshell.util.fm
import ifcopenshell.util.element
import ifcopenshell.util.classification


filter_elements_grammar = lark.Lark("""start: filter_group
    filter_group: facet_list ("+" facet_list)*
    facet_list: facet ("," facet)*

    facet: instance | entity | attribute | type | material | property | classification | location

    instance: not? globalid
    globalid: /[0-3][a-zA-Z0-9_$]{21}/
    entity: not? ifc_class
    attribute: attribute_name comparison value
    type: "type" comparison value
    material: "material" comparison value
    property: pset "." prop comparison value
    classification: "classification" comparison value
    location: "location" comparison value

    pset: quoted_string | unquoted_string | regex_string
    prop: quoted_string | unquoted_string | regex_string

    attribute_name: /[A-Z]\\w+/
    ifc_class: /Ifc\\w+/

    value: special | quoted_string | unquoted_string | regex_string
    unquoted_string: /[^.=\\s]+/
    quoted_string: ESCAPED_STRING
    regex_string: "/" /[^\\/]+/ "/"

    special: null | true | false

    comparison: not? equals
    not: "!"
    equals: "="
    null: "NULL"
    true: "TRUE"
    false: "FALSE"

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
""")

get_element_grammar = lark.Lark("""start: WORD | ESCAPED_STRING | keys_regex | keys_quoted | keys_simple
    keys_regex: "r" ESCAPED_STRING ("." ESCAPED_STRING)*
    keys_quoted: ESCAPED_STRING ("." ESCAPED_STRING)*
    keys_simple: /[^\\W][^.=<>!%*\\]]*/ ("." /[^\\W][^.=<>!%*\\]]*/)*

    // Embed common.lark for packaging
    _STRING_INNER: /.*?/
    _STRING_ESC_INNER: _STRING_INNER /(?<!\\\\)(\\\\\\\\)*?/
    ESCAPED_STRING : "\\"" _STRING_ESC_INNER "\\""
    LCASE_LETTER: "a".."z"
    UCASE_LETTER: "A".."Z"
    LETTER: UCASE_LETTER | LCASE_LETTER
    WORD: LETTER+
    WS: /[ \\t\\f\\r\\n]/+

    %ignore WS // Disregard spaces in text
 """)


def get_element_value(element, query):
    start = get_element_grammar.parse(query)
    filter_query = Selector.parse_filter_query(start.children[0])
    return Selector.get_element_value(element, filter_query["keys"], filter_query["is_regex"])


def filter_elements(ifc_file, query, elements=None):
    transformer = FacetTransformer(ifc_file, elements)
    transformer.transform(filter_elements_grammar.parse(query))
    return transformer.get_results()
    return transformer.elements


class FacetTransformer(lark.Transformer):
    def __init__(self, ifc_file, elements):
        self.file = ifc_file
        self.results = []
        self.elements = elements or set()
        self.container_parents = {}
        self.container_trees = {}

    def get_results(self):
        results = set()
        for r in self.results:
            results |= r
        return results

    def facet_list(self, args):
        if self.elements:
            self.results.append(self.elements)
            self.elements = set()

    def instance(self, args):
        if args[0].data == "globalid":
            self.elements.add(self.file.by_guid(args[0].children[0].value))
        else:
            self.elements.remove(self.file.by_guid(args[1].children[0].value))

    def entity(self, args):
        if args[0].data == "ifc_class":
            self.elements |= set(self.file.by_type(args[0].children[0].value))
        else:
            self.elements -= set(self.file.by_type(args[1].children[0].value))

    def attribute(self, args):
        name, comparison, value = args
        name = name.children[0].value

        def filter_function(element):
            element_value = getattr(element, name, None)
            return self.compare(element_value, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def type(self, args):
        comparison, value = args

        def filter_function(element):
            element_value = getattr(ifcopenshell.util.element.get_type(element), "Name", None)
            return self.compare(element_value, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def material(self, args):
        comparison, value = args

        def filter_function(element):
            materials = ifcopenshell.util.element.get_materials(element)
            result = False if materials else None
            for material in materials:
                if self.compare(material.Name, comparison, value):
                    result = True
                if self.compare(getattr(material, "Category", None), comparison, value):
                    result = True
            if result is not None:
                return result if comparison == "=" else not result
            return self.compare(None, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def property(self, args):
        pset, prop, comparison, value = args

        def filter_function(element):
            if isinstance(pset, str) and isinstance(prop, str):
                element_value = ifcopenshell.util.element.get_pset(element, pset, prop)
                return self.compare(element_value, comparison, value)
            elif isinstance(pset, str) and isinstance(prop, re.Pattern):
                element_props = ifcopenshell.util.element.get_pset(element, pset) or {}
                for element_prop, element_value in element_props.items():
                    if prop.match(element_prop):
                        return self.compare(element_value, comparison, value)
            elif isinstance(pset, re.Pattern):
                element_psets = ifcopenshell.util.element.get_psets(element)
                for element_pset, element_props in element_psets.items():
                    if not pset.match(element_pset):
                        continue
                    if isinstance(prop, str):
                        element_value = element_props.get(prop, None)
                        if element_value is not None:
                            return self.compare(element_value, comparison, value)
                    elif isinstance(prop, re.Pattern):
                        for element_prop, element_value in element_props.items():
                            if prop.match(element_prop):
                                return self.compare(element_value, comparison, value)
            return self.compare(None, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def classification(self, args):
        comparison, value = args

        def filter_function(element):
            references = ifcopenshell.util.classification.get_references(element)
            result = False if references else None
            for reference in references:
                if self.compare(reference.Name, comparison, value):
                    result = True
                if self.compare(
                    getattr(reference, "Identification", getattr(reference, "ItemReference", None)), comparison, value
                ):
                    result = True
            if result is not None:
                return result if comparison == "=" else not result
            return self.compare(None, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def location(self, args):
        comparison, value = args

        def filter_function(element):
            container = ifcopenshell.util.element.get_container(element)
            containers = self.get_container_tree(container)
            result = False if containers else None
            for container in containers:
                if self.compare(container.Name, comparison, value):
                    result = True
            if result is not None:
                return result if comparison == "=" else not result
            return self.compare(None, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def get_container_tree(self, container):
        tree = self.container_trees.get(container, None)
        if tree:
            return tree

        tree = []

        while container:
            if container.is_a("IfcProject"):
                break
            tree.append(container)
            container = ifcopenshell.util.element.get_aggregate(container)

        tree_copy = tree.copy()
        while tree_copy:
            self.container_trees[tree_copy.pop(0)] = tree_copy.copy()
        return tree

    def comparison(self, args):
        return "=" if args[0].data == "equals" else "!="

    def pset(self, args):
        return self.value(args)

    def prop(self, args):
        return self.value(args)

    def value(self, args):
        if args[0].data == "unquoted_string":
            return args[0].children[0].value
        elif args[0].data == "quoted_string":
            return args[0].children[0].value[1:-1].replace('\\"', '"')
        elif args[0].data == "regex_string":
            return re.compile(args[0].children[0].value)
        elif args[0].data == "special":
            if args[0].children[0].data == "null":
                return None
            elif args[0].children[0].data == "true":
                return True
            elif args[0].children[0].data == "false":
                return False

    def compare(self, element_value, comparison, value):
        if isinstance(value, str):
            if isinstance(element_value, int):
                value = int(value)
            elif isinstance(element_value, float):
                value = float(value)
            result = element_value == value
        elif isinstance(value, re.Pattern):
            result = bool(value.match(element_value))
        elif value in (None, True, False):
            result = element_value is value
        return result if comparison == "=" else not result


class Selector:
    @classmethod
    def parse(cls, ifc_file, query, elements=None):
        cls.file = ifc_file
        cls.elements = elements
        l = lark.Lark(
            """start: query (lfunction query)*
                    query: selector | group
                    group: "(" query (lfunction query)* ")"
                    selector: (inverse_relationship)? guid_selector | (inverse_relationship)? class_selector
                    guid_selector: "#" /[0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_$]{22}/
                    class_selector: "." WORD filter ?
                    filter: "[" filter_key (comparison filter_value)? "]"
                    filter_key: WORD | ESCAPED_STRING | keys_regex | keys_quoted | keys_simple
                    filter_value: filter_regex | ESCAPED_STRING | SIGNED_FLOAT | SIGNED_INT | BOOLEAN | NULL
                    filter_regex: "r" ESCAPED_STRING
                    keys_regex: "r" ESCAPED_STRING ("." ESCAPED_STRING)*
                    keys_quoted: ESCAPED_STRING ("." ESCAPED_STRING)*
                    keys_simple: /[^\\W][^.=<>!%*\\]]*/ ("." /[^\\W][^.=<>!%*\\]]*/)*
                    lfunction: and | or
                    inverse_relationship: types | decomposed_by | bounded_by | grouped_by
                    types: "*"
                    decomposed_by: "@"
                    bounded_by: "@@"
                    grouped_by: "@@@"
                    and: "&"
                    or: "|"
                    not: "!"
                    comparison: (not)* (oneof | contains | morethanequalto | lessthanequalto | equal | morethan | lessthan)
                    oneof: "%="
                    contains: "*="
                    morethanequalto: ">="
                    lessthanequalto: "<="
                    equal: "="
                    morethan: ">"
                    lessthan: "<"
                    BOOLEAN: "TRUE" | "FALSE" | "true" | "false"| "True" | "False"
                    NULL: "NULL"

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
                 """
        )

        start = l.parse(query)
        return cls.get_group(start)

    @classmethod
    def get_group(cls, group):
        lfunction = None
        for child in group.children:
            if child.data == "query":
                new_results = cls.get_query(child)
                if not lfunction:
                    results = new_results
                elif lfunction == "or":
                    results.extend(new_results)
                elif lfunction == "and":
                    results = list(set(results).intersection(new_results))
                results = list(set(results))
            elif child.data == "lfunction":
                lfunction = child.children[0].data
        return results

    @classmethod
    def get_query(cls, query):
        for child in query.children:
            if child.data == "selector":
                return cls.get_selector(child)
            elif child.data == "group":
                return cls.get_group(child)

    @classmethod
    def get_selector(cls, selector):
        if len(selector.children) == 1:
            inverse_relationship = None
            class_or_guid_selector = selector.children[0]
        else:
            inverse_relationship = selector.children[0]
            class_or_guid_selector = selector.children[1]

        if class_or_guid_selector.data == "class_selector":
            results = cls.get_class_selector(class_or_guid_selector)
        elif class_or_guid_selector.data == "guid_selector":
            results = cls.get_guid_selector(class_or_guid_selector)

        if not inverse_relationship:
            return results
        return cls.parse_inverse_relationship(results, inverse_relationship.children[0].data)

    @classmethod
    def parse_inverse_relationship(cls, elements, inverse_relationship):
        results = []
        for element in elements:
            if inverse_relationship == "types":
                if hasattr(element, "Types") and element.Types:
                    results.extend(element.Types[0].RelatedObjects)
                elif hasattr(element, "ObjectTypeOf") and element.ObjectTypeOf:
                    results.extend(element.ObjectTypeOf[0].RelatedObjects)
            elif inverse_relationship == "decomposed_by":
                results.extend(ifcopenshell.util.element.get_decomposition(element))
            elif inverse_relationship == "grouped_by":
                results.extend(ifcopenshell.util.element.get_grouped_by(element))
            elif inverse_relationship == "bounded_by" and hasattr(element, "BoundedBy"):
                for relationship in element.BoundedBy:
                    results.append(relationship.RelatedBuildingElement)
        return results

    @classmethod
    def get_class_selector(cls, class_selector):
        if class_selector.children[0] == "COBie":
            elements = ifcopenshell.util.fm.get_cobie_components(cls.file)
        elif class_selector.children[0] == "COBieType":
            elements = ifcopenshell.util.fm.get_cobie_types(cls.file)
        elif class_selector.children[0] == "FMHEM":
            elements = ifcopenshell.util.fm.get_fmhem_types(cls.file)
        else:
            if cls.elements is None:
                elements = cls.file.by_type(class_selector.children[0])
            else:
                elements = [e for e in cls.elements if e.is_a(class_selector.children[0])]
        if len(class_selector.children) > 1 and class_selector.children[1].data == "filter":
            return cls.filter_elements(elements, class_selector.children[1])
        return elements

    @classmethod
    def filter_elements(cls, elements, filter_rule):
        results = []
        filter_query = cls.parse_filter_query(filter_rule.children[0].children[0])
        comparison = value = None
        if len(filter_rule.children) > 1:
            comparison = filter_rule.children[1].children[0].data
            if comparison == "not":
                comparison += filter_rule.children[1].children[1].data
            filter_value = filter_rule.children[2].children[0]
            if isinstance(filter_value, lark.Tree):
                is_regex = True
                token_type = filter_value.data
            else:
                is_regex = False
                token_type = filter_value.type
            if token_type == "filter_regex":
                value = str(filter_value.children[0][1:-1])
            elif token_type == "ESCAPED_STRING":
                value = str(filter_value[1:-1])
            elif token_type == "SIGNED_INT":
                value = int(filter_value)
            elif token_type == "SIGNED_FLOAT":
                value = float(filter_value)
            elif token_type == "BOOLEAN":
                value = filter_value.lower() == "true"
            elif token_type == "NULL":
                value = None
        for element in elements:
            element_value = cls.get_element_value(element, filter_query["keys"], is_regex=filter_query["is_regex"])
            if element_value is None and value is not None and "not" not in comparison:
                continue
            if comparison and cls.filter_element(element, element_value, comparison, value, is_regex=is_regex):
                results.append(element)
            elif not comparison and element_value:
                results.append(element)
        return results

    @classmethod
    def parse_filter_query(cls, filter_query):
        keys = filter_query
        is_regex = False
        if isinstance(keys, str):
            keys = [keys]
        elif keys.data == "keys_regex":
            is_regex = True
            keys = [k[1:-1].replace('\\"', '"') for k in keys.children]
        elif keys.data == "keys_quoted":
            keys = [k[1:-1].replace('\\"', '"') for k in keys.children]
        elif keys.data == "keys_simple":
            keys = keys.children
        return {"keys": keys, "is_regex": is_regex}

    @classmethod
    def get_element_value(cls, element, keys, is_regex=False):
        value = element
        for key in keys:
            key = key.strip()
            if value is None:
                return
            if key == "type":
                value = ifcopenshell.util.element.get_type(value)
            elif key in ("material", "mat"):
                value = ifcopenshell.util.element.get_material(value, should_skip_usage=True)
            elif key in ("materials", "mats"):
                value = ifcopenshell.util.element.get_materials(value)
            elif key == "styles":
                value = ifcopenshell.util.element.get_styles(value)
            elif key in ("item", "i"):
                if value.is_a("IfcMaterialLayerSet"):
                    value = value.MaterialLayers
                elif value.is_a("IfcMaterialProfileSet"):
                    value = value.MaterialProfiles
                elif value.is_a("IfcMaterialConstituentSet"):
                    value = value.MaterialConstituents
            elif key == "container":
                value = ifcopenshell.util.element.get_container(value)
            elif key == "class":
                value = value.is_a()
            elif key == "id":
                value = value.id()
            elif isinstance(value, ifcopenshell.entity_instance):
                if key == "Name" and value.is_a("IfcMaterialLayerSet"):
                    key = "LayerSetName"  # This oddity in the IFC spec is annoying so we account for it.

                attribute = getattr(value, key, None)

                if attribute is not None:
                    value = attribute
                else:
                    # Try to extract pset
                    if is_regex:
                        psets = ifcopenshell.util.element.get_psets(value)
                        matching_psets = []
                        for pset_name, pset in psets.items():
                            if re.match(key, pset_name):
                                matching_psets.append(pset)
                        result = matching_psets or None
                    else:
                        result = ifcopenshell.util.element.get_pset(value, key)

                    value = result
            elif isinstance(value, dict):  # Such as from the result of a prior get_pset
                if is_regex:
                    results = []
                    for prop_name, prop_value in value.items():
                        if re.match(key, prop_name):
                            if isinstance(prop_value, (list, tuple)):
                                results.extend(prop_value)
                            else:
                                results.append(prop_value)
                    value = results
                else:
                    value = value.get(key, None)
            elif isinstance(value, (list, tuple)):  # If we use regex
                if key.isnumeric():
                    try:
                        value = value[int(key)]
                    except IndexError:
                        return
                else:
                    results = []
                    for v in value:
                        subvalue = cls.get_element_value(v, [key], is_regex=is_regex)
                        if isinstance(subvalue, list):
                            results.extend(subvalue)
                        else:
                            results.append(subvalue)
                    value = results
        return value

    @classmethod
    def filter_element(cls, element, element_value, comparison, value, is_regex=False):
        if comparison.startswith("not"):
            return not cls.filter_element(element, element_value, comparison[3:], value, is_regex=is_regex)
        elif comparison == "equal" and isinstance(element_value, list):
            if is_regex:
                for element_v in element_value:
                    if re.match(value, element_v):
                        return True
                return False
            return value in element_value
        elif comparison == "equal":
            if is_regex:
                return bool(re.match(value, element_value))
            return element_value == value
        elif comparison == "contains" and isinstance(element_value, list):
            return bool([ev for ev in element_value if value in str(ev)])
        elif comparison == "contains":
            return value in str(element_value)
        elif comparison == "morethan":
            return element_value > value
        elif comparison == "lessthan":
            return element_value < value
        elif comparison == "morethanequalto":
            return element_value >= value
        elif comparison == "lessthanequalto":
            return element_value <= value
        elif comparison == "oneof":
            return element_value in value.split(",")
        return False

    @classmethod
    def get_guid_selector(cls, guid_selector):
        return [cls.file.by_id(guid_selector.children[0])]
