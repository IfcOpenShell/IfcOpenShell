import os
import json

cwd = os.path.dirname(os.path.realpath(__file__))

entity_to_type_map = {}
type_to_entity_map = {}

with open(os.path.join(cwd, "entity_to_type_map_2x3.json")) as f:
    entity_to_type_map["IFC2X3"] = json.load(f)

with open(os.path.join(cwd, "entity_to_type_map_4.json")) as f:
    entity_to_type_map["IFC4"] = json.load(f)

type_to_entity_map["IFC2X3"] = {
    value: [key] for key in entity_to_type_map["IFC2X3"] for value in entity_to_type_map["IFC2X3"][key]
}

type_to_entity_map["IFC4"] = {
    value: [key] for key in entity_to_type_map["IFC4"] for value in entity_to_type_map["IFC4"][key]
}


def get_applicable_types(ifc_class, schema="IFC4"):
    return entity_to_type_map[schema].get(ifc_class, [])


def get_applicable_entities(ifc_type_class, schema="IFC4"):
    return type_to_entity_map[schema].get(ifc_type_class, [])
