# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

# See bug #1300. Dodgy quick results that we should rebuild later.
import json
import ifcopenshell
import ifcopenshell.util.schema


filepath = "IFC4.exp"
schema2x3 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC2X3")
schema4 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC4")

entity_to_type_map = {}

entity = None
is_in_where_rule = False

with open(filepath) as fp:
    line = fp.readline()
    while line:
        if "ENTITY " in line:
            entity = line[len("ENTITY ") : -1]
        elif "END_ENTITY" in line:
            is_in_where_rule = False
        elif entity and ("CorrectTypeAssigned" in line or "CorrectStyleAssigned" in line):
            is_in_where_rule = True
        elif entity and is_in_where_rule and "IN TYPEOF" in line and "RelatingType" in line:
            type_class = line.split("'")[1].split(".")[1]
            if type_class == "IFCTRANFORMERTYPE":
                # Fix typo in schema
                type_class = "IFCTRANSFORMERTYPE"
            type_class = schema4.declaration_by_name(type_class).name()
            entity_to_type_map.setdefault(entity, []).append(type_class)
        line = fp.readline()

# This type of hacky express parsing doesn't accommodate subtypes, so...


def get_inherited_map(declaration):
    if not ifcopenshell.util.schema.is_a(declaration, "IfcObject"):
        return
    if declaration.supertype().name() in entity_to_type_map:
        return entity_to_type_map[declaration.supertype().name()]
    return get_inherited_map(declaration.supertype())


for declaration in schema4.declarations():
    if not hasattr(declaration, "supertype"):
        continue
    if not ifcopenshell.util.schema.is_a(declaration, "IfcObject"):
        continue
    if declaration.is_abstract():
        continue
    if declaration.name() in entity_to_type_map:
        continue
    inherited_map = get_inherited_map(declaration)
    if inherited_map:
        entity_to_type_map[declaration.name()] = inherited_map

type_to_entity_map = {value: [key] for key in entity_to_type_map for value in entity_to_type_map[key]}

# IFC2X3 doesn't seem to define this in EXPRESS, so let's just guess

entity_to_type_map2x3 = {}


def guess_type_declaration(declaration):
    if not ifcopenshell.util.schema.is_a(declaration, "IfcObject"):
        return

    try:
        type_declaration = schema2x3.declaration_by_name(declaration.name() + "Type")
        return type_declaration
    except:
        pass

    try:
        type_declaration = schema2x3.declaration_by_name(declaration.name() + "Style")
        return type_declaration
    except:
        pass

    return guess_type_declaration(declaration.supertype())


for declaration in schema2x3.declarations():
    if not hasattr(declaration, "supertype"):
        continue
    type_declaration = guess_type_declaration(declaration)
    if not type_declaration:
        continue
    if not type_declaration.is_abstract():
        entity_to_type_map2x3.setdefault(declaration.name(), []).append(type_declaration.name())
    for subtype in type_declaration.subtypes():
        if not subtype.is_abstract():
            entity_to_type_map2x3.setdefault(declaration.name(), []).append(subtype.name())

type_to_entity_map2x3 = {value: [key] for key in entity_to_type_map2x3 for value in entity_to_type_map2x3[key]}


with open("entity_to_type_map_4.json", "w") as f:
    json.dump(entity_to_type_map, f, indent=4)


with open("entity_to_type_map_2x3.json", "w") as f:
    json.dump(entity_to_type_map2x3, f, indent=4)
