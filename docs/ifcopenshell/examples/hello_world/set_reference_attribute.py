# This file was generated with the assistance of an AI coding tool.
#
# Hello, world! (Python): assigning a reference to another instance.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
wall = model.createIfcWall()
wall.OwnerHistory = model.createIfcOwnerHistory()
# end::example

assert wall.OwnerHistory.is_a("IfcOwnerHistory")
