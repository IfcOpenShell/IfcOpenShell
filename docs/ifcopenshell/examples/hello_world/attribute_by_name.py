# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): reading attributes by name.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(wall.GlobalId)
print(wall.Name)
# end::example

assert wall.GlobalId == "0EI0MSHbX9gg8Fxwar7lL8"
