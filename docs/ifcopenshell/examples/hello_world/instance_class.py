# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): the class of an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
wall = model.by_type("IfcWall")[0]
print(wall.is_a())  # Returns 'IfcWall'
# end::example

assert wall.is_a() == "IfcWall"
