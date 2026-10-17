# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the properties of a type.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

wall = next(wall for wall in model.by_type("IfcWall") if wall.IsTypedBy)

# tag::example
import ifcopenshell.util.element

wall_type = ifcopenshell.util.element.get_type(wall)
print(ifcopenshell.util.element.get_psets(wall_type))
# end::example

assert wall_type is not None
