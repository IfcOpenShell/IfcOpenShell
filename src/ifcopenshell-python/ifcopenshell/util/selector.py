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
import numpy as np
import ifcopenshell.api.pset
import ifcopenshell.api.geometry
import ifcopenshell.util
import ifcopenshell.util.attribute
import ifcopenshell.util.fm
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.geolocation
import ifcopenshell.util.classification
import ifcopenshell.util.schema
import ifcopenshell.util.shape
import ifcopenshell.util.system
from decimal import Decimal
from typing import Optional, Any, Union, Iterable


filter_elements_grammar = lark.Lark(
    """start: filter_group
    filter_group: facet_list ("+" facet_list)*
    facet_list: facet ("," facet)*

    facet: instance | entity | attribute | type | material | query | classification | location | property | group | parent

    instance: not? globalid
    globalid: /[0-3][a-zA-Z0-9_$]{21}/
    entity: not? ifc_class
    attribute: attribute_name comparison value
    type: "type" comparison value
    material: "material" comparison value
    property: pset "." prop comparison value
    classification: "classification" comparison value
    location: "location" comparison value
    group: "group" comparison value
    parent: "parent" comparison value
    query: "query:" keys comparison value

    pset: quoted_string | regex_string | unquoted_string
    prop: quoted_string | regex_string | unquoted_string
    keys: quoted_string | unquoted_string

    attribute_name: /[A-Z]\\w+/
    ifc_class: /Ifc\\w+/

    value: special | quoted_string | regex_string | unquoted_string
    unquoted_string: /[^,.=><*!\\s]+/
    regex_string: "/" /[^\\/]+/ "/"
    quoted_string: ESCAPED_STRING

    special: null | true | false

    comparison: not? equals | morethanequalto | lessthanequalto | morethan | lessthan | not? contains
    not: "!"
    equals: "="
    morethanequalto: ">="
    lessthanequalto: "<="
    morethan: ">"
    lessthan: "<"
    contains: "*="
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
"""
)

get_element_grammar = lark.Lark(
    """start: keys

    keys: key ("." key)*
    key: quoted_string | regex_string | unquoted_string
    unquoted_string: /[^.=\\/\\s]+/
    regex_string: "/" /[^\\/]+/ "/"
    quoted_string: ESCAPED_STRING

    // Embed common.lark for packaging
    _STRING_INNER: /.*?/
    _STRING_ESC_INNER: _STRING_INNER /(?<!\\\\)(\\\\\\\\)*?/
    ESCAPED_STRING : "\\"" _STRING_ESC_INNER "\\""
    WS: /[ \\t\\f\\r\\n]/+

    %ignore WS // Disregard spaces in text
 """
)

format_grammar = lark.Lark(
    """start: function

    function: round | number | format_length | lower | upper | title | concat | substr | ESCAPED_STRING | NUMBER

    round: "round(" function "," NUMBER ")"
    number: "number(" function ["," ESCAPED_STRING ["," ESCAPED_STRING]] ")"
    format_length: metric_length | imperial_length
    metric_length: "metric_length(" function "," NUMBER "," NUMBER ")"
    imperial_length: "imperial_length(" function "," NUMBER ["," ESCAPED_STRING "," ESCAPED_STRING] ")"
    lower: "lower(" function ")"
    upper: "upper(" function ")"
    title: "title(" function ")"
    concat: "concat(" function ("," function)* ")"
    substr: "substr(" function "," SIGNED_INT ["," SIGNED_INT] ")"

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


class FormatTransformer(lark.Transformer):
    def start(self, args):
        return args[0]

    def function(self, args):
        return args[0]

    def ESCAPED_STRING(self, args):
        return args[1:-1].replace("\\", "")

    def NUMBER(self, args):
        return str(args)

    def lower(self, args):
        return str(args[0]).lower()

    def upper(self, args):
        return str(args[0]).upper()

    def title(self, args):
        return str(args[0]).title()

    def concat(self, args):
        return "".join(args)

    def substr(self, args):
        if len(args) == 3:
            if args[2] is None:
                return str(args[0])[int(args[1]) :]
            return str(args[0])[int(args[1]) : int(args[2])]
        elif len(args) == 2:
            return str(args[0])[int(args[1]) :]

    def round(self, args):
        value = Decimal(0.0 if args[0] == "None" else args[0] or 0.0)
        nearest = Decimal(args[1])
        result = round(value / nearest) * nearest
        if nearest % 1 == 0:
            return str(int(result))
        return str(result)

    def number(self, args):
        if isinstance(args[0], str):
            args[0] = float(args[0]) if "." in args[0] else int(args[0])
        if len(args) >= 3 and args[2]:
            return "{:,}".format(args[0]).replace(".", "*").replace(",", args[2]).replace("*", args[1])
        elif len(args) >= 2 and args[1]:
            return "{}".format(args[0]).replace(".", args[1])
        return "{:,}".format(args[0])

    def format_length(self, args):
        return args[0]

    def metric_length(self, args):
        value, precision, decimal_places = args
        return ifcopenshell.util.unit.format_length(
            float(value), float(precision), int(decimal_places), unit_system="metric"
        )

    def imperial_length(self, args):
        if len(args) == 2:
            input_unit, output_unit = "foot", "foot"
            value, precision = args
        else:
            value, precision, input_unit, output_unit = args
            input_unit = "inch" if input_unit == "inch" else "foot"
            output_unit = "inch" if output_unit == "inch" else "foot"

        return ifcopenshell.util.unit.format_length(
            float(value), int(precision), unit_system="imperial", input_unit=input_unit, output_unit=output_unit
        )


class GetElementTransformer(lark.Transformer):
    def start(self, args):
        return args[0]

    def keys(self, args):
        return args

    def key(self, args):
        return args[0]

    def quoted_string(self, args):
        return str(args[0])

    def regex_string(self, args):
        return re.compile(args[0])

    def unquoted_string(self, args):
        return str(args[0])

    def ESCAPED_STRING(self, args):
        return args[1:-1].replace("\\", "")


def format(query: str) -> str:
    return FormatTransformer().transform(format_grammar.parse(query))


def get_element_value(element: ifcopenshell.entity_instance, query: str) -> Any:
    keys: list[str] = GetElementTransformer().transform(get_element_grammar.parse(query))
    return _get_element_value(element, keys)


def _get_element_value(element: ifcopenshell.entity_instance, keys: list[str]) -> Any:
    value = element
    for key in keys:
        if value is None:
            return
        if key == "type":
            value = ifcopenshell.util.element.get_type(value)
        elif key in ("material", "mat"):
            value = ifcopenshell.util.element.get_material(value, should_skip_usage=True)
        elif key in ("materials", "mats"):
            value = ifcopenshell.util.element.get_materials(value)
        elif key == "profiles":
            value = ifcopenshell.util.shape.get_profiles(value)
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
        elif key == "space":
            value = ifcopenshell.util.element.get_container(value, ifc_class="IfcSpace")
        elif key == "storey":
            value = ifcopenshell.util.element.get_container(value, ifc_class="IfcBuildingStorey")
        elif key == "building":
            value = ifcopenshell.util.element.get_container(value, ifc_class="IfcBuilding")
        elif key == "site":
            value = ifcopenshell.util.element.get_container(value, ifc_class="IfcSite")
        elif key == "parent":
            value = ifcopenshell.util.element.get_parent(value)
        elif key in ("types", "occurrences"):
            value = ifcopenshell.util.element.get_types(value)
        elif key == "count":
            if isinstance(value, set):
                value = len(list(value))
            elif isinstance(value, (list, tuple)):
                value = len(value)
            else:
                value = int(1)
        elif key == "class":
            value = value.is_a()
        elif key == "predefined_type":
            value = ifcopenshell.util.element.get_predefined_type(value)
        elif key == "id":
            value = value.id()
        elif key == "classification":
            value = ifcopenshell.util.classification.get_references(value)
        elif key == "group":
            value = ifcopenshell.util.element.get_groups(value)
        elif key == "system":
            value = ifcopenshell.util.system.get_element_systems(value)
        elif key in ("x", "y", "z", "easting", "northing", "elevation") and hasattr(value, "ObjectPlacement"):
            if getattr(value, "ObjectPlacement", None):
                matrix = ifcopenshell.util.placement.get_local_placement(value.ObjectPlacement)
                xyz = matrix[:, 3][:3]
                if key in ("x", "y", "z"):
                    value = xyz["xyz".index(key)]
                else:
                    enh = ifcopenshell.util.geolocation.auto_xyz2enh(element.wrapped_data.file, *xyz)
                    value = enh[("easting", "northing", "elevation").index(key)]
            else:
                value = None
        elif isinstance(value, ifcopenshell.entity_instance):
            if key == "Name" and value.is_a("IfcMaterialLayerSet"):
                key = "LayerSetName"  # This oddity in the IFC spec is annoying so we account for it.

            if isinstance(key, re.Pattern):
                attribute = None  # Should we support regex attributes? Probably not for now.
            else:
                attribute = getattr(value, key, None)

            if attribute is not None:
                value = attribute
            else:
                # Try to extract pset
                if isinstance(key, re.Pattern):
                    psets = ifcopenshell.util.element.get_psets(value)
                    matching_psets = []
                    for pset_name, pset in psets.items():
                        if key.match(pset_name):
                            del pset["id"]
                            matching_psets.append(pset)
                    result = matching_psets or None
                    if result and len(result) == 1:
                        result = result[0]
                else:
                    result = ifcopenshell.util.element.get_pset(value, key)
                    if result:
                        del result["id"]

                value = result
        elif isinstance(value, dict):  # Such as from the result of a prior get_pset
            if isinstance(key, re.Pattern):
                results = []
                for prop_name, prop_value in value.items():
                    if key.match(prop_name):
                        if isinstance(prop_value, (list, tuple)):
                            results.extend(prop_value)
                        else:
                            results.append(prop_value)
                value = results or None
                if value and len(value) == 1:
                    value = value[0]
            else:
                value = value.get(key, None)
        elif isinstance(value, (list, tuple, set)):  # If we use regex
            if isinstance(key, str) and key.isnumeric():
                try:
                    value = value[int(key)]
                except IndexError:
                    return
            else:
                results = []
                for v in value:
                    subvalue = _get_element_value(v, [key])
                    if isinstance(subvalue, list):
                        results.extend(subvalue)
                    else:
                        results.append(subvalue)
                value = results
    return value


def filter_elements(
    ifc_file: ifcopenshell.file,
    query: str,
    elements: Optional[set[ifcopenshell.entity_instance]] = None,
    edit_in_place=False,
) -> set[ifcopenshell.entity_instance]:
    """
    Filter elements based on the provided `query`.

    :param ifc_file: The IFC file object
    :type ifc_file: ifcopenshell.file
    :param query: Query to execute
    :type query: str
    :param elements: Base set of IFC elements for the query. If not provided,
        all elements in the IFC are queried. If provided, the query will be
        applied to this set of elements, so the result will be a subset of
        elements.
    :type elements: set[ifcopenshell.entity_instance], optional
    :param edit_in_place: If `True`, mutate the provided `elements` in place. Defaults to `False`
    :type edit_in_place: bool
    :return: Set of filtered elements
    :rtype: set[ifcopenshell.entity_instance]

    Example:

    .. code:: python

        # Select all the walls and slabs in the file.
        elements = ifcopenshell.util.selector.filter_elements(ifc_file, "IfcWall, IfcSlab")

        # Add doors to the elements too.
        elements = ifcopenshell.util.selector.filter_elements(ifc_file, "IfcDoor", elements)

        # Changed our mind, exclude the slabs.
        elements = ifcopenshell.util.selector.filter_elements(ifc_file, "! IfcSlab", elements)

        # {#1=IfcWall(...), #2=IfcDoor(...)}
        print(elements)
    """
    if not query:
        return elements or set()
    if elements and not edit_in_place:
        elements = elements.copy()
    transformer = FacetTransformer(ifc_file, elements)
    transformer.transform(filter_elements_grammar.parse(query))
    return transformer.get_results()


class SetElementValueException(Exception): ...


def set_element_value(
    ifc_file: ifcopenshell.file,
    element: Union[ifcopenshell.entity_instance, Iterable[ifcopenshell.entity_instance], None],
    query: Union[str, list[str]],
    value: Any,
) -> None:
    original_element = element
    if isinstance(query, (list, tuple)):
        keys = query
    else:
        keys = GetElementTransformer().transform(get_element_grammar.parse(query))

    for i, key in enumerate(keys):
        if element is None:
            return
        if key == "type":
            element = ifcopenshell.util.element.get_type(element)
        elif key in ("material", "mat"):
            element = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
        elif key in ("materials", "mats"):
            element = ifcopenshell.util.element.get_materials(element)
        elif key == "styles":
            element = ifcopenshell.util.element.get_styles(element)
        elif key in ("item", "i"):
            if element.is_a("IfcMaterialLayerSet"):
                element = element.MaterialLayers
            elif element.is_a("IfcMaterialProfileSet"):
                element = element.MaterialProfiles
            elif element.is_a("IfcMaterialConstituentSet"):
                element = element.MaterialConstituents
        elif key == "container":
            element = ifcopenshell.util.element.get_container(element)
        elif key == "space":
            element = ifcopenshell.util.element.get_container(element, ifc_class="IfcSpace")
        elif key == "storey":
            element = ifcopenshell.util.element.get_container(element, ifc_class="IfcBuildingStorey")
        elif key == "building":
            element = ifcopenshell.util.element.get_container(element, ifc_class="IfcBuilding")
        elif key == "site":
            element = ifcopenshell.util.element.get_container(element, ifc_class="IfcSite")
        elif key == "parent":
            element = ifcopenshell.util.element.get_parent(element)
        elif key == "class":
            if element.is_a().lower() != value.lower():
                return ifcopenshell.util.schema.reassign_class(ifc_file, element, value)
            return
        elif key == "id":
            return
        elif key == "classification":
            element = ifcopenshell.util.classification.get_references(element)
        elif key in ("x", "y", "z", "easting", "northing", "elevation") and hasattr(element, "ObjectPlacement"):
            # TODO: add support
            if key in ("easting", "northing", "elevation"):
                return

            placement = element.ObjectPlacement
            if placement is None:
                matrix = np.eye(4)
            else:
                matrix = ifcopenshell.util.placement.get_local_placement(placement)

            # check if value is within tolerance to avoid api calls
            coord_i = "xyz".index(key)
            prev_value = matrix[coord_i][3]
            new_value = float(value) if value else 0.0
            if ifcopenshell.util.shape.is_x(new_value, prev_value):
                return

            matrix[coord_i][3] = new_value
            ifcopenshell.api.geometry.edit_object_placement(ifc_file, product=element, matrix=matrix, is_si=False)
            return
        elif isinstance(element, ifcopenshell.entity_instance):
            if key == "Name" and element.is_a("IfcMaterialLayerSet"):
                key = "LayerSetName"  # This oddity in the IFC spec is annoying so we account for it.

            if isinstance(key, str) and ((current_value := getattr(element, key, ...)) is not ...):
                # check if key is not last
                if len(keys) != i + 1:
                    element = current_value
                    continue

                if current_value == value:
                    return
                else:
                    # check if key is not last
                    try:
                        # Try our luck
                        return setattr(element, key, value)
                    except:
                        # Try to cast
                        data_type = ifcopenshell.util.attribute.get_primitive_type(
                            element.wrapped_data.declaration()
                            .as_entity()
                            .attribute_by_index(element.wrapped_data.get_argument_index(key))
                        )
                        if data_type == "string":
                            value = str(value)
                        elif data_type == "float":
                            value = float(value)
                        elif data_type == "integer":
                            value = int(value)
                        elif data_type == "boolean":
                            if value in ("True", "true", "TRUE", "Yes", "1"):
                                value = True
                            elif value in ("False", "false", "FALSE", "No", "0"):
                                value = False
                            else:
                                value = bool(value)
                        elif data_type == "entity":
                            value = ifc_file.by_guid(value)
                        if current_value == value:
                            return
                        return setattr(element, key, value)
            else:
                # Try to extract pset
                if isinstance(key, re.Pattern):
                    psets = ifcopenshell.util.element.get_psets(element)
                    matching_psets = []
                    for pset_name, pset in psets.items():
                        if key.match(pset_name):
                            matching_psets.append(pset)
                    result = matching_psets or None
                    if result and len(result) == 1:
                        result = result[0]
                else:
                    result = ifcopenshell.util.element.get_pset(element, key)

                    if value and not result and len(keys) == i + 2:  # The next key is the prop name
                        if "qto" in key.lower() or "quantity" in key.lower() or "quantities" in key.lower():
                            pset = ifcopenshell.api.pset.add_qto(ifc_file, product=element, name=key)
                        else:
                            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name=key)
                        result = {"id": pset.id()}

                element = result
        elif isinstance(element, dict):  # Such as from the result of a prior get_pset
            pset = ifc_file.by_id(element["id"])
            if isinstance(key, re.Pattern):
                for prop, prop_value in element.items():
                    if key.match(prop):
                        if pset.is_a("IfcPropertySet") and prop_value != value:
                            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={prop: value})
                        elif pset.is_a("IfcElementQuantity") and prop_value != float(value):
                            ifcopenshell.api.pset.edit_qto(ifc_file, qto=pset, properties={prop: float(value)})
            elif pset.is_a("IfcPropertySet") and element.get(key, None) != value:
                ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={key: value})
            elif pset.is_a("IfcElementQuantity"):
                try:
                    value = float(value)
                    if element.get(key, None) != value:
                        ifcopenshell.api.pset.edit_qto(ifc_file, qto=pset, properties={key: value})
                except:
                    pass
            return
        elif isinstance(element, (list, tuple, set)):  # If we use regex
            if key.isnumeric():
                try:
                    element = element[int(key)]
                except IndexError:
                    return
            else:
                for v in element:
                    set_element_value(ifc_file, v, keys[i:], value)
                return

    raise SetElementValueException(
        f"Failed to set value for element '{original_element}' with query '{query}' (invalid or unsupported query)."
    )


class FacetTransformer(lark.Transformer):
    def __init__(self, ifc_file: ifcopenshell.file, elements: Optional[set[ifcopenshell.entity_instance]] = None):
        self.file = ifc_file
        self.results = []
        if elements is None:
            self.base_elements = None
            self.elements = set()
        else:
            self.base_elements = elements.copy()
            self.elements = set()
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
        if self.base_elements is None:
            if args[0].data == "globalid":
                try:
                    self.elements.add(self.file.by_guid(args[0].children[0].value))
                except:
                    pass
            else:
                try:
                    self.elements.remove(self.file.by_guid(args[1].children[0].value))
                except:
                    pass
        else:
            if args[0].data == "globalid":
                self.elements |= {
                    e for e in self.base_elements if getattr(e, "GlobalId", None) == args[0].children[0].value
                }
            else:
                self.elements -= {
                    e for e in self.base_elements if getattr(e, "GlobalId", None) == args[1].children[0].value
                }

    def entity(self, args):
        if self.base_elements is None:
            if args[0].data == "ifc_class":
                try:
                    self.elements |= set(self.file.by_type(args[0].children[0].value))
                except:
                    pass
            else:
                try:
                    self.elements -= set(self.file.by_type(args[1].children[0].value))
                except:
                    pass
        else:
            if args[0].data == "ifc_class":
                self.elements |= {e for e in self.base_elements if e.is_a(args[0].children[0].value)}
            else:
                self.elements -= {e for e in self.base_elements if e.is_a(args[1].children[0].value)}

    def attribute(self, args):
        name, comparison, value = args
        name = name.children[0].value

        def filter_function(element):
            if name == "PredefinedType":
                element_value = ifcopenshell.util.element.get_predefined_type(element)
            else:
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
            if not container:
                container = ifcopenshell.util.element.get_aggregate(element)
            containers = self.get_container_tree(container)
            result = False if containers else None
            for container in containers:
                if self.compare(container.Name, "=", value):
                    result = True
            if result is not None:
                return result if comparison == "=" else not result
            return self.compare(None, comparison, value)

        self.elements = set(filter(filter_function, self.elements))

    def group(self, args):
        comparison, value = args

        def filter_function(element):
            result = False
            for rel in getattr(element, "HasAssignments", []):
                if rel.is_a("IfcRelAssignsToGroup") and rel.RelatingGroup:
                    if self.compare(rel.RelatingGroup.Name, "=", value):
                        result = True
            return result if comparison == "=" else not result

        self.elements = set(filter(filter_function, self.elements))

    def parent(self, args):
        comparison, value = args

        parents = set()
        for rel in self.file.by_type("IfcRelAggregates"):
            parent = rel.RelatingObject
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        for rel in self.file.by_type("IfcRelContainedInSpatialStructure"):
            parent = rel.RelatingStructure
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        for rel in self.file.by_type("IfcRelNests"):
            parent = rel.RelatingObject
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        for rel in self.file.by_type("IfcRelVoidsElement"):
            parent = rel.RelatingBuildingElement
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        for rel in self.file.by_type("IfcRelVoidsElement"):
            parent = rel.RelatingBuildingElement
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        for rel in self.file.by_type("IfcRelFillsElement"):
            parent = rel.RelatingOpeningElement
            if parent and self.compare(parent.Name, comparison, value):
                parents.add(parent)

        children = set()
        for parent in parents:
            children |= set(ifcopenshell.util.element.get_decomposition(parent))

        if comparison == "=":
            self.elements = self.elements & children
        else:
            self.elements -= children

    def query(self, args):
        keys, comparison, value = args

        def filter_function(element):
            return self.compare(get_element_value(element, keys), comparison, value)

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
        if args[0].data == "not":
            comparison = args[1].data
            is_not = "!"
        else:
            comparison = args[0].data
            is_not = ""

        return (
            is_not
            + {
                "equals": "=",
                "morethanequalto": ">=",
                "lessthanequalto": "<=",
                "morethan": ">",
                "lessthan": "<",
                "contains": "*=",
            }[comparison]
        )

    def keys(self, args):
        return self.value(args)

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
        if isinstance(element_value, (list, tuple)):
            return any(self.compare(ev, comparison, value) for ev in element_value)
        elif isinstance(value, str):
            try:
                if isinstance(element_value, int):
                    value = int(value)
                elif isinstance(element_value, float):
                    value = float(value)

                if isinstance(element_value, (int, float)):
                    operator = comparison.lstrip("!")
                    if operator == ">=":
                        result = element_value >= value
                    elif operator == "<=":
                        result = element_value <= value
                    elif operator == ">":
                        result = element_value > value
                    elif operator == "<":
                        result = element_value < value
                    else:
                        result = element_value == value  # Tolerance?
                elif isinstance(element_value, str):
                    operator = comparison.lstrip("!")
                    if operator == "*=":
                        result = value in element_value
                    else:
                        result = element_value == value
                else:
                    result = element_value == value
            except:
                # Potentially they are trying to compare a value which cannot
                # be legally casted to the element_value, or cannot use the
                # `in` or more / less than comparison operators.
                result = False
        elif isinstance(value, re.Pattern):
            result = bool(value.match(element_value)) if element_value is not None else False
        elif value in (None, True, False):
            result = element_value is value

        if comparison.startswith("!"):
            return not result
        return result
