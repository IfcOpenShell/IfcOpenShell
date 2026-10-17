# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): get the type of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.element

wall = model.by_type("IfcWall")[0]
wall_type = ifcopenshell.util.element.get_type(wall)
print(f"The wall type of {wall.Name} is {wall_type.Name if wall_type else None}")
# end::example
