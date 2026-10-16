# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): counting the instances of a type.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
walls = model.by_type("IfcWall")
print(len(walls))
# end::example

assert len(walls) == 1
