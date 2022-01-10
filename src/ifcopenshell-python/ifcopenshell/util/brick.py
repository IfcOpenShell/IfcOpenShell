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
    return result
