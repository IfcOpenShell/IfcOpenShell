# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): traversing references.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(model.traverse(wall))
# Or, let's just go down one level deep
print(model.traverse(wall, max_levels=1))
# end::example

assert len(model.traverse(wall, max_levels=1)) > 1
