# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): a deep copy of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

wall = model.by_type("IfcWall")[0]

# tag::example
import ifcopenshell.util.element

wall_deep_copy = ifcopenshell.util.element.copy_deep(model, wall, exclude=None)
# end::example

assert wall_deep_copy.ObjectPlacement != wall.ObjectPlacement
