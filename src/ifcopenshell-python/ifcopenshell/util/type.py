# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021, 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import os
import json
import ifcopenshell.util.schema
from typing import List

cwd = os.path.dirname(os.path.realpath(__file__))

entity_to_type_map = {}
type_to_entity_map = {}

mapped_schemas = {
    "IFC2X3": "entity_to_type_map_2x3.json",
    "IFC4": "entity_to_type_map_4.json",
    "IFC4X3": "entity_to_type_map_4x3.json",
}
for schema in mapped_schemas:
    # load entity maps from json
    schema_path = os.path.join(cwd, mapped_schemas[schema])
    with open(schema_path) as f:
        entity_to_type_map[schema] = json.load(f)

    # create type_to_entity map
    type_to_entity_map[schema] = {}
    for element, element_types in entity_to_type_map[schema].items():
        for element_type in element_types:
            type_to_entity_map[schema].setdefault(element_type, []).append(element)

    if schema == "IFC2X3":
        # There is no official mapping for IFC2X3 but this method gets us something that looks correct
        for element_type, elements in type_to_entity_map[schema].items():
            # need to take both Type (4 symbols) and Style (5 symbols) into account
            guessed_element = element_type[:-5] if element_type.endswith("Style") else element_type[:-4]
            if guessed_element in elements:
                type_to_entity_map[schema][element_type] = [e for e in elements if guessed_element in e]


def get_applicable_types(ifc_class: str, schema="IFC4") -> List[str]:
    schema = ifcopenshell.util.schema.get_fallback_schema(schema.upper())
    return entity_to_type_map[schema].get(ifc_class, [])


def get_applicable_entities(ifc_type_class: str, schema="IFC4") -> List[str]:
    schema = ifcopenshell.util.schema.get_fallback_schema(schema.upper())
    return type_to_entity_map[schema].get(ifc_type_class, [])
