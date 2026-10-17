# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): reading attributes by position.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(wall[0])  # The first attribute is the GlobalId
print(wall[2])  # The third attribute is the Name
# end::example

assert wall[2] == "Wall 01"
