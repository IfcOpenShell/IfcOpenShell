# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get all wall types.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
for wall_type in model.by_type("IfcWallType"):
    print("The wall type element is", wall_type)
    print("The name of the wall type is", wall_type.Name)
# end::example
