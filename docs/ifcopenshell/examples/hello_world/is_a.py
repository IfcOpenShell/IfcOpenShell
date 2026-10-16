# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): testing the class of an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(wall.is_a("IfcWall"))  # Returns True
print(wall.is_a("IfcElement"))  # Returns True
print(wall.is_a("IfcWindow"))  # Returns False
# end::example

assert wall.is_a("IfcElement") and not wall.is_a("IfcWindow")
