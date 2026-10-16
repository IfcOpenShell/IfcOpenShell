# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): a shallow copy of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

wall = model.by_type("IfcWall")[0]

# tag::example
import ifcopenshell.util.element

wall_shallow_copy = ifcopenshell.util.element.copy(model, wall)
# end::example

assert wall_shallow_copy.ObjectPlacement == wall.ObjectPlacement
