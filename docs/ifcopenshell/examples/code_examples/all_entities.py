# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get all entities.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
for entity in model:
    # Prints the entity as it appears in the IFC file, e.g. #1=IfcPerson(...)
    print(entity)
    # A dictionary of its attributes, and its class
    print(entity.get_info())
    print(entity.is_a())
    # Not every entity has a Name attribute
    if hasattr(entity, "Name"):
        print(entity.Name)
# end::example

assert len(list(model)) == len(model.by_type("IfcRoot")) + len(
    [entity for entity in model if not entity.is_a("IfcRoot")]
)
