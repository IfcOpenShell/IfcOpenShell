import os
import json

cwd = os.path.dirname(os.path.realpath(__file__))

entity_to_type_map = {}
type_to_entity_map = {}

with open(os.path.join(cwd, "entity_to_type_map_2x3.json")) as f:
    entity_to_type_map["IFC2X3"] = json.load(f)

with open(os.path.join(cwd, "entity_to_type_map_4.json")) as f:
    entity_to_type_map["IFC4"] = json.load(f)

for schema in ["IFC2X3", "IFC4"]:
    type_to_entity_map[schema] = {}
    for element, element_types in entity_to_type_map[schema].items():
        for element_type in element_types:
            type_to_entity_map[schema].setdefault(element_type, []).append(element)
    # TODO: this method just fails for IFC2X3 because 2X3 type mapping is just so broken.
    # Uncomment the following line to see how bad it is.
    # print(type_to_entity_map[schema])


def get_applicable_types(ifc_class, schema="IFC4"):
    return entity_to_type_map[schema].get(ifc_class, [])


def get_applicable_entities(ifc_type_class, schema="IFC4"):
    return type_to_entity_map[schema].get(ifc_type_class, [])
