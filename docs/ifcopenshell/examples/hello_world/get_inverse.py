# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): everything that references an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
print(model.get_inverse(wall))
# end::example

assert len(model.get_inverse(wall)) == 2
