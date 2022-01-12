import os
import json
import ifcopenshell
import ifcopenshell.util.element


cwd = os.path.dirname(os.path.realpath(__file__))

ifc4_to_brick_map = {}

with open(os.path.join(cwd, "ifc4_to_brick.json")) as f:
    ifc4_to_brick_map = json.load(f)


def get_brick_type(element):
    result = None
    predefined_type = ifcopenshell.util.element.get_predefined_type(element)
    if predefined_type:
        result = ifc4_to_brick_map.get(f"{element.is_a()}.{predefined_type}", None)
    if not result:
        result = ifc4_to_brick_map.get(element.is_a(), None)
    if not result:
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            ifc_type_class = element_type.is_a().replace("Type", "")
            result = ifc4_to_brick_map.get(f"{ifc_type_class}.{predefined_type}", None)
            if not result:
                result = ifc4_to_brick_map.get(ifc_type_class, None)
    if result:
        return f"https://brickschema.org/schema/Brick#{result}"
    # We choose equipment as a generic fallback
    return f"https://brickschema.org/schema/Brick#Equipment"


def get_brick_elements(ifc_file):
    elements = set(ifc_file.by_type("IfcDistributionElement"))
    elements = elements.difference(ifc_file.by_type("IfcFlowSegment"))
    elements = elements.difference(ifc_file.by_type("IfcFlowFitting"))
    return elements
