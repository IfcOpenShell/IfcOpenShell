# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): modifying data.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])
wall = model.by_type("IfcWall")[0]

# tag::example
wall.Name = "My new wall name"
# end::example

assert wall.Name == "My new wall name"
