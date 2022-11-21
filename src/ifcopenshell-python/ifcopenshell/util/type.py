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
    if schema == "IFC2X3":
        # There is no official mapping for IFC2X3 but this method gets us something that looks correct
        for element_type, elements in type_to_entity_map[schema].items():
            guessed_element = element_type[0:-len("Type")]
            if guessed_element in elements:
                type_to_entity_map[schema][element_type] = [e for e in elements if guessed_element in e]


def get_applicable_types(ifc_class, schema="IFC4"):
    return entity_to_type_map[schema].get(ifc_class, [])


def get_applicable_entities(ifc_type_class, schema="IFC4"):
    return type_to_entity_map[schema].get(ifc_type_class, [])
