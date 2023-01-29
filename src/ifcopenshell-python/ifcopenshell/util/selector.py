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

import ifcopenshell.util
import ifcopenshell.util.fm
import ifcopenshell.util.element
import lark


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
                    filter_key: WORD | pset_or_qto
                    filter_value: ESCAPED_STRING | SIGNED_FLOAT | SIGNED_INT | BOOLEAN | NULL
                    pset_or_qto: /[^\\W][^.=<>]*[^\\W]/ "." /[^\\W][^.=<>]*[^\\W]/
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
        return cls.parse_inverse_relationship(
            results, inverse_relationship.children[0].data
        )

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
                elements = [
                    e for e in cls.elements if e.is_a(class_selector.children[0])
                ]
        if (
            len(class_selector.children) > 1
            and class_selector.children[1].data == "filter"
        ):
            return cls.filter_elements(elements, class_selector.children[1])
        return elements

    @classmethod
    def filter_elements(cls, elements, filter_rule):
        results = []
        key = filter_rule.children[0].children[0]
        if not isinstance(key, str):
            key = key.children[0] + "." + key.children[1]
        comparison = value = None
        if len(filter_rule.children) > 1:
            comparison = filter_rule.children[1].children[0].data
            if comparison == "not":
                comparison += filter_rule.children[1].children[1].data
            token_type = filter_rule.children[2].children[0].type
            if token_type == "ESCAPED_STRING":
                value = str(filter_rule.children[2].children[0][1:-1])
            elif token_type == "SIGNED_INT":
                value = int(filter_rule.children[2].children[0])
            elif token_type == "SIGNED_FLOAT":
                value = float(filter_rule.children[2].children[0])
            elif token_type == "BOOLEAN":
                value = filter_rule.children[2].children[0].lower() == "true"
            elif token_type == "NULL":
                value = None
        for element in elements:
            element_value = cls.get_element_value(element, key, value)
            if element_value is None and value is not None and "not" not in comparison:
                continue
            if comparison and cls.filter_element(
                element, element_value, comparison, value
            ):
                results.append(element)
            elif not comparison and element_value:
                results.append(element)
        return results

    @classmethod
    def get_element_value(cls, element, key, value=None):
        if "." in key and key.split(".")[0] == "type":
            try:
                element = ifcopenshell.util.element.get_type(element)
                if not element:
                    return None
            except:
                return
            key = ".".join(key.split(".")[1:])
        elif "." in key and key.split(".")[0] == "material":
            try:
                material_definition = ifcopenshell.util.element.get_material(
                    element, should_skip_usage=True
                )
                if not material_definition:
                    return None
                key = ".".join(key.split(".")[1:])
                if value:
                    materials = [
                        inst
                        for inst in cls.file.traverse(material_definition)
                        if inst.is_a("IfcMaterial")
                    ]
                    for material in materials or []:
                        info = material.get_info()
                        if key in info and info[key] == value:
                            element = material
                element = material_definition 
                if not element:
                    return None
            except:
                return
        elif "." in key and key.split(".")[0] == "container":
            try:
                element = ifcopenshell.util.element.get_container(element)
                if not element:
                    return None
            except:
                return
            key = ".".join(key.split(".")[1:])
        info = element.get_info()
        if key in info:
            return info[key]
        elif "." in key:
            key_components = key.split(".")
            pset_name = key_components[0]
            prop = ".".join(key_components[1:])
            psets = ifcopenshell.util.element.get_psets(element)
            if pset_name in psets and prop in psets[pset_name]:
                return psets[pset_name][prop]

    @classmethod
    def filter_element(cls, element, element_value, comparison, value):
        if comparison.startswith("not"):
            return not cls.filter_element(element, element_value, comparison[3:], value)
        elif comparison == "equal" and isinstance(element_value, list):
            return value in element_value
        elif comparison == "equal":
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
