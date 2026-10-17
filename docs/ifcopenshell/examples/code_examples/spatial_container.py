# This file was generated with the assistance of an AI coding tool.
#
# Code examples (Python): find the spatial container of an element.

import sys

import ifcopenshell

model = ifcopenshell.open(sys.argv[1])

# tag::example
import ifcopenshell.util.element

wall = model.by_type("IfcWall")[0]
# Walls are typically located on a storey, equipment might be located in spaces, etc
container = ifcopenshell.util.element.get_container(wall)
print(f"The wall is located on {container.Name}")
# end::example

assert container.is_a("IfcBuildingStorey")
