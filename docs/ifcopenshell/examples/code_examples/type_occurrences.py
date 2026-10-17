# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get all door occurrences of a type.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.element

for door_type in model.by_type("IfcDoorType"):
    print("The door type is", door_type.Name)
    doors = ifcopenshell.util.element.get_types(door_type)
    print(f"There are {len(doors)} of this type")
    for door in doors:
        print("The door name is", door.Name)
# end::example

assert any(ifcopenshell.util.element.get_types(door_type) for door_type in model.by_type("IfcDoorType"))
