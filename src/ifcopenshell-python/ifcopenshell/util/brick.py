import os
import json


cwd = os.path.dirname(os.path.realpath(__file__))

ifc4_to_brick_map = {}

with open(os.path.join(cwd, "ifc4_to_brick.json")) as f:
    ifc4_to_brick_map = json.load(f)


def get_brick_type(element):
    predefined_type = getattr(element, "PredefinedType", None)
    result = None
    if predefined_type:
        result = ifc4_to_brick_map.get(f"{element.is_a()}.{predefined_type}", None)
    if not result:
        result = ifc4_to_brick_map.get(element.is_a(), None)
    if result:
        return f"https://brickschema.org/schema/Brick#{result}"


def get_brick_elements(ifc_file):
    classes = {c.split(".")[0] for c in ifc4_to_brick_map.keys()}
    elements = []
    for ifc_class in classes:
        try:
            elements += ifc_file.by_type(ifc_class)
        except:
            pass
    return elements
