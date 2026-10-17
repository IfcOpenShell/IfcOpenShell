# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): the STEP ID of an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(wall.id())
# end::example

assert wall.id() == 5
