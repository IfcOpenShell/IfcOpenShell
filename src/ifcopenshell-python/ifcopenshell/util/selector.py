import ifcopenshell.util
import ifcopenshell.util.element
import lark

cobie_type_assets = [
    "IfcDoorStyle",
    "IfcBuildingElementProxyType",
    "IfcChimneyType",
    "IfcCoveringType",
    "IfcDoorType",
    "IfcFootingType",
    "IfcPileType",
    "IfcRoofType",
    "IfcShadingDeviceType",
    "IfcWindowType",
    "IfcDistributionControlElementType",
    "IfcDistributionChamberElementType",
    "IfcEnergyConversionDeviceType",
    "IfcFlowControllerType",
    "IfcFlowMovingDeviceType",
    "IfcFlowStorageDeviceType",
    "IfcFlowTerminalType",
    "IfcFlowTreatmentDeviceType",
    "IfcElementAssemblyType",
    "IfcBuildingElementPartType",
    "IfcDiscreteAccessoryType",
    "IfcMechanicalFastenerType",
    "IfcReinforcingElementType",
    "IfcVibrationIsolatorType",
    "IfcFurnishingElementType",
    "IfcGeographicElementType",
    "IfcTransportElementType",
    "IfcSpatialZoneType",
    "IfcWindowStyle",
]
cobie_component_assets = [
    "IfcBuildingElementProxy",
    "IfcChimney",
    "IfcCovering",
    "IfcDoor",
    "IfcShadingDevice",
    "IfcWindow",
    "IfcDistributionControlElement",
    "IfcDistributionChamberElement",
    "IfcEnergyConversionDevice",
    "IfcFlowController",
    "IfcFlowMovingDevice",
    "IfcFlowStorageDevice",
    "IfcFlowTerminal",
    "IfcFlowTreatmentDevice",
    "IfcDiscreteAccessory",
    "IfcTendon",
    "IfcTendonAnchor",
    "IfcVibrationIsolator",
    "IfcFurnishingElement",
    "IfcGeographicElement",
    "IfcTransportElement",
]


class Selector:
    def parse(self, ifc_file, query):
        self.file = ifc_file

        l = lark.Lark(
            """start: query (lfunction query)*
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
                 """
        )

        start = l.parse(query)
        return self.get_group(start)

    def get_group(self, group):
        lfunction = None
        for child in group.children:
            if child.data == "query":
                new_results = self.get_query(child)
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

    def get_query(self, query):
        for child in query.children:
            if child.data == "selector":
                return self.get_selector(child)
            elif child.data == "group":
                return self.get_group(child)

    def get_selector(self, selector):
        if len(selector.children) == 1:
            inverse_relationship = None
            class_or_guid_selector = selector.children[0]
        else:
            inverse_relationship = selector.children[0]
            class_or_guid_selector = selector.children[1]

        if class_or_guid_selector.data == "class_selector":
            results = self.get_class_selector(class_or_guid_selector)
        elif class_or_guid_selector.data == "guid_selector":
            results = self.get_guid_selector(class_or_guid_selector)

        if not inverse_relationship:
            return results
        return self.parse_inverse_relationship(results, inverse_relationship.children[0].data)

    def parse_inverse_relationship(self, elements, inverse_relationship):
        results = []
        for element in elements:
            if inverse_relationship == "types":
                if hasattr(element, "Types") and element.Types:
                    results.extend(element.Types[0].RelatedObjects)
                elif hasattr(element, "ObjectTypeOf") and element.ObjectTypeOf:
                    results.extend(element.ObjectTypeOf[0].RelatedObjects)
            elif inverse_relationship == "contains_elements" and hasattr(element, "ContainsElements"):
                for relationship in element.ContainsElements:
                    results.extend(relationship.RelatedElements)
        return results

    def get_class_selector(self, class_selector):
        if class_selector.children[0] == "COBie":
            elements = []
            for ifc_class in cobie_component_assets:
                try:
                    elements += self.file.by_type(ifc_class)
                except:
                    pass
        elif class_selector.children[0] == "COBieType":
            elements = []
            for ifc_class in cobie_type_assets:
                try:
                    elements += self.file.by_type(ifc_class)
                except:
                    pass
        else:
            elements = self.file.by_type(class_selector.children[0])
        if len(class_selector.children) > 1 and class_selector.children[1].data == "filter":
            return self.filter_elements(elements, class_selector.children[1])
        return elements

    def filter_elements(self, elements, filter_rule):
        results = []
        key = filter_rule.children[0].children[0]
        if not isinstance(key, str):
            key = key.children[0] + "." + key.children[1]
        comparison = value = None
        if len(filter_rule.children) > 1:
            comparison = filter_rule.children[1].children[0].data
            value = filter_rule.children[2].children[0][1:-1]
        for element in elements:
            element_value = self.get_element_value(element, key)
            if element_value is None:
                continue
            if not comparison or self.filter_element(element, element_value, comparison, value):
                results.append(element)
        return results

    def get_element_value(self, element, key):
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
                element = ifcopenshell.util.element.get_material(element)
                if not element:
                    return None
            except:
                return
            key = ".".join(key.split(".")[1:])
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
            pset_name, prop = key.split(".")
            psets = ifcopenshell.util.element.get_psets(element)
            if pset_name in psets and prop in psets[pset_name]:
                return psets[pset_name][prop]

    def filter_element(self, element, element_value, comparison, value):
        if comparison == "equal":
            return str(element_value) == value
        elif comparison == "contains":
            return value in str(element_value)
        elif comparison == "morethan":
            return element_value > float(value)
        elif comparison == "lessthan":
            return element_value < float(value)
        elif comparison == "morethanequalto":
            return element_value >= float(value)
        elif comparison == "lessthanequalto":
            return element_value <= float(value)
        return False

    def get_guid_selector(self, guid_selector):
        return [self.file.by_id(guid_selector.children[0])]
