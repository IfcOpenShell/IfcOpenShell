# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021, 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

# See bug #1300. Dodgy quick results that we should rebuild later.
import json
import ifcopenshell
import ifcopenshell.util.schema


def generate_ifc4_entity_map(filepath, schema_name, manual_corrections={}):
    filepath = filepath
    schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(schema_name)

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
                type_class = schema.declaration_by_name(type_class).name()
                entity_to_type_map.setdefault(entity, []).append(type_class)
            line = fp.readline()

    for entity in manual_corrections:
        for ifc_type in manual_corrections[entity]:
            entity_to_type_map.setdefault(entity, []).append(ifc_type)

    # This type of hacky express parsing doesn't accommodate subtypes, so...
    def get_inherited_map(declaration):
        if not ifcopenshell.util.schema.is_a(declaration, "IfcObject"):
            return
        if declaration.supertype().name() in entity_to_type_map:
            return entity_to_type_map[declaration.supertype().name()]
        return get_inherited_map(declaration.supertype())

    for declaration in schema.declarations():
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

    check_all_types_are_mapped(schema, type_to_entity_map)
    schema_version = schema_name.lower().strip("ifc")
    with open(f"src/ifcopenshell-python/ifcopenshell/util/entity_to_type_map_{schema_version}.json", "w") as f:
        json.dump(entity_to_type_map, f, indent=4, sort_keys=True)

    return entity_to_type_map


# IFC2X3 doesn't seem to define this in EXPRESS, so let's just guess
# TODO: do we need some other way to validate 2x3 mapping?
def generate_ifc2x3_entity_map():
    entity_to_type_map = {}
    schema2x3 = ifcopenshell.ifcopenshell_wrapper.schema_by_name("IFC2X3")

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
            entity_to_type_map.setdefault(declaration.name(), []).append(type_declaration.name())
        for subtype in type_declaration.subtypes():
            if not subtype.is_abstract():
                entity_to_type_map.setdefault(declaration.name(), []).append(subtype.name())

    type_to_entity_map2x3 = {value: [key] for key in entity_to_type_map for value in entity_to_type_map[key]}
    check_all_types_are_mapped(schema2x3, type_to_entity_map2x3)

    with open("src/ifcopenshell-python/ifcopenshell/util/entity_to_type_map_2x3.json", "w") as f:
        json.dump(entity_to_type_map, f, indent=4, sort_keys=True)

    return entity_to_type_map


def check_all_types_are_mapped(schema, type_to_entity_map):
    def is_element_type(declaration):
        if not hasattr(declaration, "supertype"):
            return False
        return ifcopenshell.util.schema.is_a(declaration, "IfcElementType")

    for declaration in schema.declarations():
        type_name = declaration.name()
        if is_element_type(declaration) and type_name not in type_to_entity_map and not declaration.is_abstract():
            print(f"WARNING. {type_name} (not abstract) is not present in the mapping {schema.name()}.")


# specs: https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications
# ifc4x3 - https://github.com/buildingSMART/IFC4.3-html/releases/tag/sep-13-release (inside .zip)
# ifc4   - https://standards.buildingsmart.org/IFC/RELEASE/IFC4/FINAL/EXPRESS/IFC4.exp

# IfcCivilElement correction could be removed in the future releases of IFC
# if https://github.com/buildingSMART/IFC4.3.x-development/issues/583 is solved

ifc4x3_corrections = {
    "IfcCivilElement": ["IfcCivilElementType"],
    "IfcFurnishingElement": ["IfcFurnishingElementType"],
    "IfcDistributionElement": ["IfcDistributionElementType"],
    "IfcBuiltElement": ["IfcBuiltElementType"],
}
entity_to_type_map4x3 = generate_ifc4_entity_map("IFC4X3_TC1.exp", "ifc4x3", ifc4x3_corrections)

# some manual IFC4 corrections (more details in entity_to_type_map_4.json commits history)
ifc4_corrections = {
    "IfcDoor": ["IfcDoorStyle"],  # also will apply change to IfcDoorStandardCase
    "IfcWindow": ["IfcWindowStyle"],  # also will aply change to IfcWindowStandardCase
    "IfcCivilElement": ["IfcCivilElementType"],
    "IfcFurnishingElement": ["IfcFurnishingElementType"],
    "IfcDistributionElement": ["IfcDistributionElementType"],
}
#
entity_to_type_map4 = generate_ifc4_entity_map("IFC4.exp", "ifc4", ifc4_corrections)

entity_to_type_map2x3 = generate_ifc2x3_entity_map()
