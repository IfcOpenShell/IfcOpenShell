# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): inverse attributes.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(wall.IsDefinedBy)
# end::example

assert len(wall.IsDefinedBy) == 1
