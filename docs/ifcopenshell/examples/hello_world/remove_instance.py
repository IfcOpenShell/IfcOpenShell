# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): removing an instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
model.remove(wall)
# end::example

assert not model.by_type("IfcWall")
